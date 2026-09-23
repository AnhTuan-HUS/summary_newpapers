"""Module quản lý kết nối và lưu trữ vector vào Qdrant bằng LangChain QdrantVectorStore."""

from __future__ import annotations

import os
import uuid
from typing import Any, Optional
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels


class QdrantManager:
    """Quản lý kết nối tới Qdrant Vector DB và tích hợp cùng LangChain."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        collection_name: Optional[str] = None,
        vector_size: int = 768,  # Mặc định Gemini text-embedding-004 là 768 chiều
        distance: qmodels.Distance = qmodels.Distance.COSINE,
    ):
        self.host = host or os.getenv("QDRANT_HOST", "localhost")
        self.port = port or int(os.getenv("QDRANT_PORT", "6333"))
        self.collection_name = collection_name or os.getenv("QDRANT_COLLECTION", "news_articles")
        self.vector_size = vector_size
        self.distance = distance

        # Khởi tạo Qdrant Client trực tiếp
        self.client = QdrantClient(host=self.host, port=self.port, timeout=30.0)

    def ensure_collection(self) -> None:
        """Đảm bảo Collection tồn tại trong Qdrant, nếu chưa thì tạo mới."""
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]

        if self.collection_name not in collection_names:
            print(f"📦 Tạo mới Qdrant Collection '{self.collection_name}' (dim={self.vector_size}, distance={self.distance})...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qmodels.VectorParams(
                    size=self.vector_size,
                    distance=self.distance,
                ),
            )
        else:
            print(f"✅ Qdrant Collection '{self.collection_name}' đã tồn tại sẵn sàng.")

    def store_documents(
        self,
        documents: list[Document],
        embedding: Embeddings,
    ) -> list[str]:
        """Lưu trữ các Documents vào Qdrant thông qua LangChain QdrantVectorStore.
        
        Trả về danh sách vector_id (UUID) tương ứng cho từng Document.
        """
        if not documents:
            return []

        self.ensure_collection()

        # Tạo vector IDs duy nhất theo chuẩn UUID v4 cho Qdrant
        vector_ids = [str(uuid.uuid4()) for _ in documents]

        vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=embedding,
        )

        # Lưu tài liệu kèm IDs vào Qdrant
        vector_store.add_documents(documents=documents, ids=vector_ids)

        return vector_ids
