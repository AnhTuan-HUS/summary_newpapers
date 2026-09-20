from qdrant_client.models import PointStruct, VectorParams, Distance
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

def recreate_collection(collection_name: str = "summary_embeddings"):
    """Xóa collection cũ và tạo lại với size=3072 để phù hợp với Gemini"""
    client.delete_collection(collection_name=collection_name)
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
    )
    print(f"Đã tạo lại {collection_name} với size=3072!")

# Bỏ comment dòng bên dưới, chạy file này 1 lần duy nhất, sau đó comment lại.
# recreate_collection()