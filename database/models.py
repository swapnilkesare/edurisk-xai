"""
SQLAlchemy ORM Entities for EduRisk XAI
Includes Tenancy, User Authentication, Role-Based Access Control, and Audit Logging
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from database.database import Base


class Organization(Base):
    """Educational Institution / School / Academy Tenancy Entity."""
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), unique=True, nullable=False)
    code = Column(String(32), unique=True, index=True, nullable=False)
    description = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="organization")


class User(Base):
    """User Account Entity with PBKDF2 Hashing and Role-Based Permissions."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    salt = Column(String(64), nullable=False)
    full_name = Column(String(128), nullable=False)
    role = Column(String(32), nullable=False, default="TEACHER")  # TEACHER, ORG_ADMIN, SYSTEM_ADMIN
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")


class AuditLog(Base):
    """System and Student Data Access Audit Log Entity."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String(64), nullable=False)
    action = Column(String(64), nullable=False)     # LOGIN, LOGOUT, PREDICTION, ACCESS_DENIED, etc.
    resource = Column(String(64), nullable=False)   # STUDENT, PREDICTION, MODEL_RUN, etc.
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_identifier = Column(String(64), index=True, nullable=False)
    prn = Column(String(64), index=True, nullable=True)  # Normalized Permanent Roll Number
    name = Column(String(128), nullable=False)
    email = Column(String(128), nullable=True)
    course = Column(String(64), default="Computer Science & AI")
    department = Column(String(64), default="Engineering")
    batch_year = Column(String(32), default="2024–2028")
    semester = Column(Integer, default=3)
    year = Column(Integer, default=2)
    division = Column(String(16), default="A")
    enrollment_status = Column(String(32), default="Active")
    academic_history = Column(JSON, nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="students")
    predictions = relationship("Prediction", back_populates="student", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="student", cascade="all, delete-orphan")


class AcademicRecord(Base):
    __tablename__ = "academic_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    internal_test_score = Column(Float, nullable=False)
    assignment_score = Column(Float, nullable=True)
    previous_performance = Column(Float, nullable=True)
    assessment_date = Column(DateTime, default=datetime.utcnow)


class BehaviorRecord(Base):
    __tablename__ = "behavior_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    attendance = Column(Float, nullable=False)
    study_hours = Column(Float, nullable=False)
    assignment_submission_rate = Column(Float, nullable=False)
    lms_activity = Column(Float, nullable=True)
    quiz_participation = Column(Float, nullable=True)
    motivation = Column(String(32), nullable=True)
    time_management = Column(String(32), nullable=True)
    record_date = Column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    student_identifier = Column(String(64), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    model_version = Column(String(64), nullable=False)
    model_name = Column(String(64), nullable=False)
    prediction_timestamp = Column(DateTime, default=datetime.utcnow)
    predicted_class = Column(Integer, nullable=False)
    risk_tier = Column(String(16), nullable=False)  # LOW, MODERATE, HIGH
    probability = Column(Float, nullable=False)
    input_data = Column(JSON, nullable=True)

    student = relationship("Student", back_populates="predictions")
    shap_explanations = relationship("SHAPExplanation", back_populates="prediction", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="prediction", cascade="all, delete-orphan")


class SHAPExplanation(Base):
    __tablename__ = "shap_explanations"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False)
    feature_name = Column(String(64), nullable=False)
    feature_value = Column(Float, nullable=True)
    shap_value = Column(Float, nullable=False)
    direction = Column(String(16), nullable=False)  # RISK_INCREASING, PROTECTIVE
    rank = Column(Integer, nullable=False)

    prediction = relationship("Prediction", back_populates="shap_explanations")


class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True)
    risk_factor = Column(String(64), nullable=False)
    intervention = Column(Text, nullable=False)
    priority = Column(String(16), default="MEDIUM")  # HIGH, MEDIUM, LOW
    status = Column(String(32), default="Pending")    # Pending, In Progress, Completed, Dismissed
    rationale = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("Student", back_populates="interventions")
    prediction = relationship("Prediction", back_populates="interventions")


class InterventionRule(Base):
    __tablename__ = "intervention_rules"

    id = Column(Integer, primary_key=True, index=True)
    feature = Column(String(64), nullable=False)
    threshold = Column(Float, nullable=False)
    direction = Column(String(16), default="below")  # below, above, equals
    severity = Column(String(16), default="HIGH")    # HIGH, MEDIUM, LOW
    action = Column(Text, nullable=False)
    rationale = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)


class ModelRun(Base):
    __tablename__ = "model_runs"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(String(64), unique=True, index=True, nullable=False)
    model_version = Column(String(64), nullable=False)
    model_name = Column(String(64), nullable=False)
    training_timestamp = Column(DateTime, default=datetime.utcnow)
    dataset_name = Column(String(128), nullable=False)
    dataset_hash = Column(String(64), nullable=False)
    is_synthetic = Column(Boolean, default=False)
    feature_list = Column(JSON, nullable=False)
    hyperparameters = Column(JSON, nullable=True)
    cv_metrics = Column(JSON, nullable=True)
    test_metrics = Column(JSON, nullable=True)
    training_duration = Column(Float, nullable=False)
    inference_latency_ms = Column(Float, nullable=False)
    is_selected = Column(Boolean, default=False)
    selection_rationale = Column(Text, nullable=True)


class DatasetImport(Base):
    __tablename__ = "dataset_imports"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(256), nullable=False)
    source_type = Column(String(32), nullable=False)
    row_count = Column(Integer, nullable=False)
    feature_count = Column(Integer, nullable=False)
    fingerprint = Column(String(64), nullable=False)
    is_synthetic = Column(Boolean, default=False)
    import_timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(32), default="SUCCESS")
