# backend/api/v1/router.py
from fastapi import APIRouter
from backend.api.v1.endpoints import articles, categories, users

api_router = APIRouter(prefix="/api/v1")

# Các router hiện có
api_router.include_router(articles.router)
api_router.include_router(categories.router)

# Router users chứa cả đăng ký, đăng nhập, đăng xuất
api_router.include_router(users.router)