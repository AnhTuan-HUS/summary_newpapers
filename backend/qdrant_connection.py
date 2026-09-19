import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Sử dụng 'qdrant' làm host vì chúng ta đang gọi từ container backend sang container qdrant
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant") 
QDRANT_PORT = int(os.getenv("QDRANT_HTTP_PORT", 6333))

# Khởi tạo kết nối
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
COLLECTION_NAME = "news_articles_vectors"

def init_qdrant_db():
    try:
        # Kiểm tra và tạo Collection (bảng) cho Vector
        if not qdrant_client.collection_exists(COLLECTION_NAME):
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                # Kích thước 768 chiều bắt buộc dành cho model Gemini
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
            )
            print(f"✅ Đã khởi tạo thành công Qdrant collection: {COLLECTION_NAME}")
        else:
            print(f"⚡ Qdrant collection '{COLLECTION_NAME}' đã tồn tại và sẵn sàng.")
    except Exception as e:
        print(f"❌ Lỗi kết nối Qdrant: {e}")

if __name__ == "__main__":
    init_qdrant_db()