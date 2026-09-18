"""Schemas Pydantic dành cho backend API."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class CategorySchema(BaseModel):
    """Schema thông tin danh mục bài viết."""
    id: int
    name: str
    slug: str | None = None
    article_count: int | None = None

    model_config = ConfigDict(from_attributes=True)


class ArticleCategorySchema(BaseModel):
    """Schema lồng ghép danh mục trong bài viết."""
    id: int
    name: str
    slug: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ArticleListItemSchema(BaseModel):
    """Schema bài viết trong danh sách (list view)."""
    id: int
    title: str
    slug: str | None = None
    summary: str | None = None
    thumbnail_url: Any | None = None
    importance_score: float | None = None
    status: str | None = None
    published_at: datetime | None = None
    created_at: datetime | None = None
    category: ArticleCategorySchema | None = None

    model_config = ConfigDict(from_attributes=True)


class ArticleDetailSchema(BaseModel):
    """Schema chi tiết bài viết (detail view)."""
    id: int
    title: str
    slug: str | None = None
    content: str | None = None
    summary: str | None = None
    key_points: Any | None = None
    why_it_matters: str | None = None
    thumbnail_url: Any | None = None
    importance_score: float | None = None
    status: str | None = None
    published_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    category: ArticleCategorySchema | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedArticlesResponse(BaseModel):
    """Schema phản hồi danh sách bài viết kèm thông tin phân trang."""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[ArticleListItemSchema]
