"""Client wrapper giao tiếp với các LLM Provider (OpenAI, Gemini...) bằng SDK chính thức."""

from __future__ import annotations

import json
import os
from typing import Any, Optional
from dotenv import load_dotenv

load_dotenv()

from scripts.enricher.prompts import ENRICHMENT_SYSTEM_PROMPT, ENRICHMENT_USER_PROMPT_TEMPLATE
from scripts.enricher.schemas import EnrichmentOutput



class LLMEnricherClient:
    """Client tương tác với LLM API thông qua SDK chính thức (OpenAI / Google GenAI)."""

    def __init__(
        self,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        # 1. Tự động nhận diện Provider (Tham số -> Biến môi trường -> Mặc định 'gemini')
        self.provider = (
            provider
            or os.getenv("LLM_PROVIDER")
        ).lower()

        # 2. Tự động nhận diện API Key tương ứng
        self.api_key = (
            api_key or os.getenv("LLM_API_KEY") 
        )

        # 3. Tự động nhận diện Model Name linh hoạt
        self.model_name = (
            model_name
            or os.getenv("LLM_MODEL")
        )

    def enrich_article(self, title: str, content: str) -> dict[str, Any]:
        """Gửi nội dung bài viết tới LLM và trả về dictionary khớp với EnrichmentOutput schema."""
        user_prompt = ENRICHMENT_USER_PROMPT_TEMPLATE.format(
            title=title or "Untitled",
            content=(content or "")[:4000],  # Cắt ngắn nếu quá dài
        )

        if self.provider == "openai":
            return self._call_openai_sdk(user_prompt)
        elif self.provider == "gemini":
            return self._call_gemini_sdk(user_prompt)
        else:
            raise ValueError(f"Chưa hỗ trợ LLM Provider: {self.provider}")

    def _call_openai_sdk(self, user_prompt: str) -> dict[str, Any]:
        """Sử dụng SDK openai chính thức với Pydantic Structured Output."""
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            completion = client.beta.chat.completions.parse(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": ENRICHMENT_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=EnrichmentOutput,
            )
            message = completion.choices[0].message
            if message.parsed:
                return message.parsed.model_dump()
            elif message.content:
                return json.loads(message.content)
            raise ValueError("Không nhận được kết quả hợp lệ từ OpenAI SDK")
        except Exception as err:
            print(f"⚠️ Lỗi khi gọi OpenAI SDK ({self.model_name}): {err}")
            raise err

    def _call_gemini_sdk(self, user_prompt: str) -> dict[str, Any]:
        """Sử dụng SDK google-genai với xử lý Quota & Retry."""
        import time
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=self.api_key)
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=ENRICHMENT_SYSTEM_PROMPT,
                        response_mime_type="application/json",
                        response_schema=EnrichmentOutput,
                    ),
                )
                if response.text:
                    return json.loads(response.text)
                raise ValueError("Không nhận được kết quả hợp lệ từ Gemini SDK")
            except Exception as err:
                err_str = str(err)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "Quota" in err_str:
                    print(f"⚠️ Hết Quota/Rate Limit (Thử lại lần {attempt}/{max_retries} sau 10 giây...): {err}")
                    time.sleep(10 * attempt)
                else:
                    print(f"⚠️ Lỗi khi gọi Gemini SDK ({self.model_name}): {err}")
                    raise err

        raise RuntimeError("Đã hết số lần thử lại do giới hạn Quota của API.")

