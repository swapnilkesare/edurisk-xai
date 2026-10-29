"""
Tests for PRN-Based One-Time Student Registration and Academic History Tracking.
Validates normalization, validation, uniqueness, idempotent retrieval, academic placement updates,
and assessment linking without duplicating student records.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database import Base
from database.models import Student, Prediction
from database.crud import (
    normalize_prn,
    validate_prn,
    get_student_by_prn,
    register_student_prn,
    update_student_academic_placement,
    save_prediction_and_xai,
    get_student_history,
)


@pytest.fixture
def test_db_session():
    # In-memory SQLite database for isolated unit testing
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()


def test_prn_normalization_and_validation():
    # Test normalization: strip whitespace, uppercase
    assert normalize_prn("  prn-2026-001  ") == "PRN-2026-001"
    assert normalize_prn("prn_cs_042") == "PRN_CS_042"
    assert normalize_prn(None) == ""

    # Test validation
    valid, msg = validate_prn("PRN-2026-001")
    assert valid is True
    assert msg == ""

    valid, msg = validate_prn("2026CS101")
    assert valid is True

    valid, msg = validate_prn("STU-12345")
    assert valid is True

    valid, msg = validate_prn("")
    assert valid is False
    assert "empty" in msg.lower()

    valid, msg = validate_prn("   ")
    assert valid is False

    valid, msg = validate_prn("A")  # Too short (< 2 chars)
    assert valid is False

    valid, msg = validate_prn("PRN*#@!INVALID")  # Invalid symbols
    assert valid is False


def test_register_new_student_and_idempotent_retrieval(test_db_session):
    db = test_db_session
    test_prn = "PRN-TEST-9901"
    org_id = 1

    # Step 1: Register new student
    new_student, was_created, msg = register_student_prn(
        db=db,
        prn=test_prn,
        name="Aarav Sharma",
        organization_id=org_id,
        department="Computer Science",
        course="B.Tech CS",
        batch_year="2024-2028",
        semester=3,
        division="A",
        email="aarav.test@institution.edu",
    )
    assert was_created is True
    assert new_student is not None
    assert new_student.id is not None
    assert new_student.prn == test_prn
    assert new_student.student_identifier == test_prn
    assert "successfully registered" in msg.lower()
    created_id = new_student.id

    # Step 2: Registering SAME PRN again must NOT duplicate, but return existing
    same_student, was_created2, msg2 = register_student_prn(
        db=db,
        prn="  prn-test-9901  ",  # lower case with whitespace
        name="Aarav Sharma Changed Name",
        organization_id=org_id,
        department="Mechanical",
    )
    assert was_created2 is False
    assert same_student is not None
    assert same_student.id == created_id
    assert same_student.prn == test_prn
    assert "already registered" in msg2.lower()

    # Query all students with this PRN in org_id=1, must be exactly 1 record
    matches = db.query(Student).filter(Student.prn == test_prn, Student.organization_id == org_id).all()
    assert len(matches) == 1


def test_academic_placement_update_does_not_duplicate_student(test_db_session):
    db = test_db_session
    test_prn = "PRN-TEST-9902"
    org_id = 1

    # Register
    student, was_created, _ = register_student_prn(
        db=db,
        prn=test_prn,
        name="Priya Patel",
        organization_id=org_id,
        department="Data Science",
        course="B.Sc DS",
        batch_year="2023-2026",
        semester=2,
        division="B",
    )
    student_id = student.id

    # Student moves from Semester 2 Division B to Semester 3 Division A
    updated_student = update_student_academic_placement(
        db=db,
        student_id=student_id,
        new_semester=3,
        new_division="A",
        new_department="Data Science & AI",
        note="Semester progression and dept upgrade",
    )

    assert updated_student.id == student_id
    assert updated_student.semester == 3
    assert updated_student.division == "A"
    assert updated_student.department == "Data Science & AI"
    assert updated_student.academic_history is not None
    assert len(updated_student.academic_history) >= 1

    # Confirm count remains exactly 1
    all_priyas = db.query(Student).filter(Student.prn == test_prn).all()
    assert len(all_priyas) == 1


def test_multiple_assessments_link_to_same_student(test_db_session):
    db = test_db_session
    test_prn = "PRN-TEST-9903"
    org_id = 1

    student, _, _ = register_student_prn(
        db=db,
        prn=test_prn,
        name="Rohan Gupta",
        organization_id=org_id,
        department="Information Tech",
        course="B.Tech IT",
        semester=4,
    )
    student_id = student.id

    # First Assessment: Mid-term
    ass1 = save_prediction_and_xai(
        db=db,
        student_identifier=test_prn,
        model_version="1.0.0",
        model_name="Random Forest",
        predicted_class=1,
        risk_tier="High",
        probability=0.82,
        input_data={"attendance": 65, "internal_test": 45},
        organization_id=org_id,
    )

    # Second Assessment: End-term after intervention
    ass2 = save_prediction_and_xai(
        db=db,
        student_identifier=test_prn,
        model_version="1.0.0",
        model_name="Random Forest",
        predicted_class=0,
        risk_tier="Moderate",
        probability=0.55,
        input_data={"attendance": 78, "internal_test": 62},
        organization_id=org_id,
    )

    assessments = get_student_history(db, student_id)
    assert len(assessments) == 2
    assessment_ids = [a.id for a in assessments]
    assert ass1.id in assessment_ids
    assert ass2.id in assessment_ids

    # Both assessments point to the single student
    assert ass1.student_id == student_id
    assert ass2.student_id == student_id

    # Verify only 1 student exists
    assert db.query(Student).filter(Student.prn == test_prn).count() == 1


def test_organization_isolation_by_prn(test_db_session):
    db = test_db_session
    test_prn = "PRN-SHARED-001"

    # Register in Org 1
    s_org1, _, _ = register_student_prn(
        db=db,
        prn=test_prn,
        name="Student Org 1",
        organization_id=1,
        department="Science",
    )

    # Register in Org 2
    s_org2, _, _ = register_student_prn(
        db=db,
        prn=test_prn,
        name="Student Org 2",
        organization_id=2,
        department="Arts",
    )

    assert s_org1.id != s_org2.id
    assert s_org1.organization_id == 1
    assert s_org2.organization_id == 2

    # Org 1 teacher cannot retrieve Org 2 student by PRN
    retrieved_org1 = get_student_by_prn(db, test_prn, organization_id=1)
    assert retrieved_org1.name == "Student Org 1"

    retrieved_org2 = get_student_by_prn(db, test_prn, organization_id=2)
    assert retrieved_org2.name == "Student Org 2"

    # Org 99 should find None (except if fallback, but with org 99 non-null it won't match org 1 or 2)
    # Notice get_student_by_prn matches organization_id == org_id OR None. Since org_id is 1 or 2, they don't match 99.
    retrieved_org99 = get_student_by_prn(db, test_prn, organization_id=99)
    assert retrieved_org99 is None
