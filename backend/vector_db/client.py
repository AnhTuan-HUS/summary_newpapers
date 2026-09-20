import os
from qdrant_client import QdrantClient

def get_qdrant_client():
    # Tự động lấy cấu hình từ môi trường (.env hoặc Docker), mặc định fallback về localhost
    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_HTTP_PORT", 6333))
    
    return QdrantClient(host=host, port=port)