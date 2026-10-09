"""Migration: bổ sung sparse vector (BM25) cho các point cũ chỉ có dense vector.

- KHÔNG gọi lại Gemini: dense vector cũ được giữ nguyên, chỉ thêm vector 'sparse'.
- Point ID giữ nguyên -> cột `article_chunks.vector_id` trong PostgreSQL vẫn hợp lệ.
- Idempotent: point nào đã có sparse vector sẽ được bỏ qua (trừ khi dùng --force).

Cách dùng:
    python scripts/migrate_sparse_vectors.py --dry-run
    python scripts/migrate_sparse_vectors.py
    python scripts/migrate_sparse_vectors.py --collection qdrant-collections --batch-size 100
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

from qdrant_client import models  # noqa: E402

from scripts.vectorizer import QdrantManager, VietnameseSparseEmbedder  # noqa: E402


def migrate(
    collection_name: str | None,
    host: str | None,
    port: int | None,
    batch_size: int,
    limit: int | None,
    force: bool,
    dry_run: bool,
) -> dict[str, int]:
    qdrant = QdrantManager(host=host, port=port, collection_name=collection_name)
    client = qdrant.client
    name = qdrant.collection_name

    if not client.collection_exists(name):
        raise SystemExit(f"❌ Collection '{name}' không tồn tại trên {qdrant.host}:{qdrant.port}")

    total_points = client.count(name, exact=True).count
    print(f"🔗 Qdrant {qdrant.host}:{qdrant.port} | collection='{name}' | tổng {total_points} points")

    if dry_run:
        params = client.get_collection(name).config.params
        print(f"   Dense config : {params.vectors}")
        print(f"   Sparse config: {params.sparse_vectors}")
    else:
        # Thêm cấu hình sparse vector vào collection nếu chưa có
        qdrant.ensure_collection()

    sparse_embedder = VietnameseSparseEmbedder()
    sparse_name = qdrant.sparse_vector_name
    stats = {"scanned": 0, "updated": 0, "skipped_has_sparse": 0, "skipped_no_text": 0}

    offset = None
    started = time.time()
    while True:
        points, offset = client.scroll(
            collection_name=name,
            limit=batch_size,
            offset=offset,
            with_payload=True,
            # Chỉ lấy sparse vector (nếu có) để kiểm tra, không tải dense 3072 chiều
            with_vectors=[sparse_name] if not dry_run else False,
        )
        if not points:
            break

        todo_ids, todo_texts = [], []
        for point in points:
            stats["scanned"] += 1
            vectors = point.vector if isinstance(point.vector, dict) else {}
            if not force and vectors.get(sparse_name):
                stats["skipped_has_sparse"] += 1
                continue

            payload = point.payload or {}
            text = payload.get("page_content") or payload.get("text") or ""
            if not text.strip():
                stats["skipped_no_text"] += 1
                continue

            todo_ids.append(point.id)
            todo_texts.append(text)

        if todo_ids and not dry_run:
            sparse_vectors = sparse_embedder.embed_documents(todo_texts)
            client.update_vectors(
                collection_name=name,
                points=[
                    models.PointVectors(id=pid, vector={sparse_name: vec})
                    for pid, vec in zip(todo_ids, sparse_vectors)
                ],
                wait=True,
            )
        stats["updated"] += len(todo_ids)

        print(
            f"   ⏳ {stats['scanned']}/{total_points} quét | "
            f"{'sẽ cập nhật' if dry_run else 'đã cập nhật'}: {stats['updated']}"
        )

        if offset is None or (limit and stats["scanned"] >= limit):
            break

    elapsed = time.time() - started
    print("\n" + "=" * 55)
    print(f"📊 KẾT QUẢ MIGRATION SPARSE {'(DRY-RUN)' if dry_run else ''}")
    print(f" - Đã quét                 : {stats['scanned']}")
    print(f" - {'Sẽ cập nhật' if dry_run else 'Đã cập nhật'}             : {stats['updated']}")
    print(f" - Bỏ qua (đã có sparse)   : {stats['skipped_has_sparse']}")
    print(f" - Bỏ qua (thiếu text)     : {stats['skipped_no_text']}")
    print(f" - Thời gian               : {elapsed:.1f}s")
    print("=" * 55)
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Bổ sung sparse vector BM25 cho các point Qdrant cũ.")
    parser.add_argument("--collection", default=None, help="Tên collection (mặc định: QDRANT_COLLECTION)")
    parser.add_argument("--host", default=None, help="Qdrant host (mặc định: QDRANT_HOST)")
    parser.add_argument("--port", type=int, default=None, help="Qdrant port (mặc định: QDRANT_PORT)")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--limit", type=int, default=None, help="Chỉ xử lý N point đầu (để test)")
    parser.add_argument("--force", action="store_true", help="Tính lại sparse kể cả point đã có")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ thống kê, không ghi gì vào Qdrant")
    args = parser.parse_args()

    migrate(
        collection_name=args.collection,
        host=args.host,
        port=args.port,
        batch_size=args.batch_size,
        limit=args.limit,
        force=args.force,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
