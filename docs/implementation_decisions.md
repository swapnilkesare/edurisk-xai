# Implementation Decisions & Methodological Resolutions

## Overview
This document records key architectural, data-engineering, modeling, and explainability decisions for **EduRisk XAI**, ensuring complete transparency and research integrity.

---

### Decision 1: Dataset Provenance & Feature Schema Alignment
- **Context**: The research methodology defines four core operational indicators:
  1. `attendance_rate` (%)
  2. `assignment_submission_frequency` (%)
  3. `internal_test_score` (%)
  4. `study_hours` (hrs/week)
  The UCI Machine Learning Repository Student Performance dataset (Portuguese secondary school, Cortez & Silva, 2008; 649 records) naturally records `absences`, `studytime`, `G1`, and `G2`.
- **Resolution**:
  - The dataset standardizes `absences` into `attendance_rate = max(0, 100 - (absences / 93 * 100))` where 93 was the maximum recorded absence in the cohort.
  - `studytime` (categorical 1-4) is mapped to estimated hours per week (`1.0, 3.5, 7.5, 10.0`).
  - `internal_test_score` is computed from the continuous midterm assessments `(G1 + G2) / 40 * 100`.
  - `assignment_submission_frequency` is incorporated as an educational proxy variable representing assignment completion rate.
  - **Integrity Statement**: This dataset is transparently disclosed as an augmented derivative of the UCI Portuguese cohort. When synthetic demonstration data is generated, it is explicitly flagged with `[SYNTHETIC / DEMO DATA]`.

---

### Decision 2: Target Variable Definition & Leakage Prevention
- **Context**: Academic risk prediction requires an independent target label without circular leakage from the feature set.
- **Resolution**:
  - In Portuguese secondary education, the passing mark is 10 out of 20 points.
  - The binary target `target_at_risk` is defined as:
    - `1` (At-Risk) if final period grade $G3 < 10$.
    - `0` (Low-Risk / On-Track) if $G3 \ge 10$.
  - In the 649-student cohort, 100 students (15.41%) are classified as at-risk, yielding a realistic imbalanced distribution.
  - The target $G3$ is strictly excluded from all model input features to eliminate target leakage.

---

### Decision 3: Risk-Tier Mapping from Predicted Probabilities
- **Context**: Binary 0/1 labels are too coarse for proactive educational advising.
- **Resolution**:
  - Models output continuous predicted risk probability $P(\text{Risk} = 1)$.
  - Probabilities are mapped into three actionable risk tiers:
    - **HIGH RISK**: $P \ge 0.66$ (Requires urgent advisor intervention)
    - **MODERATE RISK**: $0.33 \le P < 0.66$ (Requires proactive monitoring and targeted tutoring)
    - **LOW RISK**: $P < 0.33$ (On track, standard academic progression)
  - Disclosed limitation: These thresholds represent configurable operational defaults that require empirical calibration in production deployments.

---

### Decision 4: Data-Leakage Safe Resampling (SMOTE) Pipeline
- **Context**: Applying SMOTE or preprocessing before cross-validation or train/test splitting leaks validation distribution into training data, generating falsely inflated performance metrics.
- **Resolution**:
  - The raw dataset is partitioned into an 80% training set and a 20% holdout test set using stratified sampling (`random_state=42`).
  - Preprocessing (`ColumnTransformer` with imputation, scaling, and one-hot encoding) and resampling (`SMOTE`) are bundled inside an `imblearn.pipeline.Pipeline`.
  - During 5-fold `StratifiedKFold` cross-validation, SMOTE and transformer parameters are fitted **strictly on the 4 training folds** and evaluated on the untouched validation fold.
  - The 20% holdout test set remains completely untouched until final evaluation of the selected model.

---

### Decision 5: Candidate Classifiers & Hyperparameter Search
- **Context**: The research methodology requires four lightweight classifiers.
- **Resolution**:
  1. `DecisionTreeClassifier` (Highly interpretable white-box)
  2. `SVC` with `probability=True` (Effective margin separator for non-linear boundaries)
  3. `LogisticRegression` (Linear baseline with direct odds interpretation)
  4. `RandomForestClassifier` (Ensemble bagging for robust variance reduction)
  - Hyperparameter grids are bounded and optimized for standard CPU execution.
  - Model selection is governed by **Macro F1** and **High-Risk Recall** on training cross-validation, ensuring the model prioritizes identifying vulnerable students over merely maximizing raw accuracy.

---

### Decision 6: Explainability (SHAP) Strategy
- **Context**: Educators require transparent explanations for individual predictions and global cohort trends without misleading causal claims.
- **Resolution**:
  - `TreeExplainer` is used for tree-based models (Decision Tree, Random Forest).
  - `LinearExplainer` is used for Logistic Regression.
  - `KernelExplainer` with k-means background sampling is used for SVC.
  - For each prediction, SHAP values are extracted, aligned with feature names, and categorized into **Risk-Increasing Factors** ($\phi_i > 0$) and **Protective Factors** ($\phi_i < 0$).
  - Additive consistency is verified: $\sum \phi_i + \text{base\_value} \approx \text{model\_output}$.
  - The UI presents plain-language translations while retaining technical charts.
  - Explicit disclaimer: SHAP explains model output attribution, not causal etiology.

---

### Decision 7: Pure Deterministic Intervention Engine
- **Context**: Interventions must be predictable, transparent, and pedagogically justifiable without opaque secondary models.
- **Resolution**:
  - A deterministic rule engine evaluates the student's metrics and risk-increasing SHAP factors against customizable rule thresholds stored in SQLite.
  - Generates ranked recommendations with explicit pedagogical rationale.
  - Teachers can review, edit rules, and update intervention status (`Pending`, `In Progress`, `Completed`, `Dismissed`).
