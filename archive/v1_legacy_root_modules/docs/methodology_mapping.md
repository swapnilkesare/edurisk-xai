# Methodology Mapping

This document maps the implementation back to the required five-phase methodology.

## Phase 1: Data Acquisition & Preprocessing
- **Implementation**: `ml/data_loader.py` fetches the UCIML dataset or generates synthetic data. `ml/preprocessing.py` uses `sklearn.compose.ColumnTransformer` to handle missing values, scale numeric variables, and encode categoricals.
- **Leakage Prevention**: Implemented via `imblearn.pipeline.Pipeline`, ensuring SMOTE only affects the training split during Cross-Validation.

## Phase 2: Predictive Modeling
- **Implementation**: `ml/train.py` tests four models: Decision Tree, Support Vector Classifier, Logistic Regression, and Random Forest.
- **Evaluation**: GridSearchCV with StratifiedKFold cross-validation optimizes hyperparameters based on Macro F1.

## Phase 3: Explainable AI
- **Implementation**: `ml/explain.py` uses `shap.TreeExplainer`, `shap.LinearExplainer`, or `shap.KernelExplainer` based on the selected model to derive local SHAP values for every prediction.

## Phase 4: Interactive Dashboard
- **Implementation**: `app.py` and the `app_pages/` directory provide an intuitive UI for educators to interact with models and predictions without needing python knowledge.

## Phase 5: Rule-Based Intervention Engine
- **Implementation**: `ml/intervention.py` reads active rules from the SQLite database (`database/models.py`) and maps SHAP risk-increasing factors to predefined pedagogical actions.
