"""CLI Entrypoint thu thập dữ liệu thô (Raw HTML Crawler).

Mục đích:
    Chỉ thực hiện cào dữ liệu thô và lưu vào bảng `raw_articles`.
    - `content_raw` = toàn bộ text của trang HTML đã tải về (CHƯA bóc tách bất kỳ thứ gì).
    - `title_raw`   = tiêu đề phát hiện từ RSS/API/HTML, đã chuẩn hóa (strip + collapse whitespace).
    - Không phân tích cấu trúc bài viết, không trích xuất đoạn văn hay thẻ HTML cụ thể.

Quy trình:
    1. Stage 1 (Discovery): Quét RSS/API/Listing HTML để lấy danh sách bài mới.
    2. Deduplication: Lọc bài đã có trong DB (raw_articles.external_url).
    3. Stage 2 (Raw Fetch): Tải toàn bộ HTML trang, KHÔNG parse nội dung.
    4. Storage: Lưu trực tiếp vào PostgreSQL (raw_articles).
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Đảm bảo import được các module gốc của dự án như `database`
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from crawler.registry import registry
from crawler.collectors import get_collector_for_source
from crawler.utils import normalize_url


# Thư mục lưu dữ liệu thô ra local
CRAWL_RAW_ROOT = PROJECT_ROOT / "crawl_raw"


# ---------------------------------------------------------------------------
# Hàm tiện ích
# ---------------------------------------------------------------------------

def normalize_title(title: str | None) -> str | None:
    """Chuẩn hóa tiêu đề: thu gọn khoảng trắng thừa, loại bỏ ký tự xuống dòng.

    Args:
        title: Chuỗi tiêu đề thô.

    Returns:
        Chuỗi tiêu đề đã chuẩn hóa, hoặc None nếu rỗng.
    """
    if not title:
        return None
    cleaned = title.replace("\r", " ").replace("\n", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or None


def _url_hash(url: str) -> str:
    """Tạo hash SHA-256 16 ký tự từ URL để đặt tên file."""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def save_local_raw(
    html: str,
    raw_article: dict,
    fetched_at: datetime,
    source_name: str,
) -> str | None:
    """Lưu HTML thô và metadata JSON ra thư mục crawl_raw/.

    Cấu trúc thư mục:
        crawl_raw/
          <source>/
            <YYYY>/<MM>/<DD>/
              <hash>_<HHMMSS>.html.gz   ← HTML nguyên bản nén gzip
              <hash>_<HHMMSS>.json      ← metadata bài viết

    Args:
        html: Nội dung HTML thô.
        raw_article: Dict metadata bài viết.
        fetched_at: Thời điểm tải trang.
        source_name: Tên nguồn báo.

    Returns:
        Đường dẫn file HTML đã lưu, hoặc None nếu lỗi.
    """
    try:
        url = str(raw_article.get("url") or raw_article.get("external_url") or "")
        date_path = fetched_at.strftime("%Y/%m/%d")
        file_id = f"{_url_hash(url)}_{fetched_at.strftime('%H%M%S')}"

        html_path = CRAWL_RAW_ROOT / source_name / date_path / f"{file_id}.html.gz"
        json_path = CRAWL_RAW_ROOT / source_name / date_path / f"{file_id}.json"

        html_path.parent.mkdir(parents=True, exist_ok=True)

        # Lưu HTML nén gzip
        if html and html.strip():
            with gzip.open(html_path, "wt", encoding="utf-8") as f:
                f.write(html)

        # Lưu metadata JSON đầy đủ, bao gồm content_raw (toàn bộ HTML text)
        meta_to_save = dict(raw_article)
        meta_to_save["html_file"] = str(html_path.relative_to(PROJECT_ROOT))
        json_path.write_text(
            json.dumps(meta_to_save, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

        return str(html_path)
    except Exception as err:
        print(f"   ⚠️ Lỗi lưu local: {err}")
        return None


def extract_content_block(html: str, config) -> str | None:
    """Trích xuất block HTML nội dung bài viết, giữ nguyên thẻ img/video bên trong.

    Chiến lược:
    1. Dùng content_paragraphs selectors từ YAML config để xác định container nội dung.
       Ví dụ: '.fck_detail p' → thử tìm '.fck_detail' là container.
    2. Nếu không tìm thấy container trực tiếp, lấy parent chung của các đoạn văn match.
    3. Áp dụng strip_elements từ config để loại bỏ quảng cáo, script, style.
    4. Trả về chuỗi HTML của block nội dung (giữ nguyên <img>, <video>, <figure>).

    Args:
        html: HTML đầy đủ của trang.
        config: SourceConfig chứa selectors và clean_rules.

    Returns:
        Chuỗi HTML của block nội dung, hoặc None nếu không tìm thấy.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return None

    soup = BeautifulSoup(html, "lxml")
    selectors = config.parser.selectors
    clean_rules = config.parser.clean_rules

    content_node = None

    # Bước 1: Suy ra selector container từ content_paragraphs
    # Ví dụ: '.fck_detail p' → '.fck_detail' | 'article p' → 'article'
    for sel in selectors.content_paragraphs:
        parts = sel.rsplit(" ", 1)
        container_sel = parts[0].strip() if len(parts) > 1 else sel.strip()
        node = soup.select_one(container_sel)
        if node:
            content_node = node
            break

    # Bước 2: Fallback — lấy parent của nhóm đoạn văn match nhiều nhất
    if not content_node:
        for sel in selectors.content_paragraphs:
            matched = soup.select(sel)
            if matched:
                content_node = matched[0].parent
                break

    if not content_node:
        return None

    # Bước 3: Xóa phần tử rác trong block nội dung (quảng cáo, script, style...)
    for strip_sel in clean_rules.strip_elements:
        for elem in content_node.select(strip_sel):
            elem.decompose()
    # Luôn xóa script/style/noscript dù không khai báo trong config
    for tag in content_node.find_all(["script", "style", "noscript", "iframe"]):
        tag.decompose()

    # Bước 4: Trả về HTML của block nội dung (giữ nguyên img, video, figure)
    return str(content_node)


def fetch_raw_html(url: str, source_name: str, timeout: int = 20) -> tuple[str, str, int | None]:
    """Tải toàn bộ nội dung HTML của một URL mà KHÔNG bóc tách cấu trúc.

    Args:
        url: URL bài viết đã chuẩn hóa.
        source_name: Tên định danh nguồn báo.
        timeout: Thời gian chờ tối đa (giây).

    Returns:
        Tuple gồm (html_text, final_url, http_status).
        html_text là chuỗi HTML thô nguyên bản.
    """
    config = registry.resolve_config(source_name=source_name, url=url)
    effective_timeout = timeout or config.fetcher.timeout

    fetcher = registry.create_fetcher(config, timeout=effective_timeout)
    try:
        response = fetcher.fetch(url)
        html = str(response.get("html") or "")
        final_url = str(response.get("final_url") or url)
        http_status = response.get("http_status")

        # Adaptive Fallback sang Selenium nếu HTTP 403 hoặc HTML rỗng
        if (not html.strip() or http_status == 403) and config.fetcher.type == "http":
            try:
                from crawler.fetchers import selenium_fetcher
                sf = selenium_fetcher.SeleniumFetcher(timeout=effective_timeout)
                try:
                    sel_resp = sf.fetch(url)
                    if sel_resp.get("html") and str(sel_resp.get("html")).strip():
                        html = str(sel_resp.get("html"))
                        final_url = str(sel_resp.get("final_url") or final_url)
                        http_status = sel_resp.get("http_status")
                finally:
                    sf.close()
            except Exception:
                pass

        return html, final_url, http_status if isinstance(http_status, int) else None
    finally:
        fetcher.close()


# ---------------------------------------------------------------------------
# Xử lý từng nguồn
# ---------------------------------------------------------------------------

def process_source_raw(
    source_name: str,
    limit: int = 10,
    force: bool = False,
    delay: float = 1.5,
    save_db: bool = True,
    save_local: bool = False,
) -> dict[str, int]:
    """Thu thập dữ liệu HTML thô cho một nguồn cụ thể.

    Args:
        source_name: Tên định danh nguồn.
        limit: Số bài tối đa cần phát hiện.
        force: Bỏ qua kiểm tra trùng lặp nếu True.
        delay: Khoảng trễ cơ sở giữa các request (giây).
        save_db: Lưu vào PostgreSQL nếu True.
        save_local: Lưu HTML + JSON ra crawl_raw/ nếu True.

    Returns:
        Dict thống kê {discovered, skipped, success, failed}.
    """
    config = registry.get_config_by_name(source_name)
    if not config:
        print(f"❌ Không tìm thấy cấu hình cho nguồn: '{source_name}'")
        return {"discovered": 0, "skipped": 0, "success": 0, "failed": 0}

    print(f"\n{'='*70}")
    print(f"📡 CÀO THÔ NGUỒN: [{config.display_name or config.source_name}]")
    print(f"   Kênh: {config.channel_type.upper()} | Giới hạn: {limit} bài | Lưu DB: {'BẬT' if save_db else 'TẮT'} | Lưu Local: {'BẬT' if save_local else 'TẮT'}")
    print(f"{'='*70}")

    # --- Stage 1: Discovery ---
    collector = get_collector_for_source(config)
    t0 = time.time()
    discovered_items = collector.collect(config, limit=limit)
    print(f"🔍 [Discovery] Tìm thấy {len(discovered_items)} bài ({time.time() - t0:.2f}s)")

    # --- Batch Deduplication qua DB ---
    existing_db_urls: set[str] = set()
    if not force and discovered_items:
        try:
            from database.operations import get_existing_urls
            existing_db_urls = get_existing_urls([item.url for item in discovered_items])
        except Exception as err:
            print(f"⚠️ Kiểm tra trùng lặp thất bại: {err}")

    stats = {"discovered": len(discovered_items), "skipped": 0, "success": 0, "failed": 0}

    # --- Stage 2: Raw HTML Fetch & Save ---
    for idx, item in enumerate(discovered_items, 1):
        clean_url = normalize_url(item.url.strip())
        title = normalize_title(item.title)
        print(f"\n[{idx:02d}/{len(discovered_items):02d}] {title or clean_url[:70]}")

        # Kiểm tra trùng lặp
        if not force and clean_url in existing_db_urls:
            print("   ⏩ BỎ QUA (Đã tồn tại trong DB `raw_articles`)")
            stats["skipped"] += 1
            continue

        # Delay lịch sự
        if delay > 0:
            time.sleep(delay + random.uniform(0.3, 1.0))

        fetched_at = datetime.now(timezone.utc)
        crawl_status = "UNKNOWN_ERROR"
        error_msg: str | None = None
        html = ""
        final_url = clean_url
        content_raw = None

        try:
            html, final_url, http_status = fetch_raw_html(
                url=clean_url,
                source_name=config.source_name,
            )

            if not html.strip():
                crawl_status = "EMPTY_HTML"
                error_msg = "HTML trả về rỗng"
                print(f"   ⚠️ HTML RỖNG")
            else:
                # Trích xuất block nội dung bài viết (giữ img/video trong content)
                content_raw = extract_content_block(html, config)
                if content_raw:
                    crawl_status = "SUCCESS"
                    print(f"   ✅ ĐÃ TẢI HTML ({len(html):,} ký tự) | Content block: {len(content_raw):,} ký tự")
                else:
                    crawl_status = "CONTENT_NOT_FOUND"
                    error_msg = "Không tìm thấy block nội dung qua selector"
                    print(f"   ⚠️ CONTENT BLOCK KHÔNG TÌM THẤY ({len(html):,} ký tự HTML)")

        except Exception as exc:
            crawl_status = "UNKNOWN_ERROR"
            error_msg = str(exc)
            print(f"   ❌ LỖI: {exc}")

        # Cấu trúc raw_article để lưu DB
        raw_article: dict[str, object] = {
            "source":               config.source_name,
            "canonical_article_id": None,
            "external_url":         final_url or clean_url,
            "url":                  clean_url,
            "title_raw":            title,
            # content_raw = HTML block nội dung bài viết (giữ img/video), không phải toàn trang
            "content_raw":          content_raw,
            "author":               normalize_title(item.author) if hasattr(item, "author") and item.author else None,
            "published_at":         item.published_at if hasattr(item, "published_at") else None,
            "collected_at":         fetched_at.isoformat(),
            "crawl_status":         crawl_status,
            "error":                error_msg,
        }

        # Lưu local crawl_raw/ (HTML.gz + JSON)
        if save_local and html.strip():
            saved_path = save_local_raw(
                html=html,
                raw_article=raw_article,
                fetched_at=fetched_at,
                source_name=config.source_name,
            )
            if saved_path:
                print(f"   📁 Lưu local: {saved_path}")

        if save_db:
            try:
                from database.operations import save_crawl_result_to_db
                db_res = save_crawl_result_to_db(raw_article)
                print(f"   💾 Lưu DB: raw_article_id={db_res.get('raw_article_id')}")
                stats["success"] += 1
            except Exception as db_err:
                print(f"   ⚠️ Lỗi lưu DB: {db_err}")
                stats["failed"] += 1
        else:
            # Chỉ thống kê, không lưu DB
            if crawl_status == "SUCCESS":
                stats["success"] += 1
            else:
                stats["failed"] += 1

    return stats


# ---------------------------------------------------------------------------
# Hàm điều phối chính (có thể import từ Airflow / script khác)
# ---------------------------------------------------------------------------

def run_raw_collector(
    source: str | None = None,
    channel_type: str = "all",
    limit: int = 10,
    force: bool = False,
    delay: float = 1.5,
    save_db: bool = True,
    save_local: bool = False,
    from_db: bool = True,
    all_sources: bool = False,
) -> dict[str, int]:
    """Điều phối thu thập HTML thô cho nhiều nguồn.

    Args:
        source: Tên nguồn cụ thể. None = theo channel_type hoặc all_sources.
        channel_type: Lọc theo loại kênh ('all', 'rss', 'api', 'html').
        limit: Số bài tối đa mỗi nguồn.
        force: Bỏ qua deduplication.
        delay: Khoảng trễ giữa các request (giây).
        save_db: Lưu vào PostgreSQL.
        save_local: Lưu HTML thô + JSON ra crawl_raw/.
        from_db: Nạp cấu hình nguồn từ DB.
        all_sources: Chạy tất cả nguồn đã đăng ký.

    Returns:
        Dict thống kê tổng hợp.
    """
    if from_db:
        registry.load_from_db()

    all_configs = registry.get_all_configs() if hasattr(registry, "get_all_configs") else registry._configs

    target_sources: list[str] = []
    if source:
        target_sources = [source.lower().strip()]
    elif all_sources:
        target_sources = list(all_configs.keys())
    else:
        for name, cfg in all_configs.items():
            if channel_type == "all" or cfg.channel_type == channel_type:
                target_sources.append(name)

    if not target_sources:
        print("⚠️ Không có nguồn nào phù hợp.")
        print(f"   Nguồn khả dụng: {list(all_configs.keys())}")
        return {"discovered": 0, "skipped": 0, "success": 0, "failed": 0}

    print(f"\n🚀 THU THẬP DỮ LIỆU HTML THÔ")
    print(f"   Nguồn thực thi ({len(target_sources)}): {target_sources}")
    print(f"   Nạp từ DB: {'BẬT' if from_db else 'TẮT'} | Lưu DB: {'BẬT' if save_db else 'TẮT'} | Lưu Local: {'BẬT' if save_local else 'TẮT'} | Force: {'BẬT' if force else 'TẮT'}")

    total = {"discovered": 0, "skipped": 0, "success": 0, "failed": 0}
    t_start = time.time()

    for src in target_sources:
        src_stat = process_source_raw(
            source_name=src,
            limit=limit,
            force=force,
            delay=delay,
            save_db=save_db,
            save_local=save_local,
        )
        for key in total:
            total[key] += src_stat[key]

    elapsed = time.time() - t_start
    print(f"\n{'='*70}")
    print(f"📊 BÁO CÁO THU THẬP HTML THÔ")
    print(f"{'='*70}")
    print(f"   - Phát hiện (Discovered): {total['discovered']}")
    print(f"   - Bỏ qua trùng (Skipped): {total['skipped']}")
    print(f"   - Thành công  (Success):  {total['success']}")
    print(f"   - Thất bại    (Failed):   {total['failed']}")
    print(f"   - Thời gian:              {elapsed:.2f}s")
    print(f"{'='*70}\n")

    return total


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Thu thập dữ liệu HTML thô (chưa bóc tách nội dung) và lưu vào raw_articles."
    )
    parser.add_argument("--source", default=None,
                        help="Tên nguồn cụ thể (ví dụ: vnexpress, tuoitre).")
    parser.add_argument("--type", choices=["all", "rss", "api", "html"], default="all",
                        help="Lọc nguồn theo loại kênh (mặc định: all).")
    parser.add_argument("--limit", type=int, default=10,
                        help="Số bài tối đa mỗi nguồn (mặc định: 10).")
    parser.add_argument("--force", action="store_true",
                        help="Bỏ qua kiểm tra trùng lặp, cào lại dù đã tồn tại.")
    parser.add_argument("--delay", type=float, default=1.5,
                        help="Delay cơ sở giữa các request (giây, mặc định: 1.5).")
    parser.add_argument("--all", action="store_true",
                        help="Cào toàn bộ các nguồn đã đăng ký.")
    parser.add_argument("--save-db", action=argparse.BooleanOptionalAction, default=True,
                        help="Lưu vào PostgreSQL raw_articles (mặc định: True).")
    parser.add_argument("--save-local", action="store_true",
                        help="Lưu HTML thô (.html.gz) + metadata (.json) ra thư mục crawl_raw/ (mặc định: False).")
    parser.add_argument("--no-from-db", action="store_true",
                        help="Không nạp cấu hình nguồn từ DB, chỉ dùng YAML local.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_raw_collector(
        source=args.source,
        channel_type=args.type,
        limit=args.limit,
        force=args.force,
        delay=args.delay,
        save_db=args.save_db,
        save_local=args.save_local,
        from_db=not args.no_from_db,
        all_sources=args.all,
    )


if __name__ == "__main__":
    main()
