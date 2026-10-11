# Methodology Mapping — Five-Phase Research Workflow

This document traces the implementation of EduRisk XAI directly to the five-phase educational machine-learning research methodology.

---

## Phase 1: Data Acquisition & Preprocessing
- **Source Modules**: `src/data_loader.py`, `src/schema.py`, `src/preprocessing.py`, `src/target.py`
- **Methodology Requirements**:
  1. Acquire documented educational dataset with clear provenance.
  2. Implement the four core indicators: `attendance_rate`, `assignment_submission_frequency`, `internal_test_score`, `study_hours`.
  3. Validate missing values, outliers, and class imbalance.
  4. Isolate train/test partitions (80/20) before applying any learned preprocessing.
  5. Apply SMOTE exclusively inside training folds during cross-validation.
- **Implementation Status**: **FULLY ADDRESSED**
- **Test Evidence**:
  - `tests/test_data.py` (Schema bounds, type checks, provenance tracking)
  - `tests/test_preprocessing.py` (Imputation, scaling, feature preservation)
  - `tests/test_leakage.py` (Proof that SMOTE does not contaminate test sets)
- **Remaining Limitation**: The public UCI dataset required feature derivation/augmentation for `assignment_submission_frequency`.

---

## Phase 2: Predictive Modelling
- **Source Modules**: `src/train.py`, `src/evaluate.py`, `src/model_selection.py`, `services/training_service.py`
- **Methodology Requirements**:
  1. Train four candidate classifiers: Decision Tree, Support Vector Classifier, Logistic Regression, Random Forest.
  2. Optimize hyperparameters using Stratified 5-Fold Cross-Validation.
  3. Formulate transparent model selection policy prioritizing Macro F1 and High-Risk Recall on CV evidence alone.
  4. Quarantined holdout test evaluation (20%) reported post-selection.
- **Implementation Status**: **FULLY ADDRESSED**
- **Test Evidence**:
  - `tests/test_training.py` (All 4 models successfully trained and evaluated; selection policy verified)
- **Remaining Limitation**: Standard CPU grid searches are bounded to maintain demonstration responsiveness.

---

## Phase 3: Explainable AI (XAI)
- **Source Modules**: `src/explain.py`, `services/prediction_service.py`, `app_pages/explainability.py`
- **Methodology Requirements**:
  1. Integrate Shapley Additive Explanations (SHAP) directly into inference pipeline.
  2. Model-appropriate explainers: `TreeExplainer` for trees, `LinearExplainer` for logistic regression, `KernelExplainer` for SVC.
  3. Decompose attributions into risk-increasing ($\phi > 0$) and protective ($\phi < 0$) factors.
  4. Ensure local additive consistency between expected base value, attributions, and model output.
  5. Generate plain-language educator translations alongside technical summaries.
- **Implementation Status**: **FULLY ADDRESSED**
- **Test Evidence**:
  - `tests/test_shap.py` (Local explanation structure, feature alignment, global importance)
- **Remaining Limitation**: SHAP describes feature attributions to model scores; it does not prove causal etiology.

---

## Phase 4: Interactive Dashboard
- **Source Modules**: `app.py`, `app_pages/*` (9 dedicated educator modules)
- **Methodology Requirements**:
  1. Browser-based Streamlit interface requiring zero programming expertise from teachers.
  2. Integrated workflows: Data Management, Model Training, Model Comparison, Student Prediction, Explainability, Interventions, Cohort Analytics, and Research Traceability.
  3. Active operational controls on all buttons (no fake or placeholder actions).
- **Implementation Status**: **FULLY ADDRESSED**
- **Test Evidence**:
  - `tests/test_end_to_end.py::test_streamlit_pages_import_smoke` (All page modules compile and import cleanly)
- **Remaining Limitation**: Single-institution local deployment; does not include enterprise role-based authorization.

---

## Phase 5: Pedagogical Intervention Engine
- **Source Modules**: `src/intervention.py`, `database/crud.py`, `app_pages/interventions.py`
- **Methodology Requirements**:
  1. Pure deterministic, rule-based recommendation logic (no secondary opaque ML models).
  2. Map verified SHAP risk factors to pedagogical actions (tutoring, attendance plans, study schedules).
  3. Rank interventions by urgency and severity.
  4. Provide teacher-editable rule management and status tracking (`Pending`, `In Progress`, `Completed`, `Dismissed`).
  5. Prominently include human-in-the-loop professional educator judgement disclaimers.
- **Implementation Status**: **FULLY ADDRESSED**
- **Test Evidence**:
  - `tests/test_intervention.py` (Rule triggering, priority sorting, threshold compliance)
  - `tests/test_database.py` (Status updates and audit logging in SQLite)
- **Remaining Limitation**: Pedagogical effectiveness has not been validated through longitudinal multi-semester clinical trial.
