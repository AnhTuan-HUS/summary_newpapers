# Step 02: Chuẩn hóa dữ liệu & Khử trùng lặp bài viết (Content Normalization & Near-Duplicate Detection)

## 1. Mục tiêu
- Chuyển đổi các bài viết thô từ bảng `raw_articles` (có `status = 'pending'`) thành dữ liệu bài viết sạch.
- **Phát hiện trùng lặp (Near-Duplicate Detection)**: So sánh bài mới cào với các bài viết đã có để gom nhóm bài trùng lặp.
- **Bản nháp (`status = 'draft'`)**: Chỉ chèn những bài mới độc lập vào bảng `articles` dưới dạng bản nháp `status = 'draft'`.
- **Cập nhật bài trùng (`status = 'duplicate'`)**: Các bài trùng lặp sẽ không chèn thừa vào `articles` mà chỉ cập nhật `raw_articles.status = 'duplicate'` và trỏ `canonical_article_id` về bài gốc.

---

## 2. Phạm vi xử lý (Scope)

- **Lọc dữ liệu hợp lệ**: Quét `raw_articles` có `status = 'pending'` và `canonical_article_id IS NULL`.
- **Làm sạch nội dung**: Loại bỏ HTML rác, quảng cáo, footer... chuyển thành plain text (`content`).
- **Trích xuất Media**: Bóc tách danh sách ảnh/video và caption tương ứng (`thumbnail_url` dưới dạng JSONB).
- **Trích xuất Slug**: Tạo `slug` duy nhất từ URL (kèm `raw_article_id` làm suffix).
- **So khớp trùng lặp (Deduplication)**: 
  - Tính độ tương đồng N-gram Jaccard giữa bài viết mới và danh sách các bài gần đây trong `articles`.
  - Ưu tiên: Nếu riêng **Nội dung giống nhau $\ge 75\%$** $\rightarrow$ Coi là **Trùng lặp ngay** (bất kể tiêu đề).
  - Hoặc nếu điểm kết hợp ($40\%\text{ Title} + 60\%\text{ Content}$) $\ge 80\%$ $\rightarrow$ Coi là **Trùng lặp**.
- **Cập nhật trạng thái `raw_articles`**:
  - Bài gốc / Bài mới độc lập $\rightarrow$ `status = 'processed'`, `canonical_article_id = articles.id`.
  - Bài trùng lặp $\rightarrow$ `status = 'duplicate'`, `canonical_article_id = existing_article.id`.

---

## 3. Luồng xử lý dữ liệu (Workflow)

```text
raw_articles (status = 'pending', canonical_article_id IS NULL)
       │
       ▼
[1] get_raw_articles_for_processing(limit, offset)
       │
       ▼
[2] Lấy danh sách 500 bài viết gần đây trong `articles` (candidates)
       │
       ▼
[3] Với mỗi bản ghi raw:
    ├── normalize_content(content_raw) -> content + thumbnail_url
    ├── extract_slug(external_url) -> slug
    │
    ├── [4] Check Deduplication (find_duplicate_article):
    │     │
    │     ├──► NẾU TRÙNG (Content >= 75% hoặc Combined >= 80%):
    │     │     ├── raw_articles.canonical_article_id = duplicate_article.id
    │     │     └── raw_articles.status = 'duplicate'
    │     │
    │     └──► NẾU KHÔNG TRÙNG (Bài mới độc lập):
    │           ├── INSERT INTO articles (title, slug, content, thumbnail_url, status='draft', published_at) -> article_id
    │           ├── raw_articles.canonical_article_id = article_id
    │           ├── raw_articles.status = 'processed'
    │           └── Thêm bài mới vào candidates cho các lượt lặp sau
```

---

## 4. Input & Output

### Input (`raw_articles`)
- `id`
- `external_url`
- `title_raw`
- `content_raw`
- `published_at`
- `status`: `'pending'` 

### Output khi thành công (Bài mới độc lập)
- **`articles`**:
  - `id`: Auto ID
  - `title`: Tiêu đề bài viết
  - `slug`: Slug duy nhất
  - `content`: Nội dung văn bản thuần đã làm sạch
  - `thumbnail_url`: JSONB `{"link_media": "tiêu_đề_media"}`
  - `status`: `'draft'`
  - `published_at`: Thời gian xuất bản
- **`raw_articles`**:
  - `status`: `'processed'`
  - `canonical_article_id`: Trỏ tới `articles.id` vừa tạo

### Output khi bị trùng lặp (Bài trùng)
- **`articles`**: Không chèn thêm record mới.
- **`raw_articles`**:
  - `status`: `'duplicate'`
  - `canonical_article_id`: Trỏ tới `articles.id` của bài gốc đã tồn tại trước đó.

---