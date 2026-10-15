"""Multi-dialect OBD-II Telemetry CSV Parser & Normalizer.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 10.1 & Section 10.2.
Supports Seat Leon driving event logs and UFPE standard PID CSVs.
Extracts time-series arrays, normalizes column aliases into canonical PIDs,
audits data quality, and identifies active DTC strings.
"""

from __future__ import annotations

import csv
import io
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from ml.obd.dtc import extract_dtcs_from_text
from ml.obd.schemas import DTCEntry, OBDDataQuality

# Canonical PID mapping patterns (regex pattern -> canonical name, unit, healthy range)
PID_ALIASES = [
    (re.compile(r"coolant.*temp|engine.*temp", re.I), "ENGINE_COOLANT_TEMP", "°C", [75.0, 105.0]),
    (re.compile(r"engine.*rpm|rpm", re.I), "ENGINE_RPM", "RPM", [600.0, 6500.0]),
    (re.compile(r"vehicle.*speed|speed.*sensor|speed", re.I), "VEHICLE_SPEED", "km/h", [0.0, 200.0]),
    (re.compile(r"throttle|pedal.*pos", re.I), "THROTTLE_POS", "%", [0.0, 100.0]),
    (re.compile(r"engine.*load|calc.*load", re.I), "ENGINE_LOAD", "%", [0.0, 100.0]),
    (re.compile(r"intake.*manifold.*press|intake.*press", re.I), "INTAKE_PRESSURE", "kPa", [20.0, 255.0]),
    (re.compile(r"intake.*air.*temp", re.I), "INTAKE_AIR_TEMP", "°C", [-20.0, 60.0]),
    (re.compile(r"mass.*flow|air.*flow.*rate|maf", re.I), "MAF_AIR_FLOW", "g/s", [1.0, 300.0]),
    (re.compile(r"long.*term.*fuel.*trim|ltft", re.I), "FUEL_TRIM_LONG", "%", [-15.0, 15.0]),
    (re.compile(r"short.*term.*fuel.*trim|stft", re.I), "FUEL_TRIM_SHORT", "%", [-15.0, 15.0]),
]


def match_canonical_pid(column_header: str) -> Optional[Tuple[str, str, List[float]]]:
    """Map raw column name to canonical PID, unit, and healthy reference range."""
    clean = column_header.strip()
    for pattern, canonical_name, unit, healthy_range in PID_ALIASES:
        if pattern.search(clean):
            return canonical_name, unit, healthy_range
    return None


class ParsedOBDTelemetry:
    """Structured container for parsed and cleaned OBD-II telemetry."""

    def __init__(
        self,
        canonical_data: Dict[str, List[float]],
        raw_columns: List[str],
        dtcs: List[DTCEntry],
        quality: OBDDataQuality,
        units: Dict[str, str],
        healthy_ranges: Dict[str, List[float]],
    ):
        self.canonical_data = canonical_data
        self.raw_columns = raw_columns
        self.dtcs = dtcs
        self.quality = quality
        self.units = units
        self.healthy_ranges = healthy_ranges

    @property
    def row_count(self) -> int:
        for v in self.canonical_data.values():
            return len(v)
        return 0

    @property
    def feature_names(self) -> List[str]:
        return sorted(list(self.canonical_data.keys()))


def parse_obd_csv(
    file_input: Union[str, Path, bytes],
    filename: str = "telemetry.csv",
    max_rows: int = 50000,
) -> Tuple[ParsedOBDTelemetry, List[str]]:
    """Parse CSV text/bytes, normalize PIDs, and extract DTCs."""
    warnings: List[str] = []

    if isinstance(file_input, bytes):
        text = file_input.decode("utf-8", errors="replace")
    elif isinstance(file_input, (str, Path)):
        p = Path(file_input)
        if not p.exists():
            raise FileNotFoundError(f"OBD file not found at {p}")
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    else:
        raise TypeError(f"Unsupported file_input type: {type(file_input)}")

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("Uploaded CSV file is empty.")

    # Determine delimiter
    first_line = lines[0]
    delimiter = ";" if ";" in first_line and "," not in first_line else ","

    reader = csv.reader(lines, delimiter=delimiter)
    header = next(reader, [])
    if not header:
        raise ValueError("Could not parse CSV header.")

    # Scan for DTC strings across whole document text
    detected_dtcs = extract_dtcs_from_text(text)

    # Map column headers
    col_mapping: Dict[int, Tuple[str, str, List[float]]] = {}
    unmapped_cols: List[str] = []
    units: Dict[str, str] = {}
    healthy_ranges: Dict[str, List[float]] = {}

    for idx, col in enumerate(header):
        match = match_canonical_pid(col)
        if match:
            canonical_name, unit, h_range = match
            col_mapping[idx] = (canonical_name, unit, h_range)
            units[canonical_name] = unit
            healthy_ranges[canonical_name] = h_range
        else:
            unmapped_cols.append(col)

    if not col_mapping:
        warnings.append("No standard automotive PIDs could be recognized from CSV headers.")

    canonical_series: Dict[str, List[float]] = {name: [] for name, _, _ in col_mapping.values()}
    total_cells = 0
    missing_cells = 0
    duplicate_rows = 0
    prev_row_tuple: Optional[Tuple[str, ...]] = None

    for row_idx, row in enumerate(reader):
        if row_idx >= max_rows:
            warnings.append(f"Telemetry truncated at maximum {max_rows} rows.")
            break

        # Check duplicate row
        current_tuple = tuple(row)
        if current_tuple == prev_row_tuple:
            duplicate_rows += 1
        prev_row_tuple = current_tuple

        for col_idx, (canonical_name, _, _) in col_mapping.items():
            total_cells += 1
            if col_idx < len(row):
                raw_val = row[col_idx].strip()
                try:
                    num_val = float(raw_val)
                    canonical_series[canonical_name].append(num_val)
                except ValueError:
                    # Impute using last known value or 0.0
                    missing_cells += 1
                    last_val = canonical_series[canonical_name][-1] if canonical_series[canonical_name] else 0.0
                    canonical_series[canonical_name].append(last_val)
            else:
                missing_cells += 1
                last_val = canonical_series[canonical_name][-1] if canonical_series[canonical_name] else 0.0
                canonical_series[canonical_name].append(last_val)

    missing_pct = round((missing_cells / max(1, total_cells)) * 100.0, 2)

    quality = OBDDataQuality(
        total_rows=len(next(iter(canonical_series.values()))) if canonical_series else 0,
        total_columns=len(header),
        mapped_pids_count=len(col_mapping),
        unmapped_columns=unmapped_cols[:10],
        missing_value_pct=missing_pct,
        duplicate_rows_count=duplicate_rows,
        sampling_interval_seconds=None,
        warnings=warnings,
    )

    parsed = ParsedOBDTelemetry(
        canonical_data=canonical_series,
        raw_columns=header,
        dtcs=detected_dtcs,
        quality=quality,
        units=units,
        healthy_ranges=healthy_ranges,
    )
    return parsed, warnings
