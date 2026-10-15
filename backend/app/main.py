"""FastAPI Main Application Entrypoint.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 6.
Provides health endpoints, CORS, request IDs, error handling, and API routing.
"""

from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from backend.app.api.v1.router import api_router
from backend.app.core.config import settings
from backend.app.db.session import engine, init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle handler."""
    # Initialize database tables
    await init_db()
    yield
    # Dispose engine connections on shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Based Vehicle Damage Detection and Telemetry Analysis System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_correlation_and_timing(request: Request, call_next):
    """Add correlation ID and execution time header to every response."""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = (time.perf_counter() - start_time) * 1000.0
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    return response


# Global Exception Handler formatting clean errors compliant with Spec §6.6
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred. Please try again later.",
                "request_id": correlation_id,
            }
        },
    )


# Health & Metadata Endpoints
@app.get("/health/live", tags=["Health"])
async def health_live():
    """Liveness probe: verifies process is alive."""
    return {"status": "alive", "timestamp": time.time()}


@app.get("/health/ready", tags=["Health"])
async def health_ready():
    """Readiness probe: verifies database connectivity."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "database": str(e)},
        )


@app.get("/api/v1/meta", tags=["Metadata"])
async def get_system_metadata():
    """System capability metadata."""
    return {
        "project": settings.PROJECT_NAME,
        "version": "1.0.0",
        "api_version": "v1",
        "capabilities": {
            "computer_vision_pipeline": True,
            "obd_telemetry_analytics": True,
            "langgraph_multi_agent": True,
            "rag_knowledge_retrieval": settings.RAG_ENABLED,
            "pdf_report_generation": True,
        },
        "models": {
            "filter": "efficientnet_b4",
            "classifier": "convnext_tiny",
            "detector": "yolov8x",
            "segmenter": "mask_rcnn",
            "obd_detector": "isolation_forest",
        },
    }


# Mount API Router
app.include_router(api_router, prefix=settings.API_V1_STR)
