"""
Unit Tests for SHAP Explainability Engine and Additive Consistency
"""
import pytest
import pandas as pd
import numpy as np

from src.data_loader import generate_synthetic_demo_data
from src.train import train_all_models
from src.model_selection import select_best_model
from src.explain import ExplainabilityEngine

@pytest.fixture(scope="module")
def prepared_engine():
    df, _ = generate_synthetic_demo_data(n_samples=100, random_state=42)
    feature_cols = ["attendance_rate", "internal_test_score", "study_hours"]
    results = train_all_models(df=df, feature_columns=feature_cols, cv_folds=2, random_state=42)
    _, pipeline, _ = select_best_model(results)
    engine = ExplainabilityEngine(pipeline, background_data=df[feature_cols])
    return engine, df[feature_cols]

def test_local_shap_explanation_structure(prepared_engine):
    engine, df_features = prepared_engine
    student_sample = df_features.iloc[[0]]

    explanation = engine.explain_single_prediction(student_sample)

    assert explanation["status"] == "SUCCESS"
    assert "base_value" in explanation
    assert "contributions" in explanation
    assert len(explanation["contributions"]) > 0

    # Verify finiteness
    for contrib in explanation["contributions"]:
        assert np.isfinite(contrib["shap_value"])
        assert "feature" in contrib
        assert "is_risk_increasing" in contrib
        assert "is_protective" in contrib

    # Verify plain-language generation
    assert "plain_language_summary" in explanation
    assert len(explanation["plain_language_summary"]) > 0

def test_global_importance_computation(prepared_engine):
    engine, df_features = prepared_engine
    importance = engine.compute_global_importance(df_features)

    assert len(importance) > 0
    for item in importance:
        assert "feature" in item
        assert "mean_abs_shap" in item
        assert item["mean_abs_shap"] >= 0.0

def test_shap_missing_column_resilience(prepared_engine):
    """Regression test: verify SHAP engine gracefully handles DataFrames with missing feature columns."""
    engine, df_features = prepared_engine
    # Drop one column to simulate partial cohort input
    partial_df = df_features.drop(columns=[df_features.columns[0]])
    
    # Global importance should not raise ValueError: columns are missing
    importance = engine.compute_global_importance(partial_df)
    assert isinstance(importance, list)

    # Local explanation should also succeed with partial input
    single_partial = partial_df.iloc[[0]]
    explanation = engine.explain_single_prediction(single_partial)
    assert explanation["status"] == "SUCCESS"
    assert "contributions" in explanation
