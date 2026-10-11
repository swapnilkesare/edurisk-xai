"""
SQLite Database Connection and Session Engine for EduRisk XAI
"""
from pathlib import Path
from sqlalchemy import create_engine
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

def init_db():
    """Initializes tables in SQLite database if they don't already exist."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    from database import models  # Ensure all models are registered
    Base.metadata.create_all(bind=engine)

def get_db():
    """Generator providing a scoped SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
