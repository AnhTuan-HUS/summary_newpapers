"""Router quản lý API cho Categories (Chuyên mục tin tức)."""

from fastapi import APIRouter
from backend.db_operations import get_all_categories
from backend.schemas import CategorySchema

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategorySchema])
def list_categories() -> list[dict]:
    """Lấy danh sách chuyên mục tin tức (Categories) kèm số lượng bài viết tương ứng."""
    return get_all_categories()
