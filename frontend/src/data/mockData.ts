import type { Article, Category, MenuItem, NewsletterSub } from "@/types";

export const categories: Category[] = [
  {
    id: "cat-ban-dan",
    name: "Bán dẫn & Vi mạch",
    slug: "ban-dan-vi-mach",
    description:
      "Chiến lược chip, nhà máy wafer, thiết kế IC và chuỗi cung ứng bán dẫn Việt Nam.",
  },
  {
    id: "cat-ai",
    name: "Trí tuệ nhân tạo",
    slug: "tri-tue-nhan-tao",
    description: "Mô hình ngôn ngữ, AI tạo sinh và ứng dụng AI trong doanh nghiệp.",
  },
  {
    id: "cat-startup",
    name: "Startup & Đầu tư",
    slug: "startup-dau-tu",
    description: "Gọi vốn, quỹ đầu tư mạo hiểm và hệ sinh thái khởi nghiệp công nghệ.",
  },
  {
    id: "cat-xe-dien",
    name: "Xe điện",
    slug: "xe-dien",
    description: "Pin, trạm sạc, xe điện và giao thông thông minh.",
  },
  {
    id: "cat-dien-thoai",
    name: "Điện thoại",
    slug: "dien-thoai",
    description: "Smartphone, chip di động và hệ sinh thái ứng dụng.",
  },
  {
    id: "cat-ha-tang",
    name: "Hạ tầng số",
    slug: "ha-tang-so",
    description: "Data center, 5G/6G, cloud và an ninh mạng.",
  },
];

export const menuItems: MenuItem[] = [
  { id: "menu-home", label: "Trang chủ", href: "/" },
  ...categories.map((category) => ({
    id: `menu-${category.slug}`,
    label: category.name,
    href: `/chuyen-muc/${category.slug}`,
  })),
];

export const articles: Article[] = [
  {
    id: "art-hero-ban-dan",
    title:
      "Việt Nam tăng tốc công nghiệp bán dẫn: mục tiêu 50.000 kỹ sư chip và chuỗi thiết kế – đóng gói đến 2030",
    slug: "viet-nam-tang-toc-cong-nghiep-ban-dan-50000-ky-su-chip",
    excerpt:
      "Chính phủ, Intel, Samsung và các tập đoàn trong nước đang đẩy mạnh đào tạo nhân lực, mở rộng OSAT và thu hút đầu tư wafer — kỳ vọng đưa Việt Nam thành mắt xích thiết kế vi mạch của khu vực.",
    content:
      "Chiến lược phát triển công nghiệp bán dẫn giai đoạn 2024–2030 đặt trọng tâm vào nhân lực thiết kế IC, đóng gói kiểm định (OSAT) và từng bước tham gia khâu chế tạo. Intel Products Vietnam tiếp tục mở rộng năng lực thử nghiệm chip, trong khi Samsung và một số nhà đầu tư Đài Loan – Hàn Quốc khảo sát các khu công nghệ cao tại Bắc Ninh, Đà Nẵng và TP.HCM. Các trường ĐH Bách khoa, FPT, Viettel High Tech công bố chương trình đào tạo kỹ sư vi mạch phối hợp doanh nghiệp, hướng tới mốc 50.000 nhân sự chuyên sâu.",
    coverImage:
      "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1600&q=80",
    categoryId: "cat-ban-dan",
    author: "Nguyễn Minh Khoa",
    publishedAt: "2026-09-10T07:30:00+07:00",
    views: 48210,
    isHero: true,
    isSpotlight: false,
    tags: ["bán dẫn", "vi mạch", "OSAT", "nhân lực"],
  },
  {
    id: "art-spot-ai",
    title:
      "Doanh nghiệp Việt triển khai AI tạo sinh nội bộ: tiết kiệm chi phí, siết kiểm soát dữ liệu",
    slug: "doanh-nghiep-viet-trien-khai-ai-tao-sinh-noi-bo",
    excerpt:
      "Nhiều ngân hàng và tập đoàn bán lẻ chuyển sang mô hình on-premise hoặc private cloud để dùng LLM mà không đưa dữ liệu khách hàng ra ngoài.",
    content:
      "Sau giai đoạn thử nghiệm ChatGPT và Claude, khối doanh nghiệp lớn tại Việt Nam bắt đầu tự host mô hình mã nguồn mở kết hợp RAG trên kho tài liệu nội bộ.",
    coverImage:
      "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=1200&q=80",
    categoryId: "cat-ai",
    author: "Trần Hà An",
    publishedAt: "2026-09-09T16:20:00+07:00",
    views: 22140,
    isHero: false,
    isSpotlight: true,
    tags: ["AI", "LLM", "doanh nghiệp"],
  },
  {
    id: "art-spot-startup",
    title: "Quỹ Đông Nam Á giải ngân 18 triệu USD cho startup fintech và logistics Việt Nam",
    slug: "quy-dong-nam-a-giai-ngan-18-trieu-usd-startup-viet",
    excerpt:
      "Vòng Series A tập trung các công ty có doanh thu lặp lại và giấy phép hoạt động rõ ràng, khác hẳn làn sóng tăng trưởng bằng mọi giá trước đây.",
    content:
      "Ba startup Việt vừa chốt vòng gọi vốn với sự tham gia của quỹ khu vực. Thị trường vốn mạo hiểm 2026 được đánh giá thận trọng hơn nhưng chất lượng thương vụ cao hơn.",
    coverImage:
      "https://images.unsplash.com/photo-1559136555-9303baea8ebd?auto=format&fit=crop&w=1200&q=80",
    categoryId: "cat-startup",
    author: "Phạm Quốc Huy",
    publishedAt: "2026-09-09T11:05:00+07:00",
    views: 19870,
    isHero: false,
    isSpotlight: true,
    tags: ["startup", "fintech", "gọi vốn"],
  },
  {
    id: "art-spot-xe-dien",
    title: "Mạng trạm sạc nhanh phủ 63 tỉnh: bài toán pin, lưới điện và tiêu chuẩn chung",
    slug: "mang-tram-sac-nhanh-phu-63-tinh-pin-luoi-dien",
    excerpt:
      "VinFast và các nhà cung cấp độc lập đua phủ sạc DC, trong khi ngành điện cảnh báo phụ tải đỉnh vào giờ cao điểm.",
    content:
      "Quy hoạch trạm sạc gắn với cao tốc Bắc – Nam và khu đô thị lớn. Chuyên gia đề xuất chuẩn cổng sạc thống nhất và giá điện theo khung giờ.",
    coverImage:
      "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?auto=format&fit=crop&w=1200&q=80",
    categoryId: "cat-xe-dien",
    author: "Lê Thanh Vân",
    publishedAt: "2026-09-08T19:40:00+07:00",
    views: 31560,
    isHero: false,
    isSpotlight: true,
    tags: ["xe điện", "trạm sạc", "pin"],
  },
  {
    id: "art-spot-dien-thoai",
    title: "Chip di động 3nm vào smartphone tầm trung: hiệu năng tăng, giá chưa giảm nhanh",
    slug: "chip-di-dong-3nm-smartphone-tam-trung",
    excerpt:
      "Các hãng Android đẩy tiến trình tiên tiến xuống phân khúc 8–12 triệu đồng, nhưng chênh lệch giá linh kiện vẫn lớn so với thế hệ cũ.",
    content:
      "Modem 5G thế hệ mới và NPU mạnh hơn cho AI trên máy là lý do nhà sản xuất chấp nhận tăng BOM. Người dùng Việt Nam vẫn cân nhắc pin và cập nhật phần mềm dài hạn.",
    coverImage:
      "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=1200&q=80",
    categoryId: "cat-dien-thoai",
    author: "Đỗ Nhật Minh",
    publishedAt: "2026-09-08T09:15:00+07:00",
    views: 27430,
    isHero: false,
    isSpotlight: true,
    tags: ["smartphone", "chip", "3nm"],
  },
  {
    id: "art-latest-01",
    title: "FPT và đối tác Đài Loan mở phòng lab thiết kế IC analog tại TP.HCM",
    slug: "fpt-doi-tac-dai-loan-phong-lab-thiet-ke-ic-analog",
    excerpt:
      "Phòng lab phục vụ đào tạo thực chiến EDA và prototype cảm biến cho công nghiệp, y tế.",
      content:
      "Việc mở phòng lab thiết kế IC analog tại TP.HCM đánh dấu bước tiến mới trong hoạt động đào tạo và phát triển nguồn nhân lực bán dẫn tại Việt Nam.\n\n"
      + "Phòng lab được xây dựng nhằm tạo môi trường thực hành trực tiếp cho sinh viên và kỹ sư trẻ. Thay vì chỉ học lý thuyết về mạch điện và thiết kế vi mạch, người học có thể tiếp cận các công cụ EDA và quy trình thiết kế gần với môi trường doanh nghiệp.\n\n"
      + "Một trong những trọng tâm của phòng lab là thiết kế IC analog. Đây là lĩnh vực có vai trò quan trọng trong nhiều thiết bị điện tử như cảm biến, thiết bị y tế, hệ thống điều khiển và các thiết bị IoT.\n\n"
      + "Theo định hướng của dự án, người học sẽ được làm quen với quy trình từ xây dựng ý tưởng mạch, mô phỏng, kiểm tra thiết kế cho đến tạo prototype. Cách tiếp cận này giúp rút ngắn khoảng cách giữa kiến thức trong trường đại học và yêu cầu thực tế của doanh nghiệp.\n\n"
      + "Việc hợp tác với đối tác Đài Loan cũng mang lại cơ hội tiếp cận kinh nghiệm từ một trong những trung tâm sản xuất và thiết kế bán dẫn lớn tại châu Á. Các chương trình đào tạo có thể được xây dựng theo hướng kết hợp giữa chuyên gia doanh nghiệp và giảng viên đại học.\n\n"
      + "Đối với Việt Nam, phát triển nguồn nhân lực là một trong những yếu tố quan trọng nếu muốn tham gia sâu hơn vào chuỗi giá trị bán dẫn. Bên cạnh số lượng kỹ sư, thị trường cần những nhân sự có khả năng sử dụng thành thạo công cụ thiết kế và hiểu rõ quy trình phát triển sản phẩm.\n\n"
      + "Trong thời gian tới, phòng lab được kỳ vọng trở thành nơi thử nghiệm các dự án IC analog phục vụ những bài toán thực tế. Các nhóm nghiên cứu có thể bắt đầu từ những mạch nhỏ trước khi tiến tới những thiết kế phức tạp hơn.\n\n"
      + "Sự kết hợp giữa đào tạo, nghiên cứu và nhu cầu của doanh nghiệp sẽ quyết định hiệu quả lâu dài của mô hình này. Nếu được triển khai đúng hướng, các phòng lab tương tự có thể góp phần tạo ra nguồn nhân lực bán dẫn chất lượng cao cho thị trường Việt Nam.",
    coverImage:
      "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=1200&q=80",
    categoryId: "cat-ban-dan",
    author: "Nguyễn Minh Khoa",
    publishedAt: "2026-09-10T10:00:00+07:00",
    views: 6120,
    isHero: false,
    isSpotlight: false,
    tags: ["FPT", "IC analog", "đào tạo"],
  },
  {
    id: "art-latest-02",
    title: "Việt Nam cấp phép thêm data center xanh tại Bắc Ninh và Đà Nẵng",
    slug: "viet-nam-cap-phep-data-center-xanh-bac-ninh-da-nang",
    excerpt:
      "Yêu cầu PUE thấp và nguồn điện tái tạo đi kèm giấy phép xây dựng trung tâm dữ liệu quy mô lớn.",
    content:
      "Bộ Thông tin và Truyền thông nhấn mạnh hạ tầng số phải đi cùng hiệu quả năng lượng.",
    coverImage:
      "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80",
    categoryId: "cat-ha-tang",
    author: "Bùi Gia Hân",
    publishedAt: "2026-09-10T08:45:00+07:00",
    views: 8940,
    isHero: false,
    isSpotlight: false,
    tags: ["data center", "PUE", "hạ tầng số"],
  },
  {
    id: "art-latest-03",
    title: "Mô hình mở Việt Nam cạnh tranh LLM quốc tế trên tác vụ tiếng Việt",
    slug: "mo-hinh-mo-viet-nam-canh-tranh-llm-tieng-viet",
    excerpt:
      "Benchmark pháp lý, y tế và khách hàng cho thấy mô hình nội địa vượt một số API lớn ở ngữ cảnh địa phương.",
    content:
      "Nhóm nghiên cứu công bố bộ dữ liệu đánh giá tiếng Việt có kiểm soát bản quyền.",
    coverImage:
      "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=1200&q=80",
    categoryId: "cat-ai",
    author: "Trần Hà An",
    publishedAt: "2026-09-09T20:10:00+07:00",
    views: 15320,
    isHero: false,
    isSpotlight: false,
    tags: ["LLM", "tiếng Việt", "mã nguồn mở"],
  },
  {
    id: "art-latest-04",
    title: "Startup nông nghiệp số gọi vốn pre-Series A để mở rộng cảm biến ruộng lúa",
    slug: "startup-nong-nghiep-so-pre-series-a-cam-bien-ruong-lua",
    excerpt:
      "Thiết bị đo độ ẩm, sâu bệnh và tưới nhỏ giọt kết nối 4G được thử nghiệm tại ĐBSCL.",
    content:
      "Nhà đầu tư impact fund đánh giá khả năng giảm phân bón và nước tưới.",
    coverImage:
      "https://images.unsplash.com/photo-1574943320219-553eb213f72d?auto=format&fit=crop&w=1200&q=80",
    categoryId: "cat-startup",
    author: "Phạm Quốc Huy",
    publishedAt: "2026-09-09T14:30:00+07:00",
    views: 4310,
    isHero: false,
    isSpotlight: false,
    tags: ["agritech", "IoT", "ĐBSCL"],
  },
  {
    id: "art-latest-05",
    title: "Pin LFP nội địa: bước đi giảm phụ thuộc nhập khẩu cho xe bus điện",
    slug: "pin-lfp-noi-dia-xe-bus-dien",
    excerpt:
      "Nhà máy lắp ráp pack pin tại Hải Phòng hướng tới xe buýt công cộng trước khi vào ô tô cá nhân.",
    content:
      "Công nghệ LFP an toàn nhiệt tốt hơn NMC, phù hợp vận tải công cộng.",
    coverImage:
      "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?auto=format&fit=crop&w=1200&q=80",
    categoryId: "cat-xe-dien",
    author: "Lê Thanh Vân",
    publishedAt: "2026-09-09T08:00:00+07:00",
    views: 10280,
    isHero: false,
    isSpotlight: false,
    tags: ["pin LFP", "xe bus điện", "BMS"],
  },
  {
    id: "art-latest-06",
    title: "Android 17 beta: quyền riêng tư camera và AI dịch realtime trên máy",
    slug: "android-17-beta-quyen-rieng-tu-camera-ai-dich",
    excerpt:
      "Google siết quyền truy cập ảnh gần đây và đẩy nhận diện giọng nói offline cho nhiều ngôn ngữ châu Á.",
    content:
      "Bản beta nhấn mạnh xử lý trên thiết bị để giảm gửi audio lên mây.",
    coverImage:
      "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?auto=format&fit=crop&w=1200&q=80",
    categoryId: "cat-dien-thoai",
    author: "Đỗ Nhật Minh",
    publishedAt: "2026-09-08T21:25:00+07:00",
    views: 18750,
    isHero: false,
    isSpotlight: false,
    tags: ["Android", "quyền riêng tư", "on-device AI"],
  },
  {
    id: "art-latest-07",
    title: "5G Standalone tại 5 thành phố lớn: độ trễ thấp cho nhà máy thông minh",
    slug: "5g-standalone-5-thanh-pho-lon-nha-may-thong-minh",
    excerpt:
      "Mạng SA tách hoàn toàn lõi 4G, mở đường slicing cho robot AGV và camera kiểm định.",
    content:
      "Ba nhà mạng công bố gói riêng cho khu công nghiệp. Doanh nghiệp sản xuất quan tâm SLA hơn tốc độ download trên giấy.",
    coverImage:
      "https://images.unsplash.com/photo-1544197150-b99a5804f8b1?auto=format&fit=crop&w=1200&q=80",
    categoryId: "cat-ha-tang",
    author: "Bùi Gia Hân",
    publishedAt: "2026-09-08T15:50:00+07:00",
    views: 7640,
    isHero: false,
    isSpotlight: false,
    tags: ["5G SA", "network slicing", "nhà máy"],
  },
  {
    id: "art-latest-08",
    title: "Cảnh báo tấn công chuỗi cung ứng phần mềm mã nguồn mở tại doanh nghiệp vừa",
    slug: "canh-bao-tan-cong-chuoi-cung-ung-phan-mem-ma-nguon-mo",
    excerpt:
      "Gói npm/PyPI giả mạo đánh cắp token CI/CD; CERT khuyến nghị khóa dependency và quét SBOM.",
    content:
      "Nhiều SME Việt Nam kéo thư viện không kiểm tra checksum. Chuyên gia an ninh đề xuất chính sách cập nhật có kiểm soát.",
    coverImage:
      "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=80",
    categoryId: "cat-ha-tang",
    author: "Ngô Đức Tâm",
    publishedAt: "2026-09-07T18:35:00+07:00",
    views: 12890,
    isHero: false,
    isSpotlight: false,
    tags: ["an ninh mạng", "chuỗi cung ứng", "SBOM"],
  },
];

export const newsletterSubs: NewsletterSub[] = [
  {
    id: "sub-001",
    email: "minh.khoa@example.com",
    name: "Nguyễn Minh Khoa",
    subscribedAt: "2026-08-12T09:00:00+07:00",
    isActive: true,
  },
  {
    id: "sub-002",
    email: "ha.an@techcorp.vn",
    name: "Trần Hà An",
    subscribedAt: "2026-08-28T14:22:00+07:00",
    isActive: true,
  },
  {
    id: "sub-003",
    email: "quoc.huy@startup.vn",
    name: "Phạm Quốc Huy",
    subscribedAt: "2026-09-02T08:11:00+07:00",
    isActive: false,
  },
];

export const heroArticle: Article = articles.find((article) => article.isHero)!;

export const spotlightArticles: Article[] = articles.filter(
  (article) => article.isSpotlight,
);

export const latestArticles: Article[] = articles
  .filter((article) => !article.isHero && !article.isSpotlight)
  .sort(
    (a, b) =>
      new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime(),
  );

export const mostViewedArticles: Article[] = [...articles]
  .sort((a, b) => b.views - a.views)
  .slice(0, 5);

export const getCategoryById = (id: string): Category | undefined =>
  categories.find((category) => category.id === id);
