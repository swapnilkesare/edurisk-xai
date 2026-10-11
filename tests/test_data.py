"""
Unit Tests for Data Ingestion, Schema Validation, and Provenance Tracking
"""
import pytest
import pandas as pd
import numpy as np

from src.schema import validate_dataframe_schema, get_dataset_metadata, CORE_FEATURE_BOUNDS
from src.data_loader import load_dataset, generate_synthetic_demo_data, compute_dataframe_fingerprint
from config.settings import RAW_DATA_PATH, CORE_FEATURES, TARGET_COLUMN

def test_load_real_or_fallback_dataset():
    df, prov = load_dataset(fallback_to_synthetic=True)
    assert not df.empty
    assert len(df) > 50
    assert TARGET_COLUMN in df.columns
    assert prov.fingerprint is not None
    assert prov.source_type in ["REAL_PUBLIC", "SYNTHETIC_DEMO"]

def test_synthetic_data_generation_integrity():
    df_syn, prov_syn = generate_synthetic_demo_data(n_samples=150, random_state=123)
    assert len(df_syn) == 150
    assert prov_syn.is_synthetic is True
    assert "[SYNTHETIC / DEMO DATA]" in prov_syn.name
    assert TARGET_COLUMN in df_syn.columns
    # Check that both classes exist
    assert set(df_syn[TARGET_COLUMN].unique()) == {0, 1}

def test_schema_validation_passes_on_valid_data():
    df_valid = pd.DataFrame({
        "attendance_rate": [85.0, 92.0, 45.0],
        "internal_test_score": [65.0, 78.0, 30.0],
        "assignment_submission_frequency": [90.0, 95.0, 40.0],
        "study_hours": [4.0, 6.0, 1.0],
        TARGET_COLUMN: [0, 0, 1]
    })
    is_valid, errors, warnings = validate_dataframe_schema(df_valid, required_features=CORE_FEATURES)
    assert is_valid is True
    assert len(errors) == 0

def test_schema_validation_detects_missing_features():
    df_invalid = pd.DataFrame({
        "attendance_rate": [85.0],
        "internal_test_score": [65.0],
        TARGET_COLUMN: [0]
    })
    is_valid, errors, warnings = validate_dataframe_schema(df_invalid, required_features=CORE_FEATURES)
    assert is_valid is False
    assert any("Missing required feature" in err for err in errors)

def test_schema_validation_detects_non_binary_target():
    df_bad_target = pd.DataFrame({
        "attendance_rate": [85.0, 90.0],
        "internal_test_score": [65.0, 70.0],
        "assignment_submission_frequency": [90.0, 85.0],
        "study_hours": [4.0, 5.0],
        TARGET_COLUMN: [0, 2]  # 2 is invalid
    })
    is_valid, errors, warnings = validate_dataframe_schema(df_bad_target, required_features=CORE_FEATURES)
    assert is_valid is False
    assert any("must contain binary values" in err for err in errors)
