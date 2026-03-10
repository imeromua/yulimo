# syntax=docker/dockerfile:1

# ---------- Базовий образ ----------
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# ---------- Залежності ----------
FROM base AS deps
COPY backend/requirements.txt .
# psycopg2-binary потребує libpq — встановлюємо системну бібліотеку
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

# ---------- Фінальний образ ----------
FROM deps AS final

COPY backend/ .

# Директорія для логів
RUN mkdir -p /app/logs

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "2"]
