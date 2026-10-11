# Research Gap Matrix — 15-Paper Literature Grounding

This matrix grounds the prototype's design directly against the 15-paper literature review established in the research manuscript.

| Paper | Year | Method | Main Result | Identified Gap | Prototype Response | Implementation Status | Evidence | Remaining Limitation |
|---|---|---|---|---|---|---|---|---|
| Pan, J. et al. [1] | 2025 | Literature Survey | Benchmarked ML models | No consensus on best model | Four-model parallel pipeline with transparent CV selection | **FULLY ADDRESSED** | `src/train.py`, `app_pages/model_comparison.py` | Selected model may be dataset specific |
| Jha, M. K. et al. [2] | 2025 | XGNN-AP Framework | 99.71% Acc, F1: 1.00 | Deep models lack transparency | Integration of SHAP TreeExplainer/LinearExplainer/KernelExplainer | **FULLY ADDRESSED** | `src/explain.py`, `app_pages/explainability.py` | SHAP explains model behavior, not causality |
| Kalita, E. et al. [3] | 2025 | Time-Series DL | 88.23% Accuracy | High compute; opaque network | Pure scikit-learn pipeline (CPU deployable) | **FULLY ADDRESSED** | `requirements.txt`, CPU benchmark in `train.py` | Lower sequence awareness than recurrent deep networks |
| Angeioplastis, A. et al. [4] | 2025 | Classification | F1-Score > 0.80 | Ignores student dynamics | Longitudinal SQLite tracking of multi-period predictions | **PARTIALLY ADDRESSED** | `database/models.py`, `app_pages/analytics.py` | Evaluates discrete snapshots rather than continuous spatio-temporal graphs |
| Gonzales, W. et al. [5] | 2025 | Hybrid ML-DL | Superior sensitivity | Few models for basic school | UI abstraction removing programming requirements for educators | **FULLY ADDRESSED** | `app.py`, Streamlit framework | Requires institutional device access |
| Johora, F. T. & Hasan, M. N. [6] | 2025 | Voting Ensemble | 86.38% Accuracy | Black-box trust barrier | Plain-English explanations + SHAP attribution breakdown | **FULLY ADDRESSED** | `src/explain.py`, `app_pages/explainability.py` | Formal educator trust user study not yet conducted |
| Paul, R. et al. [7] | 2025 | Regression & ML | Forecasted 1st Sem GPA | Late at-risk detection | Early-semester indicators used (attendance, formative assessments) | **FULLY ADDRESSED** | `config/settings.py`, `src/schema.py` | Requires early recording of formative assignments |
| Lu, J. et al. [8] | 2024 | Survey & Stats | Motivation impacts GPA | Overlooked behavioral traits | Behavioral indicators mapped into feature schema and database | **FULLY ADDRESSED** | `database/models.py`, `src/schema.py` | Self-reported motivation exhibits subjective bias |
| Luo, Z. et al. [9] | 2024 | Spatio-Temporal | High trajectory precision | Static data over-reliance | Temporal multi-point auditing in SQLite | **PARTIALLY ADDRESSED** | `database/crud.py`, `app_pages/analytics.py` | Snapshot intervals depend on manual or periodic import |
| Pires, J. P. J. et al. [10] | 2024 | Supervised ML | Forecasted coding risk | Needs domain-tailored tool | Retrainable pipeline with dynamic feature configuration | **FULLY ADDRESSED** | `src/train.py`, `services/training_service.py` | Retraining required per specialized academic department |
| Akbar, S. [11] | 2024 | Rule Mining | Rule-based pathways | Lacks accessible pipeline | One-click browser-based training and inference pipeline | **FULLY ADDRESSED** | `app_pages/model_training.py` | Requires local or private server execution |
| Liu, Y. et al. [12] | 2023 | Log Mining | Linked logs to exam marks | Underutilized LMS logs | Generic CSV/schema ingestion supporting clickstream and activity | **PARTIALLY ADDRESSED** | `services/import_service.py`, `src/schema.py` | No live OAuth API to Canvas/Moodle implemented (Future) |
| Feng, G. & Fan, M. [13] | 2022 | Data Cleaning | Mitigated overfitting | Poor data curation/noise | Leakage-safe ColumnTransformer with in-fold SMOTE and scaling | **FULLY ADDRESSED** | `src/preprocessing.py`, `src/train.py`, `tests/test_leakage.py` | Severe systemic missingness cannot be entirely imputed |
| Zhang, Y. et al. [14] | 2021 | Comparative Analysis | Accuracy-compute trade-off | Hardware selection limits | Lightweight Python stack running entirely on commodity CPU | **FULLY ADDRESSED** | `requirements.txt`, `src/train.py` | In-memory training limits cohort scalability to ~100k rows |
| Alshanqiti, A. & Namoun, A. [15] | 2020 | Multi-Label Reg | Granular grade tiers | Binary pass/fail is coarse | Probabilistic thresholding into LOW, MODERATE, HIGH risk tiers | **FULLY ADDRESSED** | `src/target.py`, `src/risk.py`, `app_pages/predict_student.py` | Threshold calibration requires domain agreement |

---

### Grounding Summary
- **Fully Addressed (12 / 15)**: Gaps directly resolved through tested codebase components, models, and interfaces.
- **Partially Addressed (3 / 15)**: Gaps resolved at prototype architecture and database tracking levels (discrete snapshot persistence and CSV logging abstraction) without overclaiming real-time LMS cloud APIs or complex deep spatio-temporal neural networks.
- **Future Work**: Live OAuth LMS synchronization and clinical multi-semester intervention effectiveness studies.
