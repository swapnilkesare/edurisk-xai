"""
Data Loading and Provenance Management for EduRisk XAI
"""
from typing import Dict, Any, Tuple, Optional
from pathlib import Path
import hashlib
import json
import pandas as pd
import numpy as np

from config.settings import RAW_DATA_PATH, CORE_FEATURES, TARGET_COLUMN
from src.schema import validate_dataframe_schema, get_dataset_metadata

class DatasetProvenance:
    """
    Tracks origin, integrity, and status of loaded datasets.
    """
    def __init__(
        self,
        source_type: str,
        name: str,
        path: Optional[str] = None,
        row_count: int = 0,
        feature_count: int = 0,
        fingerprint: Optional[str] = None,
        is_synthetic: bool = False,
        description: str = "",
        target_distribution: Optional[Dict[int, int]] = None,
    ):
        self.source_type = source_type  # "REAL_PUBLIC", "USER_UPLOADED", "SYNTHETIC_DEMO"
        self.name = name
        self.path = str(path) if path else None
        self.row_count = row_count
        self.feature_count = feature_count
        self.fingerprint = fingerprint
        self.is_synthetic = is_synthetic
        self.description = description
        self.target_distribution = target_distribution or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_type": self.source_type,
            "name": self.name,
            "path": self.path,
            "row_count": self.row_count,
            "feature_count": self.feature_count,
            "fingerprint": self.fingerprint,
            "is_synthetic": self.is_synthetic,
            "description": self.description,
            "target_distribution": self.target_distribution,
        }


def compute_file_fingerprint(filepath: Path) -> str:
    """Computes SHA-256 hash of a file for experiment reproducibility."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()[:16]


def compute_dataframe_fingerprint(df: pd.DataFrame) -> str:
    """Computes SHA-256 hash of a DataFrame representation."""
    data_bytes = pd.util.hash_pandas_object(df, index=True).values.tobytes()
    return hashlib.sha256(data_bytes).hexdigest()[:16]


def load_dataset(
    filepath: Optional[Path] = None,
    fallback_to_synthetic: bool = True
) -> Tuple[pd.DataFrame, DatasetProvenance]:
    """
    Loads the standard raw educational dataset from disk or falls back to synthetic data.

    Returns:
        (DataFrame, DatasetProvenance)
    """
    target_path = Path(filepath) if filepath else RAW_DATA_PATH

    if target_path.exists():
        try:
            df = pd.read_csv(target_path)
            is_valid, errors, _ = validate_dataframe_schema(df, check_target=True)
            if is_valid:
                fingerprint = compute_file_fingerprint(target_path)
                meta = get_dataset_metadata(df)
                provenance = DatasetProvenance(
                    source_type="REAL_PUBLIC",
                    name="UCI Student Performance (Augmented)",
                    path=str(target_path),
                    row_count=len(df),
                    feature_count=len(df.columns) - (1 if TARGET_COLUMN in df.columns else 0),
                    fingerprint=fingerprint,
                    is_synthetic=False,
                    description="UCI Portuguese Secondary Student Performance Dataset (Cortez & Silva, 2008) with methodology alignment.",
                    target_distribution=meta.get("target_distribution", {})
                )
                return df, provenance
            else:
                print(f"[Warning] Dataset schema invalid: {errors}. Falling back to demo data.")
        except Exception as e:
            print(f"[Warning] Failed to load dataset from {target_path}: {e}")

    if fallback_to_synthetic:
        print("[Notice] Using SYNTHETIC / DEMO DATA for demonstration.")
        return generate_synthetic_demo_data(n_samples=300, random_state=42)

    raise FileNotFoundError(f"Dataset file not found at {target_path} and fallback is disabled.")


def generate_synthetic_demo_data(
    n_samples: int = 300,
    random_state: int = 42
) -> Tuple[pd.DataFrame, DatasetProvenance]:
    """
    Generates a deterministic synthetic student dataset purely for demonstration/testing.
    Clearly flagged and labeled as SYNTHETIC / DEMO DATA.
    """
    rng = np.random.RandomState(random_state)

    # Core indicators
    attendance = rng.beta(a=7, b=2, size=n_samples) * 100.0  # Mean ~77%
    study_hours = rng.gamma(shape=2.5, scale=1.5, size=n_samples)  # Mean ~3.75 hrs
    study_hours = np.clip(study_hours, 0.5, 20.0)

    internal_test = rng.normal(loc=65.0, scale=18.0, size=n_samples)
    internal_test = np.clip(internal_test, 10.0, 100.0)

    assignment_sub = rng.beta(a=6, b=2.5, size=n_samples) * 100.0
    assignment_sub = np.clip(assignment_sub, 15.0, 100.0)

    # Demographic & contextual proxies
    sex = rng.choice(["F", "M"], size=n_samples, p=[0.53, 0.47])
    age = rng.randint(15, 22, size=n_samples)
    failures = rng.choice([0, 1, 2, 3], size=n_samples, p=[0.75, 0.15, 0.07, 0.03])
    internet = rng.choice(["yes", "no"], size=n_samples, p=[0.82, 0.18])
    health = rng.choice([1, 2, 3, 4, 5], size=n_samples, p=[0.1, 0.15, 0.25, 0.25, 0.25])
    goout = rng.choice([1, 2, 3, 4, 5], size=n_samples, p=[0.1, 0.2, 0.35, 0.2, 0.15])
    famsup = rng.choice(["yes", "no"], size=n_samples, p=[0.6, 0.4])

    # Realistic synthetic risk probability function based on pedagogical factors
    # Risk increases when attendance, test score, assignments, or study hours are low
    risk_score = (
        - 0.045 * attendance
        - 0.035 * internal_test
        - 0.025 * assignment_sub
        - 0.20 * study_hours
        + 1.10 * failures
        + rng.normal(0, 0.4, size=n_samples)
        + 6.2  # offset
    )

    prob = 1.0 / (1.0 + np.exp(-risk_score))
    target_at_risk = (prob >= 0.50).astype(int)

    df = pd.DataFrame({
        "attendance_rate": np.round(attendance, 2),
        "assignment_submission_frequency": np.round(assignment_sub, 2),
        "internal_test_score": np.round(internal_test, 2),
        "study_hours": np.round(study_hours, 2),
        "failures": failures,
        "sex": sex,
        "age": age,
        "internet": internet,
        "health": health,
        "goout": goout,
        "famsup": famsup,
        TARGET_COLUMN: target_at_risk
    })

    fingerprint = compute_dataframe_fingerprint(df)
    meta = get_dataset_metadata(df)

    provenance = DatasetProvenance(
        source_type="SYNTHETIC_DEMO",
        name="[SYNTHETIC / DEMO DATA] Generated Academic Cohort",
        path=None,
        row_count=n_samples,
        feature_count=len(df.columns) - 1,
        fingerprint=fingerprint,
        is_synthetic=True,
        description="Deterministic synthetic demonstration cohort generated for pipeline verification. NOT real institutional student data.",
        target_distribution=meta.get("target_distribution", {})
    )

    return df, provenance
