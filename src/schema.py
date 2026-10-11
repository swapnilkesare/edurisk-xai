"""
Data Schema Definitions and Validation Logic for EduRisk XAI
"""
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np

# Core methodology features and expected value ranges
CORE_FEATURE_BOUNDS: Dict[str, Tuple[float, float]] = {
    "attendance_rate": (0.0, 100.0),
    "assignment_submission_frequency": (0.0, 100.0),
    "internal_test_score": (0.0, 100.0),
    "study_hours": (0.0, 40.0),
}

# Categorical column acceptable values for UCI-based dataset
CATEGORICAL_LEVELS: Dict[str, List[str]] = {
    "sex": ["F", "M"],
    "address": ["U", "R"],
    "famsize": ["LE3", "GT3"],
    "Pstatus": ["T", "A"],
    "schoolsup": ["yes", "no"],
    "famsup": ["yes", "no"],
    "activities": ["yes", "no"],
    "internet": ["yes", "no"],
    "romantic": ["yes", "no"],
}

TARGET_COLUMN = "target_at_risk"

def validate_dataframe_schema(
    df: pd.DataFrame,
    required_features: Optional[List[str]] = None,
    check_target: bool = True
) -> Tuple[bool, List[str], List[str]]:
    """
    Validates a DataFrame against expected feature columns, types, and value boundaries.

    Returns:
        (is_valid, errors, warnings)
    """
    errors: List[str] = []
    warnings: List[str] = []

    if df.empty:
        errors.append("Dataset is empty (0 rows).")
        return False, errors, warnings

    if required_features is None:
        required_features = list(CORE_FEATURE_BOUNDS.keys())

    # Check for missing required features
    missing_cols = [col for col in required_features if col not in df.columns]
    if missing_cols:
        errors.append(f"Missing required feature columns: {missing_cols}")

    # Check for target column if required
    if check_target and TARGET_COLUMN not in df.columns:
        errors.append(f"Target column '{TARGET_COLUMN}' is missing from the dataset.")

    # Check bounds for present numeric core features
    for col, (low, high) in CORE_FEATURE_BOUNDS.items():
        if col in df.columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                errors.append(f"Column '{col}' must be numeric, found type {df[col].dtype}.")
            else:
                out_of_bounds = df[(df[col] < low) | (df[col] > high)]
                if len(out_of_bounds) > 0:
                    warnings.append(
                        f"Column '{col}' has {len(out_of_bounds)} values outside expected range [{low}, {high}]."
                    )

    # Check target distribution if target exists
    if TARGET_COLUMN in df.columns:
        unique_vals = set(df[TARGET_COLUMN].dropna().unique())
        if not unique_vals.issubset({0, 1, 0.0, 1.0}):
            errors.append(f"Target column '{TARGET_COLUMN}' must contain binary values (0 or 1), found {unique_vals}.")
        else:
            class_counts = df[TARGET_COLUMN].value_counts().to_dict()
            if len(class_counts) < 2:
                errors.append(f"Target column has only one class ({class_counts}). Both classes (0 and 1) are required.")
            else:
                minority_count = min(class_counts.values())
                if minority_count < 5:
                    warnings.append(f"Severe class imbalance: minority class has only {minority_count} samples.")

    # Check for missing value proportions
    null_counts = df.isnull().sum()
    for col, count in null_counts.items():
        if count > 0:
            pct = (count / len(df)) * 100
            if pct > 50:
                warnings.append(f"High missingness in '{col}': {count} missing values ({pct:.1f}%).")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def get_dataset_metadata(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Extracts summary metadata for a validated dataset.
    """
    metadata: Dict[str, Any] = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "numeric_columns": list(df.select_dtypes(include=[np.number]).columns),
        "categorical_columns": list(df.select_dtypes(include=["object", "category"]).columns),
        "missing_values_total": int(df.isnull().sum().sum()),
        "missing_per_column": df.isnull().sum().to_dict(),
    }
    if TARGET_COLUMN in df.columns:
        counts = df[TARGET_COLUMN].value_counts().to_dict()
        total = len(df.dropna(subset=[TARGET_COLUMN]))
        metadata["target_distribution"] = {
            int(k): int(v) for k, v in counts.items()
        }
        metadata["at_risk_percentage"] = float((counts.get(1, 0) / total) * 100) if total > 0 else 0.0

    return metadata
