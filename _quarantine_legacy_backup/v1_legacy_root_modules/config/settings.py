import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
SAMPLE_DATA_DIR = DATA_DIR / 'sample'

MODEL_DIR = BASE_DIR / 'models'
CURRENT_MODEL_DIR = MODEL_DIR / 'current'
MODEL_VERSIONS_DIR = MODEL_DIR / 'versions'

# Database
DATABASE_URL = os.getenv('DATABASE_URL', f"sqlite:///{BASE_DIR}/edurisk.db")

# Reproducibility
RANDOM_SEED = int(os.getenv('RANDOM_SEED', 42))

# Application Config
APP_NAME = os.getenv('APP_NAME', "Explainable AI in Education")
APP_VERSION = os.getenv('APP_VERSION', "1.0.0")

# Risk Thresholds
RISK_THRESHOLD_HIGH = 0.66
RISK_THRESHOLD_MODERATE = 0.33

# Methodology Feature List
CORE_FEATURES = [
    'attendance_rate',
    'assignment_submission_frequency',
    'internal_test_score',
    'study_hours'
]

# Ensure necessary directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, SAMPLE_DATA_DIR, CURRENT_MODEL_DIR, MODEL_VERSIONS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
