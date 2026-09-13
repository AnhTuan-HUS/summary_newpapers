"""Module hỗ trợ tính toán độ tương đồng giữa các bài viết để phục vụ deduplication."""

from __future__ import annotations

import re
from typing import Any

_WORD_RE = re.compile(r"\w+", re.UNICODE)


def _get_ngrams(text: str, n: int = 3) -> set[str]:
    """Tách văn bản thành tập hợp các n-gram (mặc định n=3 từ)."""
    words = _WORD_RE.findall(text.lower())
    if len(words) < n:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i : i + n]) for i in range(len(words) - n + 1)}


def compute_jaccard_similarity(text1: str | None, text2: str | None, n: int = 3) -> float:
    """Tính độ tương đồng Jaccard giữa 2 đoạn văn bản dựa trên n-gram.

    Args:
        text1: Văn bản 1.
        text2: Văn bản 2.
        n: Độ dài n-gram (mặc định: 3).

    Returns:
        float: Giá trị trong khoảng [0.0, 1.0].
    """
    if not text1 or not text2:
        return 0.0

    set1 = _get_ngrams(text1, n=n)
    set2 = _get_ngrams(text2, n=n)

    if not set1 or not set2:
        return 0.0

    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))

    return intersection / union if union > 0 else 0.0


def find_duplicate_article(
    title: str,
    content: str | None,
    candidate_articles: list[dict[str, Any]],
    threshold: float = 0.80,
    content_threshold: float = 0.75,
) -> dict[str, Any] | None:
    """Tìm xem bài viết mới có bị trùng lặp với bài nào trong danh sách ứng viên đã có hay không.

    Tiêu chí trùng lặp:
      1. Nếu riêng NỘI DUNG (content_score) giống nhau >= 75% -> Coi là TRÙNG LẶP ngay (dù tiêu đề khác nhau).
      2. Nếu kết hợp cả Tiêu đề + Nội dung (combined_score) >= 80% -> Coi là TRÙNG LẶP.

    Args:
        title: Tiêu đề bài mới.
        content: Nội dung đã làm sạch của bài mới.
        candidate_articles: Danh sách các bài đã có trong `articles` (gồm id, title, content).
        threshold: Ngưỡng tính trùng lặp kết hợp (mặc định: 0.80).
        content_threshold: Ngưỡng tính trùng lặp riêng nội dung (mặc định: 0.75).

    Returns:
        dict | None: Bản ghi bài viết bị trùng trong candidate_articles nếu có, ngược lại trả về None.
    """
    if not title or not candidate_articles:
        return None

    best_match = None
    max_score = 0.0

    for cand in candidate_articles:
        cand_title = cand.get("title") or ""
        cand_content = cand.get("content") or ""

        # 1. So sánh tiêu đề (dùng 2-gram)
        title_score = compute_jaccard_similarity(title, cand_title, n=2)

        # 2. So sánh nội dung (dùng 3-gram)
        content_score = compute_jaccard_similarity(content, cand_content, n=3) if content and cand_content else title_score

        # Quy tắc 1: Nếu nội dung trùng lặp cao (>= 75%) -> Đánh dấu trùng lặp ngay bất kể tiêu đề
        if content_score >= content_threshold:
            if content_score > max_score:
                max_score = content_score
                best_match = cand
            continue

        # Quy tắc 2: Điểm kết hợp (40% tiêu đề + 60% nội dung) >= 80%
        combined_score = 0.4 * title_score + 0.6 * content_score

        if combined_score > max_score and combined_score >= threshold:
            max_score = combined_score
            best_match = cand

    return best_match


