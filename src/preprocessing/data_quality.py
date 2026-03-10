from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


@dataclass
class DataQualityReport:
    created_at: str
    row_count: int
    column_count: int
    null_counts: Dict[str, int]
    duplicate_rows: int
    numeric_summary: Dict[str, Dict[str, float]]
    class_balance: Optional[Dict[str, int]] = None

    def to_dict(self) -> Dict:
        return asdict(self)


def generate_quality_report(df: pd.DataFrame, target_class_col: str | None = None) -> DataQualityReport:
    null_counts = df.isna().sum().to_dict()
    duplicate_rows = int(df.duplicated().sum())

    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    numeric_summary: Dict[str, Dict[str, float]] = {}
    for c in numeric_cols:
        s = df[c].astype(float)
        numeric_summary[c] = {
            "min": float(np.nanmin(s.values)) if len(s) else 0.0,
            "max": float(np.nanmax(s.values)) if len(s) else 0.0,
            "mean": float(np.nanmean(s.values)) if len(s) else 0.0,
            "std": float(np.nanstd(s.values)) if len(s) else 0.0,
        }

    class_balance = None
    if target_class_col and target_class_col in df.columns:
        class_balance = df[target_class_col].value_counts(dropna=False).to_dict()

    return DataQualityReport(
        created_at=datetime.now().isoformat(),
        row_count=int(len(df)),
        column_count=int(df.shape[1]),
        null_counts={k: int(v) for k, v in null_counts.items()},
        duplicate_rows=duplicate_rows,
        numeric_summary=numeric_summary,
        class_balance={str(k): int(v) for k, v in (class_balance or {}).items()} or None,
    )

