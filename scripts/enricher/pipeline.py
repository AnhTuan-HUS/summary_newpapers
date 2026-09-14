"""Pipeline điều phối quá trình xử lý làm giàu thông tin bài viết (Step 03)."""

from __future__ import annotations

import time
from typing import Any, Optional

from database.operations import get_draft_articles_for_enrichment, update_enriched_article
from scripts.enricher.client import LLMEnricherClient


def process_enrichment_batch(
    limit: int = 50,
    provider: str = "gemini",
    model_name: Optional[str] = None,
    database_url: Optional[str] = None,
) -> dict[str, int]:
    """Lấy các bài viết draft từ DB, gọi LLM phân tích và cập nhật kết quả vào DB."""
    draft_articles = get_draft_articles_for_enrichment(limit=limit, database_url=database_url)

    if not draft_articles:
        print("ℹ️ Không có bài viết nào ở trạng thái 'draft' cần xử lý.")
        return {"processed": 0, "success": 0, "failed": 0}

    print(f"🚀 Bắt đầu làm giàu nội dung cho {len(draft_articles)} bài viết (Provider: {provider})...")

    enricher = LLMEnricherClient(provider=provider, model_name=model_name)

    stats = {"processed": 0, "success": 0, "failed": 0}

    for idx, article in enumerate(draft_articles, 1):
        stats["processed"] += 1
        article_id = article["id"]
        title = article["title"]
        content = article["content"]

        print(f"\n[{idx}/{len(draft_articles)}] Xử lý Bài viết ID: {article_id} - '{title[:50]}...'")


        try:
            enrichment_data = enricher.enrich_article(title=title, content=content)
            updated = update_enriched_article(
                article_id=article_id,
                enrichment_data=enrichment_data,
                database_url=database_url,
            )
            if updated:
                print(f"   ✅ Đã cập nhật thành công bài viết {article_id} (Status -> published)")
                stats["success"] += 1
            else:
                print(f"   ❌ Không thể cập nhật DB cho bài viết {article_id}")
                stats["failed"] += 1

        except Exception as err:
            print(f"   ❌ Lỗi xử lý bài viết {article_id}: {err}")
            stats["failed"] += 1

        time.sleep(0.5)  # Tránh trạm trần rate limit API

    print("\n" + "=" * 50)
    print(f"📊 KẾT QUẢ STEP 03 ENRICHMENT:")
    print(f" - Tổng bài đã xử lý: {stats['processed']}")
    print(f" - Thành công       : {stats['success']}")
    print(f" - Thất bại          : {stats['failed']}")
    print("=" * 50)

    return stats
