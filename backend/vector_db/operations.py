from qdrant_client.models import PointStruct
from .client import get_qdrant_client

client = get_qdrant_client()

def save_vector(collection_name: str, point_id: int, vector: list[float], metadata: dict):
    """Lưu vector kèm theo metadata (tiêu đề, url, id bài viết...)"""
    client.upsert(
        collection_name=collection_name,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload=metadata
            )
        ]
    )

def search_vector(collection_name: str, query_vector: list[float], limit: int = 5):
    """Tìm kiếm vector tương đồng nhất"""
    results = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=limit
    )
    return results