from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from src.database.models import MarketReadinessScores


DEFAULT_BINS: List[Tuple[int, int]] = [
    (20, 30),
    (30, 40),
    (40, 50),
    (50, 60),
    (60, 70),
    (70, 80),
    (80, 90),
    (90, 100),
]


def _bin_labels(bins: List[Tuple[int, int]]) -> List[str]:
    return [f"{a}-{b}" for a, b in bins]


def _bin_counts(values: List[float], bins: List[Tuple[int, int]]) -> List[int]:
    counts = [0 for _ in bins]
    for v in values:
        vv = max(0.0, min(100.0, float(v)))
        for i, (a, b) in enumerate(bins):
            if (i < len(bins) - 1 and vv >= a and vv < b) or (i == len(bins) - 1 and vv >= a and vv <= b):
                counts[i] += 1
                break
    return counts


def _proportions(counts: List[int]) -> List[float]:
    total = float(sum(counts)) or 1.0
    return [c / total for c in counts]


def psi(expected: List[float], actual: List[float], eps: float = 1e-8) -> float:
    """
    Population Stability Index for binned distributions.
    PSI = sum((a - e) * ln(a / e))
    """
    if len(expected) != len(actual):
        raise ValueError("expected and actual must have same length")

    e = np.array(expected, dtype=float)
    a = np.array(actual, dtype=float)
    e = np.clip(e, eps, None)
    a = np.clip(a, eps, None)
    return float(np.sum((a - e) * np.log(a / e)))


@dataclass
class DriftBaseline:
    created_at: str
    bins: List[Tuple[int, int]]
    expected_counts: List[int]
    expected_props: List[float]
    expected_level_counts: Dict[str, int] | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "created_at": self.created_at,
            "bins": self.bins,
            "expected_counts": self.expected_counts,
            "expected_props": self.expected_props,
            "expected_level_counts": self.expected_level_counts,
        }


def build_drift_baseline_from_training_frame(df: pd.DataFrame, bins: List[Tuple[int, int]] = DEFAULT_BINS) -> DriftBaseline:
    if "readiness_score" not in df.columns:
        raise ValueError("df must include readiness_score")

    values = [float(v) for v in df["readiness_score"].values if v is not None and not pd.isna(v)]
    counts = _bin_counts(values, bins=bins)
    props = _proportions(counts)

    level_counts = None
    if "readiness_level" in df.columns:
        level_counts = df["readiness_level"].value_counts(dropna=False).to_dict()
        level_counts = {str(k): int(v) for k, v in level_counts.items()}

    return DriftBaseline(
        created_at=datetime.now().isoformat(),
        bins=bins,
        expected_counts=counts,
        expected_props=props,
        expected_level_counts=level_counts,
    )


def save_drift_baseline(models_dir: Path, baseline: DriftBaseline) -> Path:
    models_dir.mkdir(parents=True, exist_ok=True)
    path = models_dir / "drift_baseline.json"
    path.write_text(json.dumps(baseline.to_dict(), indent=2))
    return path


def load_drift_baseline(models_dir: Path) -> DriftBaseline | None:
    path = models_dir / "drift_baseline.json"
    if not path.exists():
        return None
    raw = json.loads(path.read_text())
    return DriftBaseline(
        created_at=str(raw.get("created_at")),
        bins=[tuple(x) for x in raw.get("bins", DEFAULT_BINS)],
        expected_counts=list(raw.get("expected_counts", [])),
        expected_props=list(raw.get("expected_props", [])),
        expected_level_counts=raw.get("expected_level_counts"),
    )


def compute_drift_report(session: Session, models_dir: Path) -> Dict[str, Any]:
    baseline = load_drift_baseline(models_dir)

    values = session.query(MarketReadinessScores.readiness_score).all()
    actual_values = [float(v[0] or 0.0) for v in values if v and v[0] is not None]

    if baseline is None:
        # Fallback: initialize the baseline on first request so the endpoint
        # remains functional even if training artifacts were not generated.
        baseline_bins = DEFAULT_BINS
        actual_counts = _bin_counts(actual_values, bins=baseline_bins)
        actual_props = _proportions(actual_counts)

        baseline = DriftBaseline(
            created_at=datetime.now().isoformat(),
            bins=baseline_bins,
            expected_counts=actual_counts,
            expected_props=actual_props,
            expected_level_counts=None,
        )
        save_drift_baseline(models_dir=models_dir, baseline=baseline)
        return {
            "available": True,
            "initialized": True,
            "reason": "Initialized drift baseline from current database scores.",
            "computed_at": datetime.now().isoformat(),
            "psi_readiness_score": 0.0,
            "bins": _bin_labels(baseline.bins),
            "expected_props": baseline.expected_props,
            "actual_props": actual_props,
            "expected_counts": baseline.expected_counts,
            "actual_counts": actual_counts,
            "expected_level_counts": None,
            "actual_level_counts": {},
        }

    actual_counts = _bin_counts(actual_values, bins=baseline.bins)
    actual_props = _proportions(actual_counts)

    psi_score = psi(baseline.expected_props, actual_props)

    # Also track readiness level count drift (qualitative).
    actual_level_counts: Dict[str, int] = {}
    level_rows = session.query(MarketReadinessScores.readiness_level, MarketReadinessScores.id).all()
    for lvl, _id in level_rows:
        if lvl is None:
            continue
        actual_level_counts[str(lvl)] = actual_level_counts.get(str(lvl), 0) + 1

    report = {
        "available": True,
        "computed_at": datetime.now().isoformat(),
        "psi_readiness_score": psi_score,
        "bins": _bin_labels(baseline.bins),
        "expected_props": baseline.expected_props,
        "actual_props": actual_props,
        "expected_counts": baseline.expected_counts,
        "actual_counts": actual_counts,
        "expected_level_counts": baseline.expected_level_counts,
        "actual_level_counts": actual_level_counts,
    }

    # Persist for the dashboard.
    (models_dir / "drift_report.json").write_text(json.dumps(report, indent=2))
    return report

