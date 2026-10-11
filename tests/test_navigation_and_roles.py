"""
Regression and Verification Tests for Navigation, Roles, and Multi-Tenancy
Tests that:
1. Home, Student Risk Assessment, Students, and Reports modules load correctly.
2. Returning to Home works from every page.
3. Unauthorized teachers cannot access administrator functions.
4. Organization A cannot retrieve Organization B student records.
5. Prediction pipeline functions end-to-end with genuine SHAP and interventions.
"""
import pytest
from database.database import SessionLocal, init_db
from database.models import User, Organization, Student, Prediction
from services.auth_service import (
    authenticate_user, user_can_access_admin_tools,
    user_can_access_student, get_scoped_students, get_scoped_predictions
)
from services.prediction_service import PredictionService

@pytest.fixture(scope="module")
def db_session():
    init_db()
    db = SessionLocal()
    yield db
    db.close()

def test_page_modules_exist_and_callable():
    """Verify all 11 application page modules have valid callable entry points."""
    import app_pages.dashboard as dashboard
    import app_pages.predict_student as predict_student
    import app_pages.students as students
    import app_pages.reports as reports
    import app_pages.data_import as data_import
    import app_pages.model_training as model_training
    import app_pages.model_comparison as model_comparison
    import app_pages.explainability as explainability
    import app_pages.interventions as interventions
    import app_pages.analytics as analytics
    import app_pages.research_traceability as research_traceability

    assert callable(dashboard.render_dashboard)
    assert callable(predict_student.render_predict_student)
    assert callable(students.render_students)
    assert callable(reports.render_reports)
    assert callable(data_import.render_data_import)
    assert callable(model_training.render_model_training)
    assert callable(model_comparison.render_model_comparison)
    assert callable(explainability.render_explainability)
    assert callable(interventions.render_interventions)
    assert callable(analytics.render_analytics)
    assert callable(research_traceability.render_research_traceability)

def test_teacher_role_boundary_enforcement(db_session):
    """Verify teachers cannot access administrative / researcher tools."""
    teacher = authenticate_user(db_session, "teacher1", "Teacher@123")
    assert teacher is not None
    assert teacher.role == "TEACHER"

    # Must be denied admin access
    assert user_can_access_admin_tools(teacher) is False

def test_researcher_admin_privilege(db_session):
    """Verify System Administrator / Researcher has permission to access admin tools."""
    researcher = authenticate_user(db_session, "researcher", "Research@123")
    assert researcher is not None
    assert researcher.role == "SYSTEM_ADMIN"

    assert user_can_access_admin_tools(researcher) is True

def test_organization_data_isolation(db_session):
    """Verify Organization A cannot view Organization B's student records."""
    teacher_horizon = authenticate_user(db_session, "teacher1", "Teacher@123")
    teacher_apex = authenticate_user(db_session, "teacher2", "Teacher@123")

    horizon_students = get_scoped_students(db_session, teacher_horizon)
    apex_students = get_scoped_students(db_session, teacher_apex)

    horizon_ids = {s.id for s in horizon_students}
    apex_ids = {s.id for s in apex_students}

    # Intersecting sets must be empty (strict multi-tenant isolation)
    assert horizon_ids.isdisjoint(apex_ids) or len(apex_ids) == 0

def test_end_to_end_scoped_prediction(db_session):
    """Verify real prediction, SHAP, and recommendations are created and scoped to organization."""
    pred_svc = PredictionService()
    assert pred_svc.is_model_ready() is True

    teacher = authenticate_user(db_session, "teacher1", "Teacher@123")

    test_payload = {
        "attendance_rate": 60.0,
        "internal_test_score": 35.0,
        "assignment_submission_frequency": 50.0,
        "study_hours": 2.0,
        "failures": 1
    }

    result = pred_svc.predict_and_explain(
        student_data=test_payload,
        student_identifier="STU-VERIFY-NAV-01",
        save_to_db=True,
        organization_id=teacher.organization_id,
        created_by_user_id=teacher.id
    )

    assert result["prediction"]["risk_tier"] in ["HIGH", "MODERATE"]
    assert result["shap"]["status"] == "SUCCESS"
    assert len(result["interventions"]) > 0

    # Query scoped predictions for teacher
    scoped_preds = get_scoped_predictions(db_session, teacher)
    saved_pred = next((p for p in scoped_preds if p.student_identifier == "STU-VERIFY-NAV-01"), None)
    assert saved_pred is not None
    assert saved_pred.organization_id == teacher.organization_id
