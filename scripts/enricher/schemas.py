"""Định nghĩa Pydantic schema cho kết quả LLM Enrichment."""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class EnrichmentOutput(BaseModel):
    """Schema chuẩn cho dữ liệu trích xuất và bổ sung từ bài viết tin tức thô."""

    category_id: int = Field(
        description=(
            "ID của chuyên mục phù hợp nhất cho bài viết: "
            "1: Trí tuệ nhân tạo (AI, Machine Learning, LLM, Trợ lý ảo) "
            "2: An ninh mạng (Bảo mật, Mã độc, Hacking, An toàn thông tin) "
            "3: Thị trường (Kinh doanh, Tập đoàn, Đầu tư, Gọi vốn, Tài chính công nghệ) "
            "4: Robotics (Tự động hóa, Robot, Drone) "
            "5: Bán dẫn & vi mạch (Semiconductor, Chip, Nhà máy bán dẫn, Hardware) "
            "6: Chuyển đổi số (Hạ tầng số, Viễn thông, 5G, Chính phủ số, IoT) "
            "7: Khác (Các chủ đề công nghệ khác chưa thuộc 6 chuyên mục trên)"
        )
    )

    summary: str = Field(
        description="Bản tóm tắt ngắn gọn nội dung bài viết (TL;DR) khoảng 2-3 câu bằng tiếng Việt."
    )
    key_points: List[str] = Field(
        description="Danh sách từ 3 đến 5 điểm cốt lõi/luận điểm chính của bài viết."
    )
    why_it_matters: str = Field(
        description="Đánh giá ngắn gọn lý do vì sao tin tức này quan trọng hoặc tác động của nó tới ngành/người dùng."
    )
    importance_score: float = Field(
        description="Đánh giá mức độ quan trọng/độ HOT của tin tức trên thang điểm từ 0.0 (rất bình thường) đến 1.0 (tin chấn động/rất quan trọng)."
    )
