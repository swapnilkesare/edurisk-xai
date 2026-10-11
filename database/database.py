"""
SQLite Database Connection and Session Engine for EduRisk XAI
Includes safe, reversible additive migrations for multi-tenancy and audit fields
"""
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

from config.settings import DATABASE_URL, DB_PATH

Base = declarative_base()

# SQLite engine with check_same_thread=False for Streamlit multi-threading
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def _apply_additive_migrations(conn):
    """Safely adds missing columns to existing SQLite tables without data loss."""
    # Check students table
    cursor = conn.execute(text("PRAGMA table_info(students)"))
    student_cols = [row[1] for row in cursor.fetchall()]
    if "organization_id" not in student_cols:
        conn.execute(text("ALTER TABLE students ADD COLUMN organization_id INTEGER"))
    if "created_by_user_id" not in student_cols:
        conn.execute(text("ALTER TABLE students ADD COLUMN created_by_user_id INTEGER"))

    # Check predictions table
    cursor = conn.execute(text("PRAGMA table_info(predictions)"))
    pred_cols = [row[1] for row in cursor.fetchall()]
    if "organization_id" not in pred_cols:
        conn.execute(text("ALTER TABLE predictions ADD COLUMN organization_id INTEGER"))
    if "created_by_user_id" not in pred_cols:
        conn.execute(text("ALTER TABLE predictions ADD COLUMN created_by_user_id INTEGER"))

def init_db():
    """Initializes tables in SQLite database if they don't already exist and applies additive migrations."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    from database import models  # Ensure all models are registered
    Base.metadata.create_all(bind=engine)
    
    with engine.connect() as conn:
        _apply_additive_migrations(conn)
        conn.commit()

def get_db():
    """Generator providing a scoped SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
