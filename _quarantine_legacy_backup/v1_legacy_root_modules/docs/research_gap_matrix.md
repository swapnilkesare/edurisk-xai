# Research Gap Matrix

| Paper | Year | Method | Main Result | Identified Gap | Prototype Response | Implementation Status | Evidence | Remaining Limitation |
|---|---|---|---|---|---|---|---|---|
| Pan, J. et al. [1] | 2025 | Literature Survey | Benchmarked ML models | No consensus on best model | Four-model parallel pipeline with transparent CV selection | FULLY ADDRESSED | `ml/train.py`, Model Training UI | Selected model may be dataset specific |
| Jha, M. K. et al. [2] | 2025 | XGNN-AP Framework | 99.71% Acc, F1: 1.00 | Deep models lack transparency | Integration of SHAP TreeExplainer/KernelExplainer | FULLY ADDRESSED | `ml/explain.py`, Explainability UI | None |
| Kalita, E. et al. [3] | 2025 | Time-Series DL | 88.23% Accuracy | High compute; opaque network | Pure scikit-learn pipeline (CPU deployable) | FULLY ADDRESSED | `requirements.txt`, CPU testing | Lower sequence awareness than LSTM |
| Angeioplastis, A. et al. [4] | 2025 | Classification | F1-Score > 0.80 | Ignores student dynamics | Longitudinal SQLite tracking of predictions | PARTIALLY ADDRESSED | `database/models.py`, Students UI | Not a true spatio-temporal deep model |
| Gonzales, W. et al. [5] | 2025 | Hybrid ML-DL | Superior sensitivity | Few models for basic school | UI abstraction removing coding requirements for teachers | FULLY ADDRESSED | `app.py`, Streamlit framework | None |
| Johora, F. T. & Hasan, M. N. [6] | 2025 | Voting Ensemble | 86.38% Accuracy | Black-box trust barrier | Plain-English explanations + SHAP UI | FULLY ADDRESSED | `app_pages/explainability.py` | None |
| Paul, R. et al. [7] | 2025 | Regression & ML | Forecasted 1st Sem GPA | Late at-risk detection | Early-semester indicators used (attendance, assignments) | FULLY ADDRESSED | `ml/data_loader.py` | Limited to available early metrics |
| Lu, J. et al. [8] | 2024 | Survey & Stats | Motivation impacts GPA | Overlooked behavioral traits | Behavioral feature mapping supported | FULLY ADDRESSED | `config/settings.py` CORE_FEATURES | Real behavioral data depends on institution |
| Luo, Z. et al. [9] | 2024 | Spatio-Temporal | High trajectory precision | Static data over-reliance | SQLite persistence of temporal snapshots | PARTIALLY ADDRESSED | `database/crud.py` | Requires manual or periodic API trigger |
| Pires, J. P. J. et al. [10] | 2024 | Supervised ML | Forecasted coding risk | Needs domain-tailored tool | Retrainable pipeline with feature expansion | FULLY ADDRESSED | `ml/train.py` dynamic feature handling | Retraining required per domain |
| Akbar, S. [11] | 2024 | Rule Mining | Rule-based pathways | Lacks accessible pipeline | One-click Streamlit training interface | FULLY ADDRESSED | `app_pages/model_training.py` | None |
| Liu, Y. et al. [12] | 2023 | Log Mining | Linked logs to exam marks | Underutilized LMS logs | Generic DataSource abstraction + CSV Import | PARTIALLY ADDRESSED | `datasources/csv_source.py`, Data Import UI | No live API connection to Canvas/Moodle implemented |
| Feng, G. & Fan, M. [13] | 2022 | Data Cleaning | Mitigated overfitting | Poor data curation/noise | Robust pipeline with scaling, imputation, and leakage-safe SMOTE | FULLY ADDRESSED | `ml/preprocessing.py`, `ml/train.py` | High missingness cannot be perfectly fixed |
| Zhang, Y. et al. [14] | 2021 | Comparative Analysis | Accuracy-compute trade-off | Hardware selection limits | Python 3.10 standard stack; runs on consumer CPU | FULLY ADDRESSED | Entire project footprint | CPU limits dataset scaling to ~100k rows |
| Alshanqiti, A. & Namoun, A. [15] | 2020 | Multi-Label Reg | Granular grade tiers | Binary pass/fail is coarse | Probabilistic thresholding into LOW, MODERATE, HIGH | FULLY ADDRESSED | `services/prediction_service.py` | Threshold calibration depends on institution |
