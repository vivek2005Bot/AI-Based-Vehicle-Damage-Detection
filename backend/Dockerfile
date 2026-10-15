# Multi-stage Dockerfile for FastAPI Backend
FROM python:3.11-slim as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies including libmagic, libgl for OpenCV, and fonts for ReportLab
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY pyproject.toml /app/
RUN pip install --upgrade pip setuptools wheel && \
    pip install .

# Copy application source code
COPY ml /app/ml
COPY agents /app/agents
COPY rag /app/rag
COPY reports /app/reports
COPY backend /app/backend

# Create uploads and report directories
RUN mkdir -p /app/storage/uploads /app/storage/reports

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
