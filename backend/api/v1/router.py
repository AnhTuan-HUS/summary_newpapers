"""Router tổng gom tất cả các API endpoints của v1."""

from fastapi import APIRouter
from backend.api.v1.endpoints import articles, categories

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(articles.router)
api_router.include_router(categories.router)

