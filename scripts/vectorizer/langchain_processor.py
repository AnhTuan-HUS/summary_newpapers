"""Module phân tách nội dung bài viết thành các chunk bằng LangChain RecursiveCharacterTextSplitter."""

from __future__ import annotations

import json
from typing import Any
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class NewsChunker:
    """Sử dụng LangChain RecursiveCharacterTextSplitter để phân đoạn bài viết thông minh."""

    def __init__(
        self,
        chunk_size: int = 1200,
        chunk_overlap: int = 200,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            keep_separator=True,
        )

    def split_article(self, article: dict[str, Any]) -> list[Document]:
        """Tạo các LangChain Document chứa chunk nội dung kèm metadata phong phú.
        
        Để tăng độ liên quan cho RAG, mỗi chunk được tiền tố tiêu đề bài viết.
        """
        article_id = article["id"]
        title = article.get("title") or ""
        summary = article.get("summary") or ""
        content = article.get("content") or ""
        category_name = article.get("category_name") or "General"
        published_at = str(article.get("published_at") or article.get("created_at") or "")
        slug = article.get("slug") or ""

        # Kết hợp văn bản để chia chunk: nếu có summary, đưa vào đầu nội dung
        text_to_split = content.strip()
        if not text_to_split:
            text_to_split = summary.strip() or title.strip()

        raw_chunks = self.splitter.split_text(text_to_split)
        if not raw_chunks:
            raw_chunks = [title]

        documents: list[Document] = []
        for idx, chunk_text in enumerate(raw_chunks):
            # Tạo metadata đồng nhất cho Document
            metadata = {
                "article_id": article_id,
                "title": title,
                "slug": slug,
                "category": category_name,
                "published_at": published_at,
                "chunk_index": idx,
                "total_chunks": len(raw_chunks),
            }

            # Prepend context tiêu đề vào nội dung chunk để embedding mang đầy đủ ngữ cảnh bài viết
            augmented_content = f"Tiêu đề: {title}\nChuyên mục: {category_name}\n\n{chunk_text.strip()}"

            doc = Document(
                page_content=augmented_content,
                metadata=metadata,
            )
            documents.append(doc)

        return documents
