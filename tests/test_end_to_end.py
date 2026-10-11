"""
End-to-End System Integration Test for EduRisk XAI
"""
import pytest
import pandas as pd
from pathlib import Path

from src.data_loader import load_dataset
from src.schema import validate_dataframe_schema
from services.training_service import TrainingService
from services.prediction_service import PredictionService
from services.report_service import ReportService
from config.settings import ARTIFACTS_DIR, EXPERIMENTS_DIR

def test_full_pipeline_end_to_end():
    """
    Executes complete workflow: Data -> 4-Model Train -> Selection -> Inference -> SHAP -> Intervention -> Report.
    """
    # 1. Data Loading
    df, provenance = load_dataset(fallback_to_synthetic=True)
    assert not df.empty
    is_valid, errors, _ = validate_dataframe_schema(df)
    assert is_valid, f"Dataset schema invalid: {errors}"

    # 2. Multi-Model Training
    train_svc = TrainingService()
    # Use smaller subset for fast CI/test execution
    df_sample = df.sample(min(len(df), 120), random_state=42)
    experiment_record = train_svc.run_full_training(
        df=df_sample,
        provenance=provenance,
        use_smote=True
    )

    assert "experiment_id" in experiment_record
    assert experiment_record["selected_model"] is not None
    assert (ARTIFACTS_DIR / "best_model.pkl").exists()
    assert (ARTIFACTS_DIR / "model_metadata.json").exists()

    # 3. Prediction & Explainability
    pred_svc = PredictionService()
    assert pred_svc.is_model_ready() is True

    test_student = {
        "attendance_rate": 62.0,
        "internal_test_score": 48.0,
        "assignment_submission_frequency": 60.0,
        "study_hours": 2.0,
    }

    result = pred_svc.predict_and_explain(
        student_data=test_student,
        student_identifier="STU-E2E-TEST",
        save_to_db=True
    )

    assert "prediction" in result
    assert result["prediction"]["risk_tier"] in ["LOW", "MODERATE", "HIGH"]
    assert "shap" in result
    assert result["shap"]["status"] in ["SUCCESS", "UNAVAILABLE"]
    assert "interventions" in result
    assert isinstance(result["interventions"], list)

    # 4. Reporting & Figures
    report_svc = ReportService()
    figs = report_svc.generate_experiment_figures(experiment_record)
    assert len(figs) >= 1
    report_md = report_svc.generate_markdown_report(experiment_record)
    assert len(report_md) > 100

def test_streamlit_pages_import_smoke():
    """
    Verifies that all Streamlit page modules compile and import cleanly.
    """
    import app_pages.dashboard
    import app_pages.data_import
    import app_pages.model_training
    import app_pages.model_comparison
    import app_pages.predict_student
    import app_pages.explainability
    import app_pages.interventions
    import app_pages.analytics
    import app_pages.research_traceability
    import app_pages.students
    import app_pages.reports
    assert True

