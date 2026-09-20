import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Khởi tạo Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_gemini_embedding(text: str, model: str = "text-embedding-004") -> list[float]:
    """Chuyển đổi văn bản thành Vector 768 chiều dùng Gemini"""
    if not text or not text.strip():
        return []
    
    response = client.models.embed_content(
        model=model,
        contents=text,
    )
    return response.embedding.values