"""
SQLAlchemy ORM Entities for EduRisk XAI
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from database.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_identifier = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    course = Column(String(64), default="Computer Science & AI")
    department = Column(String(64), default="Engineering")
    semester = Column(Integer, default=3)
    year = Column(Integer, default=2)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
