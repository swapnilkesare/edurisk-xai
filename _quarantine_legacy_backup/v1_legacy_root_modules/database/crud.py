from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_URL
from database.models import Base, InterventionRule

# Initialize engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create all tables
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_default_rules(db):
    """Seed the database with default intervention rules if empty."""
    if db.query(InterventionRule).count() == 0:
        defaults = [
            {"feature_name": "attendance_rate", "direction": "shap_positive", "severity": "High", "intervention_action": "Mentor check-in and attendance improvement plan.", "priority": 1},
            {"feature_name": "internal_test_score", "direction": "shap_positive", "severity": "High", "intervention_action": "Peer tutoring and remedial session.", "priority": 2},
            {"feature_name": "assignment_submission_frequency", "direction": "shap_positive", "severity": "Medium", "intervention_action": "Assignment reminder and support.", "priority": 3},
            {"feature_name": "study_hours", "direction": "shap_positive", "severity": "Medium", "intervention_action": "Study planning and time-management support.", "priority": 4},
            {"feature_name": "failures", "direction": "shap_positive", "severity": "High", "intervention_action": "Academic counseling and targeted revision.", "priority": 1},
        ]
        for rule in defaults:
            db.add(InterventionRule(**rule))
        db.commit()

# Call this once on startup
db = SessionLocal()
init_default_rules(db)
db.close()
