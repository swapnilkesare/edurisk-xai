from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from config.settings import DATABASE_URL

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_identifier = Column(String, unique=True, index=True)
    name = Column(String)
    course = Column(String)
    department = Column(String)
    semester = Column(Integer)
    year = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    records = relationship("AcademicRecord", back_populates="student")
    behaviors = relationship("BehaviorRecord", back_populates="student")
    predictions = relationship("Prediction", back_populates="student")
    interventions = relationship("Intervention", back_populates="student")

class AcademicRecord(Base):
    __tablename__ = 'academic_records'
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    internal_test_score = Column(Float)
    assignment_score = Column(Float)
    previous_performance = Column(String)
    assessment_date = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="records")

class BehaviorRecord(Base):
    __tablename__ = 'behavior_records'
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    attendance = Column(Float)
    study_hours = Column(Float)
    assignment_submission_rate = Column(Float)
    lms_activity = Column(Float)
    quiz_participation = Column(Float)
    motivation = Column(String)
    time_management = Column(String)
    record_date = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="behaviors")

class Prediction(Base):
    __tablename__ = 'predictions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    model_version = Column(String)
    prediction_timestamp = Column(DateTime, default=datetime.utcnow)
    predicted_class = Column(Integer) # 1 for at-risk, 0 for not
    risk_tier = Column(String) # LOW, MODERATE, HIGH
    probability = Column(Float)
    
    student = relationship("Student", back_populates="predictions")
    shap_explanations = relationship("SHAPExplanation", back_populates="prediction")
    interventions = relationship("Intervention", back_populates="prediction")

class SHAPExplanation(Base):
    __tablename__ = 'shap_explanations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    prediction_id = Column(Integer, ForeignKey('predictions.id'))
    feature_name = Column(String)
    feature_value = Column(Float) # raw or scaled
    shap_value = Column(Float)
    direction = Column(String) # 'positive' or 'negative' relative to risk
    rank = Column(Integer)
    
    prediction = relationship("Prediction", back_populates="shap_explanations")

class InterventionRule(Base):
    __tablename__ = 'intervention_rules'
    id = Column(Integer, primary_key=True, autoincrement=True)
    feature_name = Column(String, index=True)
    threshold = Column(Float, nullable=True) # Optional, can rely just on SHAP direction
    direction = Column(String) # "below" or "above" or "shap_positive"
    severity = Column(String) # "High", "Medium", "Low"
    intervention_action = Column(String)
    priority = Column(Integer) # lower number = higher priority
    is_active = Column(Boolean, default=True)

class Intervention(Base):
    __tablename__ = 'interventions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    prediction_id = Column(Integer, ForeignKey('predictions.id'))
    risk_factor = Column(String)
    intervention_action = Column(String)
    priority = Column(Integer)
    status = Column(String, default="Pending") # Pending, In Progress, Completed, Dismissed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    student = relationship("Student", back_populates="interventions")
    prediction = relationship("Prediction", back_populates="interventions")

class ModelRun(Base):
    __tablename__ = 'model_runs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_version = Column(String, unique=True, index=True)
    model_name = Column(String)
    training_timestamp = Column(DateTime, default=datetime.utcnow)
    dataset_version = Column(String)
    dataset_hash = Column(String)
    feature_list = Column(String) # comma separated
    hyperparameters = Column(String) # JSON string
    cv_metrics = Column(String) # JSON string
    test_metrics = Column(String) # JSON string
    training_time = Column(Float)
    inference_time = Column(Float)
    selected_model = Column(Boolean, default=False)
