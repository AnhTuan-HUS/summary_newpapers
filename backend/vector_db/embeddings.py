import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

try:
    from google import genai
    from google.genai import types  # Cần import types để cấu hình số chiều (dimension)
except ImportError:  # pragma: no cover
    genai = None


def _get_gemini_client() -> Any:
    """Tạo client Gemini theo các biến môi trường thường gặp."""
    if genai is None:
        raise RuntimeError("Thiếu dependency 'google-genai'. Hãy cài: pip install google-genai")

    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("LLM_API_KEY")
    )
    if not api_key:
        raise ValueError(
            "Thiếu API key Gemini. Hãy set GEMINI_API_KEY hoặc GOOGLE_API_KEY hoặc LLM_API_KEY trong file .env"
        )

    return genai.Client(api_key=api_key)


def get_gemini_embedding(text: str, model: str = "gemini-embedding-2", dimension: int = 768) -> list[float]:
    """Chuyển đổi văn bản thành vector dùng Gemini với số chiều cố định."""
    if not text or not text.strip():
        return []

    client = _get_gemini_client()
    
    # Cấu hình output_dimensionality để ép cứng số chiều trả về (mặc định 768)
    response = client.models.embed_content(
        model=model,
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=dimension)
    )

    embeddings = getattr(response, "embeddings", None)
    if not embeddings:
        raise ValueError("Gemini không trả về embedding hợp lệ.")

    first_embedding = embeddings[0]
    values = getattr(first_embedding, "values", None)
    if values is None:
        raise ValueError("Kết quả embedding không chứa trường 'values'.")

    return list(values)