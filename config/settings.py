"""
EduRisk XAI Configuration and Global Settings
"""
from pathlib import Path
import os

# Project Root Directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data Directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "student_data.csv"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
METADATA_DIR = DATA_DIR / "metadata"

# Model and Artifact Directories
MODELS_DIR = PROJECT_ROOT / "models"
ARTIFACTS_DIR = MODELS_DIR / "artifacts"
VERSIONS_DIR = MODELS_DIR / "versions"

# Results Directories
RESULTS_DIR = PROJECT_ROOT / "results"
EXPERIMENTS_DIR = RESULTS_DIR / "experiments"
FIGURES_DIR = RESULTS_DIR / "figures"
REPORTS_DIR = RESULTS_DIR / "reports"

# Database Configuration
DATABASE_DIR = PROJECT_ROOT / "database"
DB_PATH = DATABASE_DIR / "edurisk.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Ensure directories exist
for p in [
    PROCESSED_DATA_DIR, SAMPLE_DATA_DIR, METADATA_DIR,
    ARTIFACTS_DIR, VERSIONS_DIR,
    EXPERIMENTS_DIR, FIGURES_DIR, REPORTS_DIR,
    DATABASE_DIR
]:
    p.mkdir(parents=True, exist_ok=True)

# Methodology Core Features (Mandatory 4 inputs)
CORE_FEATURES = [
    "attendance_rate",
    "assignment_submission_frequency",
    "internal_test_score",
    "study_hours",
]

# Extended Feature Sets for Full Dataset Training
EXTENDED_NUMERIC_FEATURES = [
    "age",
    "Medu",
    "Fedu",
    "traveltime",
    "failures",
    "goout",
    "Dalc",
    "Walc",
    "health"
]

EXTENDED_CATEGORICAL_FEATURES = [
    "sex",
    "address",
    "famsize",
    "Pstatus",
    "schoolsup",
    "famsup",
    "activities",
    "internet",
    "romantic"
]

TARGET_COLUMN = "target_at_risk"

# Risk Tier Thresholds
HIGH_RISK_THRESHOLD = 0.66
MODERATE_RISK_THRESHOLD = 0.33

# Modeling & Reproducibility Parameters
RANDOM_STATE = 42
TEST_SIZE = 0.20
CV_FOLDS = 5

# Hyperparameter search grids (Bounded, CPU-optimized)
PARAM_GRIDS = {
    "Decision Tree": {
        "classifier__max_depth": [3, 5, 8],
        "classifier__min_samples_split": [2, 5],
        "classifier__criterion": ["gini", "entropy"]
    },
    "Support Vector Classifier": {
        "classifier__C": [0.1, 1.0, 10.0],
        "classifier__kernel": ["rbf", "linear"]
    },
    "Logistic Regression": {
        "classifier__C": [0.1, 1.0, 10.0],
        "classifier__solver": ["lbfgs"],
        "classifier__max_iter": [1000]
    },
    "Random Forest": {
        "classifier__n_estimators": [50, 100],
        "classifier__max_depth": [4, 8],
        "classifier__min_samples_split": [2, 5]
    }
}


# Default Deterministic Pedagogical Intervention Rules
DEFAULT_INTERVENTION_RULES = [
    {
        "feature": "attendance_rate",
        "threshold": 75.0,
        "direction": "below",
        "severity": "HIGH",
        "priority": 1,
        "action": "Mentor check-in and attendance improvement agreement.",
        "rationale": "Attendance below 75% significantly correlates with missed instructional content and heightened academic vulnerability."
    },
    {
        "feature": "internal_test_score",
        "threshold": 50.0,
        "direction": "below",
        "severity": "HIGH",
        "priority": 1,
        "action": "Remedial tutoring sessions and targeted concept practice.",
        "rationale": "Internal test performance below 50% indicates foundational curriculum comprehension gaps requiring immediate academic remediation."
    },
    {
        "feature": "assignment_submission_frequency",
        "threshold": 70.0,
        "direction": "below",
        "severity": "MEDIUM",
        "priority": 2,
        "action": "Assignment deadline alerts and faculty coursework follow-up.",
        "rationale": "Inconsistent submission patterns diminish formative practice opportunities and elevate risk of continuous evaluation penalties."
    },
    {
        "feature": "study_hours",
        "threshold": 2.5,
        "direction": "below",
        "severity": "MEDIUM",
        "priority": 3,
        "action": "Weekly study schedule planning and time-management workshop.",
        "rationale": "Independent study under 2.5 hours weekly is insufficient for consolidating technical course topics."
    }
]
