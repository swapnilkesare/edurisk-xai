"""
Unit and Integration Tests for Authentication, Password Security, Multi-Tenancy Scoping, and RBAC
"""
import pytest
from datetime import datetime
from database.database import SessionLocal, init_db
from database.models import User, Organization, Student, AuditLog
from services.auth_service import (
    hash_password, verify_password, authenticate_user,
    seed_default_auth, get_scoped_students, user_can_access_student,
    user_can_access_admin_tools, log_audit_event
)

@pytest.fixture(scope="module", autouse=True)
def setup_database_and_auth():
    init_db()
    db = SessionLocal()
    seed_default_auth(db)
    db.close()

def test_password_hashing_and_verification():
    raw_pass = "SecureEducatorPass#2026"
    h1, s1 = hash_password(raw_pass)
    h2, s2 = hash_password(raw_pass)

    # Different random salts must yield different hashes
    assert s1 != s2
    assert h1 != h2

    # Verification must succeed with correct salt
    assert verify_password(raw_pass, s1, h1) is True
    assert verify_password("WrongPassword123", s1, h1) is False

def test_seed_users_and_authentication():
    db = SessionLocal()
    try:
        # Teacher auth
        teacher = authenticate_user(db, "teacher1", "Teacher@123")
        assert teacher is not None
        assert teacher.role == "TEACHER"
        assert teacher.organization.code == "HORIZON"

        # Org Admin auth
        admin = authenticate_user(db, "orgadmin", "OrgAdmin@123")
        assert admin is not None
        assert admin.role == "ORG_ADMIN"

        # Researcher / System Admin auth
        researcher = authenticate_user(db, "researcher", "Research@123")
        assert researcher is not None
        assert researcher.role == "SYSTEM_ADMIN"

        # Failed auth
        failed = authenticate_user(db, "teacher1", "WrongPassword")
        assert failed is None
    finally:
        db.close()

def test_role_based_access_privileges():
    db = SessionLocal()
    try:
        teacher = db.query(User).filter(User.username == "teacher1").first()
        org_admin = db.query(User).filter(User.username == "orgadmin").first()
        sys_admin = db.query(User).filter(User.username == "researcher").first()

        # Teachers and Org Admins must NOT have admin/research tool access
        assert user_can_access_admin_tools(teacher) is False
        assert user_can_access_admin_tools(org_admin) is False

        # Only System Admin has research/admin tool access
        assert user_can_access_admin_tools(sys_admin) is True
    finally:
        db.close()

def test_multi_tenancy_student_scoping():
    db = SessionLocal()
    try:
        horizon_org = db.query(Organization).filter(Organization.code == "HORIZON").first()
        apex_org = db.query(Organization).filter(Organization.code == "APEX").first()

        # Create student in Apex
        apex_student = db.query(Student).filter(Student.student_identifier == "STU-APEX-001").first()
        if not apex_student:
            apex_student = Student(
                student_identifier="STU-APEX-001",
                name="Apex Student Alpha",
                organization_id=apex_org.id,
                created_at=datetime.utcnow()
            )
            db.add(apex_student)
            db.commit()

        teacher_horizon = db.query(User).filter(User.username == "teacher1").first()
        teacher_apex = db.query(User).filter(User.username == "teacher2").first()
        sys_admin = db.query(User).filter(User.username == "researcher").first()

        # Teacher Horizon cannot access Apex student
        assert user_can_access_student(teacher_horizon, apex_student) is False

        # Teacher Apex CAN access Apex student
        assert user_can_access_student(teacher_apex, apex_student) is True

        # System Admin can access any student
        assert user_can_access_student(sys_admin, apex_student) is True

        # Scoped roster query
        horizon_students = get_scoped_students(db, teacher_horizon)
        for s in horizon_students:
            assert s.organization_id == horizon_org.id
    finally:
        db.close()

def test_audit_logging_persistence():
    db = SessionLocal()
    try:
        log_entry = log_audit_event(
            db=db,
            user_id=1,
            username="test_audit_user",
            action="TEST_ACTION",
            resource="TEST_RESOURCE",
            details="Unit test verification of audit persistence"
        )
        assert log_entry.id is not None

        queried = db.query(AuditLog).filter(AuditLog.id == log_entry.id).first()
        assert queried.username == "test_audit_user"
        assert queried.action == "TEST_ACTION"
    finally:
        db.close()
