# Production images are built from the repository root Dockerfile (bundles `ml/`).
# docker build -f Dockerfile ..
#
# Legacy single-service build (FastAPI only, no bundled ML stack):
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
