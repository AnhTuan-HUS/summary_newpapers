"""Step 2: Content Normalization Pipeline.

Đọc các bản ghi raw_articles có status='SUCCESS' và canonical_article_id IS NULL, thực hiện:
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
    update_raw_article_status,
)


# ---------------------------------------------------------------------------
# Slug Extractor
# ---------------------------------------------------------------------------

_SLUG_CLEANUP_RE = re.compile(r"[^\w\-]")
_MULTI_DASH_RE = re.compile(r"-{2,}")


def extract_slug(url: str) -> str | None:
    """Bóc tách slug từ URL bài báo."""
    if not url:
        return None

    try:
        path = urlsplit(url).path.rstrip("/")
    except Exception:
        return None

    if not path:
        return None

    last_segment = path.split("/")[-1]
    last_segment = re.sub(r"\.[a-z]{2,4}$", "", last_segment, flags=re.IGNORECASE)

    if not last_segment:
        return None

    slug = _SLUG_CLEANUP_RE.sub("-", last_segment.lower())
    slug = _MULTI_DASH_RE.sub("-", slug).strip("-")

    return slug or None


def make_unique_slug(base_slug: str | None, raw_article_id: int) -> str:
    """Tạo slug duy nhất bằng cách thêm suffix là raw_article_id."""
    if base_slug:
        return f"{base_slug}-{raw_article_id}"
    return f"article-{raw_article_id}"


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def show_stats(database_url: str | None = None) -> None:
    """Hiển thị thống kê số lượng bản ghi theo trạng thái chuẩn trong DB."""
    from database.connection import get_connection

    try:
        with get_connection(database_url) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM raw_articles WHERE status IN ('pending', 'SUCCESS') AND canonical_article_id IS NULL;")
            pending_count = int(cursor.fetchone()[0])

            cursor.execute("SELECT COUNT(*) FROM raw_articles WHERE status = 'processed' OR (canonical_article_id IS NOT NULL AND status != 'duplicate');")
            processed_count = int(cursor.fetchone()[0])

            cursor.execute("SELECT COUNT(*) FROM raw_articles WHERE status IN ('duplicate', 'DUPLICATE');")
            duplicate_count = int(cursor.fetchone()[0])

            cursor.execute("SELECT COUNT(*) FROM raw_articles;")
            total_raw = int(cursor.fetchone()[0])

            cursor.execute("SELECT COUNT(*) FROM articles;")
            total_articles = int(cursor.fetchone()[0])
            cursor.close()
    except Exception as e:
        print(f"  ⚠️ Không thể kết nối DB: {e}")
        pending_count = processed_count = duplicate_count = total_raw = total_articles = 0

    print(f"\n  📊 Thống kê raw_articles theo trạng thái Schema:")
    print(f"     [pending]    Chờ normalize               : {pending_count}")
    print(f"     [processed]  Đã normalize thành công     : {processed_count}")
    print(f"     [duplicate]  Trùng lặp với bài khác       : {duplicate_count}")
    print(f"     --------------------------------------------------")
    print(f"     Tổng raw_articles                        : {total_raw}")
    print(f"     Tổng bài viết trong bảng articles        : {total_articles}\n")



# ---------------------------------------------------------------------------
# Core Processing
# ---------------------------------------------------------------------------

def process_batch(
    limit: int = 200,
    offset: int = 0,
    dry_run: bool = False,
    verbose: bool = False,
    database_url: str | None = None,
) -> dict[str, int]:
    """Xử lý một batch raw_articles: normalize → check deduplication → insert articles → update canonical."""
    from scripts.processor.dedup import find_duplicate_article
    from database.operations import get_recent_articles   # lấy các bài viết trong 3 ngày gần đây để làm candidate so sánh trùng lặp

    stats: dict[str, int] = {"processed": 0, "duplicates": 0, "failed": 0, "total": 0}

    rows = get_raw_articles_for_processing(
        limit=limit,
        offset=offset,
        database_url=database_url,
    )
    stats["total"] = len(rows)

    if not rows:
        print("  ℹ️  Không có bản ghi nào cần xử lý.")
        return stats

    # Lấy danh sách các bài viết trong 3 ngày gần đây từ `articles` để làm ứng viên so sánh trùng lặp
    candidates = get_recent_articles(days=3, limit=1000, database_url=database_url)

    print(f"  🔄 Bắt đầu normalize {len(rows)} bản ghi (offset={offset}, dry_run={dry_run})...")

    for raw in rows:
        raw_id: int = raw["id"]
        url: str = raw.get("external_url") or ""
        title: str = raw.get("title_raw") or ""
        content_raw: str | None = raw.get("content_raw")

        try:
            # 1. Normalize content
            normalized = normalize_content(content_raw)
            content: str | None = normalized.get("content_raw")  # type: ignore[assignment]
            thumbnail_url: dict[str, str] = normalized.get("thumbnail_url") or {}  # type: ignore[assignment]

            # 2. Extract slug
            base_slug = extract_slug(url)
            slug = make_unique_slug(base_slug, raw_id)

            # 3. Check Deduplication (So sánh trùng lặp với các bài đã có)
            dup_match = find_duplicate_article(title, content, candidates, threshold=0.80)

            if dup_match:
                canonical_id = dup_match["id"]
                if verbose:
                    print(f"  [TRÙNG LẶP] raw_id={raw_id} trùng với article_id={canonical_id} ('{dup_match.get('title')[:40]}...')")

                if not dry_run:
                    update_raw_article_canonical(raw_id, canonical_id, database_url=database_url)
                    update_raw_article_status(raw_id, "duplicate", database_url=database_url)

                stats["duplicates"] += 1
                continue

            if verbose:
                preview = (content or "")[:80].replace("\n", " ")
                media_count = len(thumbnail_url)
                print(f"  [{raw_id}] slug={slug} | media={media_count} | content={preview!r}...")

            if dry_run:
                stats["processed"] += 1
                continue

            # 4. Insert bài mới vào bảng articles (Canonical Article)
            article_data: dict[str, Any] = {
                "title": title,
                "slug": slug,
                "content": content,
                "thumbnail_url": thumbnail_url,
                "status": "draft",
                "published_at": raw.get("published_at"),
            }
            article_id = insert_article(article_data, database_url=database_url)

            # 5. Cập nhật canonical_article_id và status trong raw_articles
            update_raw_article_canonical(raw_id, article_id, database_url=database_url)
            update_raw_article_status(raw_id, "processed", database_url=database_url)

            # Bổ sung bài mới vừa insert vào danh sách candidates để so sánh cho các bài tiếp theo trong batch
            candidates.append({"id": article_id, "title": title, "slug": slug, "content": content})

            stats["processed"] += 1

            if verbose:
                print(f"       ✅ → articles.id={article_id}")

        except Exception as exc:
            stats["failed"] += 1
            print(f"  ❌ raw_article id={raw_id} ({url[:60]}): {exc}")

    return stats



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

    result = process_batch(
        limit=args.limit,
        offset=args.offset,
        dry_run=args.dry_run,
        verbose=args.verbose,
        database_url=args.database_url,
    )

    mode = "[DRY-RUN] " if args.dry_run else ""
    print(
        f"\n  {mode}✅ Kết quả: "
        f"processed={result['processed']} | "
        f"failed={result['failed']} | "
        f"total={result['total']}"
    )


if __name__ == "__main__":
    main()
