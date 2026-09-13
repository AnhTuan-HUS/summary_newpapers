# Đây là mục sẽ tiến hành step 2 của dự án: Normalize content & 
## 1. Chuẩn hóa content_raw
- Thực hiện lấy dữ liệu raw trong bảng raw_aritcles có trạng thái "SUCCESS"
- Bóc tách dữ liệu bằng BeautifulSoup :
    + content_raw ------>  normal_content + thumbnail_url (là dict có dạng ```{link ảnh/video : tiêu đề}```)
- normal_url -----> slug : bóc tách từ url để lấy slug cho từng bài báo
=> Output của mục này sẽ trả về dữ liệu theo định dạng `{"id", "category_id", "title" , "slug" ,"content", "thumbnail_url", "status", "published_at"}`
## 2. Khử trùng lặp về nội dung bằng thuật toán N-gram Jaccard
- Sau khi dữ liệu được chuẩn hóa -> content sạch, ta sẽ tiến hành khử trùng lặp về nội dung
- Sử dụng thuật toán `Jaccard`
$$
J(A,B) = \frac{|A \cap B|}{|A \cup B|}
$$
=> xét sự trùng lặp về từ ngữ  trong các bài viết lấy được 3 days gần nhất => gán status `duplicate` cho các bài phát hiện trùng lặp, gán `raw_articles.canonical_article_id = articles.id`