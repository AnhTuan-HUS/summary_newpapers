# Step 2: Xử lý dữ liệu thô và chuẩn hóa

## Mục tiêu

Sau khi Step 1 đã thu thập dữ liệu từ nguồn và xuất ra các trường cơ bản như author, title, url, content_raw, publish_at, source, ... thì Step 2 thực hiện các thao tác để chuyển dữ liệu thô thành dữ liệu sạch, chuẩn hóa, có thể so sánh và gộp duplicate. Sau đó mới tiến hành sinh summary và key points cho bài viết.

## Scope

Bộ xử lý này bao gồm:

- lọc dữ liệu hợp lệ từ bảng raw_articles
- làm sạch nội dung và chuẩn hóa metadata
- chuẩn hóa URL, tạo slug và canonical URL
- xác định ngôn ngữ
- so sánh độ tương đồng giữa các bài viết
- phát hiện duplicate / near-duplicate
- chọn canonical article
- bảo toàn provenance
- validate chất lượng dữ liệu
- chuẩn bị dữ liệu cho bước tiếp theo: news understanding, retrieval, chat, content generation

## Input

Bảng nguồn: `raw_articles`

Các trường cần lấy:

- id
- status
- url
- title
- author
- content_raw
- publish_at
- source
- crawled_at
- raw_html
- metadata khác nếu có

Điều kiện lọc ban đầu:

- `status = success`
- `content_raw IS NOT NULL`
- `url IS NOT NULL`

## Output mong muốn

Từ mỗi bài viết raw, cần tạo ra dữ liệu chuẩn hóa có dạng:

- id
- raw_article_id
- source
- title
- title_normalized
- author
- author_normalized
- url_original
- url_normalized
- canonical_url
- slug
- content_raw
- content_normalized
- language
- publish_at
- publish_at_normalized
- duplicate_group_id
- canonical_article_id
- is_duplicate
- similarity_score
- summary
- key_points
- quality_score
- validation_passed
- provenance

## Quy trình thực hiện

### 1) Lọc raw data hợp lệ

Bắt đầu với dữ liệu từ bảng `raw_articles`:

- lọc `status == success`
- bỏ các record thiếu `content_raw` hoặc `url`
- ghi lại số lượng record hợp lệ để theo dõi

Mục tiêu:
- loại bỏ dữ liệu lỗi, dữ liệu trống, dữ liệu crawl không thành công

### 2) Chuẩn hóa nội dung

Từ `content_raw`, thực hiện các bước:

- loại bỏ HTML rác, boilerplate, sidebar, footer, ads, comments
- chuyển HTML thành text thuần
- xử lý entity, encoding và Unicode
- bỏ khoảng trắng thừa
- gộp lại các đoạn văn hợp lý
- giữ nguyên thông tin quan trọng như title, author, publish_at, content chính

Output:

- `content_normalized`
- `title_normalized`
- `author_normalized`
- `publish_at_normalized`

### 3) Chuẩn hóa URL

Từ `url` thực hiện:

- lower-case domain
- bỏ query params không cần thiết
- bỏ tracking params
- bỏ fragment/hash
- chuẩn hóa lại đường dẫn
- sinh `url_normalized`
- sinh `canonical_url`
- sinh `slug`

Ví dụ:

- url gốc: `https://example.com/news?utm_source=abc&id=123#top`
- url_normalized: `https://example.com/news`
- slug: `news`

Mục tiêu:
- chuẩn hóa URL để so sánh duplicate và group các bài tương đồng

### 4) Xác định ngôn ngữ

Sau khi có `content_normalized`, chạy language detection:

- vi
- en
- ja
- etc.
- mixed nếu đa ngôn ngữ

Lưu vào trường:

- `language`
- `language_confidence`

Lưu ý quan trọng:

- language detection phải làm sau khi content đã được normalize
- summary và key points chỉ nên sinh sau khi language đã xác định rõ

### 5) So sánh độ tương đồng

Sau khi có `content_normalized`, `title_normalized`, `url_normalized`, `slug`, tiến hành xác định xem bài viết có trùng hoặc gần trùng với bài khác hay không.

Các tiêu chí so sánh:

- cùng `url_normalized`
- title tương đồng
- nội dung tương đồng
- hash/embedding tương đồng
- similarity score > threshold

Output:

- `duplicate_group_id`
- `is_duplicate`
- `duplicate_of`
- `similarity_score`

### 6) Chọn canonical article

Sau khi nhóm duplicate/near-duplicate, chọn bài đại diện tốt nhất trong nhóm:

- nội dung đầy đủ hơn
- title rõ ràng hơn
- metadata chính xác hơn
- source đáng tin cậy hơn
- thời gian xuất bản rõ hơn

Output:

- `canonical_article_id`

### 7) Bảo toàn provenance

Đừng xóa raw record sau khi đã canonicalize.

Cần giữ mapping:

- raw_article_id -> canonical_article_id
- raw_url -> normalized_url
- raw content -> cleaned content -> canonical article

Mục tiêu:
- vẫn có traceability từ dữ liệu chuẩn hóa về dữ liệu gốc

### 8) Sinh summary và key points

Chỉ thực hiện sau khi:

- content đã normalize
- URL đã chuẩn hóa
- language đã xác định
- duplicate đã phân nhóm
- canonical article đã chọn

Khi `language == vi`, tạo:

- `summary_vi`
- `key_points_vi`

Nếu cần đa ngôn ngữ thì tạo thêm:

- `summary_en`
- `key_points_en`

Lưu ý quan trọng:

- không nên sinh summary ngay trên raw content
- không nên đánh summary trên nhiều bài lặp cùng một topic mà chưa gộp canonical

### 9) Validate chất lượng dữ liệu

Sau khi xử lý, chạy các rule kiểm tra:

- title không rỗng
- content_normalized không rỗng
- published_at hợp lệ
- url_normalized hợp lệ
- language đã xác định
- canonical_article_id được gán đúng
- summary và key_points không bị trống

Output:

- `quality_score`
- `validation_passed`
- `rejection_reason`

### 10) Publish dữ liệu chuẩn hóa

Sau khi pass validation, dữ liệu sẽ được publish để dùng cho bước tiếp theo:

- news understanding
- topic classification
- named entities
- embeddings
- retrieval & chat
- content generation / short-video generation

## Flow đúng theo thứ tự

```text
raw_articles
  -> filter status = success
  -> get content_raw + url + title + author + publish_at
  -> content_raw -> content_normalized
  -> url -> url_normalized + canonical_url + slug
  -> content_normalized -> language
  -> compare similarity / duplicate detection
  -> choose canonical article
  -> preserve provenance
  -> summary + key_points (sau khi canonical đã xác định)
  -> validation + quality score
  -> publish canonical article
```

## Logic ưu tiên đúng

Thứ tự đúng nên là:

1. Filter dữ liệu thô
2. Clean + normalize
3. URL normalize + slug
4. Detect language
5. Dedupe / near-duplicate
6. Canonicalize
7. Summary / key points
8. Validation
9. Publish

## Kết luận

Step 2 không chỉ là “đọc raw data và biến thành text sạch”, mà còn là bước chuẩn hóa, dedupe và canonicalization để đảm bảo dữ liệu đầu vào cho các bước sau là dữ liệu chính xác, không lặp và có thể truy nguyên nguồn gốc.

Đây là nền tảng để thực hiện:

- news understanding
- topic/category extraction
- named entities
- embeddings
- retrieval
- chat
- content generation

## Acceptance criteria

Step 2 được coi là hoàn tất khi:

- tất cả record `status = success` đã qua clean + normalize
- URL đã được canonicalize và gắn slug
- language được xác định rõ cho từng bài
- duplicate và near-duplicate đã được phát hiện và gom nhóm
- mỗi nhóm có 1 canonical article
- provenance được lưu đầy đủ
- summary và key points chỉ được sinh trên canonical article
- validation quality pass được ghi nhận

## Ghi chú

Nếu trong tương lai cần triển khai theo code, nên tách thành các module rõ ràng như:

- `normalize_content()`
- `normalize_url()`
- `detect_language()`
- `compute_similarity()`
- `build_canonical_cluster()`
- `generate_summary()`
- `validate_article()`

Mỗi module nên có unit test riêng để đảm bảo dữ liệu đầu ra ổn định.
