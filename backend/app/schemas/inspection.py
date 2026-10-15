"""Inspection and Analysis Schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class InspectionCreate(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = Field(default=None, ge=1900, le=2035)
    mileage: Optional[float] = Field(default=None, ge=0.0)
    mileage_unit: str = "km"
    vin: Optional[str] = Field(default=None, description="Optional VIN; masked upon receipt")


class InspectionFileResponse(BaseModel):
    id: str
    role: str
    original_filename: str
    byte_size: int
    media_type: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisJobResponse(BaseModel):
    job_id: str
    inspection_id: str
    status: str
    current_stage: str
    error_message: Optional[str] = None
    created_at: datetime
    finished_at: Optional[datetime] = None


class InspectionResponse(BaseModel):
    id: str
    user_id: str
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    mileage: Optional[float] = None
    mileage_unit: str
    vin_masked: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    files: List[InspectionFileResponse] = Field(default_factory=list)
    has_report: bool = False
    risk_class: Optional[str] = None

    model_config = {"from_attributes": True}


class InspectionStatusResponse(BaseModel):
    inspection_id: str
    job_id: Optional[str] = None
    status: str
    current_stage: str
    completed_stages: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
