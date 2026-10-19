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
from ml.obd.pid_definitions import PID_REGISTRY
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
        min_len = min(len(telemetry.canonical_data[f]) for f in features)
        if min_len < 5:
            return False, 0.0, []
        matrix = np.column_stack([np.array(telemetry.canonical_data[f][:min_len], dtype=float) for f in features])

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

        # Attribute flagged PIDs by inspecting out-of-range values and valid sample counts
        flagged: List[FlaggedPID] = []
        dtc_codes = [d.code for d in telemetry.dtcs]

        for feat in features:
            values = np.array(telemetry.canonical_data[feat], dtype=float)
            h_range = telemetry.healthy_ranges.get(feat)
            unit = telemetry.units.get(feat, "")
            raw_col = telemetry.raw_column_mapping.get(feat, feat)
            valid_mask = telemetry.valid_masks.get(feat)

            # Extract valid, finite recorded observations
            if valid_mask is not None:
                valid_indices = [i for i, is_v in enumerate(valid_mask) if is_v and i < len(values) and np.isfinite(values[i])]
            else:
                valid_indices = [i for i in range(len(values)) if np.isfinite(values[i])]

            valid_count = len(valid_indices)

            # Check for range violations if valid numeric samples exist
            if valid_count > 0 and h_range and len(h_range) == 2:
                min_h, max_h = float(h_range[0]), float(h_range[1])
                valid_vals = values[valid_indices]
                out_of_bounds = (valid_vals < min_h) | (valid_vals > max_h)
                outside_count = int(np.sum(out_of_bounds))
                viol_ratio = outside_count / float(valid_count)
                pct_outside = round(viol_ratio * 100.0, 1)

                if viol_ratio > 0.05:  # more than 5% readings outside configured bounds
                    # Identify the most extreme deviation among valid observations
                    midpoint = (min_h + max_h) / 2.0
                    worst_local_idx = int(np.argmax(np.abs(valid_vals - midpoint)))
                    observed = float(valid_vals[worst_local_idx])

                    config = PID_REGISTRY.get_config(feat)
                    if config:
                        direction, value_meaning = PID_REGISTRY.explain_directionality(
                            feat, observed, unit, h_range
                        )
                        sample_expl = PID_REGISTRY.build_sample_explanation(
                            outside_count, valid_count, pct_outside
                        )
                        causes = (
                            config.possible_causes_low
                            if direction in ("negative", "below_range")
                            else config.possible_causes_high
                        )
                        cross_notice = PID_REGISTRY.check_p0171_fuel_trim_consistency(
                            dtc_codes,
                            feat,
                            observed,
                            has_timestamps=bool(telemetry.quality.sampling_interval_seconds),
                            same_bank=(config.bank == 1),
                        )
                        reason = (
                            f"Readings outside configured monitoring range [{min_h}, {max_h}] {unit} "
                            f"({pct_outside}% of recorded samples)"
                        )
                        what_we_found = (
                            "The vehicle's computer is making a larger-than-expected adjustment to the amount of fuel supplied to the engine."
                            if "FUEL_TRIM" in feat
                            else f"Sensor readings were recorded outside the application's configured monitoring range [{min_h}, {max_h}] {unit}."
                        )

                        flagged.append(
                            FlaggedPID(
                                pid_name=feat,
                                raw_column_name=raw_col,
                                observed_value=round(observed, 2),
                                unit=unit,
                                expected_range=h_range,
                                anomaly_contribution=round(float(viol_ratio), 3),
                                reason=reason,
                                simple_title=config.display_title,
                                what_we_found=what_we_found,
                                value_meaning=value_meaning,
                                sample_percentage_outside=pct_outside,
                                sample_count_evaluated=valid_count,
                                sample_count_outside=outside_count,
                                sample_explanation=sample_expl,
                                configured_range=list(config.configured_range),
                                range_source=config.range_source,
                                what_you_should_do=config.recommended_action,
                                possible_causes=list(causes),
                                limitations=list(config.limitations),
                                cross_finding_notice=cross_notice,
                                technical_details=config.technical_details,
                                source=config.source_citation,
                                directionality=direction,
                            )
                        )
                    else:
                        # Unknown or unmapped PID honest fallback
                        fallback = PID_REGISTRY.build_honest_fallback(
                            raw_column_name=raw_col,
                            observed_value=observed,
                            unit=unit,
                            valid_outside=outside_count,
                            valid_total=valid_count,
                            pct_outside=pct_outside,
                        )
                        flagged.append(
                            FlaggedPID(
                                pid_name=feat,
                                raw_column_name=raw_col,
                                observed_value=round(observed, 2),
                                unit=unit,
                                expected_range=h_range,
                                anomaly_contribution=round(float(viol_ratio), 3),
                                reason=(
                                    f"Recorded {round(observed, 1)} {unit} — outside unverified threshold "
                                    f"({pct_outside}% of recorded samples)"
                                ),
                                simple_title=fallback["simple_title"],
                                what_we_found=fallback["what_we_found"],
                                value_meaning=fallback["value_meaning"],
                                sample_percentage_outside=pct_outside,
                                sample_count_evaluated=valid_count,
                                sample_count_outside=outside_count,
                                sample_explanation=fallback["sample_explanation"],
                                configured_range=None,
                                range_source=fallback["range_source"],
                                what_you_should_do=fallback["what_you_should_do"],
                                possible_causes=fallback["possible_causes"],
                                limitations=fallback["limitations"],
                                cross_finding_notice=None,
                                technical_details=fallback["technical_details"],
                                source=fallback["source"],
                                directionality="unverified",
                            )
                        )

        # Sort flagged PIDs by contribution
        flagged.sort(key=lambda x: x.anomaly_contribution, reverse=True)

        return is_anomalous, round(avg_score, 4), flagged
