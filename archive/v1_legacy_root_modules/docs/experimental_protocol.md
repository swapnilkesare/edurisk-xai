# Experimental Protocol

## Dataset Source
The system utilizes the **UCI Student Performance Dataset** (ID: 320) representing secondary education outcomes.

## Feature Engineering & Preprocessing
- Features used: `attendance_rate` (derived from absences), `study_hours` (mapped from categorical studytime), `internal_test_score` (average of G1/G2), and `assignment_submission_frequency` (synthetically correlated to study and test indicators due to absence in raw UCI data).
- Missing values are imputed (median for continuous, mode for categorical).
- Categorical features are one-hot encoded, and continuous features are scaled using `StandardScaler`.

## Train/Test Partition & Class Imbalance
- An 80/20 train/test split is enforced.
- **Leakage Prevention**: The `SMOTE` oversampling technique is applied *only* to the training partition via `imblearn.pipeline.Pipeline`, preserving the integrity of the test set and CV validation folds.

## Cross-Validation Strategy
- Stratified k-fold cross-validation is used (folds determined dynamically based on minority class size).
- GridSearchCV optimizes hyperparameters using the **Macro F1** scoring metric.

## Model Selection
Four classical algorithms are evaluated:
1. Decision Tree
2. Support Vector Classifier (SVC)
3. Logistic Regression
4. Random Forest

Selection criteria heavily weight **High-Risk Recall** alongside Macro F1 and Accuracy, while incorporating a tie-breaking penalty for less interpretable models (e.g. SVC).

## Reproducibility
- Random seed is fixed (42).
- Model artifacts store hyperparameters, dataset schema, and version timestamps.
