"""Pydantic schemas for OBD-II telemetry analysis and DTC processing.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 10.3 and Master Prompt Step 7.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OBDStatus(str, Enum):
    NOT_PROVIDED = "not_provided"
    COMPLETED = "completed"
    INVALID_INPUT = "invalid_input"
    FAILED = "failed"
    MODEL_UNAVAILABLE = "model_unavailable"


class FlaggedPID(BaseModel):
    pid_name: str = Field(..., description="Canonical PID identifier (e.g., ENGINE_COOLANT_TEMP)")
    raw_column_name: str
    observed_value: float
    unit: str = ""
    expected_range: Optional[List[float]] = Field(default=None, description="[min, max] healthy reference range")
    anomaly_contribution: float = Field(default=0.0, ge=0.0, description="Relative feature importance or deviation score")
    reason: str


class DTCEntry(BaseModel):
    code: str = Field(..., description="SAE J2012 standardized DTC (e.g., P0300, P0171)")
    system: str = Field(..., description="Powertrain (P), Chassis (C), Body (B), Network (U)")
    description: str = Field(..., description="Verified technical fault description")
    severity: str = Field(default="moderate", description="critical, major, moderate, or minor")
    escalate_risk: bool = Field(default=False, description="Whether this DTC mandates safety risk escalation")
    source: str = "SAE J2012 standard reference"


class OBDDataQuality(BaseModel):
    total_rows: int = 0
    total_columns: int = 0
    mapped_pids_count: int = 0
    unmapped_columns: List[str] = Field(default_factory=list)
    missing_value_pct: float = 0.0
    duplicate_rows_count: int = 0
    sampling_interval_seconds: Optional[float] = None
    warnings: List[str] = Field(default_factory=list)


class OBDAnalysisResult(BaseModel):
    status: OBDStatus = OBDStatus.NOT_PROVIDED
    filename: Optional[str] = None
    anomaly_detected: Optional[bool] = None
    anomaly_score: Optional[float] = Field(default=None, description="Continuous score; values closer to -1 indicate stronger anomalies in Isolation Forest")
    flagged_pids: List[FlaggedPID] = Field(default_factory=list)
    dtcs: List[DTCEntry] = Field(default_factory=list)
    data_quality: OBDDataQuality = Field(default_factory=OBDDataQuality)
    model_metadata: Dict[str, Any] = Field(default_factory=lambda: {
        "model": "isolation_forest",
        "contamination": 0.05,
        "features_used": [],
    })
    diagnostic_limitations: List[str] = Field(default_factory=list)
