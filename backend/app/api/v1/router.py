"""API v1 Master Router."""

from __future__ import annotations

from fastapi import APIRouter
from backend.app.api.v1.endpoints import auth, inspections

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(inspections.router)
