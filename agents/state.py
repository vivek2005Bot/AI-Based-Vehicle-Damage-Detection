"""Typed State Definitions for LangGraph Multi-Agent Orchestration.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 11.3.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from agents.rules import RiskAssessment
from ml.obd.schemas import OBDAnalysisResult
from ml.vision.schemas import VisionPipelineResult
from rag.schemas import RAGRetrievalResult


class VehicleMetadata(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    mileage: Optional[float] = None
    mileage_unit: str = "km"
    vin_redacted: bool = True
    vin_masked: Optional[str] = None


class InspectionGraphState(BaseModel):
    inspection_id: str
    job_id: str
    user_id: str
    image_paths: List[str] = Field(default_factory=list, description="Private storage keys for images")
    image_filenames: List[str] = Field(default_factory=list)
    image_file_ids: List[str] = Field(default_factory=list, description="InspectionFile ids parallel to images")
    obd_csv_path: Optional[str] = Field(default=None, description="Private storage key for OBD CSV")
    obd_filename: Optional[str] = None
    vehicle_info: VehicleMetadata = Field(default_factory=VehicleMetadata)

    # Specialist Agent Outputs
    vision_result: Optional[VisionPipelineResult] = None
    obd_result: Optional[OBDAnalysisResult] = None
    rag_result: Optional[RAGRetrievalResult] = None
    risk_result: Optional[RiskAssessment] = None

    # Execution Tracking
    current_stage: str = "initialized"
    completed_stages: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    status: str = "processing"
    report_payload: Optional[Dict[str, Any]] = None
