"""Module truy vấn cơ sở dữ liệu dành riêng cho backend API."""

from __future__ import annotations

import json
from typing import Any
from database.connection import get_connection


def get_all_categories() -> list[dict[str, Any]]:
    """Lấy tất cả danh mục cùng số lượng bài viết thuộc từng danh mục."""
    query = """
        SELECT
            c.id,
            c.name,
            c.slug,
            COUNT(a.id) AS article_count
        FROM categories c
        LEFT JOIN articles a ON a.category_id = c.id
        GROUP BY c.id, c.name, c.slug
        ORDER BY c.id ASC;
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        results: list[dict[str, Any]] = []
        if cursor.description:
            colnames = [col[0] for col in cursor.description]
            for row in rows:
                row_dict = dict(zip(colnames, row)) if not isinstance(row, dict) else dict(row)
                results.append(row_dict)
        cursor.close()
        return results


def get_articles(
    category_id: int | None = None,
    category_slug: str | None = None,
    status: str | None = None,
    limit: int = 10,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], int]:
    """Lấy danh sách bài viết theo bộ lọc và phân trang, kèm tổng số lượng (total)."""
    where_clauses: list[str] = []
    params: dict[str, Any] = {"limit": limit, "offset": offset}

    if category_id is not None:
        where_clauses.append("a.category_id = %(category_id)s")
        params["category_id"] = category_id

    if category_slug is not None:
        where_clauses.append("c.slug = %(category_slug)s")
        params["category_slug"] = category_slug

    if status is not None:
        where_clauses.append("a.status = %(status)s")
        params["status"] = status

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    count_query = f"""
        SELECT COUNT(*)
        FROM articles a
        LEFT JOIN categories c ON a.category_id = c.id
        {where_sql};
    """

    data_query = f"""
        SELECT
            a.id,
            a.title,
            a.slug,
            a.summary,
            a.thumbnail_url,
            a.importance_score,
            a.status,
            a.published_at,
            a.created_at,
            c.id AS category_id,
            c.name AS category_name,
            c.slug AS category_slug
        FROM articles a
        LEFT JOIN categories c ON a.category_id = c.id
        {where_sql}
        ORDER BY COALESCE(a.published_at, a.created_at) DESC, a.id DESC
        LIMIT %(limit)s OFFSET %(offset)s;
    """

    with get_connection() as conn:
        cursor = conn.cursor()

        # Get total count
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]

        # Get records
        cursor.execute(data_query, params)
        rows = cursor.fetchall()
        results: list[dict[str, Any]] = []
        if cursor.description:
            colnames = [col[0] for col in cursor.description]
            for row in rows:
                row_dict = dict(zip(colnames, row)) if not isinstance(row, dict) else dict(row)

                # Format category object
                cat_id = row_dict.pop("category_id", None)
                cat_name = row_dict.pop("category_name", None)
                cat_slug = row_dict.pop("category_slug", None)
                if cat_id:
                    row_dict["category"] = {
                        "id": cat_id,
                        "name": cat_name,
                        "slug": cat_slug,
                    }
                else:
                    row_dict["category"] = None

                results.append(row_dict)
        cursor.close()
        return results, total


def get_article_by_id(article_id: int) -> dict[str, Any] | None:
    """Lấy chi tiết một bài viết theo `article_id`."""
    query = """
        SELECT
            a.id,
            a.title,
            a.slug,
            a.content,
            a.summary,
            a.key_points,
            a.why_it_matters,
            a.thumbnail_url,
            a.importance_score,
            a.status,
            a.published_at,
            a.created_at,
            a.updated_at,
            c.id AS category_id,
            c.name AS category_name,
            c.slug AS category_slug
        FROM articles a
        LEFT JOIN categories c ON a.category_id = c.id
        WHERE a.id = %(article_id)s;
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, {"article_id": article_id})
        row = cursor.fetchone()
        if not row:
            cursor.close()
            return None

        colnames = [col[0] for col in cursor.description]
        row_dict = dict(zip(colnames, row)) if not isinstance(row, dict) else dict(row)

        cat_id = row_dict.pop("category_id", None)
        cat_name = row_dict.pop("category_name", None)
        cat_slug = row_dict.pop("category_slug", None)
        if cat_id:
            row_dict["category"] = {
                "id": cat_id,
                "name": cat_name,
                "slug": cat_slug,
            }
        else:
            row_dict["category"] = None

        # Parse key_points if json string
        if row_dict.get("key_points"):
            try:
                row_dict["key_points"] = json.loads(row_dict["key_points"])
            except Exception:
                pass

        cursor.close()
        return row_dict

def get_user_by_email(email: str) -> dict[str, Any] | None:
    """Lấy thông tin user dựa theo email."""
    query = "SELECT * FROM users WHERE email = %(email)s;"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, {"email": email})
        row = cursor.fetchone()
        if not row:
            cursor.close()
            return None
        
        colnames = [col[0] for col in cursor.description]
        row_dict = dict(zip(colnames, row)) if not isinstance(row, dict) else dict(row)
        cursor.close()
        return row_dict


def create_user(email: str, password_hash: str, name: str | None = None) -> dict[str, Any]:
    """Tạo mới một user vào bảng users."""
    query = """
        INSERT INTO users (email, password_hash, name, created_at)
        VALUES (%(email)s, %(password_hash)s, %(name)s, NOW())
        RETURNING id, email, name, created_at, last_login_at;
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, {"email": email, "password_hash": password_hash, "name": name})
        row = cursor.fetchone()
        conn.commit()
        
        colnames = [col[0] for col in cursor.description]
        row_dict = dict(zip(colnames, row)) if not isinstance(row, dict) else dict(row)
        cursor.close()
        return row_dict


def update_last_login(user_id: int) -> None:
    """Cập nhật thời gian đăng nhập lần cuối (last_login_at)."""
    query = "UPDATE users SET last_login_at = NOW() WHERE id = %(user_id)s;"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, {"user_id": user_id})
        conn.commit()
        cursor.close()