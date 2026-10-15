#!/usr/bin/env python3
"""Build deterministic, leakage-free train/val/test splits for vehicle damage detection.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 9.3.
Enforces fixed random seed, stratified sampling, and generates reproducible split manifests.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def hash_file_header(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read(8192))
    return h.hexdigest()


def build_splits(
    dataset_root: Path,
    output_dir: Path,
    seed: int = 42,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    max_damaged_samples: int = 1500,  # Stratified balancing cap for development / training
) -> Dict[str, Any]:
    random.seed(seed)
    damaged_dir = dataset_root / "damaged"
    undamaged_dir = dataset_root / "undamaged"

    if not damaged_dir.exists() or not undamaged_dir.exists():
        raise FileNotFoundError("dataset/damaged and dataset/undamaged must exist.")

    damaged_files = sorted([p for p in damaged_dir.rglob("*") if p.is_file() and not p.name.startswith(".")])
    undamaged_files = sorted([p for p in undamaged_dir.rglob("*") if p.is_file() and not p.name.startswith(".")])

    # Shuffle deterministically
    random.shuffle(damaged_files)
    random.shuffle(undamaged_files)

    # Subsample damaged to create a balanced evaluation set while maintaining ample training samples
    selected_damaged = damaged_files[:max_damaged_samples] if max_damaged_samples > 0 else damaged_files
    selected_undamaged = undamaged_files

    def split_list(items: List[Path]) -> tuple[List[Path], List[Path], List[Path]]:
        n = len(items)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        return items[:n_train], items[n_train : n_train + n_val], items[n_train + n_val :]

    d_train, d_val, d_test = split_list(selected_damaged)
    u_train, u_val, u_test = split_list(selected_undamaged)

    def format_records(paths: List[Path], label: str) -> List[Dict[str, Any]]:
        return [
            {
                "file_path": str(p.relative_to(dataset_root)),
                "label": label,
                "file_name": p.name,
                "file_hash_sample": hash_file_header(p),
            }
            for p in paths
        ]

    train_records = format_records(d_train, "damaged") + format_records(u_train, "undamaged")
    val_records = format_records(d_val, "damaged") + format_records(u_val, "undamaged")
    test_records = format_records(d_test, "damaged") + format_records(u_test, "undamaged")

    random.shuffle(train_records)
    random.shuffle(val_records)
    random.shuffle(test_records)

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "split_ratios": {"train": train_ratio, "val": val_ratio, "test": round(1.0 - train_ratio - val_ratio, 2)},
        "counts": {
            "total_selected": len(train_records) + len(val_records) + len(test_records),
            "train": {"total": len(train_records), "damaged": len(d_train), "undamaged": len(u_train)},
            "val": {"total": len(val_records), "damaged": len(d_val), "undamaged": len(u_val)},
            "test": {"total": len(test_records), "damaged": len(d_test), "undamaged": len(u_test)},
        },
        "train": train_records,
        "val": val_records,
        "test": test_records,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "split_manifest.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated splits in {out_file}:")
    print(f"  Train: {len(train_records)} ({len(d_train)} dmg, {len(u_train)} undmg)")
    print(f"  Val:   {len(val_records)} ({len(d_val)} dmg, {len(u_val)} undmg)")
    print(f"  Test:  {len(test_records)} ({len(d_test)} dmg, {len(u_test)} undmg)")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate deterministic train/val/test splits.")
    parser.add_argument("--dataset-root", type=str, default="./dataset")
    parser.add_argument("--output-dir", type=str, default="./data/splits")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train-ratio", type=float, default=0.70)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--max-damaged", type=int, default=1500)
    args = parser.parse_args()

    build_splits(
        Path(args.dataset_root),
        Path(args.output_dir),
        seed=args.seed,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        max_damaged_samples=args.max_damaged,
    )
