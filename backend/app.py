"""Backend API dịch vụ AI Tech News phục vụ ứng dụng frontend và kiểm tra sức khỏe hệ thống."""

import os

import psycopg
from fastapi import FastAPI, HTTPException


app = FastAPI(title="AI Tech News Backend", version="0.1.0")



@app.get("/")
def root() -> dict[str, str]:
    """Endpoint gốc trả về thông tin trạng thái hoạt động của backend service."""
    return {
        "service": "backend",
        "message": "Dịch vụ AI Tech News API đang hoạt động bình thường",
    }



@app.get("/health")
def health() -> dict[str, str]:
    """Endpoint kiểm tra tình trạng sức khỏe của ứng dụng."""
    return {"status": "ok"}


@app.get("/db-check")
def database_check() -> dict[str, str]:
    """Endpoint kiểm tra kết nối tới cơ sở dữ liệu PostgreSQL."""
    database_url = os.environ["DATABASE_URL"]

    try:
        with psycopg.connect(database_url, connect_timeout=3) as connection:
            connection.execute("SELECT 1")

        return {
            "status": "ok",
            "database": "connected",
        }

    except psycopg.Error as error:
        raise HTTPException(
            status_code=503,
            detail="Không thể kết nối đến cơ sở dữ liệu PostgreSQL",
        ) from error


# ============================================================
# LẤY DANH SÁCH BÀI VIẾT
# Công việc:
# - Vào kho articles.
# - Lấy các bài viết có trạng thái published.
# - Sắp xếp bài mới nhất lên trước.
# - Trả danh sách bài viết về cho người gọi API.
#
# Nếu kho articles chưa có bài:
# - Không báo lỗi.
# - Trả về [].
# ============================================================

@app.get("/api/articles")
def get_articles(limit: int = 20) -> list[dict]:
    """Lấy danh sách các bài viết đã được xuất bản."""

    database_url = os.environ["DATABASE_URL"]

    sql = """
        SELECT
            a.id,
            a.title,
            a.slug,
            a.content,
            a.thumbnail_url,
            a.summary,
            a.key_points,
            a.why_it_matters,
            a.importance_score,
            a.status,
            a.published_at,
            a.created_at,
            c.id AS category_id,
            c.name AS category_name,
            c.slug AS category_slug
        FROM articles AS a
        LEFT JOIN categories AS c
            ON a.category_id = c.id
        WHERE a.status = 'published'
        ORDER BY a.published_at DESC NULLS LAST, a.id DESC
        LIMIT %s
    """

    try:
        with psycopg.connect(database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (limit,))

                columns = [column.name for column in cursor.description]
                rows = cursor.fetchall()

        return [dict(zip(columns, row)) for row in rows]

    except psycopg.Error as error:
        raise HTTPException(
            status_code=503,
            detail="Không thể lấy danh sách bài viết",
        ) from error


# ============================================================
# LẤY DANH MỤC
# Công việc:
# - Vào kho categories.
# - Lấy danh sách các danh mục của website.
# - Trả danh sách danh mục về cho người gọi API.
# ============================================================

@app.get("/api/categories")
def get_categories() -> list[dict]:
    """Lấy danh sách tất cả danh mục bài viết."""

    database_url = os.environ["DATABASE_URL"]

    sql = """
        SELECT
            id,
            name,
            slug
        FROM categories
        ORDER BY id
    """

    try:
        with psycopg.connect(database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)

                columns = [column.name for column in cursor.description]
                rows = cursor.fetchall()

        return [dict(zip(columns, row)) for row in rows]

    except psycopg.Error as error:
        raise HTTPException(
            status_code=503,
            detail="Không thể lấy danh sách danh mục",
        ) from error


# ============================================================
# QUẦY LẤY BÀI VIẾT THEO DANH MỤC
# Công việc:
# - Nhận slug của danh mục.
# - Vào kho categories tìm danh mục đó.
# - Sau đó vào kho articles lấy các bài thuộc danh mục.
#
# Ví dụ:
# /api/categories/ai/articles
# /api/categories/robotics/articles
#
# Nếu danh mục chưa có bài:
# - Không báo lỗi.
# - Trả về [].
# ============================================================

@app.get("/api/categories/{category_slug}/articles")
def get_articles_by_category(
    category_slug: str,
    limit: int = 20,
) -> list[dict]:
    """Lấy danh sách bài viết theo slug của danh mục."""

    database_url = os.environ["DATABASE_URL"]

    sql = """
        SELECT
            a.id,
            a.title,
            a.slug,
            a.content,
            a.thumbnail_url,
            a.summary,
            a.key_points,
            a.why_it_matters,
            a.importance_score,
            a.status,
            a.published_at,
            a.created_at,
            c.id AS category_id,
            c.name AS category_name,
            c.slug AS category_slug
        FROM articles AS a
        INNER JOIN categories AS c
            ON a.category_id = c.id
        WHERE c.slug = %s
          AND a.status = 'published'
        ORDER BY a.published_at DESC NULLS LAST, a.id DESC
        LIMIT %s
    """

    try:
        with psycopg.connect(database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (category_slug, limit))

                columns = [column.name for column in cursor.description]
                rows = cursor.fetchall()

        return [dict(zip(columns, row)) for row in rows]

    except psycopg.Error as error:
        raise HTTPException(
            status_code=503,
            detail="Không thể lấy bài viết theo danh mục",
        ) from error


# ============================================================
# LẤY MỘT BÀI VIẾT
# Công việc:
# - Nhận slug của một bài viết.
# - Vào kho articles tìm đúng bài đó.
# - Nếu tìm thấy: trả bài viết.
# - Nếu không tìm thấy: trả lỗi 404.
#
# Ví dụ:
# /api/articles/openai-ra-mat-mo-hinh-moi
# ============================================================

@app.get("/api/articles/{article_slug}")
def get_article(article_slug: str) -> dict:
    """Lấy một bài viết cụ thể bằng slug."""

    database_url = os.environ["DATABASE_URL"]

    sql = """
        SELECT
            a.id,
            a.title,
            a.slug,
            a.content,
            a.thumbnail_url,
            a.summary,
            a.key_points,
            a.why_it_matters,
            a.importance_score,
            a.status,
            a.published_at,
            a.created_at,
            c.id AS category_id,
            c.name AS category_name,
            c.slug AS category_slug
        FROM articles AS a
        LEFT JOIN categories AS c
            ON a.category_id = c.id
        WHERE a.slug = %s
          AND a.status = 'published'
        LIMIT 1
    """

    try:
        with psycopg.connect(database_url, connect_timeout=3) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (article_slug,))

                row = cursor.fetchone()

                if row is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Không tìm thấy bài viết",
                    )

                columns = [column.name for column in cursor.description]

        return dict(zip(columns, row))

    except psycopg.Error as error:
        raise HTTPException(
            status_code=503,
            detail="Không thể lấy bài viết",
        ) from error