"""Backend Configuration Management.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 15.3.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "development"
    PROJECT_NAME: str = "Vehicle Damage AI"
    API_V1_STR: str = "/api/v1"

    # Security
    JWT_SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production-must-be-at-least-32-chars",
        description="Secret key for JWT signature",
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_MINUTES: int = 60

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./vehicle_damage.db",
        description="Async SQLAlchemy database connection string",
    )
    REDIS_URL: str = "redis://localhost:6379/0"

    # File Storage
    FILE_STORAGE_BACKEND: str = "local"
    FILE_STORAGE_ROOT: str = "./private_uploads"
    REPORTS_DIR: str = "./reports/generated"
    DATASET_ROOT: str = "./dataset"
    OBD_DATASET_DIR: str = "./obdiidata"

    # Upload Limits
    MAX_IMAGE_UPLOAD_MB: int = 25
    MAX_OBD_UPLOAD_MB: int = 15
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png"]
    ALLOWED_OBD_EXTENSIONS: List[str] = [".csv"]

    # ML Pipeline
    FILTER_THRESHOLD: float = 0.85
    RAG_ENABLED: bool = True
    RAG_TOP_K: int = 5

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()

# Ensure local storage directories exist
Path(settings.FILE_STORAGE_ROOT).mkdir(parents=True, exist_ok=True)
Path(settings.REPORTS_DIR).mkdir(parents=True, exist_ok=True)
