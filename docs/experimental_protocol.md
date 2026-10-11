# Experimental Protocol & Evaluation Design

## 1. Experimental Objectives
The experimental protocol establishes a rigorous, leak-free benchmark comparing four lightweight supervised classifiers for early student academic risk identification, evaluating predictive accuracy, high-risk recall, explainability fidelity, and computational overhead.

---

## 2. Dataset Specification
- **Dataset**: UCI Student Performance Dataset (Cortez & Silva, 2008) — Portuguese Secondary Cohort with operational indicator alignment.
- **Sample Count**: 649 instances.
- **Feature Space**: 22 predictive attributes (4 core methodology features + 18 academic/demographic context features).
  - Core features: `attendance_rate`, `assignment_submission_frequency`, `internal_test_score`, `study_hours`.
- **Target Definition**: Binary target `target_at_risk` where $G3 < 10 \implies 1$ (At-Risk) and $G3 \ge 10 \implies 0$ (On-Track).
- **Target Distribution**: 549 On-Track (84.59%), 100 At-Risk (15.41%). Imbalance ratio: ~5.49 : 1.
- **Fingerprint**: SHA-256 hash `396e1d5d8ecf1bc5`.

---

## 3. Data-Leakage Safe Protocol
1. **Quarantine Partition**: The dataset is split stratified into **80% Training (519 instances)** and **20% Test (130 instances)** using random seed `42`.
2. **Untouched Test Set**: The 130-instance test set is quarantined immediately. It is never accessed during imputation fitting, scaler fitting, categorical vocabulary compilation, SMOTE resampling, or hyperparameter selection.
3. **In-Fold Preprocessing & Resampling**:
   - Packaged inside `imblearn.pipeline.Pipeline`.
   - Preprocessing (`SimpleImputer`, `StandardScaler`, `OneHotEncoder`) fits strictly on training folds.
   - `SMOTE` with dynamic neighbor adaptation ($k = \max(1, \min(3, \text{minority\_in\_fold} - 1))$) oversamples strictly within training folds.
   - Validation folds are never resampled.

---

## 4. Candidate Classifiers & Hyperparameter Spaces
All candidate classifiers run in 5-fold Stratified K-Fold Cross-Validation:

1. **Decision Tree (`DecisionTreeClassifier`)**
   - `criterion`: `['gini', 'entropy']`
   - `max_depth`: `[3, 5, 8]`
   - `min_samples_split`: `[2, 5]`
2. **Support Vector Classifier (`SVC(probability=True)`)**
   - `C`: `[0.1, 1.0, 10.0]`
   - `kernel`: `['rbf', 'linear']`
3. **Logistic Regression (`LogisticRegression(max_iter=1000)`)**
   - `C`: `[0.1, 1.0, 10.0]`
   - `solver`: `['lbfgs']`
4. **Random Forest (`RandomForestClassifier`)**
   - `n_estimators`: `[50, 100]`
   - `max_depth`: `[4, 8]`
   - `min_samples_split`: `[2, 5]`

---

## 5. Evaluation Metrics & Selection Criteria
- **Optimization Metric**: Cross-Validation **Macro F1** on training folds.
- **Safety Priority**: **High-Risk Recall** ($\frac{TP}{TP + FN}$) to minimize false negatives (unidentified struggling students).
- **Secondary Metrics**: Accuracy, Precision, Binary F1, Weighted F1, ROC-AUC, PR-AUC, Training Time (s), Inference Latency per sample (ms), Model Size on Disk (KB).
- **Parsimony Rule**: In case of a performance tie (within 0.015 CV Macro F1), prefer simpler model architectures.
