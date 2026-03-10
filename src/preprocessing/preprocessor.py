from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


DEFAULT_ID_COLUMNS = ["student_id", "role_id"]
DEFAULT_TARGET_COLUMNS = ["readiness_score", "readiness_level"]


@dataclass(frozen=True)
class PreprocessSpec:
    feature_columns: List[str]
    id_columns: List[str] = None  # type: ignore[assignment]
    target_columns: List[str] = None  # type: ignore[assignment]

    def __post_init__(self):
        object.__setattr__(self, "id_columns", self.id_columns or list(DEFAULT_ID_COLUMNS))
        object.__setattr__(self, "target_columns", self.target_columns or list(DEFAULT_TARGET_COLUMNS))


def validate_training_frame(df: pd.DataFrame, spec: PreprocessSpec) -> None:
    """Validate that required columns exist and are numeric where expected."""
    missing = [c for c in (spec.feature_columns + spec.id_columns + spec.target_columns) if c not in df.columns]
    if missing:
        raise ValueError(f"Training DataFrame missing required columns: {missing}")

    # Ensure features are numeric (this project uses explicit one-hot + numeric engineered features)
    non_numeric = [c for c in spec.feature_columns if not pd.api.types.is_numeric_dtype(df[c])]
    if non_numeric:
        raise ValueError(f"Non-numeric feature columns found (expected numeric): {non_numeric}")


def validate_inference_frame(df: pd.DataFrame, spec: PreprocessSpec) -> None:
    missing = [c for c in spec.feature_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Inference DataFrame missing required feature columns: {missing}")

    non_numeric = [c for c in spec.feature_columns if not pd.api.types.is_numeric_dtype(df[c])]
    if non_numeric:
        raise ValueError(f"Non-numeric feature columns found (expected numeric): {non_numeric}")


def build_preprocessor(feature_columns: Sequence[str]) -> Pipeline:
    """
    Build a reusable preprocessing pipeline.

    Even though current features are numeric + one-hot, we still:
    - impute missing values (robustness)
    - scale numeric columns (needed for linear/logistic baselines)
    """
    numeric_features = list(feature_columns)
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    # ColumnTransformer keeps stable column ordering.
    pre = ColumnTransformer(
        transformers=[("num", numeric_transformer, numeric_features)],
        remainder="drop",
        verbose_feature_names_out=False,
    )

    return Pipeline(steps=[("preprocess", pre)])


def group_train_test_split(
    df: pd.DataFrame,
    group_col: str,
    test_size: float = 0.2,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Leakage-safe split: keep all rows of a group (student) in either train or test.
    """
    if group_col not in df.columns:
        raise ValueError(f"group_col '{group_col}' not in DataFrame")

    groups = df[group_col].dropna().unique()
    rng = np.random.default_rng(random_state)
    rng.shuffle(groups)

    n_test = max(1, int(round(len(groups) * test_size)))
    test_groups = set(groups[:n_test].tolist())

    is_test = df[group_col].isin(test_groups)
    return df.loc[~is_test].copy(), df.loc[is_test].copy()

