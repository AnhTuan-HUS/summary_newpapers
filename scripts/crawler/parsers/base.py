"""Module định nghĩa giao diện trừu tượng (Base Interface) cho các bộ bóc tách dữ liệu bài viết (Parsers)."""

from abc import ABC, abstractmethod


class BaseParser(ABC):
    """Lớp trừu tượng định nghĩa phương thức parse chung cho mọi bộ phân tích bài báo."""

    @abstractmethod
    def parse(self, html: str) -> dict[str, str | None]:
        """Phân tích nội dung HTML thô và trích xuất các trường thông tin chuẩn của bài viết.
        
        Args:
            html: Nội dung mã nguồn HTML thô của trang bài viết.
            
        Returns:
            dict[str, str | None]: Từ điển chứa các trường thông tin bài viết:
            - 'title': Tiêu đề bài viết hoặc None.
            - 'author': Tên tác giả bài viết hoặc None.
            - 'published_at': Chuỗi thời gian xuất bản hoặc None.
            - 'content_raw': Chuỗi HTML block nội dung bài viết (đã loại bỏ các thẻ rác) hoặc None.
        """
        pass

