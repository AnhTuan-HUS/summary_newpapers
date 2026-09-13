# Step 2: Xử lý dữ liệu thô, Chuẩn hóa & Khử trùng lặp nội dung

## 1. Mục tiêu

Sau khi Step 1 đã thu thập dữ liệu từ các nguồn (RSS, API, Web Listing) vào bảng `raw_articles`, Step 2 thực hiện:
1. Làm sạch dữ liệu thô (loại bỏ HTML rác, quảng cáo, trích xuất text thuần).
2. Bóc tách danh sách media/thumbnail và tạo slug duy nhất.
3. **Phát hiện trùng lặp nội dung (Near-Duplicate Detection)** giữa các bài báo từ nhiều nguồn khác nhau.
4. Lưu bài viết đại diện sạch vào bảng `articles` dưới dạng bản nháp (`status = 'draft'`).
5. Bảo toàn nguồn gốc (provenance) bằng cách gắn `canonical_article_id` và cập nhật trạng thái `raw_articles` (`processed` hoặc `duplicate`).

---

## 2. Phạm vi & Trạng thái dữ liệu (Data Status Standard)

Theo chuẩn Schema của Database (`001_create_database.sql`), bảng `raw_articles` được quản lý bởi 3 trạng thái chuẩn:
- **`pending`**: Bài báo thô vừa được cào về, đang chờ được xử lý ở Step 2.
- **`processed`**: Bài báo đã được làm sạch và đưa vào bảng `articles` với vai trò là bài đại diện độc lập (Canonical Article).
- **`duplicate`**: Bài báo được phát hiện trùng lặp nội dung với một bài báo đã có trong `articles`.

Bảng `articles` lưu trữ các bài đại diện:
- **`status = 'draft'`**: Bài viết đã làm sạch nội dung từ Step 2, đang chờ bổ sung tri thức AI ở Step 3.
- các trường LLM (`summary`, `key_points`, `why_it_matters`, `importance_score`, `category_id`) để `NULL` tạm thời cho đến Step 3.

---

## 3. Thuật toán phát hiện trùng lặp (Deduplication Engine)

Thực hiện trong module `scripts/processor/dedup.py`:
- Sử dụng thuật toán **N-gram Jaccard Similarity** ($n=2$ cho Tiêu đề, $n=3$ cho Nội dung).
- **Quy tắc 1 (Trùng nội dung)**: Nếu riêng nội dung trùng lặp $\ge 75\%$ $\rightarrow$ Coi là trùng lặp ngay (dù tiêu đề khác nhau).
- **Quy tắc 2 (Trùng kết hợp)**: $40\%\text{ Title} + 60\%\text{ Content} \ge 80\%$ $\rightarrow$ Coi là trùng lặp.

---

## 4. Quy trình xử lý (Workflow)

```text
raw_articles (status = 'pending', canonical_article_id IS NULL)
   └──> Lấy batch bài thô (get_raw_articles_for_processing)
   └──> Lấy 500 bài gần nhất trong `articles` làm ứng viên so sánh
   └──> Với mỗi bài thô:
         ├── 1. Làm sạch HTML -> content (plain text) + thumbnail_url (dict)
         ├── 2. Sinh slug duy nhất từ URL
         ├── 3. Kiểm tra trùng lặp (find_duplicate_article):
         │     ├── NẾU TRÙNG LẶP:
         │     │     ├── raw_articles.canonical_article_id = canonical_article.id
         │     │     └── raw_articles.status = 'duplicate'
         │     │
         │     └── NẾU BÀI MỚI ĐỘC LẬP:
         │           ├── INSERT bài mới vào `articles` (status = 'draft') -> nhận article_id
         │           ├── raw_articles.canonical_article_id = article_id
         │           └── raw_articles.status = 'processed'
```

---

## 5. Tệp nguồn chính (Source Code Implementation)

- Pipeline thực thi CLI: [`scripts/processor/normalize.py`](file:///home/mr-tuan/Projects/news_summary/scripts/processor/normalize.py)
- Thuật toán so khớp trùng lặp: [`scripts/processor/dedup.py`](file:///home/mr-tuan/Projects/news_summary/scripts/processor/dedup.py)
- Thao tác Database: [`database/operations.py`](file:///home/mr-tuan/Projects/news_summary/database/operations.py)
- Hàm làm sạch DOM & HTML: [`scripts/crawler/utils.py`](file:///home/mr-tuan/Projects/news_summary/scripts/crawler/utils.py)
- Tài liệu tóm tắt ngắn: [`docs/step_02_content_normalization.md`](file:///home/mr-tuan/Projects/news_summary/docs/step_02_content_normalization.md)

---

## 6. Hướng dẫn chạy & Kiểm thử

```bash
# 1. Thống kê số lượng theo 3 trạng thái Schema (pending / processed / duplicate)
python -m scripts.processor.normalize --stats

# 2. Chạy thử nghiệm xem log không ghi DB (--dry-run)
python -m scripts.processor.normalize --dry-run --limit 10 -v

# 3. Chạy thực tế (mặc định batch 200 bài)
python -m scripts.processor.normalize --limit 200 -v
```
