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
    expected_range: Optional[List[float]] = Field(default=None, description="[min, max] monitoring reference range")
    anomaly_contribution: float = Field(default=0.0, ge=0.0, description="Relative feature importance or deviation score")
    reason: str
    # Plain-English and audit metadata fields
    simple_title: str = Field(default="", description="Plain-English title for non-technical vehicle owners")
    what_we_found: str = Field(default="", description="Everyday language description of the observed finding")
    value_meaning: str = Field(default="", description="Explanation of what this number and directionality mean")
    sample_percentage_outside: Optional[float] = Field(default=None, description="Percentage of valid samples outside range")
    sample_count_evaluated: int = Field(default=0, description="Total number of valid numeric samples evaluated")
    sample_count_outside: int = Field(default=0, description="Number of valid samples outside range")
    sample_explanation: str = Field(default="", description="Clear explanation of the sample percentage calculation")
    configured_range: Optional[List[float]] = Field(default=None, description="[min, max] configured monitoring bounds")
    range_source: str = Field(default="", description="Source and context of the configured monitoring range")
    what_you_should_do: str = Field(default="", description="Actionable recommendations without speculative diagnosis")
    possible_causes: List[str] = Field(default_factory=list, description="Possible causes, clearly labelled as possibilities")
    limitations: List[str] = Field(default_factory=list, description="Diagnostic boundaries and uncertainties")
    cross_finding_notice: Optional[str] = Field(default=None, description="Cross-finding context (e.g., P0171 vs negative trim)")
    technical_details: str = Field(default="", description="Standard engineering/diagnostic explanation")
    source: str = Field(default="", description="Technical citation or standard source")
    directionality: str = Field(default="", description="negative, positive, above_range, below_range, within_range, etc.")


class DTCEntry(BaseModel):
    code: str = Field(..., description="SAE J2012 standardized DTC (e.g., P0300, P0171)")
    system: str = Field(..., description="Powertrain (P), Chassis (C), Body (B), Network (U)")
    description: str = Field(..., description="Verified technical fault description")
    severity: str = Field(default="moderate", description="critical, major, moderate, or minor")
    escalate_risk: bool = Field(default=False, description="Whether this DTC mandates safety risk escalation")
    source: str = "SAE J2012 standard reference"
    # User-friendly plain-English presentation fields
    simple_title: str = Field(default="", description="Short title understandable to non-technical users")
    what_it_means: str = Field(default="", description="1-2 sentences explaining the fault in everyday English")
    what_you_might_notice: List[str] = Field(default_factory=list, description="Possible observable symptoms (may or may not occur)")
    what_you_should_do: str = Field(default="", description="Actionable next step without assuming a specific component is broken")
    urgency: str = Field(default="schedule_check", description="Urgency slug: informational, schedule_check, prompt_attention, or stop_safely")
    urgency_label: str = Field(default="Schedule a Check", description="Human-readable urgency label")
    why_it_matters: str = Field(default="", description="Practical consequence explained in plain language")
    technical_details: str = Field(default="", description="Standard engineering/diagnostic explanation")
    possible_causes: List[str] = Field(default_factory=list, description="Likely contributing causes or inspection targets")
    limitations: List[str] = Field(default_factory=list, description="Explicit boundaries and uncertainties")


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
