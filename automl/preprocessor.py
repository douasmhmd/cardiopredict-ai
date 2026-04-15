"""Validate and clean patient CSV data before PyCaret."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


TARGET_HINTS = (
    "target",
    "label",
    "outcome",
    "disease",
    "class",
    "diagnosis",
    "risk",
    "heart_disease",
    "chd",
    "stroke",
    "diabetes",
    "ckd",
)


@dataclass
class PreprocessResult:
    df: pd.DataFrame
    issues: list[str]
    suggested_target: Optional[str]


def suggest_target_column(df: pd.DataFrame) -> Optional[str]:
    cols_lower = {c.lower(): c for c in df.columns}
    for hint in TARGET_HINTS:
        if hint in cols_lower:
            return cols_lower[hint]
    for c in df.columns:
        cl = c.lower()
        if any(h in cl for h in ("target", "outcome", "label", "disease")):
            return c
    numeric = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric) == 1:
        return numeric[0]
    return None


def validate_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    issues: list[str] = []
    if df is None or df.empty:
        issues.append("The file appears empty. Please upload a CSV with patient rows.")
        return df, issues

    if df.shape[1] < 2:
        issues.append("Need at least two columns (predictors and one outcome column).")

    dup_cols = df.columns[df.columns.duplicated()].tolist()
    if dup_cols:
        issues.append(f"Duplicate column names found: {dup_cols}. Please rename them.")
        df = df.loc[:, ~df.columns.duplicated()]

    null_pct = df.isna().mean()
    high_null = null_pct[null_pct > 0.5]
    if not high_null.empty:
        issues.append(
            "Some columns are mostly missing (>50% empty): "
            + ", ".join(high_null.index.tolist()[:5])
            + ". Consider filling or removing them."
        )

    return df, issues


def prepare_for_automl(df: pd.DataFrame, target_column: str) -> tuple[pd.DataFrame, list[str]]:
    """Basic cleaning: drop rows with missing target; coerce numeric where possible."""
    issues: list[str] = []
    if target_column not in df.columns:
        issues.append(f"Target column '{target_column}' is not in the data.")
        return df, issues

    out = df.copy()
    out = out.dropna(subset=[target_column])
    if out.empty:
        issues.append("After removing rows with missing target, no rows remain.")
        return out, issues

    for col in out.columns:
        if col == target_column:
            continue
        if out[col].dtype == object:
            coerced = pd.to_numeric(out[col], errors="coerce")
            if coerced.notna().sum() > 0.8 * len(out):
                out[col] = coerced

    return out, issues
