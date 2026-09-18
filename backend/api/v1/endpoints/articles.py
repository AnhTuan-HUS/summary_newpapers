"""Router quản lý API cho Articles (Bài viết tin tức)."""

import math
from fastapi import APIRouter, HTTPException, Query

from backend.db_operations import (
    get_article_by_id,
    get_articles,
)
from backend.schemas import (
    ArticleDetailSchema,
    PaginatedArticlesResponse,
)

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.get("", response_model=PaginatedArticlesResponse)
def list_articles(
    category_id: int | None = Query(None, description="Lọc theo ID chuyên mục"),
    category_slug: str | None = Query(None, description="Lọc theo slug chuyên mục (ví dụ: ai, an-ninh-mang)"),
    status: str | None = Query(None, description="Lọc theo trạng thái bài viết (draft, published)"),
    page: int = Query(1, ge=1, description="Trang hiện tại (bắt đầu từ 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Số lượng bài viết trên mỗi trang"),
) -> dict:
    """Lấy danh sách bài viết hỗ trợ phân trang và lọc theo category/status."""
    offset = (page - 1) * page_size
    items, total = get_articles(
        category_id=category_id,
        category_slug=category_slug,
        status=status,
        limit=page_size,
        offset=offset,
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": items,
    }


@router.get("/latest", response_model=PaginatedArticlesResponse)
def list_latest_articles(
    limit: int = Query(10, ge=1, le=50, description="Số lượng bài mới nhất cần lấy"),
) -> dict:
    """Lấy danh sách các bài viết mới nhất."""
    items, total = get_articles(
        limit=limit,
        offset=0,
    )
    return {
        "total": total,
        "page": 1,
        "page_size": limit,
        "total_pages": 1,
        "items": items,
    }


@router.get("/trending", response_model=PaginatedArticlesResponse)
def list_trending_articles(
    limit: int = Query(10, ge=1, le=50, description="Số lượng bài trending cần lấy"),
) -> dict:
    """Lấy danh sách các bài viết nổi bật/trending (đã xuất bản và ưu tiên tầm quan trọng)."""
    items, total = get_articles(
        status="published",
        limit=limit,
        offset=0,
    )
    if not items:
        items, total = get_articles(limit=limit, offset=0)

    return {
        "total": total,
        "page": 1,
        "page_size": limit,
        "total_pages": 1,
        "items": items,
    }


@router.get("/{article_id}", response_model=ArticleDetailSchema)
def get_article_detail(article_id: int) -> dict:
    """Lấy thông tin chi tiết của một bài viết gồm nội dung, tóm tắt, key points và metadata."""
    article = get_article_by_id(article_id)
    if not article:
        raise HTTPException(
            status_code=404, detail=f"Không tìm thấy bài viết với ID {article_id}"
        )
    return article


