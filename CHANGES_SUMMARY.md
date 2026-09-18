# Summary of Changes and Purpose

Tài liệu này tổng hợp chi tiết các thay đổi gần đây trong dự án **AI Tech News System**, lý do và mục đích của từng thay đổi nhằm kết nối toàn diện giữa Backend (FastAPI), Frontend (Next.js), Database (PostgreSQL) và khắc phục các vấn đề liên quan tới Docker / Docker Compose.

---

## 1. Backend Integration (FastAPI)

### 📄 Các tệp liên quan:
- `backend/Dockerfile`
- `backend/app.py`
- `backend/api/` (Endpoints)
- `backend/db_operations.py`
- `backend/schemas.py`

### 🛠 Thay đổi thực hiện:
1. **Khắc phục lỗi Module Import trong Docker**: 
   - Đã điều chỉnh `PYTHONPATH` và vị trí thư mục ứng dụng trong `backend/Dockerfile` để Python có thể nhận diện đúng module `app` và các package con khi ứng dụng chạy bên trong Docker container.
2. **Bổ sung Middleware CORS (`backend/app.py`)**:
   - Thêm `CORSMiddleware` cho phép ứng dụng Next.js Frontend (chạy trên cổng `13000` / `localhost:13000`) gọi API trực tiếp sang Backend mà không bị trình duyệt chặn cross-origin.
3. **Phát triển các Endpoint API chính**:
   - `/api/v1/articles`: Lấy danh sách bài viết đã được xử lý/phân tích (có hỗ trợ phân trang `page`, `page_size` và lọc theo `category`).
   - `/api/v1/categories`: Lấy danh sách chuyên mục kèm số lượng bài viết tương ứng.

### 🎯 Mục đích:
Xây dựng một lớp RESTful API chuẩn hóa, hiệu năng cao giúp truyền tải dữ liệu bài viết và chuyên mục đã được enrich bằng AI từ Postgres DB đến người dùng cuối.

---

## 2. Frontend Integration & Dynamic Data (Next.js)

### 📄 Các tệp liên quan:
- `frontend/src/app/page.tsx` (Trang chủ)
- `frontend/src/app/chuyen-muc/[slug]/page.tsx` (Trang chuyên mục)
- `frontend/src/components/Header.tsx`
- `frontend/src/types/index.ts`

### 🛠 Thay đổi thực hiện:
1. **Kết nối dữ liệu thực từ Backend**:
   - Thay thế mock data cứng (dữ liệu mẫu) bằng logic Fetching API gọi đến `http://localhost:18080/api/v1/articles` và `/api/v1/categories`.
   - Chuẩn hóa TypeScript Types (`ApiArticleItem`, `ApiArticleDetail`, `PaginatedResponse`) trong `src/types/index.ts` để tương thích chính xác với schema dữ liệu từ Backend.
2. **Cập nhật giao diện trang chủ (`page.tsx`)**:
   - Hiển thị danh sách bài viết thật từ cơ sở dữ liệu.
   - Sắp xếp bài viết nổi bật (Hero/Spotlight) dựa trên điểm số quan trọng `importance_score` do AI tính toán.
3. **Cập nhật điều hướng chuyên mục (`Header.tsx` & `[slug]/page.tsx`)**:
   - Chuyên mục trên thanh Header phản ánh đúng các danh mục thực tế có trong hệ thống (Công nghệ AI, An ninh mạng, Thị trường, v.v.).
   - Khi truy cập vào từng chuyên mục, trang sẽ tự động lọc dữ liệu bài viết thuộc chuyên mục đó.

### 🎯 Mục đích:
Hoàn thiện luồng trải nghiệm người dùng end-to-end, đảm bảo dữ liệu hiển thị trên giao diện là dữ liệu thời gian thực được thu thập, làm sạch và phân tích tự động.

---

## 3. Docker Compose & Environment Stability

### 📄 Các tệp liên quan:
- `docker-compose.yml`

### 🛠 Thay đổi thực hiện:
1. **Tối ưu hóa Service Configuration**:
   - Cập nhật định nghĩa service `backend` trong `docker-compose.yml`, thiết lập port mapping `18080:8000`.
   - Đảm bảo các biến môi trường kết nối Database (`POSTGRES_HOST=postgres`, `POSTGRES_DB=news_db`, v.v.) đồng bộ giữa các container.
2. **Sửa lỗi khởi động & Build container**:
   - Kiểm tra và tái khởi động sạch hệ thống bằng lệnh `docker compose up --build -d`.
   - Xác minh toàn bộ 6 services (`postgres`, `backend`, `frontend`, `airflow-webserver`, `airflow-scheduler`, `airflow-postgres`) đều đạt trạng thái `Up (healthy)`.

### 🎯 Mục đích:
Đảm bảo toàn bộ hệ thống Microservices bao gồm Crawler, Processing Pipeline, Airflow Orchestrator, Backend API và Frontend UI hoạt động ổn định và nhất quán trong môi trường Dockerized.
