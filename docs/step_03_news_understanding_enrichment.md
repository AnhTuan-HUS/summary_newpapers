# Step 03: Hiểu tin tức & Bổ sung tri thức AI (News Understanding & LLM Enrichment)

## 1. Mục tiêu
Đọc các bài viết dạng bản nháp (`status = 'draft'`) từ bảng `articles`, sử dụng mô hình ngôn ngữ lớn (LLM / NLP Pipeline) để tạo tóm tắt, trích xuất điểm chính, phân loại chuyên mục và chấm điểm quan trọng. Sau đó cập nhật bài viết thành `status = 'published'`.

## 2. Phạm vi xử lý (Scope)
- **Lấy bài viết draft**: Quét bảng `articles` lọc các bài có `status = 'draft'`.
- **Phân loại Chuyên mục (`category_id`)**: Phân loại bài viết vào các chuyên mục (AI, Robotics, Research, Startup, Big Tech, Hardware).
- **Tóm tắt (`summary`)**: Sinh bản tóm tắt ngắn (TL;DR 2-3 câu).
- **Điểm chính (`key_points`)**: Trích xuất 3-5 ý cốt lõi của bài viết dạng JSON array.
- **Tầm quan trọng / Bối cảnh (`why_it_matters`)**: Phân tích lý do tin tức này quan trọng.
- **Chấm điểm (`importance_score`)**: Đánh giá độ HOT/ảnh hưởng của tin tức trên thang điểm 0.0 - 1.0.
- **Cập nhật bài viết**: Đổi `status` thành `'published'`.

## 3. Luồng xử lý dữ liệu (Workflow)

```text
articles (status = 'draft')
       │
       ▼
[1] Lấy batch các bài viết draft
       │
       ▼
[2] LLM Pipeline (Prompting / Structured Output):
    ├── Phân loại category -> category_id
    ├── Sinh tóm tắt -> summary
    ├── Trích xuất ý chính -> key_points (JSON)
    ├── Phân tích ảnh hưởng -> why_it_matters
    └── Chấm điểm -> importance_score (0.0 - 1.0)
       │
       ▼
[3] UPDATE articles SET 
      category_id = ...,
      summary = ...,
      key_points = ...,
      why_it_matters = ...,
      importance_score = ...,
      status = 'published',
      updated_at = NOW()
    WHERE id = article_id
```

## 4. Input & Output

### Input
- Bản ghi `articles` có `status = 'draft'`.

### Output
- Cập nhật bản ghi `articles`:
  - `category_id`: INTEGER (liên kết bảng `categories`)
  - `summary`: TEXT
  - `key_points`: TEXT (JSON String / Array)
  - `why_it_matters`: TEXT
  - `importance_score`: FLOAT
  - `status`: `'published'`

