# EduRisk XAI — Research-Grade Student Academic Risk Prediction, Explainability, and Intervention Framework

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-1.40+-red.svg)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)]()
[![Platform](https://img.shields.io/badge/Platform-Consumer%20CPU-orange.svg)]()
[![Explainability](https://img.shields.io/badge/XAI-SHAP%20Integrated-purple.svg)](https://shap.readthedocs.io/)

> **An Interpretable, SHAP-Driven Lightweight Framework for Transparent Student Risk Assessment and Pedagogical Intervention**

---

## 📌 Executive Summary

**EduRisk XAI** is an executable, reproducible, modular research platform built from scratch to address recurring limitations identified across 15 literature studies in educational machine learning. 

It provides an end-to-end, five-phase workflow that bridges early predictive warning, model-faithful **SHAP (SHapley Additive exPlanations)** attribution, and deterministic **rule-based pedagogical interventions** without requiring cloud dependencies, proprietary APIs, or specialized GPU hardware.

---

## 🔬 Core Capabilities & Five-Phase Methodology

```
┌─────────────────┐     ┌───────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Phase 1     │     │      Phase 2      │     │     Phase 3     │     │     Phase 4     │     │     Phase 5     │
│  Data Ingestion │ ──> │ Predictive Models │ ──> │   SHAP (XAI)    │ ──> │ Multi-Role UI   │ ──> │  Deterministic  │
│  & In-Fold SMOTE│     │  & Model Selection│     │ Local & Global  │     │  & PRN Registry │     │  Interventions  │
└─────────────────┘     └───────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

1. **Phase 1: Data Acquisition & Preprocessing**
   - Supports 4 core operational indicators: `attendance_rate`, `assignment_submission_frequency`, `internal_test_score`, and `study_hours`.
   - Strict leakage prevention: 80% train / 20% test split performed before any transformation.
   - Resampling (`SMOTE`) is applied **strictly inside training folds** during cross-validation to prevent optimistic evaluation bias.
2. **Phase 2: Predictive Modelling & Parsimonious Selection**
   - Implements four candidate classifiers: **Random Forest**, **Decision Tree**, **Support Vector Classifier (SVC)**, and **Logistic Regression**.
   - Hyperparameters tuned using 5-fold `StratifiedKFold` and bounded `GridSearchCV`.
   - Transparent selection policy based on Cross-Validation Macro F1, High-Risk Recall, and computational parsimony.
3. **Phase 3: Explainable AI (SHAP)**
   - Integrates model-appropriate SHAP explainers (`TreeExplainer`, `LinearExplainer`, `KernelExplainer`).
   - Decomposes predictions into **Risk-Increasing Factors** ($\phi > 0$) and **Protective Factors** ($\phi < 0$).
   - Generates both technical waterfall/bar attributions and plain-language educator explanations.
4. **Phase 4: Interactive Web Platform & PRN Registry**
   - Modular Streamlit application with role-based access control (RBAC) and NIST PBKDF2-SHA256 authentication.
   - Permanent Roll Number (PRN) student registry with idempotent profiling and longitudinal tracking.
   - Accompanying standalone responsive HTML5/CSS3 prototype (`ui_prototype_white/`).
5. **Phase 5: Pedagogical Intervention Engine**
   - Deterministic rule-based engine linking verified risk factors to targeted pedagogical actions (e.g., peer mentoring, faculty office hours, tailored study schedules).
   - Editable rule criteria and SQLite lifecycle tracking (`Pending`, `In Progress`, `Completed`, `Dismissed`).

---

## 📊 Empirical Benchmark Results (Holdout Test Set)

Results from formal experimental execution (`exp_1791693461_a5bae9`) on the 649-student UCI cohort (130 test instances, 20 high-risk):

| Classifier | CV Macro F1 (Train) | Test Macro F1 | Test Accuracy | High-Risk Recall | False Negatives | ROC-AUC | Training Time | Latency / Sample |
|---|---|---|---|---|---|---|---|---|
| **Random Forest** (Selected) | **0.8787** | 0.8077 | 87.69% | **90.00%** | 2 | 0.9236 | 8.82s | 18.98ms |
| **Decision Tree** | 0.8522 | 0.8077 | 87.69% | **90.00%** | 2 | 0.9255 | 3.19s | 9.15ms |
| **Logistic Regression** | 0.8376 | **0.8467** | **90.77%** | **90.00%** | 2 | 0.9382 | **1.03s** | 9.21ms |
| **Support Vector (SVC)** | 0.8256 | 0.8365 | 90.00% | **90.00%** | 2 | **0.9459** | 4.49s | **8.90ms** |

*All 4 models successfully identified 18 of 20 at-risk students (90.00% Recall), demonstrating high safety for proactive academic intervention.*

---

## 🔑 Role-Based Access Control & Demo Accounts

EduRisk incorporates multi-tenant institutional scoping and role-based access control. Pre-configured demo accounts are available out of the box:

| Role | Username | Password | Organization / Scope | Permissions |
| :--- | :--- | :--- | :--- | :--- |
| **🔬 Lead AI Researcher** | `researcher` | `Research@123` | Global Research System | Full global cohort access, training pipeline, model diagnostics & system settings |
| **🏫 Institutional Admin** | `orgadmin` | `OrgAdmin@123` | Horizon High School | Educator dashboard, student PRN registry & institution user management |
| **🧑‍🏫 Educator (Horizon)** | `teacher1` | `Teacher@123` | Horizon High School | Student risk prediction, SHAP explanations & interventions for Horizon students |
| **🧑‍🏫 Educator (Apex)** | `teacher2` | `Teacher@123` | Apex Academy | Student risk prediction, SHAP explanations & interventions for Apex students |

*(Quick-login presets are also available directly on the login screen).*

---

## 📂 Project Directory Structure

```text
edurisk-xai/
├── app.py                      # Main Streamlit web application & router
├── train_experiment.py         # Standalone CLI training and figure generator
├── requirements.txt            # Pinned CPU-compatible Python dependencies
├── README.md                   # Project overview and technical documentation
├── .env.example                # Configurable environment variables template
├── .gitignore                  # Git exclusions (caches, virtual environments, local DBs)
├── app_pages/                  # Modular Streamlit views
│   ├── dashboard.py            # Overview metrics, alerts, and quick actions
│   ├── data_import.py          # Data ingestion, schema validation, synthetic data generator
│   ├── model_training.py       # Multi-model training, in-fold SMOTE, hyperparameter grid search
│   ├── model_comparison.py     # Cross-validation & test benchmarks, ROC curves, confusion matrices
│   ├── predict_student.py      # Single-student risk inference & real-time assessment
│   ├── explainability.py       # Local and global SHAP attributions, waterfall & summary plots
│   ├── interventions.py        # Pedagogical intervention engine and rule editor
│   ├── analytics.py            # Cohort analytics, distribution charts, longitudinal trajectories
│   ├── reports.py              # Publication figures and automated markdown report exports
│   ├── students.py             # Permanent Roll Number (PRN) student registry & placement editor
│   └── research_traceability.py# 15-paper literature gap review and mapping matrix
├── archive/                    # Historical snapshots and legacy refactoring archives
│   ├── README.md               # Description of archived prototypes
│   ├── pre_simplification_backup/
│   ├── v1_legacy_root_modules/
│   └── v2_phase2_prototype/
├── config/                     # Settings and styling
│   ├── settings.py             # Feature definitions, paths, hyperparameter grids, thresholds
│   └── theme.py                # Accessible UI design tokens and custom CSS injectors
├── data/                       # Datasets and catalog metadata
│   ├── raw/                    # Base benchmark dataset (student_data.csv)
│   ├── processed/              # Ingested and validated datasets
│   ├── sample/                 # Demonstration subsets
│   └── metadata/               # Data catalogs and hashes
├── database/                   # Persistence layer
│   ├── database.py             # SQLite engine and session factory
│   ├── models.py               # SQLAlchemy ORM entities (Users, Orgs, Students, Predictions, Rules)
│   ├── crud.py                 # Multi-tenant transactional operations
│   ├── migrate_prn.py          # Database migration script for permanent roll numbers
│   └── edurisk.db              # Local SQLite database
├── docs/                       # Research documentation
│   ├── manuscript/             # Original research papers, PDFs, and audit figures
│   │   ├── README.md           # Catalog of research publications
│   │   ├── SY AIDS_AI MANUSCRIPT_24.pdf
│   │   ├── SY AIDS_AI_Methodology_24.pdf
│   │   ├── random_forest_results_audit.md
│   │   └── random_forest_confusion_matrix_corrected.png
│   ├── system_architecture.md  # Architectural layout and data flow
│   ├── methodology_mapping.md  # Direct mapping to 5-phase research methodology
│   ├── research_gap_matrix.md  # 15-paper literature gap review and groundings
│   ├── experimental_protocol.md# Protocols, splits, grids, and metrics
│   ├── model_results.md        # Actual generated experimental evidence
│   ├── limitations.md          # Methodological and ethical limitations
│   └── reproducibility.md      # Exact commands to install, test, and run
├── models/                     # Trained models and versioning
│   ├── artifacts/              # Active best_model.pkl and metadata
│   └── versions/               # Timestamped historical model pipelines
├── results/                    # Experimental outputs
│   ├── experiments/            # Machine-readable JSON and CSV run logs
│   ├── figures/                # Publication-quality evaluation plots
│   └── reports/                # Formatted markdown experimental summaries
├── services/                   # Application service layer
│   ├── auth_service.py         # NIST PBKDF2-SHA256 hashing, RBAC, session audits
│   ├── training_service.py     # Training orchestration and persistence
│   ├── prediction_service.py   # Live prediction and SHAP XAI pipeline
│   ├── import_service.py       # CSV upload validation and audit
│   └── report_service.py       # Publication figure and report generation
├── src/                        # Core algorithmic package
│   ├── schema.py               # Dataset validation and boundary rules
│   ├── data_loader.py          # Data ingestion and synthetic generator
│   ├── preprocessing.py        # Leak-free ColumnTransformer pipeline
│   ├── target.py               # Risk target construction and tier mapping
│   ├── train.py                # 4-model GridSearch CV with in-fold SMOTE
│   ├── evaluate.py             # Rigorous multi-metric evaluation suite
│   ├── model_selection.py      # CV-based model selection and parsimony rule
│   ├── predict.py              # Single-student inference interface
│   ├── explain.py              # Local and global SHAP explainability engine
│   ├── risk.py                 # Risk tier categorization (LOW, MODERATE, HIGH)
│   └── intervention.py         # Deterministic pedagogical intervention engine
├── tests/                      # Automated test suite
│   ├── test_data.py            # Dataset loading and schema checks
│   ├── test_preprocessing.py   # Preprocessing transformations and naming
│   ├── test_target.py          # Target construction and tier boundaries
│   ├── test_leakage.py         # Leakage safeguards and SMOTE isolation
│   ├── test_training.py        # 4-model training and selection logic
│   ├── test_prediction.py      # Inference output schema and risk tiers
│   ├── test_shap.py            # Local/global SHAP and additive consistency
│   ├── test_intervention.py    # Rule matching and priority ranking
│   ├── test_database.py        # SQLAlchemy ORM transactions and SQLite
│   ├── test_prn_registration.py# PRN registration, idempotency, and institutional scoping
│   └── test_end_to_end.py      # Full integration pipeline and UI smoke test
└── ui_prototype_white/         # Standalone HTML5/CSS3/Vanilla JS UI prototype
    ├── README.md               # Prototype overview and styling guide
    ├── index.html              # Single-page interface
    ├── styles.css              # Light accessible design system
    ├── main.js                 # Interactive router and state manager
    ├── animations.js           # Anime.js micro-interactions
    └── vendor/anime.min.js     # Bundled offline animation library
```

---

## ⚡ Quickstart Guide

### 1. Prerequisites & Environment Setup
Ensure Python 3.10+ is installed:
```bash
git clone https://github.com/swapnilkesare/edurisk-xai.git
cd edurisk-xai
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Test Suite
Validate data leakage prevention, SMOTE isolation, PRN registration, and pipeline integrity:
```bash
python -m pytest tests -v
```
*(All unit and integration tests execute and pass in seconds).*

### 3. Run Standalone Training Experiment (Optional)
To train all 4 classifiers with in-fold SMOTE, execute hyperparameter grid search, and generate publication figures:
```bash
python train_experiment.py
```

### 4. Launch the Web Application
Start the primary Streamlit platform:
```bash
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser and log in with any demo account (e.g. `teacher1` / `Teacher@123` or `researcher` / `Research@123`).

### 5. Launch the Standalone White UI Prototype (Optional)
To preview the lightweight client-side HTML5/CSS3 prototype:
```bash
# Serve the prototype directory with Python's built-in HTTP server:
cd ui_prototype_white
python -m http.server 3000
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

---

## ⚖️ Research Integrity & Ethical Statement

- **Non-Causality Principle**: SHAP values quantify feature contributions to the mathematical model's score; they do not establish direct sociological or psychological causality for academic struggles.
- **Support, Not Punishment**: Risk tiers provide proactive decision support for academic advisors and tutors. The system must never be used for punitive disciplinary actions or exclusionary tracking.
- **Human Oversight**: Automated suggestions require professional review by qualified educators prior to enacting interventions.
- **Privacy & Security**: Passwords are protected using NIST-compliant PBKDF2-HMAC-SHA256 (200,000 iterations). Student records are multi-tenant isolated by organization.

---


