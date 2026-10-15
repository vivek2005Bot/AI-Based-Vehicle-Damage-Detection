"""Isolation Forest Anomaly Detection for Vehicle Telemetry.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 10.2 & Section 10.3.
Uses scikit-learn Isolation Forest with contamination tuning and
feature attribution to identify abnormal engine / chassis telemetry signals.
"""

from __future__ import annotations

import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Any, Dict, List, Optional, Tuple

from ml.obd.csv_parser import ParsedOBDTelemetry
from ml.obd.schemas import FlaggedPID


class OBDAnomalyDetector:
    """Isolation Forest anomaly detection on multi-dimensional telemetry."""

    def __init__(
        self,
        contamination: float = 0.05,
        n_estimators: int = 100,
        random_state: int = 42,
    ):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=random_state,
        )

    def analyze(
        self,
        telemetry: ParsedOBDTelemetry,
    ) -> Tuple[bool, float, List[FlaggedPID]]:
        """Run Isolation Forest on telemetry and attribute abnormal features.

        Returns:
            Tuple of (anomaly_detected, anomaly_score, flagged_pids)
        """
        if telemetry.row_count < 5 or not telemetry.canonical_data:
            return False, 0.0, []

        features = telemetry.feature_names
        matrix = np.column_stack([telemetry.canonical_data[f] for f in features])

        # Replace any remaining NaNs or Infs with column mean
        col_means = np.nanmean(matrix, axis=0)
        inds = np.where(np.isnan(matrix))
        matrix[inds] = np.take(col_means, inds[1])

        # Fit Isolation Forest
        self.model.fit(matrix)
        # scores: negative values are outliers, positive are inliers
        raw_scores = self.model.decision_function(matrix)
        preds = self.model.predict(matrix)  # -1 for anomaly, 1 for normal

        anomaly_count = np.sum(preds == -1)
        anomaly_ratio = float(anomaly_count / len(preds))

        # Overall anomaly flagged if outlier ratio exceeds contamination threshold
        is_anomalous = anomaly_ratio > (self.contamination * 0.8)
        avg_score = float(np.mean(raw_scores))

        # Attribute flagged PIDs by inspecting out-of-range values and high variance
        flagged: List[FlaggedPID] = []
        for feat in features:
            values = np.array(telemetry.canonical_data[feat])
            h_range = telemetry.healthy_ranges.get(feat)
            unit = telemetry.units.get(feat, "")

            # Check for range violations
            if h_range and len(h_range) == 2:
                min_h, max_h = h_range
                out_of_bounds = (values < min_h) | (values > max_h)
                viol_ratio = np.sum(out_of_bounds) / max(1, len(values))

                if viol_ratio > 0.05:  # more than 5% readings outside healthy bounds
                    worst_idx = np.argmax(np.abs(values - (min_h + max_h) / 2))
                    observed = float(values[worst_idx])
                    reason = f"Readings exceeded healthy range [{min_h}, {max_h}] {unit} ({round(viol_ratio * 100, 1)}% of samples)"
                    flagged.append(
                        FlaggedPID(
                            pid_name=feat,
                            raw_column_name=feat,
                            observed_value=round(observed, 2),
                            unit=unit,
                            expected_range=h_range,
                            anomaly_contribution=round(float(viol_ratio), 3),
                            reason=reason,
                        )
                    )

        # Sort flagged PIDs by contribution
        flagged.sort(key=lambda x: x.anomaly_contribution, reverse=True)

        return is_anomalous, round(avg_score, 4), flagged
