"""Khởi tạo Embeddings cho Hybrid Search.

- Dense : Gemini Embeddings qua LangChain (ngữ nghĩa).
- Sparse: PyVi tách từ + lọc stopword tiếng Việt + FastEmbed BM25 (từ khóa).
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable, Optional

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from qdrant_client import models

DEFAULT_STOPWORDS_PATH = Path(__file__).resolve().parents[1] / "sparse_content" / "vietnamese-stopwords.txt"
DEFAULT_SPARSE_MODEL = "Qdrant/bm25"

# Token chỉ gồm ký tự không phải chữ/số (dấu câu, ký hiệu...)
_PUNCT_ONLY = re.compile(r"^[\W_]+$")


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

    model = (
        model_name
        or os.getenv("EMBEDDING_MODEL")
        or os.getenv("GEMINI_EMBEDDING_MODEL")
        or "gemini-embedding-2-preview"
    )

    return GoogleGenerativeAIEmbeddings(
        model=f"models/{model}" if not model.startswith("models/") else model,
        google_api_key=key,
    )


def load_stopwords(path: Optional[str | Path] = None) -> set[str]:
    """Đọc stopwords, lưu cả dạng có khoảng trắng và dạng nối '_' (khớp output PyVi)."""
    stopwords_path = Path(path) if path else DEFAULT_STOPWORDS_PATH
    stopwords: set[str] = set()
    if not stopwords_path.exists():
        print(f"⚠️ Không tìm thấy file stopwords: {stopwords_path}")
        return stopwords

    with open(stopwords_path, "r", encoding="utf-8") as f:
        for line in f:
            word = line.strip().lower()
            if word:
                stopwords.add(word)
                stopwords.add(word.replace(" ", "_"))
    return stopwords


class VietnameseSparseEmbedder:
    """Sinh Sparse Vector BM25 cho văn bản tiếng Việt.

    Pipeline: lowercase -> PyVi tách từ ghép ("trí tuệ" -> "trí_tuệ")
              -> lọc stopword & dấu câu -> FastEmbed BM25.

    Lưu ý: FastEmbed BM25 chỉ sinh phần TF; phần IDF do Qdrant tính
    (sparse vector config cần `modifier=models.Modifier.IDF`).
    """

    def __init__(
        self,
        model_name: str = DEFAULT_SPARSE_MODEL,
        stopwords_path: Optional[str | Path] = None,
        batch_size: int = 64,
    ):
        self.model_name = model_name
        self.batch_size = batch_size
        self.stopwords = load_stopwords(stopwords_path)
        self._model = None  # lazy-load để import module không bị chậm

    @property
    def model(self):
        if self._model is None:
            from fastembed import SparseTextEmbedding

            # Tắt stemmer tiếng Anh: tránh cắt hậu tố sai trên từ tiếng Việt
            self._model = SparseTextEmbedding(model_name=self.model_name, disable_stemmer=True)
        return self._model

    def preprocess(self, text: str) -> str:
        """Tách từ tiếng Việt bằng PyVi rồi lọc stopword / ký tự rác."""
        if not text:
            return ""
        from pyvi import ViTokenizer

        tokens = ViTokenizer.tokenize(text.lower().strip()).split()
        kept = [
            tok
            for tok in tokens
            if tok not in self.stopwords and not _PUNCT_ONLY.match(tok)
        ]
        return " ".join(kept)

    @staticmethod
    def _to_qdrant(sparse) -> models.SparseVector:
        return models.SparseVector(
            indices=sparse.indices.tolist(),
            values=sparse.values.tolist(),
        )

    def embed_documents(self, texts: Iterable[str]) -> list[models.SparseVector]:
        """Sparse vectors cho danh sách chunk (dùng khi index)."""
        cleaned = [self.preprocess(t) for t in texts]
        return [
            self._to_qdrant(vec)
            for vec in self.model.embed(cleaned, batch_size=self.batch_size)
        ]

    def embed_query(self, text: str) -> models.SparseVector:
        """Sparse vector cho câu truy vấn (BM25 query: mỗi term weight = 1)."""
        cleaned = self.preprocess(text)
        return self._to_qdrant(next(iter(self.model.query_embed(cleaned))))
