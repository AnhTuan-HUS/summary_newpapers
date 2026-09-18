

| API dự kiến | Mục đích | Dữ liệu đầu vào | Dữ liệu đầu ra | Truy vấn như thế nào |
| ----- | ----- | ----- | ----- | ----- |
| `GET /api/articles` | Lấy danh sách bài viết để hiển thị trên website, hỗ trợ phân trang và lọc tin |  |  |  |
| `GET /api/articles/{article_id}` | Lấy thông tin chi tiết của một bài viết gồm nội dung, tóm tắt, key points, nguồn và metadata |  |  |  |
| `GET /api/articles/latest` | Lấy danh sách các bài viết mới nhất |  |  |  |
| `GET /api/articles/trending` | Lấy danh sách tin nổi bật/trending dựa trên importance score, thời gian và mức độ quan tâm |  |  |  |
| `GET /api/articles/{article_id}/related` | Tìm các bài viết có nội dung, chủ đề hoặc sự kiện liên quan đến bài hiện tại |  |  |  |
| `GET /api/categories` | Lấy danh sách chuyên mục như AI, Robotics, Research, Startup, Big Tech, Hardware |  |  |  |
| `GET /api/topics` | Lấy danh sách chủ đề đang được hệ thống theo dõi và liên kết với các bài viết |  |  |  |
| `GET /api/topics/{topic_id}/articles` | Lấy các bài viết thuộc một chủ đề cụ thể |  |  |  |
| `GET /api/sources` | Lấy danh sách nguồn tin như OpenAI, Google DeepMind, Anthropic, NVIDIA, RSS, YouTube, Reddit... |  |  |  |
| `GET /api/sources/{source_id}/articles` | Lấy danh sách bài viết theo một nguồn tin cụ thể |  |  |  |
| `GET /api/search` | Tìm kiếm bài viết theo từ khóa và các điều kiện lọc cơ bản |  |  |  |
| `POST /api/search/semantic` | Tìm kiếm ngữ nghĩa bằng embedding/vector database thay vì chỉ khớp từ khóa |  |  |  |
| `POST /api/articles/{article_id}/tldr` | Sinh hoặc lấy bản tóm tắt theo thời lượng đọc như 30 giây, 1 phút, 3 phút hoặc Full |  |  |  |
| `POST /api/chat/article` | Article Chat: hỏi đáp trong phạm vi một bài viết đang đọc và một số bài liên quan |  |  |  |
| `POST /api/chat/global` | Global News Chat: hỏi đáp, tổng hợp và phân tích trên toàn bộ kho tin tức bằng RAG |  |  |  |
| `GET /api/chat/{conversation_id}/messages` | Lấy lịch sử hội thoại của chatbot |  |  |  |
| `POST /api/collect/rss` | Kích hoạt thu thập tin từ các nguồn RSS đã cấu hình |  |  |  |
| `POST /api/collect/web` | Kích hoạt crawler để thu thập bài viết từ website |  |  |  |
| `POST /api/collect/social` | Thu thập nội dung từ các nguồn mạng xã hội như YouTube, X, Reddit |  |  |  |
| `POST /api/collect/technical` | Thu thập dữ liệu từ các nguồn kỹ thuật/học thuật như arXiv và GitHub |  |  |  |
| `POST /api/articles/process` | Đưa bài viết thô vào pipeline làm sạch, chuẩn hóa và trích xuất nội dung chính |  |  |  |
| `POST /api/articles/deduplicate` | Kiểm tra và gom các bài viết trùng lặp hoặc cùng nói về một tin thành Canonical Article |  |  |  |
| `POST /api/articles/{article_id}/analyze` | Chạy News Understanding: classification, entity extraction, summarization, key points, impact analysis... |  |  |  |
| `POST /api/articles/{article_id}/embedding` | Sinh embedding cho bài viết, summary và chunks để lưu vào Vector DB phục vụ semantic search/RAG |  |  |  |
| `POST /api/content/angle` | Phân tích bài viết và chọn góc nội dung phù hợp như Breaking News, Why It Matters, Comparison... |  |  |  |
| `POST /api/content/generate` | Sinh nội dung từ bài báo cho LinkedIn, Facebook, X/Twitter hoặc Newsletter |  |  |  |
| `POST /api/content/short-script` | Sinh kịch bản TikTok/YouTube Shorts gồm hook, visual plan, voice script, caption và hashtag |  |  |  |
| `POST /api/videos/generate` | Khởi tạo pipeline tạo video ngắn từ script đã sinh |  |  |  |
| `GET /api/videos/{video_id}` | Lấy thông tin một video đã tạo, trạng thái và metadata liên quan |  |  |  |
| `GET /api/videos/{video_id}/status` | Theo dõi trạng thái background job tạo TTS, subtitle, asset và render video |  |  |  |
| `POST /api/videos/{video_id}/render` | Kích hoạt bước composition/render cuối bằng Remotion/FFmpeg |  |  |  |
| `POST /api/assets/upload` | Upload hoặc đăng ký hình ảnh, audio, thumbnail và các asset dùng trong quá trình tạo video |  |  |  |
| `GET /api/assets/{asset_id}` | Lấy metadata hoặc đường dẫn truy cập asset trong MinIO/S3 |  |  |  |
| `POST /api/auth/login` | Đăng nhập người dùng hoặc quản trị viên |  |  |  |
| `POST /api/auth/logout` | Kết thúc phiên đăng nhập |  |  |  |
| `GET /api/users/me` | Lấy thông tin tài khoản người dùng hiện tại |  |  |  |
| `GET /api/admin/dashboard` | Cung cấp số liệu tổng quan cho Admin Dashboard như số bài, nguồn, job xử lý, video... |  |  |  |
| `GET /api/jobs/{job_id}` | Theo dõi trạng thái các background job như crawl, embedding, summarize và render video |  |  |  |
| `POST /api/jobs/{job_id}/retry` | Cho phép chạy lại một background job bị lỗi |  |  |  |

