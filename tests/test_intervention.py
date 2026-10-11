"""
Unit Tests for Rule-Based Pedagogical Intervention Engine
"""
import pytest
from src.intervention import InterventionEngine

def test_deterministic_intervention_triggering():
    engine = InterventionEngine()

    vulnerable_student = {
        "attendance_rate": 55.0,        # < 75% -> Should trigger
        "internal_test_score": 40.0,    # < 50% -> Should trigger
        "assignment_submission_frequency": 65.0, # < 70% -> Should trigger
        "study_hours": 1.5,             # < 2.5 -> Should trigger
    }

    shap_mock = {
        "status": "SUCCESS",
        "risk_increasing_factors": [
            {"feature": "attendance_rate", "shap_value": 0.35},
            {"feature": "internal_test_score", "shap_value": 0.25}
        ]
    }

    recommendations = engine.evaluate_interventions(
        student_features=vulnerable_student,
        shap_explanation=shap_mock,
        risk_tier="HIGH"
    )

    assert len(recommendations) >= 3

    triggered_features = [r["feature"] for r in recommendations]
    assert "attendance_rate" in triggered_features
    assert "internal_test_score" in triggered_features

    # Verify SHAP verification flag
    att_rec = next(r for r in recommendations if r["feature"] == "attendance_rate")
    assert att_rec["shap_verified"] is True
    assert att_rec["priority"] == "HIGH"
    assert "disclaimer" in att_rec

def test_on_track_student_triggers_no_interventions():
    engine = InterventionEngine()

    excellent_student = {
        "attendance_rate": 95.0,
        "internal_test_score": 85.0,
        "assignment_submission_frequency": 92.0,
        "study_hours": 8.0,
    }

    recommendations = engine.evaluate_interventions(
        student_features=excellent_student,
        shap_explanation=None,
        risk_tier="LOW"
    )

    assert len(recommendations) == 0
