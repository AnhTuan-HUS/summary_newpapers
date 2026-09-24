"""Pipeline điều phối quá trình xử lý vector hóa dữ liệu (Step 04).

Quy trình:
1. Lấy danh sách các bài viết ở trạng thái 'published' chưa được chia chunk.
2. Dùng LangChain RecursiveCharacterTextSplitter để tách thành các đoạn (chunks).
3. Đóng gói thành các LangChain Document kèm metadata.
4. Tạo embedding bằng Gemini và lưu vào Qdrant Vector DB.
5. Ghi nhận các chunks cùng vector_id vào bảng PostgreSQL 'article_chunks'.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from database.connection import get_database_url
from database.operations import get_unvectorized_articles, save_article_chunks
from scripts.vectorizer import NewsChunker, QdrantManager, get_gemini_embeddings


def process_vectorize_batch(
    limit: int = 20,
    database_url: Optional[str] = None,
    qdrant_host: Optional[str] = None,
    qdrant_port: Optional[int] = None,
    collection_name: Optional[str] = None,
    embedding_model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> dict[str, int]:
    """Lấy các bài viết published chưa vector hóa, chia chunk, lưu vào Qdrant và DB."""
    database_url = database_url or get_database_url()
    articles = get_unvectorized_articles(limit=limit, database_url=database_url)

    if not articles:
        print("ℹ️ Không có bài viết nào cần vector hóa (tất cả đã được lưu vào Qdrant / article_chunks).")
        return {"processed": 0, "success": 0, "failed": 0, "total_chunks": 0}

    print(f"🚀 Bắt đầu vector hóa cho {len(articles)} bài viết...")

    # Khởi tạo Chunker, Embeddings và Qdrant Manager
    chunker = NewsChunker(chunk_size=1200, chunk_overlap=200)
    embedding = get_gemini_embeddings(model_name=embedding_model, api_key=api_key)
    qdrant = QdrantManager(
        host=qdrant_host,
        port=qdrant_port,
        collection_name=collection_name,
        vector_size=3072,  
    )

    stats = {
        "processed": 0,
        "success": 0,
        "failed": 0,
        "total_chunks": 0,
    }

    for idx, article in enumerate(articles, 1):
        stats["processed"] += 1
        article_id = article["id"]
        title = article["title"]

        print(f"\n[{idx}/{len(articles)}] Xử lý bài viết ID: {article_id} - '{title[:60]}...'")

        try:
            # 1. Tách văn bản thành LangChain Documents
            docs = chunker.split_article(article)
            print(f"   ✂️ Chia thành {len(docs)} chunks...")

            # 2. Lưu vào Qdrant thông qua LangChain QdrantVectorStore
            vector_ids = qdrant.store_documents(documents=docs, embedding=embedding)
            print(f"   📥 Đã lưu {len(vector_ids)} vectors vào Qdrant collection '{qdrant.collection_name}'")

            # 3. Chuẩn bị dữ liệu lưu vào PostgreSQL bảng article_chunks
            chunks_records = []
            for doc, vid in zip(docs, vector_ids):
                chunks_records.append(
                    {
                        "article_id": article_id,
                        "chunk_index": doc.metadata["chunk_index"],
                        "chunk_text": doc.page_content,
                        "vector_id": vid,
                    }
                )

            # 4. Ghi nhận vào DB
            inserted_count = save_article_chunks(chunks_records, database_url=database_url)
            print(f"   ✅ Đã lưu {inserted_count} bản ghi vào bảng article_chunks")

            stats["success"] += 1
            stats["total_chunks"] += len(vector_ids)

        except Exception as err:
            print(f"   ❌ Lỗi khi vector hóa bài viết {article_id}: {err}")
            stats["failed"] += 1

        time.sleep(1.0)  # Nghỉ 1 giây tránh chạm giới hạn embedding rate limit

    print("\n" + "=" * 50)
    print(f"📊 KẾT QUẢ STEP 04 VECTORIZATION:")
    print(f" - Tổng bài đã xử lý  : {stats['processed']}")
    print(f" - Thành công          : {stats['success']}")
    print(f" - Thất bại             : {stats['failed']}")
    print(f" - Tổng số chunks lưu  : {stats['total_chunks']}")
    print("=" * 50)

    return stats


def main():
    limit = int(os.getenv("VECTORIZE_BATCH_LIMIT", "20"))
    process_vectorize_batch(limit=limit)


if __name__ == "__main__":
    main()
