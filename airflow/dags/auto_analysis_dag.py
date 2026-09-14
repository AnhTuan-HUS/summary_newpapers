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

from scripts.enrich_news import process_enrichment_batch  # noqa: E402


def execute_llm_analysis() -> None:
    """Task callable chạy LLM enrichment step 3 đánh giá bài viết draft."""
    limit = int(os.getenv("ENRICH_LIMIT", "10"))
    provider = os.getenv("LLM_PROVIDER", "gemini")
    model_name = os.getenv("LLM_MODEL", None)

    stats = process_enrichment_batch(
        limit=limit,
        provider=provider,
        model_name=model_name,
    )

    print(f"📊 Kết quả Airflow DagRun (LLM Analysis Step 3): {stats}")
    if stats.get("failed", 0) > 0 and stats.get("success", 0) == 0 and stats.get("processed", 0) > 0:
        raise AirflowException("LLM Analysis step 3 thất bại cho toàn bộ batch.")


with DAG(
    dag_id="auto_analysis",
    description="DAG Step 3 dùng LLM (Gemini/OpenAI) đánh giá và làm giàu tri thức tin tức",
    schedule="0 * * * *",  # Chạy mỗi tiếng 1 lần, bắt đầu vào phút 00 (00:00, 01:00, 02:00, ...)
    start_date=pendulum.datetime(2026, 1, 1, tz="Asia/Ho_Chi_Minh"),
    catchup=False,
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=45),
    default_args={
        "owner": "news-platform-test",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["analysis", "llm", "gemini", "enrichment", "step3"],
) as dag:
    task_analysis = PythonOperator(
        task_id="llm_analysis_task",
        python_callable=execute_llm_analysis,
    )

    task_analysis
