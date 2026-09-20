from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_article_into_chunks(content: str, chunk_size: int = 800, chunk_overlap: int = 120) -> list[str]:
    """Cắt nhỏ nội dung bài báo theo đoạn văn và dấu chấm"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_text(content)
    return chunks