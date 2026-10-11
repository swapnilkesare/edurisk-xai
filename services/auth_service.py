"""
Authentication, Authorization, Multi-Tenancy Scoping, and Audit Service for EduRisk
Implements NIST-compliant PBKDF2-SHA256 password hashing and Role-Based Access Control (RBAC).
"""
import hashlib
import hmac
import secrets
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
from sqlalchemy.orm import Session, joinedload

from database.models import User, Organization, Student, Prediction, AuditLog

PBKDF2_ITERATIONS = 200_000
SALT_BYTES = 32

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Hashes a password using PBKDF2-HMAC-SHA256 with 200,000 iterations.
    Returns (hex_hash, hex_salt).
    """
    if not salt:
        salt = secrets.token_hex(SALT_BYTES)
    
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        PBKDF2_ITERATIONS
    )
    return key.hex(), salt

def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    """Verifies a candidate password using constant-time hash comparison."""
    computed_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(computed_hash, expected_hash)

def authenticate_user(db: Session, username_or_email: str, password: str) -> Optional[User]:
    """Authenticates user credentials and records audit telemetry."""
    user = db.query(User).options(joinedload(User.organization)).filter(
        (User.username == username_or_email.strip()) | 
        (User.email == username_or_email.strip())
    ).first()

    if not user or not user.is_active:
        log_audit_event(db, None, username_or_email, "LOGIN_FAILED", "USER", "User not found or inactive")
        return None

    if verify_password(password, user.salt, user.password_hash):
        user.last_login = datetime.utcnow()
        db.commit()
        log_audit_event(db, user.id, user.username, "LOGIN_SUCCESS", "SESSION", f"User logged in with role {user.role}")
        return user
    else:
        log_audit_event(db, user.id, user.username, "LOGIN_FAILED", "SESSION", "Invalid password provided")
        return None

def log_audit_event(
    db: Session,
    user_id: Optional[int],
    username: str,
    action: str,
    resource: str,
    details: Optional[str] = None
) -> AuditLog:
    """Persists a secure audit log entry for administrative and student data access tracking."""
    log_entry = AuditLog(
        user_id=user_id,
        username=username[:64] if username else "ANONYMOUS",
        action=action[:64],
        resource=resource[:64],
        details=details,
        timestamp=datetime.utcnow()
    )
    db.add(log_entry)
    db.commit()
    return log_entry

def seed_default_auth(db: Session):
    """
    Ensures default organizations and demonstration role accounts exist in SQLite database.
    Seeds are securely hashed with individual unique salts.
    """
    # 1. Organizations
    org_count = db.query(Organization).count()
    if org_count == 0:
        org1 = Organization(
            name="Horizon High School",
            code="HORIZON",
            description="Public Secondary Academic Institution (District 4)",
            created_at=datetime.utcnow()
        )
        org2 = Organization(
            name="Apex Academy",
            code="APEX",
            description="STEM & Technical Preparatory Institute",
            created_at=datetime.utcnow()
        )
        db.add_all([org1, org2])
        db.commit()

    horizon_org = db.query(Organization).filter(Organization.code == "HORIZON").first()
    apex_org = db.query(Organization).filter(Organization.code == "APEX").first()

    # 2. Users
    user_count = db.query(User).count()
    if user_count == 0:
        # Default Teacher 1 (Horizon)
        p1_hash, s1 = hash_password("Teacher@123")
        u1 = User(
            username="teacher1",
            email="clara.reed@horizon.edu",
            password_hash=p1_hash,
            salt=s1,
            full_name="Ms. Clara Reed",
            role="TEACHER",
            organization_id=horizon_org.id if horizon_org else None,
            is_active=True
        )

        # Default Teacher 2 (Apex)
        p2_hash, s2 = hash_password("Teacher@123")
        u2 = User(
            username="teacher2",
            email="david.vance@apex.edu",
            password_hash=p2_hash,
            salt=s2,
            full_name="Mr. David Vance",
            role="TEACHER",
            organization_id=apex_org.id if apex_org else None,
            is_active=True
        )

        # Default Organization Administrator (Horizon)
        p3_hash, s3 = hash_password("OrgAdmin@123")
        u3 = User(
            username="orgadmin",
            email="arthur.vance@horizon.edu",
            password_hash=p3_hash,
            salt=s3,
            full_name="Principal Arthur Vance",
            role="ORG_ADMIN",
            organization_id=horizon_org.id if horizon_org else None,
            is_active=True
        )

        # Default System Administrator / AI Lead Researcher (Global)
        p4_hash, s4 = hash_password("Research@123")
        u4 = User(
            username="researcher",
            email="elena.rostova@edurisk-research.org",
            password_hash=p4_hash,
            salt=s4,
            full_name="Dr. Elena Rostova",
            role="SYSTEM_ADMIN",
            organization_id=None,
            is_active=True
        )

        db.add_all([u1, u2, u3, u4])
        db.commit()

    # 3. Attach existing unassigned students to Horizon High School for immediate demonstration
    if horizon_org:
        db.query(Student).filter(Student.organization_id == None).update(
            {"organization_id": horizon_org.id},
            synchronize_session=False
        )
        db.query(Prediction).filter(Prediction.organization_id == None).update(
            {"organization_id": horizon_org.id},
            synchronize_session=False
        )
        db.commit()

def get_scoped_students(db: Session, user: Optional[User]) -> List[Student]:
    """Retrieves students scoped by user role and organization."""
    if not user:
        return []
    if user.role == "SYSTEM_ADMIN":
        return db.query(Student).order_by(Student.name.asc()).all()
    if user.organization_id:
        return db.query(Student).filter(Student.organization_id == user.organization_id).order_by(Student.name.asc()).all()
    return []

def get_scoped_predictions(db: Session, user: Optional[User], limit: int = 50) -> List[Prediction]:
    """Retrieves predictions scoped by user role and organization."""
    if not user:
        return []
    if user.role == "SYSTEM_ADMIN":
        return db.query(Prediction).order_by(Prediction.prediction_timestamp.desc()).limit(limit).all()
    if user.organization_id:
        return db.query(Prediction).filter(
            (Prediction.organization_id == user.organization_id) | 
            (Prediction.organization_id == None)
        ).order_by(Prediction.prediction_timestamp.desc()).limit(limit).all()
    return []

def user_can_access_student(user: Optional[User], student: Student) -> bool:
    """Enforces fine-grained student record permission boundary."""
    if not user:
        return False
    if user.role == "SYSTEM_ADMIN":
        return True
    if student.organization_id and user.organization_id == student.organization_id:
        return True
    return False

def user_can_access_admin_tools(user: Optional[User]) -> bool:
    """Verifies privilege to access research, model benchmarking, and training tools."""
    if not user:
        return False
    return user.role == "SYSTEM_ADMIN"
