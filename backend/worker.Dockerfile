# Background Worker Dockerfile
FROM python:3.11-slim as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/
RUN pip install --upgrade pip setuptools wheel && \
    pip install .

COPY ml /app/ml
COPY agents /app/agents
COPY rag /app/rag
COPY reports /app/reports
COPY backend /app/backend

RUN mkdir -p /app/storage/uploads /app/storage/reports

# Worker process checks and executes pipeline jobs
CMD ["python", "-m", "backend.app.services.job_worker"]
