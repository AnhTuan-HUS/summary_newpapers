FROM apache/airflow:2.10.5-python3.12

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends chromium chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

COPY scripts/requirements.txt /tmp/crawler-requirements.txt

# Cài đặt requirements kết hợp với Constraints chuẩn từ Apache Airflow
# giúp cài được openai, google-genai mà KHÔNG Bị xung đột/hỏng các package cốt lõi của Airflow
RUN pip install --no-cache-dir -r /tmp/crawler-requirements.txt \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.12.txt" || \
    pip install --no-cache-dir -r /tmp/crawler-requirements.txt
