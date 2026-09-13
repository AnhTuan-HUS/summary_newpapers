"""DAG Airflow điều phối Step 2: normalize raw_articles -> articles."""

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

from scripts.processor.run_normalize_pipeline import run_normalize_pipeline  # noqa: E402


def execute_normalize_step2(**context: object) -> None:
    """Task callable chạy normalize step 2 trên raw_articles."""
    limit = int(os.getenv("NORMALIZE_LIMIT", "200"))
    offset = int(os.getenv("NORMALIZE_OFFSET", "0"))
    dry_run = os.getenv("NORMALIZE_DRY_RUN", "false").lower() == "true"
    verbose = os.getenv("NORMALIZE_VERBOSE", "false").lower() == "true"

    stats = run_normalize_pipeline(
        limit=limit,
        offset=offset,
        dry_run=dry_run,
        verbose=verbose,
    )

    print(f"📊 Kết quả Airflow DagRun (Normalize Step 2): {stats}")
    if stats.get("failed", 0) > 0 and stats.get("processed", 0) == 0:
        raise AirflowException("Normalize step 2 thất bại cho toàn bộ batch.")


with DAG(
    dag_id="auto_normalize_step2",
    description="DAG Step 2 normalize raw_articles thành articles",
    schedule="0 8 * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz="Asia/Ho_Chi_Minh"),
    catchup=False,
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=30),
    default_args={
        "owner": "news-platform-test",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["test", "normalize", "postgres", "step2"],
) as dag:
    task_normalize = PythonOperator(
        task_id="normalize_step2_task",
        python_callable=execute_normalize_step2,
    )

    # DAG này chạy riêng, không mắc dependency với DAG Collect.
    task_normalize
