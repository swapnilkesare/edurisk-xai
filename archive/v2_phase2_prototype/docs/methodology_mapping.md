# Methodology Mapping

This document maps the implementation back to the required five-phase methodology defined in the manuscript.

## Phase 1: Data Acquisition & Preprocessing
- **Phase 2 Prototype**: 
  - `src/data_loader.py`: Fetches real UCIML dataset or falls back to "DEMO" synthetic data if offline. Maps raw data down to 4 highly-interpretable, teacher-friendly variables (`attendance_rate`, `study_hours`, `internal_test_score`, `assignment_submission_frequency`).
  - `src/preprocessing.py`: Imputes missing values and scales numerics.
- **Status**: IMPLEMENTED IN PHASE 2

## Phase 2: Predictive Modeling
- **Phase 2 Prototype**: 
  - `src/train.py`: Trains Decision Tree, SVC, Logistic Regression, and Random Forest using `StratifiedKFold`.
  - Implements an `imblearn.pipeline.Pipeline` with `SMOTE` strictly inside the cross-validation folds to mathematically prevent data leakage.
- **Status**: IMPLEMENTED IN PHASE 2

## Phase 3: Explainable AI / SHAP Layer
- **Phase 2 Prototype**: 
  - `src/explain.py`: Automatically generates model-specific SHAP explanations (e.g. `TreeExplainer` for Random Forest).
  - Translates abstract SHAP mathematics into "Increased predicted risk" vs "Reduced predicted risk" arrows.
- **Status**: IMPLEMENTED IN PHASE 2

## Phase 4: Interactive Web Dashboard
- **Phase 2 Prototype**: 
  - `app.py`: Contains a single-page Streamlit application with intuitive tabs for Teacher demonstration, without complex databases or logins.
- **Status**: IMPLEMENTED IN PHASE 2

## Phase 5: Rule-Based Intervention Engine
- **Phase 2 Prototype**: 
  - `src/intervention.py`: A lightweight, hard-coded rule engine mapping SHAP outputs directly to pedagogical recommendations.
- **Status**: IMPLEMENTED IN PHASE 2

---

## Planned for Final System
While Phase 2 successfully demonstrates the core mechanics, the **final production system** will extend this with:
- Full persistent relational database (SQLite/PostgreSQL) tracking longitudinal changes across semesters.
- Multi-user authentication for faculty and administrative roles.
- CSV/LMS bulk data ingestion.
- Editable intervention logic stored dynamically in a database rather than hardcoded logic.
- Cohort-level advanced analytics and tracking tables.
