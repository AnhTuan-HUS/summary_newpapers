# Đây là mục sẽ tiến hành step 2 của dự án: Normalize content & 
## 1. Chuẩn hóa content_raw
- Thực hiện lấy dữ liệu raw trong bảng raw_aritcles có trạng thái "SUCCESS"
- Bóc tách dữ liệu bằng BeautifulSoup :
    + content_raw ------>  normal_content + thumbnail_url (là dict có dạng ```{link ảnh/video : tiêu đề}```)
- normal_url -----> slug : bóc tách từ url để lấy slug cho từng bài báo
=> Output của mục này sẽ trả về dữ liệu theo định dạng {"id", "category_id", "title" , "slug" ,"content", "thumbnail_url", "status", "published_at"}