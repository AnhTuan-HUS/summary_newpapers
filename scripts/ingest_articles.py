import sys
import os

# Thêm đường dẫn gốc để import được các module trong backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.vector_db.embeddings import get_gemini_embedding
from backend.vector_db.chunking import split_article_into_chunks
from backend.vector_db.operations import save_vector
# Nếu bạn có hàm lấy dữ liệu từ DB, hãy import tại đây (ví dụ từ db_operations)
# from backend.db_operations import get_all_articles

def process_and_store_article(article_data: dict):
    """
    article_data cần có các key: id, title, content, summary
    """
    article_id = article_data['id']
    print(f"🔄 Đang xử lý bài báo ID {article_id}: {article_data['title'][:50]}...")
    
    # 1. Xử lý Summary Embeddings
    if article_data.get('summary'):
        summary_vec = get_gemini_embedding(article_data['summary'])
        save_vector(
            collection_name="summary_embeddings",
            point_id=article_id,
            vector=summary_vec,
            metadata={"article_id": article_id, "title": article_data['title'], "type": "summary"}
        )
    
    # 2. Xử lý Article Embeddings (Title + Đoạn đầu content)
    article_header = f"{article_data['title']}. {article_data['content'][:500]}"
    article_vec = get_gemini_embedding(article_header)
    save_vector(
        collection_name="article_embeddings",
        point_id=article_id,
        vector=article_vec,
        metadata={"article_id": article_id, "title": article_data['title'], "type": "article"}
    )
    
    # 3. Xử lý Chunk Embeddings (Cắt nhỏ content)
    chunks = split_article_into_chunks(article_data['content'])
    for idx, chunk_text in enumerate(chunks):
        chunk_vec = get_gemini_embedding(chunk_text)
        
        # Tạo ID duy nhất cho chunk (VD: article_id = 15 -> chunk_id = 15000, 15001...)
        chunk_point_id = int(f"{article_id}{idx:03d}")
        
        save_vector(
            collection_name="chunk_embeddings",
            point_id=chunk_point_id,
            vector=chunk_vec,
            metadata={
                "article_id": article_id,
                "chunk_index": idx,
                "text": chunk_text,
                "title": article_data['title']
            }
        )
    print(f"✅ Hoàn tất bài báo ID {article_id} (Tạo được {len(chunks)} chunks)")

if __name__ == "__main__":
    # --- PHẦN CHẠY THỬ NGHIỆM ---
    # Thay vì lấy từ DB ngay, chúng ta tạo 1 mock data dựa trên file SQL của bạn để test luồng
    sample_article = {
        "id": 999, 
        "title": "Nhà mạng được hưởng chính sách đặc biệt khi đầu tư phát triển mạng 5G",
        "summary": "Các nhà mạng sẽ nhận được nhiều ưu đãi khi triển khai hạ tầng 5G tại Việt Nam.",
        "content": "Theo quy định mới, các nhà mạng viễn thông khi tham gia đầu tư phát triển mạng 5G sẽ được hưởng nhiều chính sách đặc biệt. Điều này bao gồm hỗ trợ về thuế, thủ tục cấp phép và tiếp cận mặt bằng trạm phát sóng...\n\nSự hỗ trợ này nhằm đẩy nhanh tiến độ phủ sóng 5G trên toàn quốc, đáp ứng nhu cầu chuyển đổi số..."
    }
    
    print("Bắt đầu Ingestion Pipeline...")
    process_and_store_article(sample_article)
    print("🎉 Ingestion thành công! Kiểm tra dữ liệu trên Qdrant.")