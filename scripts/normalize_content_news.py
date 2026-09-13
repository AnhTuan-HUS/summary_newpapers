"""Pipeline Step 2: normalize raw_articles -> articles.

Chạy luồng chuẩn hóa nội dung bài viết đã thu thập ở step 1.
"""

from __future__ import annotations

import argparse
from html import parser
import os
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.processor.normalize import process_batch, show_stats  # noqa: E402


def normalize_pipeline(
    limit: int = 200,
    offset: int = 0,
    dry_run: bool = False,
    verbose: bool = False,
    database_url: str | None = None,
) -> dict[str, int]:
    """Thực thi batch normalize cho raw_articles."""
    stats = process_batch(
        limit=limit,
        offset=offset,
        dry_run=dry_run,
        verbose=verbose,
        database_url=database_url,
    )
    print(f"📊 Normalize pipeline result: {stats}")
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chạy pipeline Step 2 normalize raw_articles -> articles",
    )
    parser.add_argument("--limit", type=int, default=200, help="Số lượng record tối đa xử lý.")
    parser.add_argument("--offset", type=int, default=0, help="Offset bắt đầu đọc dữ liệu.")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ kiểm tra và thống kê, không ghi DB.")
    parser.add_argument("--verbose", action="store_true", help="Hiển thị log chi tiết từng record.")
    parser.add_argument("--stats", action="store_true", help="Hiển thị thống kê tổng quan thay vì chạy batch.")
    args = parser.parse_args()

    if args.stats:
        show_stats()
        return

    normalize_pipeline(
        limit=args.limit,
        offset=args.offset,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
