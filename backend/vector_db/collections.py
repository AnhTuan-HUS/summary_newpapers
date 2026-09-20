from qdrant_client.models import Distance, VectorParams
from .client import get_qdrant_client

def init_collections():
    client = get_qdrant_client()
    
    # Danh sách 3 collections cần khởi tạo theo đúng thiết kế
    collections = ["article_embeddings", "chunk_embeddings", "summary_embeddings"]
    
    try:
        for col_name in collections:
            if not client.collection_exists(collection_name=col_name):
                client.create_collection(
                    collection_name=col_name,
                    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
                )
                print(f"⚡ Đã khởi tạo thành công Qdrant collection: {col_name}")
            else:
                print(f"⚡ Qdrant collection '{col_name}' đã tồn tại và sẵn sàng.")
    except Exception as e:
        print(f"❌ Lỗi kết nối hoặc khởi tạo Qdrant: {e}")