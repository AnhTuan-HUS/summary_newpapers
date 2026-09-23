"""Khởi tạo Gemini Embeddings sử dụng LangChain."""

from __future__ import annotations

import os
from typing import Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def get_gemini_embeddings(
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
) -> GoogleGenerativeAIEmbeddings:
    """Trả về instance GoogleGenerativeAIEmbeddings từ LangChain."""
    key = api_key or os.getenv("LLM_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise ValueError(
            "Không tìm thấy API Key cho Gemini Embeddings. "
            "Vui lòng thiết lập biến môi trường LLM_API_KEY hoặc GOOGLE_API_KEY."
        )

    model = model_name or os.getenv("GEMINI_EMBEDDING_MODEL") or "text-embedding-004"

    return GoogleGenerativeAIEmbeddings(
        model=f"models/{model}" if not model.startswith("models/") else model,
        google_api_key=key,
    )
