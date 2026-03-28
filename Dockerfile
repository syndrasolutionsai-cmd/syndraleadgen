FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir . --timeout 120

CMD ["sh", "-c", "uvicorn leadforge.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
