#!/usr/bin/env python3
"""Script CLI thực thi Step 03: Hiểu tin tức & Bổ sung tri thức AI (News Understanding & Enrichment)."""

import argparse
import sys
from pathlib import Path

# Thêm root directory vào sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from scripts.enricher.pipeline import process_enrichment_batch


def main():
    parser = argparse.ArgumentParser(
        description="Step 03: LLM News Understanding & Enrichment CLI"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Số lượng bài viết draft tối đa cần xử lý trong 1 lần (Default: 10)",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="openai",
        choices=["openai", "gemini"],
        help="LLM Provider sử dụng (openai hoặc gemini)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Tên model LLM cụ thể (Ví dụ: gpt-4o-mini, gemini-2.5-flash)",
    )

    args = parser.parse_args()

    process_enrichment_batch(
        limit=args.limit,
        provider=args.provider,
        model_name=args.model,
    )


if __name__ == "__main__":
    main()
