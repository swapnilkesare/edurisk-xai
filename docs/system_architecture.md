# System Architecture — EduRisk XAI

## 1. Architectural Overview
EduRisk XAI is architected as a modular, lightweight Python decision support prototype designed for consumer CPU deployment. The architecture enforces separation of concerns across data engineering, pipeline execution, explainability, deterministic pedagogical rule matching, relational persistence, and educator-facing interface.

```text
                                  +-----------------------+
                                  |   Raw Data Sources    |
                                  | (UCI CSV / Uploads)   |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  |   src/schema.py       |
                                  |  Validation & Bounds  |
                                  +-----------+-----------+
                                              |
                     +------------------------+------------------------+
                     |                                                 |
                     v                                                 v
        +-------------------------+                       +-------------------------+
        | Phase 1: Preprocessing  |                       | Phase 2: Model Training |
        |  ColumnTransformer      |                       | StratifiedKFold (k=5)   |
        |  (Impute, Scale, Enc)   |                       | In-Fold SMOTE Pipeline  |
        +------------+------------+                       | GridSearchCV Tuning     |
                     |                                    +------------+------------+
                     +------------------------+------------------------+
                                              |
                                              v
                                  +-----------------------+
                                  |  Model Selection      |
                                  |  CV Macro F1 + Recall |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  | Models & Artifacts    |
                                  | best_model.pkl        |
                                  | model_metadata.json   |
                                  +-----------+-----------+
                                              |
                     +------------------------+------------------------+
                     |                                                 |
                     v                                                 v
        +-------------------------+                       +-------------------------+
        | Phase 3: Explainability |                       | Phase 5: Interventions  |
        | SHAP Explainer Engine   |                       | Deterministic Rule Eng  |
        | (Tree/Linear/Kernel)    |                       | (Threshold & Priority)  |
        +------------+------------+                       +------------+------------+
                     |                                                 |
                     +------------------------+------------------------+
                                              |
                                              v
                                  +-----------------------+
                                  |  Database (SQLite)    |
                                  |  Students, Audits     |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  | Phase 4: Streamlit UI |
                                  | 9 Specialized Pages   |
                                  +-----------------------+
```

---

## 2. Component Specifications

### 2.1 Core Modules (`src/`)
- `schema.py`: Validates tabular schema against standard core boundaries (`attendance_rate`, `study_hours`, `internal_test_score`, `assignment_submission_frequency`), detects invalid types, checks missingness, and ensures binary target formatting.
- `data_loader.py`: Ingests dataset, calculates SHA-256 fingerprint, tags provenance (`REAL_PUBLIC`, `USER_UPLOADED`, `SYNTHETIC_DEMO`), and generates controlled synthetic demonstration cohorts.
- `target.py`: Constructs binary academic risk label ($G3 < 10$), maps predicted probabilities into operational tiers (`LOW`, `MODERATE`, `HIGH`), and validates target leakage safety.
- `preprocessing.py`: Builds leakage-safe `ColumnTransformer` applying median numerical imputation, standard scaling, and one-hot encoding while tracking output feature names.
- `train.py`: Executes 4-model stratified cross-validation with in-fold SMOTE resampling and bounded hyperparameter grid search.
- `evaluate.py`: Calculates multi-dimensional performance metrics (Accuracy, Precision, Recall, Macro F1, High-Risk Recall, False Negatives, ROC-AUC, latency, and memory footprint).
- `model_selection.py`: Selects best model based purely on CV Macro F1 and high-risk recall on training data; the holdout test set is never accessed during selection.
- `predict.py`: Single-student inference interface aligning feature inputs and translating probabilities to risk tiers.
- `explain.py`: Model-appropriate SHAP engine (`TreeExplainer`, `LinearExplainer`, `KernelExplainer`) computing additive local contributions and global importance.
- `intervention.py`: Pure rule-based pedagogical engine translating risk factors and SHAP evidence into prioritized educational support actions.

### 2.2 Service Layer (`services/`)
- `training_service.py`: Orchestrates end-to-end multi-model training runs, artifact persistence, and SQLite logging.
- `prediction_service.py`: Coordinates live student risk prediction, SHAP explanation generation, intervention rule matching, and database auditing.
- `import_service.py`: Processes and audits CSV file uploads for structure, schema compliance, and target leakage.
- `report_service.py`: Generates publication-ready figures and structured Markdown reports from actual experiment executions.

### 2.3 Persistence Layer (`database/`)
- SQLite storage via SQLAlchemy ORM (`edurisk.db`).
- Entities: `Student`, `AcademicRecord`, `BehaviorRecord`, `Prediction`, `SHAPExplanation`, `Intervention`, `InterventionRule`, `ModelRun`, `DatasetImport`.
- Supports longitudinal student tracking across multi-period assessments.
