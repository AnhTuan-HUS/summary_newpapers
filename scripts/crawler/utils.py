"""Module tiện ích hỗ trợ: chuẩn hóa URL, băm mã hash, làm sạch văn bản và nén lưu artifacts."""

import re
import gzip
import hashlib
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# Thư mục gốc của dự án và thư mục lưu trữ dữ liệu cào
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = PROJECT_ROOT / "crawl_data"

# Danh sách các tham số truy vấn theo dõi (tracking params) cần lọc bỏ khỏi URL
TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
}


def normalize_url(url: str) -> str:
    """Chuẩn hóa URL bằng cách loại bỏ các tham số theo dõi và phân tích (UTM, Facebook click ID, Google click ID).
    
    Args:
        url: Chuỗi URL bài viết ban đầu.
        
    Returns:
        str: Chuỗi URL sạch, chuẩn hóa.
    """
    parts = urlsplit(url.strip())
    clean_query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key.lower() not in TRACKING_PARAMS
    ]
    return urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(clean_query), "")
    )


import html

def clean_text(value: str | None, preserve_newlines: bool = False) -> str | None:
    """Chuẩn hóa chuỗi văn bản: loại bỏ/giữ ký tự xuống dòng (\n), giải mã HTML, chuyển đổi dấu ngoặc kép và thu gọn khoảng trắng.
    
    Args:
        value: Chuỗi văn bản thô hoặc None.
        preserve_newlines: Nếu True, giữ lại cấu trúc dòng/đoạn văn bản và chuẩn hóa khoảng trắng trên từng dòng.
        
    Returns:
        str | None: Chuỗi văn bản sạch hoặc None nếu chuỗi rỗng.
    """
    if not value:
        return None
    # 1. Giải mã các ký tự mã hóa HTML (ví dụ: &quot; -> ", &amp; -> &)
    value = html.unescape(value)
    # 2. Xóa các ký tự backslash đứng trước dấu ngoặc kép nếu có
    value = value.replace('\\"', '"')

    # 3. Chuyển đổi các cặp dấu ngoặc kép thẳng "..." thành dấu ngoặc cong “...” chuẩn tiếng Việt để không bị escape \\" trong JSON
    if '"' in value:
        res = []
        in_quote = False
        for char in value:
            if char == '"':
                if not in_quote:
                    res.append('“')
                    in_quote = True
                else:
                    res.append('”')
                    in_quote = False
            else:
                res.append(char)
        value = "".join(res)

    if not preserve_newlines:
        # 4. Loại bỏ ký tự xuống dòng (\n, \r) và chuẩn hóa khoảng trắng
        value = value.replace("\r", " ").replace("\n", " ")
        value = re.sub(r"\s+", " ", value).strip()
    else:
        # 4b. Chuẩn hóa khoảng trắng ngang trên mỗi dòng, bảo toàn các đoạn văn (\n\n)
        lines = [re.sub(r"[ \t\u00a0]+", " ", line).strip() for line in value.splitlines()]
        value = "\n".join(lines)
        value = re.sub(r"\n{3,}", "\n\n", value).strip()

    return value or None


def clean_media_url(url: str | None) -> str | None:
    """Làm sạch chuỗi URL media: loại bỏ các ký tự ngoặc kép, ngoặc đơn, gạch chéo ngược thừa và HTML entities."""
    if not url:
        return None
    u = str(url).strip()
    u = u.replace("&quot;", "").replace("&apos;", "").replace("%22", "").replace("%27", "")
    u = u.strip("'\"\\ ").strip()
    u = re.sub(r"^[\"'\\]+|[\"'\\]+$", "", u)
    return u or None


def parse_srcset(srcset_val: str) -> list[str]:
    """Bóc tách thuộc tính srcset thành danh sách các URL đơn lẻ sạch sẽ."""
    if not srcset_val:
        return []
    urls = []
    for item in srcset_val.split(","):
        item = item.strip()
        if not item:
            continue
        parts = item.split()
        if parts:
            clean_u = clean_media_url(parts[0])
            if clean_u and clean_u.startswith(("http://", "https://", "//", "/")):
                urls.append(clean_u)
    return urls


def get_universal_media_key(url: str) -> tuple[str, str]:
    """Tạo nhận dạng tổng quát cho media dựa trên tên miền và tên tệp gốc (Domain + Filename Stem).
    Hoàn toàn không hardcode danh sách tham số hay quy tắc thư mục của bất kỳ trang báo/CDN nào.
    """
    clean_u = clean_media_url(url)
    if not clean_u:
        return ("", "")
    try:
        parts = urlsplit(clean_u)
        path_obj = Path(parts.path)
        filename = path_obj.name
        stem = path_obj.stem
        # Loại bỏ quy chuẩn kích thước ảnh phổ biến ở tên tệp (vd: _600x400, -240x160)
        stem = re.sub(r"[_\-]\d+x\d+$", "", stem, flags=re.IGNORECASE)
        return (parts.netloc.lower(), stem.lower())
    except Exception:
        return ("", clean_u)


def get_url_quality_score(url: str) -> tuple[int, int, int, float]:
    """Tính điểm chất lượng độ phân giải của URL một cách động (không hardcode tên tham số)."""
    parts = urlsplit(url)
    query_dict = dict(parse_qsl(parts.query))

    dpr = 1.0
    try:
        if "dpr" in query_dict:
            dpr = float(query_dict["dpr"])
    except Exception:
        pass

    # Lấy các chỉ số kích thước từ query parameters (loại bỏ w=0 hoặc h=0)
    query_nums = [int(n) for n in re.findall(r"\d+", parts.query) if int(n) > 0]
    max_query_num = max(query_nums) if query_nums else 0

    # Lấy chỉ số kích thước dạng 600x400 từ đường dẫn
    path_dim_match = re.search(r"[_\-]\d+x\d+", parts.path)
    path_dim_num = 0
    if path_dim_match:
        dims = [int(n) for n in re.findall(r"\d+", path_dim_match.group(0)) if int(n) > 0]
        path_dim_num = max(dims) if dims else 0

    # Lấy các chỉ số kích thước từ thư mục đường dẫn (loại trừ số năm 202x)
    raw_path_digits = re.findall(r"/(\d+)/", parts.path)
    path_numbers = [int(n) for n in raw_path_digits if not (len(n) == 4 and n.startswith("202")) and int(n) > 0]
    max_path_num = max(path_numbers) if path_numbers else 0

    return (max_query_num, path_dim_num, max_path_num, dpr)


def extract_article_content(soup) -> str | None:
    """Bóc tách văn bản bài viết từ cây DOM soup đã qua lọc boilerplate, giữ nguyên cấu trúc đoạn văn (\n\n)."""
    # Thay thế các thẻ ngắt dòng <br> bằng ký tự xuống dòng \n
    for br in soup.find_all("br"):
        br.replace_with("\n")

    block_elements = soup.find_all(["p", "h2", "h3", "h4", "h5", "h6", "li", "blockquote"])
    paragraphs: list[str] = []
    seen: set[str] = set()

    if block_elements:
        for el in block_elements:
            if el.parent is None or el.find_parent(["p", "li", "blockquote"]):
                continue
            # Lấy text nguyên bản từ thẻ block (giữ nguyên \n từ <br> nhưng không chèn \n rác vào các thẻ inline <a>, <span>, <b>, ...)
            raw_p = el.get_text("", strip=False)
            cleaned_p = clean_text(raw_p, preserve_newlines=True)
            if cleaned_p and len(cleaned_p) >= 5 and cleaned_p not in seen:
                seen.add(cleaned_p)
                paragraphs.append(cleaned_p)

    # Dự phòng: Nếu trang web không dùng thẻ block chuẩn mà phân tách bằng dòng
    if not paragraphs or sum(len(p) for p in paragraphs) < 50:
        lines = soup.get_text("\n", strip=True).splitlines()
        fallback_paras = []
        for line in lines:
            cleaned_line = clean_text(line, preserve_newlines=True)
            if cleaned_line and len(cleaned_line) >= 5 and cleaned_line not in seen:
                seen.add(cleaned_line)
                fallback_paras.append(cleaned_line)
        if sum(len(p) for p in fallback_paras) > sum(len(p) for p in paragraphs):
            paragraphs = fallback_paras

    if not paragraphs:
        return None

    return "\n\n".join(paragraphs)


def normalize_content(content_raw: str | None) -> dict[str, str | dict[str, str] | None]:
    """Bóc tách content_raw (chuỗi HTML thô của nội dung bài viết) thành:
    - 'content_raw': Chuỗi văn bản thuần đã được chuẩn hóa, giữ nguyên cấu trúc đoạn văn (\n\n).
    - 'thumbnail_url': Dict ánh xạ {link_media_gốc: tiêu_đề_media}.

    Args:
        content_raw: Chuỗi HTML block nội dung bài viết hoặc None.

    Returns:
        dict[str, str | dict[str, str] | None]: Từ điển chứa {"content_raw": ..., "thumbnail_url": ...}
    """
    if not content_raw or not content_raw.strip():
        return {"content_raw": None, "thumbnail_url": {}}

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        text_only = re.sub(r"<br\s*/?>", "\n", content_raw, flags=re.I)
        text_only = re.sub(r"</p>", "\n\n", text_only, flags=re.I)
        text_only = re.sub(r"<[^>]+>", " ", text_only)
        return {
            "content_raw": clean_text(text_only, preserve_newlines=True),
            "thumbnail_url": {},
        }

    soup = BeautifulSoup(content_raw, "lxml")

    # 1. Trích xuất danh sách ảnh, video và tiêu đề/chú thích tương ứng (thumbnail_url)
    media_groups: dict[tuple[str, str], list[tuple[str, str]]] = {}  # key -> list of (url, caption)

    def extract_caption(elem) -> str:
        """Trích xuất tiêu đề/chú thích từ thuộc tính hoặc thẻ figure/caption lân cận."""
        parent_fig = elem.find_parent("figure")
        if parent_fig:
            figcaption = parent_fig.find("figcaption")
            if figcaption and figcaption.get_text(" ", strip=True):
                return clean_text(figcaption.get_text(" ", strip=True)) or ""

        title = elem.get("title") or elem.get("alt") or elem.get("aria-label") or ""
        if not title:
            parent_block = elem.find_parent(["figure", "div", "p"])
            if parent_block:
                caption = parent_block.find("figcaption") or parent_block.find(["p", "span"], class_=re.compile(r"caption|title|desc|sub", re.I))
                if caption:
                    title = caption.get_text(" ", strip=True)
        return clean_text(str(title)) or ""

    IMAGE_EXT_PATTERN = re.compile(r"\.(jpg|jpeg|png|webp|gif|bmp|svg|avif)(\?|#|$)", re.IGNORECASE)
    VIDEO_EXT_PATTERN = re.compile(r"\.(mp4|m3u8|webm|ogg|mov|flv|ts|mpd)(\?|#|$)", re.IGNORECASE)
    VIDEO_KEYWORD_PATTERN = re.compile(r"/video/|/vlog/|player|embed|stream|youtube|vimeo|tiktok|dailymotion", re.IGNORECASE)

    def add_media_candidate(raw_url: str, caption: str) -> None:
        clean_u = clean_media_url(raw_url)
        if not clean_u:
            return

        # Loại bỏ hoàn toàn các liên kết video, mp4, m3u8... chỉ giữ lại ảnh
        if VIDEO_EXT_PATTERN.search(clean_u) or (
            VIDEO_KEYWORD_PATTERN.search(clean_u) and not IMAGE_EXT_PATTERN.search(clean_u)
        ):
            return

        media_key = get_universal_media_key(clean_u)
        if not media_key[0] or not media_key[1]:
            return

        clean_caption = caption.replace("[Video]", "").strip() if caption else ""

        if media_key not in media_groups:
            media_groups[media_key] = []
        media_groups[media_key].append((clean_u, clean_caption))

    # 1.1 Bóc tách <img> (xử lý cả srcset và thuộc tính ảnh đơn)
    for img in soup.find_all("img"):
        candidate_urls = []
        for attr in ["data-original", "data-src", "srcset", "data-lazy-src", "data-url", "src"]:
            val = img.get(attr)
            if val and isinstance(val, str) and not val.strip().startswith("data:"):
                if attr == "srcset":
                    candidate_urls.extend(parse_srcset(val))
                else:
                    clean_u = clean_media_url(val)
                    if clean_u:
                        candidate_urls.append(clean_u)

        caption = extract_caption(img)
        for u in candidate_urls:
            add_media_candidate(u, caption)

    # 1.2 Bóc tách <picture> <source> chứa ảnh cho các trang hỗ trợ responsive image
    for source in soup.find_all("source"):
        if source.find_parent("video"):
            continue
        candidate_urls = []
        for attr in ["srcset", "data-srcset", "src"]:
            val = source.get(attr)
            if val and isinstance(val, str) and not val.strip().startswith("data:"):
                if "srcset" in attr:
                    candidate_urls.extend(parse_srcset(val))
                else:
                    clean_u = clean_media_url(val)
                    if clean_u:
                        candidate_urls.append(clean_u)

        caption = extract_caption(source)
        for u in candidate_urls:
            add_media_candidate(u, caption)

    # 1.3 Khử trùng lặp tổng quát: Chọn 1 URL tốt nhất cho mỗi nhóm media
    media_dict: dict[str, str] = {}
    for group_key, candidates in media_groups.items():
        if not candidates:
            continue
        # Tự động chọn URL có điểm chất lượng độ phân giải cao nhất
        best_url, _ = max(candidates, key=lambda c: get_url_quality_score(c[0]))
        # Nối/chọn chú thích tốt nhất (dài nhất) trong nhóm
        best_caption = max((c[1] for c in candidates), key=len, default="")
        media_dict[best_url] = best_caption

    # 2. Bóc tách và chuẩn hóa nội dung văn bản (content)
    # Loại bỏ các thẻ rác/kịch bản/khối tin liên quan/tác giả trước khi lấy text
    BOILERPLATE_PATTERN = re.compile(r"related|lien-quan|recommend|sidebar|comment|tags|breadcrumb|box-tin|topic-news|caption|photo|author|author_mail", re.I)

    for tag in soup.find_all(["script", "style", "noscript", "header", "footer", "nav", "aside", "figure", "figcaption", "picture", "img", "video", "iframe", "source"]):
        tag.decompose()

    for tag in soup.find_all(True):
        if tag.parent is None:
            continue
        class_id = f"{tag.get('class', '')} {tag.get('id', '')}"
        style = str(tag.get("style", "")).lower()
        align = str(tag.get("align", "")).lower()

        if BOILERPLATE_PATTERN.search(class_id) or "text-align:right" in style or "text-align: right" in style or align == "right":
            tag.decompose()

    normalized_content = extract_article_content(soup)

    return {
        "content_raw": normalized_content,
        "thumbnail_url": media_dict,
    }



def url_hash(url: str) -> str:
    """Tạo chuỗi băm hex 16 ký tự duy nhất từ URL đã được chuẩn hóa (SHA-256).
    
    Args:
        url: Chuỗi URL.
        
    Returns:
        str: 16 ký tự đầu của chuỗi băm SHA-256.
    """
    return hashlib.sha256(normalize_url(url).encode("utf-8")).hexdigest()[:16]


# comment toàn bộ văn bản dưới

def save_artifacts(
    html: str,
    source_name: str,
    url: str,
    final_url: str | None,
    fetched_at: datetime,
    article: dict[str, object],
    http_status: int | None = None,
    crawl_status: str = "pending",
    error_message: str | None = None,
    discovery_method: str = "direct",
    discovery_metadata: dict[str, object] | None = None,
    save_local: bool = False,
) -> dict[str, object]:
    """Tạo đối tượng metadata bài viết đã bóc tách. Chỉ lưu file local nếu save_local=True (mặc định: False).

        Lưu ý: content_raw là HTML block thô từ GenericParser, KHÔNG qua bước normalize.
        Bước normalize_content() là xử lý downstream riêng biệt (không gọi ở đây).
    """
    raw_title = article.get("title") or article.get("title_raw")
    raw_content = article.get("content_raw") or article.get("content")

    metadata = {
        "source": source_name,
        "canonical_article_id": article.get("canonical_article_id"),
        "external_url": final_url or url,
        "title_raw": clean_text(str(raw_title)) if raw_title else None,
        "content_raw": str(raw_content) if raw_content else None,
        "author": clean_text(str(article["author"])) if article.get("author") else None,
        "published_at": article.get("published_at"),
        "collected_at": fetched_at.isoformat(),
        "fetched_at": fetched_at.isoformat(),
        "http_status": http_status,
        "crawl_status": crawl_status,
        "error": error_message,
        "error_message": error_message,
        "discovery_method": discovery_method,
        "discovery_metadata": discovery_metadata,
        "url": url,
    }

    if save_local:
        try:
            date_path = fetched_at.astimezone().strftime("%Y/%m/%d")
            crawl_id = f"{url_hash(url)}_{fetched_at.strftime('%H%M%S_%f')}"
            raw_path = OUTPUT_ROOT / "raw" / source_name / date_path / f"{crawl_id}.html.gz"
            metadata_path = OUTPUT_ROOT / "metadata" / source_name / date_path / f"{crawl_id}.json"

            raw_path.parent.mkdir(parents=True, exist_ok=True)
            metadata_path.parent.mkdir(parents=True, exist_ok=True)

            if html and html.strip():
                with gzip.open(raw_path, "wt", encoding="utf-8") as file:
                    file.write(html)

            metadata_path.write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as err:
            print(f"   ⚠️ Cảnh báo save_local: Không thể ghi file local ({err}) - Tiếp tục luồng ghi DB.")

    return metadata


def find_existing_artifact(url: str, source_name: str | None = None) -> dict[str, object] | None:
    """Kiểm tra bài viết đã từng tồn tại trong Database hay chưa (không kiểm tra local file)."""
    try:
        from database.operations import check_url_exists
        if check_url_exists(url):
            return {"url": url, "crawl_status": "SUCCESS", "skipped": True}
    except Exception:
        pass
    return None
