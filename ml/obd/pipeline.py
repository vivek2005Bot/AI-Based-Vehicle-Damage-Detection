"""Complete OBD-II Telemetry Processing Pipeline.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 10 and Master Prompt Step 7.
Coordinates:
  1. CSV parsing & PID header normalization
  2. Telemetry data quality auditing
  3. Isolation Forest anomaly scoring
  4. SAE J2012 DTC extraction & verified severity tagging
  5. Fallback & limitations reporting
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Optional, Union

from ml.obd.anomaly import OBDAnomalyDetector
from ml.obd.csv_parser import parse_obd_csv
from ml.obd.schemas import OBDAnalysisResult, OBDDataQuality, OBDStatus


class OBDPipeline:
    """End-to-end OBD-II telemetry analysis coordinator."""

    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination
        self.detector = OBDAnomalyDetector(contamination=contamination)

    def analyze(
        self,
        csv_input: Optional[Union[str, Path, bytes]],
        filename: Optional[str] = None,
    ) -> OBDAnalysisResult:
        """Process optional OBD CSV input and return comprehensive analysis."""
        if csv_input is None:
            return OBDAnalysisResult(
                status=OBDStatus.NOT_PROVIDED,
                filename=None,
                anomaly_detected=None,
                anomaly_score=None,
                flagged_pids=[],
                dtcs=[],
                data_quality=OBDDataQuality(warnings=["No telemetry CSV was provided with the inspection."]),
                diagnostic_limitations=[
                    "Telemetry analysis was not performed because no OBD-II CSV log was provided.",
                    "Visual inspection alone cannot detect hidden mechanical or electronic powertrain defects."
                ],
            )

        start_time = time.perf_counter()
        name = filename or "telemetry.csv"

        try:
            telemetry, warnings = parse_obd_csv(csv_input, filename=name)
        except Exception as e:
            return OBDAnalysisResult(
                status=OBDStatus.INVALID_INPUT,
                filename=name,
                anomaly_detected=None,
                anomaly_score=None,
                flagged_pids=[],
                dtcs=[],
                data_quality=OBDDataQuality(warnings=[f"Failed to parse CSV: {e}"]),
                diagnostic_limitations=[
                    f"Uploaded file could not be decoded as valid automotive telemetry: {e}"
                ],
            )

        if telemetry.row_count == 0:
            return OBDAnalysisResult(
                status=OBDStatus.INVALID_INPUT,
                filename=name,
                anomaly_detected=None,
                anomaly_score=None,
                flagged_pids=[],
                dtcs=telemetry.dtcs,
                data_quality=telemetry.quality,
                diagnostic_limitations=["CSV file contained headers but zero valid numeric telemetry records."],
            )

        # Run Isolation Forest Anomaly Detection
        is_anomalous, score, flagged_pids = self.detector.analyze(telemetry)

        # Build diagnostic limitations
        limitations = [
            f"Unsupervised Isolation Forest model evaluated across {len(telemetry.feature_names)} canonical PIDs.",
            "Analysis is based on offline recorded telemetry and does not represent live ECU communication."
        ]
        if telemetry.quality.missing_value_pct > 10.0:
            limitations.append(f"Elevated missing value rate ({telemetry.quality.missing_value_pct}%) may influence anomaly scores.")
        for p in flagged_pids:
            if p.cross_finding_notice and p.cross_finding_notice not in limitations:
                limitations.append(p.cross_finding_notice)

        return OBDAnalysisResult(
            status=OBDStatus.COMPLETED,
            filename=name,
            anomaly_detected=is_anomalous or len(telemetry.dtcs) > 0,
            anomaly_score=score,
            flagged_pids=flagged_pids,
            dtcs=telemetry.dtcs,
            data_quality=telemetry.quality,
            model_metadata={
                "model": "isolation_forest",
                "contamination": self.contamination,
                "features_used": telemetry.feature_names,
                "rows_analyzed": telemetry.row_count,
            },
            diagnostic_limitations=limitations,
        )
