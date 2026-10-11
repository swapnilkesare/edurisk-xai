"""
Unit Tests for 4-Model Training Pipeline and Model Selection
"""
import pytest
import pandas as pd
from src.data_loader import generate_synthetic_demo_data
from src.train import train_all_models
from src.model_selection import select_best_model

def test_all_four_candidate_models_trained():
    df, _ = generate_synthetic_demo_data(n_samples=120, random_state=42)
    feature_cols = ["attendance_rate", "internal_test_score", "study_hours"]

    results = train_all_models(
        df=df,
        feature_columns=feature_cols,
        cv_folds=3,
        use_smote=True,
        random_state=42
    )

    models = results["models"]
    expected_models = [
        "Decision Tree",
        "Support Vector Classifier",
        "Logistic Regression",
        "Random Forest"
    ]

    for model_name in expected_models:
        assert model_name in models, f"Model {model_name} missing from training output"
        assert models[model_name]["status"] == "SUCCESS", f"Model {model_name} failed: {models[model_name].get('error')}"
        assert models[model_name]["cv_macro_f1_mean"] > 0.0
        assert "accuracy" in models[model_name]["test_metrics"]
        assert "macro_f1" in models[model_name]["test_metrics"]
        assert "high_risk_recall" in models[model_name]["test_metrics"]

def test_model_selection_policy():
    df, _ = generate_synthetic_demo_data(n_samples=120, random_state=42)
    feature_cols = ["attendance_rate", "internal_test_score", "study_hours"]

    results = train_all_models(
        df=df,
        feature_columns=feature_cols,
        cv_folds=3,
        use_smote=True,
        random_state=42
    )

    selected_name, pipeline, rationale = select_best_model(results)
    assert selected_name in results["models"]
    assert pipeline is not None
    assert len(rationale) > 20
    assert "Cross-Validation Macro F1" in rationale or "parsimony" in rationale
