"""Module quản lý Qdrant cho Hybrid Search: mỗi point gồm 1 dense vector + 1 sparse vector."""

from __future__ import annotations

import os
import uuid
from typing import Any, Optional

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from qdrant_client import QdrantClient, models

from scripts.vectorizer.embedder import VietnameseSparseEmbedder

DENSE_VECTOR_NAME = "dense"
SPARSE_VECTOR_NAME = "sparse"


class QdrantManager:
    """Quản lý kết nối Qdrant, lưu trữ và tìm kiếm Hybrid (Dense + Sparse BM25)."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        collection_name: Optional[str] = None,
        vector_size: int = 3072,
        distance: models.Distance = models.Distance.COSINE,
    ):
        self.host = host or os.getenv("QDRANT_HOST", "localhost")
        self.port = port or int(os.getenv("QDRANT_PORT", "6333"))
        self.collection_name = collection_name or os.getenv("QDRANT_COLLECTION", "news_articles")
        self.vector_size = vector_size
        self.distance = distance

        self.client = QdrantClient(host=self.host, port=self.port, timeout=30.0)

        # Tên dense vector thực tế trong collection:
        #  - collection mới  -> "dense"
        #  - collection cũ (tạo bởi LangChain, vector không tên) -> ""
        self.dense_vector_name: str = DENSE_VECTOR_NAME
        self.sparse_vector_name: str = SPARSE_VECTOR_NAME
        self._collection_ensured = False

    # ------------------------------------------------------------------ #
    # Collection
    # ------------------------------------------------------------------ #
    def ensure_collection(self) -> None:
        """Đảm bảo collection tồn tại và có đủ dense + sparse vector (idempotent)."""
        if self._collection_ensured:
            return

        sparse_params = models.SparseVectorParams(modifier=models.Modifier.IDF)

        if not self.client.collection_exists(self.collection_name):
            print(f"📦 Tạo mới Hybrid Collection '{self.collection_name}' (dense={self.vector_size}d + sparse BM25)...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    DENSE_VECTOR_NAME: models.VectorParams(size=self.vector_size, distance=self.distance),
                },
                sparse_vectors_config={SPARSE_VECTOR_NAME: sparse_params},
            )
            self.dense_vector_name = DENSE_VECTOR_NAME
        else:
            params = self.client.get_collection(self.collection_name).config.params
            self.dense_vector_name = self._detect_dense_vector_name(params.vectors)
            existing_sparse = params.sparse_vectors or {}

            if SPARSE_VECTOR_NAME not in existing_sparse:
                print(f"➕ Bổ sung sparse vector '{SPARSE_VECTOR_NAME}' vào collection '{self.collection_name}'...")
                self.client.create_vector_name(
                    collection_name=self.collection_name,
                    vector_name=SPARSE_VECTOR_NAME,
                    vector_name_config=models.SparseVectorNameConfig(
                        sparse=models.SparseVectorConfig(modifier=models.Modifier.IDF)
                    ),
                )
            elif existing_sparse[SPARSE_VECTOR_NAME].modifier != models.Modifier.IDF:
                # BM25 của FastEmbed cần Qdrant tính IDF
                self.client.update_collection(
                    collection_name=self.collection_name,
                    sparse_vectors_config={SPARSE_VECTOR_NAME: sparse_params},
                )

            print(
                f"✅ Collection '{self.collection_name}' sẵn sàng "
                f"(dense='{self.dense_vector_name}', sparse='{SPARSE_VECTOR_NAME}')."
            )

        self._collection_ensured = True

    @staticmethod
    def _detect_dense_vector_name(vectors_config: Any) -> str:
        if isinstance(vectors_config, dict):
            if DENSE_VECTOR_NAME in vectors_config:
                return DENSE_VECTOR_NAME
            if "" in vectors_config:
                return ""
            return next(iter(vectors_config))
        # VectorParams đơn (không tên) -> vector mặc định ""
        return ""

    def _dense_using(self) -> Optional[str]:
        """Giá trị `using` cho query: None nghĩa là vector mặc định (không tên)."""
        return self.dense_vector_name or None

    # ------------------------------------------------------------------ #
    # Write
    # ------------------------------------------------------------------ #
    def store_documents(
        self,
        documents: list[Document],
        dense_embedding: Embeddings,
        sparse_embedding: VietnameseSparseEmbedder,
        batch_size: int = 64,
    ) -> list[str]:
        """Sinh dense + sparse cho mỗi chunk và lưu thành 1 point trong collection.

        Payload giữ format LangChain (`page_content`, `metadata`) để tương thích dữ liệu cũ.
        Trả về danh sách vector_id (UUID) theo đúng thứ tự `documents`.
        """
        if not documents:
            return []

        self.ensure_collection()
        vector_ids = [str(uuid.uuid4()) for _ in documents]

        for start in range(0, len(documents), batch_size):
            batch_docs = documents[start : start + batch_size]
            batch_ids = vector_ids[start : start + batch_size]
            texts = [doc.page_content for doc in batch_docs]

            dense_vectors = dense_embedding.embed_documents(texts)
            sparse_vectors = sparse_embedding.embed_documents(texts)

            points = [
                models.PointStruct(
                    id=point_id,
                    vector={
                        self.dense_vector_name: dense_vec,
                        self.sparse_vector_name: sparse_vec,
                    },
                    payload={"page_content": doc.page_content, "metadata": doc.metadata},
                )
                for point_id, doc, dense_vec, sparse_vec in zip(batch_ids, batch_docs, dense_vectors, sparse_vectors)
            ]
            self.client.upsert(collection_name=self.collection_name, points=points, wait=True)

        return vector_ids

    # ------------------------------------------------------------------ #
    # Search
    # ------------------------------------------------------------------ #
    def hybrid_search(
        self,
        query: str,
        dense_embedding: Embeddings,
        sparse_embedding: VietnameseSparseEmbedder,
        top_k: int = 5,
        prefetch_limit: Optional[int] = None,
        query_filter: Optional[models.Filter] = None,
    ) -> list[tuple[Document, float]]:
        """Tìm kiếm Hybrid: dense (ngữ nghĩa) + sparse (BM25), gộp bằng RRF."""
        self.ensure_collection()
        limit = prefetch_limit or max(top_k * 4, 20)

        response = self.client.query_points(
            collection_name=self.collection_name,
            prefetch=[
                models.Prefetch(
                    query=dense_embedding.embed_query(query),
                    using=self._dense_using(),
                    limit=limit,
                    filter=query_filter,
                ),
                models.Prefetch(
                    query=sparse_embedding.embed_query(query),
                    using=self.sparse_vector_name,
                    limit=limit,
                    filter=query_filter,
                ),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=top_k,
            with_payload=True,
        )
        return [self._to_document(point) for point in response.points]

    @staticmethod
    def _to_document(point: models.ScoredPoint) -> tuple[Document, float]:
        payload = point.payload or {}
        metadata = dict(payload.get("metadata") or {})
        metadata["_id"] = str(point.id)
        return Document(page_content=payload.get("page_content", ""), metadata=metadata), point.score
