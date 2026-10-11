"""
Unit Tests for SQLite Persistence and SQLAlchemy ORM CRUD Operations
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database import Base
from database.models import Student, Prediction, Intervention, InterventionRule
from database.crud import (
    get_or_create_student,
    save_prediction_and_xai,
    update_intervention_status,
    get_student_history,
    seed_default_rules_if_empty
)

@pytest.fixture
def test_db_session():
    # In-memory SQLite database for isolated unit testing
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    seed_default_rules_if_empty(db)
    yield db
    db.close()

def test_database_student_creation_and_retrieval(test_db_session):
    student = get_or_create_student(test_db_session, "STU-TEST-001", "Alex Smith")
    assert student.id is not None
    assert student.student_identifier == "STU-TEST-001"

    # Fetch again, should return same entity without duplicate
    student_again = get_or_create_student(test_db_session, "STU-TEST-001")
    assert student_again.id == student.id

def test_save_prediction_and_interventions(test_db_session):
    student_id = "STU-TEST-002"
    pred = save_prediction_and_xai(
        db=test_db_session,
        student_identifier=student_id,
        model_version="v_test",
        model_name="Decision Tree",
        predicted_class=1,
        risk_tier="HIGH",
        probability=0.78,
        input_data={"attendance_rate": 50.0},
        shap_explanation={
            "status": "SUCCESS",
            "contributions": [
                {
                    "feature": "attendance_rate",
                    "raw_value": 50.0,
                    "shap_value": 0.35,
                    "is_risk_increasing": True,
                    "is_protective": False
                }
            ]
        },
        interventions=[
            {
                "feature": "attendance_rate",
                "action": "Mentor check-in",
                "priority": "HIGH",
                "rationale": "Low attendance"
            }
        ]
    )

    assert pred.id is not None
    assert pred.risk_tier == "HIGH"
    assert len(pred.shap_explanations) == 1
    assert len(pred.interventions) == 1

    interv_id = pred.interventions[0].id
    assert pred.interventions[0].status == "Pending"

    # Test status update
    updated = update_intervention_status(test_db_session, interv_id, "Completed")
    assert updated is True
    assert pred.interventions[0].status == "Completed"

    # Test longitudinal history
    history = get_student_history(test_db_session, student_id)
    assert len(history) == 1
    assert history[0].id == pred.id
