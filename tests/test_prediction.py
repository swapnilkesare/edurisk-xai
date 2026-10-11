"""
Unit Tests for Single-Student Prediction and Risk Tier Inference
"""
import pytest
import pandas as pd
from src.data_loader import generate_synthetic_demo_data
from src.train import train_all_models
from src.model_selection import select_best_model
from src.predict import predict_single_student
from src.risk import RiskClassifier

@pytest.fixture(scope="module")
def fitted_pipeline():
    df, _ = generate_synthetic_demo_data(n_samples=100, random_state=42)
    feature_cols = ["attendance_rate", "internal_test_score", "study_hours"]
    results = train_all_models(df=df, feature_columns=feature_cols, cv_folds=2, random_state=42)
    _, pipeline, _ = select_best_model(results)
    return pipeline

def test_single_student_prediction_output_shape_and_types(fitted_pipeline):
    student_data = {
        "attendance_rate": 60.0,
        "internal_test_score": 45.0,
        "study_hours": 2.0
    }
    pred_res = predict_single_student(fitted_pipeline, student_data)

    assert "predicted_class" in pred_res
    assert pred_res["predicted_class"] in [0, 1]
    assert "risk_probability" in pred_res
    assert 0.0 <= pred_res["risk_probability"] <= 1.0
    assert pred_res["risk_tier"] in ["LOW", "MODERATE", "HIGH"]
    assert "urgency" in pred_res
    assert pred_res["input_features"] == student_data

def test_risk_classifier_consistency():
    classifier = RiskClassifier(high_threshold=0.66, moderate_threshold=0.33)
    high_res = classifier.classify_probability(0.75)
    mod_res = classifier.classify_probability(0.50)
    low_res = classifier.classify_probability(0.20)

    assert high_res["risk_tier"] == "HIGH"
    assert mod_res["risk_tier"] == "MODERATE"
    assert low_res["risk_tier"] == "LOW"
