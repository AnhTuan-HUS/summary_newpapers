"""Module bộ bóc tách dữ liệu vạn năng (GenericParser) dựa trên cấu hình khai báo YAML.

Hỗ trợ cơ chế bóc tách đa tầng (Cascade Extraction):
1. Tầng 1: Trích xuất metadata có cấu trúc Schema.org JSON-LD (NewsArticle, Article).
2. Tầng 2: Áp dụng tập luật CSS Selectors và trích xuất thuộc tính thẻ HTML (@attr).
3. Tầng 3: Tự động xóa các phần tử DOM rác (strip_elements) trước khi lấy nội dung văn bản.
4. Tầng 4: Dự phòng bóc tách tự động qua mô hình heuristic (Trafilatura) khi layout web bị thay đổi.
"""

from __future__ import annotations

import json
from bs4 import BeautifulSoup
from .base import BaseParser
from ..config_loader import SourceConfig
from ..utils import clean_text


class GenericParser(BaseParser):
    """Bộ bóc tách HTML đa năng, hoạt động dựa trên các quy tắc định nghĩa trong SourceConfig."""

    def __init__(self, config: SourceConfig):
        """Khởi tạo parser với cấu hình nguồn cụ thể."""
        self.config = config

    @staticmethod
    def _extract_by_selector_rule(soup: BeautifulSoup, rule: str) -> str | None:
        """Trích xuất chuỗi văn bản hoặc giá trị thuộc tính HTML theo cú pháp quy tắc.
        
        Các định dạng quy tắc hỗ trợ:
        - "h1.title-detail" -> Lấy nội dung text đã làm sạch của thẻ h1.title-detail.
        - "meta[property='og:image']@content" -> Lấy giá trị của thuộc tính 'content' trong thẻ meta.
        - "img.thumb@src" -> Lấy giá trị của thuộc tính 'src' trong thẻ img.
        """
        if "@" in rule:
            selector, attr_name = rule.split("@", 1)
            selector = selector.strip()
            attr_name = attr_name.strip()
            node = soup.select_one(selector)
            if node and node.has_attr(attr_name):
                return clean_text(node[attr_name])
            return None

        node = soup.select_one(rule.strip())
        if node:
            return clean_text(node.get_text(" ", strip=True))
        return None

    def _extract_first(self, soup: BeautifulSoup, rules: list[str]) -> str | None:
        """Duyệt danh sách các quy tắc theo thứ tự ưu tiên (fallback) cho đến khi tìm thấy giá trị hợp lệ."""
        for rule in rules:
            value = self._extract_by_selector_rule(soup, rule)
            if value:
                return value
        return None

    def _extract_jsonld(self, soup: BeautifulSoup) -> dict[str, str | None]:
        """Trích xuất thông tin bài viết từ các thẻ <script type='application/ld+json'> (Schema.org)."""
        extracted: dict[str, str | None] = {}
        for script in soup.select("script[type='application/ld+json']"):
            try:
                data = json.loads(script.string or "{}")
                # Chuẩn hóa nếu dữ liệu là mảng hoặc chứa cấu trúc @graph
                items = []
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict):
                    if "@graph" in data and isinstance(data["@graph"], list):
                        items = data["@graph"]
                    else:
                        items = [data]

                for item in items:
                    if not isinstance(item, dict):
                        continue
                    schema_type = str(item.get("@type", "")).lower()
                    if schema_type in ("newsarticle", "article", "reportagereport"):
                        if not extracted.get("title") and item.get("headline"):
                            extracted["title"] = clean_text(item["headline"])
                        if not extracted.get("published_at") and item.get("datePublished"):
                            extracted["published_at"] = clean_text(item["datePublished"])
                        if not extracted.get("thumbnail_url") and item.get("image"):
                            img = item["image"]
                            if isinstance(img, str):
                                extracted["thumbnail_url"] = clean_text(img)
                            elif isinstance(img, dict) and img.get("url"):
                                extracted["thumbnail_url"] = clean_text(img["url"])
                            elif isinstance(img, list) and len(img) > 0 and isinstance(img[0], str):
                                extracted["thumbnail_url"] = clean_text(img[0])
                        if not extracted.get("author") and item.get("author"):
                            auth = item["author"]
                            if isinstance(auth, str):
                                extracted["author"] = clean_text(auth)
                            elif isinstance(auth, dict) and auth.get("name"):
                                extracted["author"] = clean_text(auth["name"])
                            elif isinstance(auth, list) and len(auth) > 0:
                                first_auth = auth[0]
                                if isinstance(first_auth, str):
                                    extracted["author"] = clean_text(first_auth)
                                elif isinstance(first_auth, dict) and first_auth.get("name"):
                                    extracted["author"] = clean_text(first_auth["name"])
            except Exception:
                continue
        return extracted

    def parse(self, html: str) -> dict[str, str | None]:
        """Phân tích mã nguồn HTML và trích xuất các trường: title, author, published_at, content_raw."""
        soup = BeautifulSoup(html, "lxml")
        selectors = self.config.parser.selectors
        clean_rules = self.config.parser.clean_rules

        # 1. Trích xuất metadata Schema.org JSON-LD để dự phòng (fallback)
        jsonld_data = self._extract_jsonld(soup)

        # 2. Trích xuất các trường metadata đơn giá trị
        title = self._extract_first(soup, selectors.title) or jsonld_data.get("title")
        author = self._extract_first(soup, selectors.author) or jsonld_data.get("author")
        published_at = (
            self._extract_first(soup, selectors.published_at)
            or jsonld_data.get("published_at")
        )

        # 3. Tìm container chứa block nội dung bài viết
        content_node = None

        # Suy ra selector container từ content_paragraphs (ví dụ: '.fck_detail p' -> '.fck_detail')
        for sel in selectors.content_paragraphs:
            parts = sel.rsplit(" ", 1)
            container_sel = parts[0].strip() if len(parts) > 1 else sel.strip()
            node = soup.select_one(container_sel)
            if node:
                content_node = node
                break

        # Fallback 1: Lấy parent của các đoạn văn khớp selector
        if not content_node:
            for sel in selectors.content_paragraphs:
                matched = soup.select(sel)
                if matched:
                    content_node = matched[0].parent
                    break

        # Fallback 2: Thử thẻ <article>, <main>, hoặc <body>
        if not content_node:
            content_node = soup.find("article") or soup.find("main") or soup.find("body")

        # 4. Loại bỏ các thẻ rác (kịch bản, kiểu dáng) khỏi block nội dung
        content_raw: str | None = None
        if content_node:
            for strip_sel in clean_rules.strip_elements:
                for elem in content_node.select(strip_sel):
                    elem.decompose()
            for tag in content_node.find_all(["script", "style", "noscript"]):
                tag.decompose()
            content_raw = str(content_node)

        return {
            "title": title,
            "author": author,
            "published_at": published_at,
            "content_raw": content_raw,
        }



