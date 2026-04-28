# Build from repository root (directory containing backend/, ml/, analytics/).
# Mirrors local paths so ai_reports/bigquery_client SQL resolution stays correct.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

COPY backend/requirements.txt backend/requirements-ml.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt -r backend/requirements-ml.txt

COPY backend/app ./backend/app
COPY ml ./ml
COPY analytics ./analytics

ENV PYTHONPATH=/workspace/backend

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
