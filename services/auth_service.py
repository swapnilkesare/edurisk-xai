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

# ============================================================================
# CENTRALIZED DEMO ACCOUNTS REGISTRY
# Source of truth for pre-configured development and demonstration access
# ============================================================================
DEMO_ACCOUNTS: List[Dict[str, Any]] = [
    {
        "username": "teacher1",
        "email": "clara.reed@horizon.edu",
        "default_password": "Teacher@123",
        "full_name": "Ms. Clara Reed",
        "role": "TEACHER",
        "org_code": "HORIZON",
        "org_name": "Horizon High School",
        "label": "🧑‍🏫 Teacher 1",
        "badge": "Educator (Horizon)",
        "scope": "Teacher workflow scoped to Horizon High School student cohort"
    },
    {
        "username": "teacher2",
        "email": "david.vance@apex.edu",
        "default_password": "Teacher@123",
        "full_name": "Mr. David Vance",
        "role": "TEACHER",
        "org_code": "APEX",
        "org_name": "Apex Academy",
        "label": "🧑‍🏫 Teacher 2",
        "badge": "Educator (Apex)",
        "scope": "Teacher workflow scoped to Apex Academy student cohort"
    },
    {
        "username": "orgadmin",
        "email": "arthur.vance@horizon.edu",
        "default_password": "OrgAdmin@123",
        "full_name": "Principal Arthur Vance",
        "role": "ORG_ADMIN",
        "org_code": "HORIZON",
        "org_name": "Horizon High School",
        "label": "🏫 Org Admin",
        "badge": "Institutional Admin",
        "scope": "Educator dashboard + student roster registration & management"
    },
    {
        "username": "researcher",
        "email": "elena.rostova@edurisk-research.org",
        "default_password": "Research@123",
        "full_name": "Dr. Elena Rostova",
        "role": "SYSTEM_ADMIN",
        "org_code": None,
        "org_name": "Global Research System",
        "label": "🔬 Researcher",
        "badge": "Lead AI Researcher",
        "scope": "Global cohort access + protected Research & Admin Tools"
    }
]

def seed_default_auth(db: Session):
    """
    Ensures default organizations and demonstration role accounts exist in SQLite database.
    Strictly idempotent:
    - Never duplicates organizations or users across restarts or multiple executions.
    - Never overwrites an existing user's password or salt.
    - Hashes initial default passwords with unique cryptographic salts using PBKDF2-HMAC-SHA256.
    """
    # 1. Organizations: Ensure both default organizations exist idempotently
    default_orgs = [
        ("HORIZON", "Horizon High School", "Public Secondary Academic Institution (District 4)"),
        ("APEX", "Apex Academy", "STEM & Technical Preparatory Institute")
    ]
    for code, name, desc in default_orgs:
        existing_org = db.query(Organization).filter(Organization.code == code).first()
        if not existing_org:
            new_org = Organization(
                name=name,
                code=code,
                description=desc,
                created_at=datetime.utcnow()
            )
            db.add(new_org)
    db.commit()

    # Build code-to-id mapping for organizations
    org_map = {org.code: org.id for org in db.query(Organization).all()}

    # 2. Users: Idempotently ensure each demo account exists without overwriting existing accounts
    for demo_cfg in DEMO_ACCOUNTS:
        uname = demo_cfg["username"]
        existing_user = db.query(User).filter(User.username == uname).first()
        if not existing_user:
            p_hash, salt = hash_password(demo_cfg["default_password"])
            org_id = org_map.get(demo_cfg["org_code"]) if demo_cfg["org_code"] else None
            new_user = User(
                username=uname,
                email=demo_cfg["email"],
                password_hash=p_hash,
                salt=salt,
                full_name=demo_cfg["full_name"],
                role=demo_cfg["role"],
                organization_id=org_id,
                is_active=True
            )
            db.add(new_user)
        else:
            # User already exists; preserve their existing password, credentials, and settings
            pass
    db.commit()

    # 3. Attach unassigned demonstration students to Horizon High School for immediate cohort view
    horizon_id = org_map.get("HORIZON")
    if horizon_id:
        db.query(Student).filter(Student.organization_id == None).update(
            {"organization_id": horizon_id},
            synchronize_session=False
        )
        db.query(Prediction).filter(Prediction.organization_id == None).update(
            {"organization_id": horizon_id},
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
