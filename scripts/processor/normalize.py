"""Step 2: Content Normalization Pipeline.

Đọc các bản ghi raw_articles có status='SUCCESS', thực hiện:
  1. normalize_content(content_raw)  -> content (plain text) + thumbnail_url (dict)
  2. Bóc tách slug từ external_url
  3. Insert vào bảng articles với status='draft'
  4. Cập nhật canonical_article_id trong raw_articles

Cách dùng:
    # Chạy toàn bộ (mặc định 200 bản ghi mỗi lần)
    python -m scripts.processor.normalize

    # Chỉ định limit / offset
    python -m scripts.processor.normalize --limit 50 --offset 0

    # Dry-run: chỉ in kết quả, không ghi DB
    python -m scripts.processor.normalize --dry-run

    # Xem thống kê số lượng cần xử lý
    python -m scripts.processor.normalize --stats
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

# Thêm project root vào sys.path để import module project
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.crawler.utils import normalize_content
from database.operations import (
    get_raw_articles_for_processing,
    insert_article,
    update_raw_article_canonical,
    update_raw_article_status
)


# ---------------------------------------------------------------------------
# Hàm bóc tách slug từ URL
# ---------------------------------------------------------------------------

def extract_slug_from_url(url: str) -> str | None:
    """Bóc tách phần slug từ URL bài báo.

    Chiến lược:
    - Lấy path cuối cùng của URL (phần sau dấu '/' cuối cùng).
    - Loại bỏ phần extension (.html, .htm, .aspx, ...).
    - Nếu path cuối là chuỗi số (ID thuần túy), lấy thêm phần trước nó.
    - Giới hạn độ dài slug tối đa 200 ký tự.

    Args:
        url: URL bài báo đầy đủ.

    Returns:
        str | None: Chuỗi slug hoặc None nếu không thể bóc tách.

    Examples:
        >>> extract_slug_from_url("https://vnexpress.net/gpt-5-sap-ra-mat-3456789.html")
        'gpt-5-sap-ra-mat-3456789'
        >>> extract_slug_from_url("https://techcrunch.com/2024/03/01/openai-releases-new-model/")
        'openai-releases-new-model'
    """
    if not url:
        return None

    try:
        parts = urlsplit(url.strip())
        path = parts.path.rstrip("/")
        if not path:
            return None

        # Lấy segment cuối cùng của path
        segments = [s for s in path.split("/") if s]
        if not segments:
            return None

        slug = segments[-1]

        # Loại bỏ phần extension phổ biến
        slug = re.sub(r"\.(html?|aspx?|php|jsp|shtml)$", "", slug, flags=re.IGNORECASE)

        # Nếu slug thuần số (vd: article ID), kết hợp với segment trước
        if re.fullmatch(r"\d+", slug) and len(segments) >= 2:
            slug = f"{segments[-2]}-{slug}"

        # Làm sạch: chỉ giữ lại ký tự hợp lệ cho slug
        slug = re.sub(r"[^\w\-]", "-", slug).strip("-")
        slug = re.sub(r"-{2,}", "-", slug)

        return slug[:200] if slug else None

    except Exception:
        return None


def make_unique_slug(base_slug: str, existing_slugs: set[str]) -> str:
    """Đảm bảo slug là duy nhất bằng cách thêm hậu tố số nếu cần.

    Args:
        base_slug: Slug cơ sở muốn sử dụng.
        existing_slugs: Tập hợp các slug đã tồn tại trong phiên xử lý hiện tại.

    Returns:
        str: Slug duy nhất.
    """
    if base_slug not in existing_slugs:
        return base_slug
    counter = 1
    while f"{base_slug}-{counter}" in existing_slugs:
        counter += 1
    return f"{base_slug}-{counter}"


# ---------------------------------------------------------------------------
# Hàm xử lý chính từng bản ghi
# ---------------------------------------------------------------------------

def process_raw_article(raw: dict[str, Any], existing_slugs: set[str]) -> dict[str, Any] | None:
    """Chuẩn hóa một bản ghi raw_article thành dữ liệu sẵn sàng insert vào bảng articles.

    Args:
        raw: Bản ghi raw_article (dict) lấy từ DB.
        existing_slugs: Tập slug đã dùng trong phiên xử lý hiện tại (để tránh trùng).

    Returns:
        dict | None: Dữ liệu article đã chuẩn hóa, hoặc None nếu không thể xử lý.
    """
    raw_id = raw.get("id")
    url = raw.get("external_url") or ""
    title_raw = raw.get("title_raw") or ""
    content_raw = raw.get("content_raw") or ""

    # 1. Bóc tách slug từ URL
    base_slug = extract_slug_from_url(url)
    if not base_slug:
        print(f"   ⚠️  [id={raw_id}] Không thể bóc tách slug từ URL: {url!r}")
        return None

    slug = make_unique_slug(base_slug, existing_slugs)
    existing_slugs.add(slug)

    # 2. Normalize content_raw -> content + thumbnail_url
    normalized = normalize_content(content_raw)
    content = normalized.get("content_raw")   # plain text sau normalize
    thumbnail_url = normalized.get("thumbnail_url") or {}

    # đổi trường status trong raw_articles từ 'pending' sang 'processed'
    update_raw_article_status(raw_id, "processed")

    return {
        "raw_article_id": raw_id,
        "title": title_raw,
        "slug": slug,
        "content": content,
        "thumbnail_url": thumbnail_url,
        "status": "draft",
        "published_at": raw.get("published_at"),
    }


# ---------------------------------------------------------------------------
# Pipeline chính
# ---------------------------------------------------------------------------

def run_pipeline(
    limit: int = 100,
    offset: int = 0,
    dry_run: bool = False,
    database_url: str | None = None,
    verbose: bool = False,
) -> dict[str, int]:
    """Chạy pipeline chuẩn hóa nội dung: raw_articles -> articles.

    Args:
        limit: Số bản ghi tối đa cần xử lý mỗi lần chạy.
        offset: Vị trí bắt đầu trong bảng raw_articles.
        dry_run: Nếu True, chỉ in kết quả mà không ghi vào DB.
        database_url: Chuỗi kết nối DB (nếu None sẽ dùng biến môi trường).
        verbose: In chi tiết từng bản ghi nếu True.

    Returns:
        dict: Thống kê kết quả {total, processed, inserted, skipped, errors}.
    """
    stats = {"total": 0, "processed": 0, "inserted": 0, "skipped": 0, "errors": 0}
    existing_slugs: set[str] = set()

    print(f"\n{'='*60}")
    print(f"  🚀 Step 2: Content Normalization Pipeline")
    print(f"{'='*60}")
    print(f"  📋 Limit: {limit} | Offset: {offset} | Dry-run: {dry_run}")
    print(f"{'='*60}\n")

    # Lấy dữ liệu raw_articles cần xử lý
    print(f"  📥 Đang lấy raw_articles từ DB (status=SUCCESS, canonical_article_id IS NULL)...")
    raw_articles = get_raw_articles_for_processing(
        limit=limit,
        offset=offset,
        database_url=database_url,
    )
    stats["total"] = len(raw_articles)
    print(f"  ✅ Tìm thấy {stats['total']} bản ghi cần xử lý.\n")

    if not raw_articles:
        print("  ℹ️  Không có bản ghi nào cần xử lý. Pipeline kết thúc.")
        return stats

    for i, raw in enumerate(raw_articles, 1):
        raw_id = raw.get("id")
        url = raw.get("external_url", "")
        title = (raw.get("title_raw") or "")[:60]

        if verbose:
            print(f"  [{i:>4}/{stats['total']}] id={raw_id} | {title!r}")
            print(f"         URL: {url}")

        try:
            article_data = process_raw_article(raw, existing_slugs)

            if article_data is None:
                stats["skipped"] += 1
                if not verbose:
                    print(f"  ⏭️  [{i:>4}] id={raw_id} - Bỏ qua (không thể bóc tách slug)")
                continue

            stats["processed"] += 1

            if dry_run:
                print(f"  🔍 [DRY-RUN] id={raw_id} | slug={article_data['slug']!r}")
                if verbose:
                    content_preview = (article_data.get("content") or "")[:80]
                    media_count = len(article_data.get("thumbnail_url") or {})
                    print(f"         content: {content_preview!r}...")
                    print(f"         media: {media_count} items")
                continue

            # Insert vào bảng articles
            article_id = insert_article(article_data, database_url=database_url)

            if article_id == -1:
                # Slug đã tồn tại, bỏ qua
                stats["skipped"] += 1
                if verbose:
                    print(f"         ⏭️  Slug đã tồn tại, bỏ qua.")
                else:
                    print(f"  ⏭️  [{i:>4}] id={raw_id} - Slug '{article_data['slug']}' đã tồn tại")
            else:
                # Cập nhật canonical_article_id trong raw_articles
                update_raw_article_canonical(
                    raw_article_id=raw_id,
                    article_id=article_id,
                    database_url=database_url,
                )
                stats["inserted"] += 1
                if verbose:
                    print(f"         ✅ Đã insert articles.id={article_id} | slug={article_data['slug']!r}")
                else:
                    print(f"  ✅ [{i:>4}] id={raw_id} -> articles.id={article_id} | slug={article_data['slug']!r}")

        except Exception as err:
            stats["errors"] += 1
            print(f"  ❌ [{i:>4}] id={raw_id} - Lỗi: {err}")
            if verbose:
                import traceback
                traceback.print_exc()

    # In thống kê cuối
    print(f"\n{'='*60}")
    print(f"  📊 Kết quả pipeline:")
    print(f"     Tổng bản ghi lấy về  : {stats['total']}")
    print(f"     Đã xử lý (normalize)  : {stats['processed']}")
    print(f"     Đã insert articles     : {stats['inserted']}")
    print(f"     Bỏ qua (trùng/lỗi slug): {stats['skipped']}")
    print(f"     Lỗi                   : {stats['errors']}")
    print(f"{'='*60}\n")

    return stats


def show_stats(database_url: str | None = None) -> None:
    """Hiển thị thống kê số lượng bản ghi cần xử lý."""
    from database.operations import count_raw_articles

    total_success = count_raw_articles(status="SUCCESS", database_url=database_url)

    try:
        from database.connection import get_connection
        with get_connection(database_url) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*) FROM raw_articles
                WHERE status = 'pending'
                  AND canonical_article_id IS NULL
                  AND content_raw IS NOT NULL;
                """
            )
            row = cursor.fetchone()
            pending = int(row[0]) if row else 0
            cursor.close()
    except Exception:
        pending = 0

    print(f"\n  📊 Thống kê raw_articles:")
    print(f"     Tổng status=SUCCESS              : {total_success}")
    print(f"     Chờ normalize (canonical IS NULL) : {pending}")
    print(f"     Đã xử lý (canonical IS NOT NULL)  : {total_success - pending}\n")


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Step 2 - Content Normalization: raw_articles -> articles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=200,
        help="Số bản ghi tối đa cần xử lý (mặc định: 200)",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Vị trí bắt đầu trong raw_articles (mặc định: 0)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Chỉ in kết quả, không ghi vào DB",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Hiển thị thống kê số lượng bản ghi cần xử lý rồi thoát",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="In chi tiết từng bản ghi",
    )
    parser.add_argument(
        "--database-url",
        type=str,
        default=None,
        help="Chuỗi kết nối PostgreSQL (nếu bỏ trống sẽ dùng biến môi trường DATABASE_URL)",
    )

    args = parser.parse_args()

    if args.stats:
        show_stats(database_url=args.database_url)
        return

    run_pipeline(
        limit=args.limit,
        offset=args.offset,
        dry_run=args.dry_run,
        database_url=args.database_url,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
