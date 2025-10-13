# python_backend/Dockerfile

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev libpq5 tini \
    && rm -rf /var/lib/apt/lists/*

# 의존성 복사 및 설치
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt

# 전체 코드 복사
COPY . /app

RUN adduser --system --group --no-create-home appuser && \
    chown -R appuser:appuser /app
USER appuser

# ---- 네트워크/엔트리포인트 ----
EXPOSE 8080
ENTRYPOINT ["/usr/bin/tini","--"]
# Cloud Run/프록시 환경 고려 옵션 추가
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers", "--forwarded-allow-ips=*"]