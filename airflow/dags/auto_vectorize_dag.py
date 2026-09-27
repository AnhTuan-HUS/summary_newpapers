"""DAG Airflow điều phối Step 4: Vector hóa dữ liệu bài viết sang Qdrant."""

from __future__ import annotations

import os
import sys
from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.operators.python import PythonOperator

# Thêm đường dẫn project vào sys.path
for path in (
    "/opt/project",
    "/opt/project/scripts",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../scripts")),
):
    if path not in sys.path and os.path.exists(path):
        sys.path.insert(0, path)

from scripts.vectorize_news import process_vectorize_batch  # noqa: E402


def execute_vectorization(**context: object) -> None:
    """Task callable chạy vectorization step 4 trên các bài viết published."""
    limit = int(os.getenv("VECTORIZE_BATCH_LIMIT", "20"))
    qdrant_host = os.getenv("QDRANT_HOST", "qdrant_db")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
    collection_name = os.getenv("QDRANT_COLLECTION", "news_articles")
    embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
    api_key = os.getenv("LLM_API_KEY")

    stats = process_vectorize_batch(
        limit=limit,
        qdrant_host=qdrant_host,
        qdrant_port=qdrant_port,
        collection_name=collection_name,
        embedding_model=embedding_model,
        api_key=api_key,
    )

    print(f"📊 Kết quả Airflow DagRun (Vectorization Step 4): {stats}")
    if stats.get("failed", 0) > 0 and stats.get("success", 0) == 0 and stats.get("processed", 0) > 0:
        raise AirflowException("Vectorization step 4 thất bại cho toàn bộ batch.")


with DAG(
    dag_id="auto_vectorize",
    description="DAG Step 4 dùng LangChain + Gemini Embeddings chuyển bài viết sang Qdrant Vector DB",
    schedule=None,  # Được trigger trực tiếp từ DAG auto_analysis hoặc kích hoạt thủ công
    start_date=pendulum.datetime(2026, 1, 1, tz="Asia/Ho_Chi_Minh"),
    catchup=False,
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=45),
    default_args={
        "owner": "news-platform-test",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["vectorize", "qdrant", "langchain", "embeddings", "gemini", "step4"],
) as dag:
    task_vectorize = PythonOperator(
        task_id="vectorize_to_qdrant_task",
        python_callable=execute_vectorization,
    )

    task_vectorize
