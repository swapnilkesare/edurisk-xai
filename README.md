# EduRisk XAI — Research-Grade Student Academic Risk Prediction, Explainability, and Intervention Framework

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-25%20Passing-brightgreen.svg)]()
[![Platform](https://img.shields.io/badge/Platform-Consumer%20CPU-orange.svg)]()

> **An Interpretable, SHAP-Driven Lightweight Framework for Transparent Student Risk Assessment and Pedagogical Intervention**

---

## 📌 Executive Summary
**EduRisk XAI** is an executable, reproducible, modular research prototype built from scratch to address recurring limitations identified across 15 literature studies in educational machine learning. 

It provides a transparent, five-phase workflow that bridges early predictive warning, model-faithful **SHAP explainability**, and deterministic **rule-based pedagogical interventions** without requiring cloud dependencies or specialized hardware.

---

## 🔬 Core Capabilities & Five-Phase Methodology

1. **Phase 1: Data Acquisition & Preprocessing**
   - Supports 4 core operational indicators: `attendance_rate`, `assignment_submission_frequency`, `internal_test_score`, `study_hours`.
   - Strict leakage prevention: 80% train / 20% test split performed before any transformation.
   - Resampling (`SMOTE`) is applied **strictly inside training folds** during cross-validation.
2. **Phase 2: Predictive Modelling**
   - Implements four required candidate classifiers: **Decision Tree**, **Support Vector Classifier (SVC)**, **Logistic Regression**, and **Random Forest**.
   - Hyperparameters tuned using 5-fold `StratifiedKFold` and bounded `GridSearchCV`.
   - Transparent selection policy based on Cross-Validation Macro F1 and High-Risk Recall on training folds.
3. **Phase 3: Explainable AI (SHAP)**
   - Integrates model-appropriate SHAP explainers (`TreeExplainer`, `LinearExplainer`, `KernelExplainer`).
   - Decomposes predictions into **Risk-Increasing Factors** ($\phi > 0$) and **Protective Factors** ($\phi < 0$).
   - Generates both technical waterfall/bar attributions and plain-language educator explanations.
4. **Phase 4: Interactive Educator Dashboard**
   - 9-page Streamlit application designed for instructors without coding knowledge.
   - Multi-model benchmarking, single-student inference, cohort analytics, and longitudinal trajectory tracking.
5. **Phase 5: Pedagogical Intervention Engine**
   - Deterministic rule-based engine linking verified risk factors to pedagogical actions (mentoring, tutoring, study planning).
   - Editable rule criteria and SQLite status tracking (`Pending`, `In Progress`, `Completed`, `Dismissed`).

---

## 📊 Empirical Benchmark Results (Holdout Test Set)

Results from formal experimental execution (`exp_1791693461_a5bae9`) on the 649-student UCI cohort (130 test instances, 20 high-risk):

| Classifier | CV Macro F1 (Train) | Test Macro F1 | Test Accuracy | High-Risk Recall | False Negatives | ROC-AUC | Training Time | Latency / Sample |
|---|---|---|---|---|---|---|---|---|
| **Random Forest** (Selected) | **0.8787** | 0.8077 | 87.69% | **90.00%** | 2 | 0.9236 | 8.82s | 18.98ms |
| **Decision Tree** | 0.8522 | 0.8077 | 87.69% | **90.00%** | 2 | 0.9255 | 3.19s | 9.15ms |
| **Logistic Regression** | 0.8376 | **0.8467** | **90.77%** | **90.00%** | 2 | 0.9382 | **1.03s** | 9.21ms |
| **Support Vector (SVC)** | 0.8256 | 0.8365 | 90.00% | **90.00%** | 2 | **0.9459** | 4.49s | **8.90ms** |

*All 4 models detected 18 of 20 at-risk students (90.00% Recall), demonstrating balanced safety for proactive early intervention.*

---

## 📂 Project Directory Structure

```text
edurisk-xai/
├── app.py                      # Main Streamlit dashboard application
├── train_experiment.py         # Standalone CLI training and figure generator
├── requirements.txt            # Pinned CPU-compatible Python dependencies
├── README.md                   # Project overview and documentation
├── .env.example                # Configurable environment variables
├── .gitignore                  # Git exclusions
├── config/
│   └── settings.py             # Feature definitions, paths, grids, thresholds
├── data/
│   ├── raw/                    # Base benchmark dataset (student_data.csv)
│   ├── processed/              # Ingested and validated datasets
│   ├── sample/                 # Demonstration subsets
│   └── metadata/               # Data catalogs and hashes
├── models/
│   ├── artifacts/              # Active best_model.pkl and metadata
│   └── versions/               # Timestamped historical model pipelines
├── results/
│   ├── experiments/            # Machine-readable JSON and CSV run logs
│   ├── figures/                # Publication-quality evaluation plots
│   └── reports/                # Formatted markdown experimental summaries
├── database/
│   ├── database.py             # SQLite engine and session factory
│   ├── models.py               # SQLAlchemy ORM entities
│   └── crud.py                 # Persistence transactions and queries
├── src/
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
├── services/
│   ├── training_service.py     # Training orchestration and persistence
│   ├── prediction_service.py   # Live prediction and XAI pipeline
│   ├── import_service.py       # CSV upload validation and audit
│   └── report_service.py       # Publication figure and report generation
├── app_pages/
│   ├── dashboard.py            # Home / Research Overview
│   ├── data_import.py          # Data Management & Ingestion
│   ├── model_training.py       # Multi-Model Pipeline Training
│   ├── model_comparison.py     # Multi-Model Benchmarking & Matrices
│   ├── predict_student.py      # Single-Student Risk Prediction
│   ├── explainability.py       # SHAP Feature Attributions
│   ├── interventions.py        # Recommended Support & Rule Management
│   ├── analytics.py            # Cohort Analytics & Longitudinal Trajectories
│   └── research_traceability.py# 15-Paper Literature Gap Matrix
├── tests/
│   ├── test_data.py            # Dataset loading and schema checks
│   ├── test_preprocessing.py   # Preprocessing transformations and naming
│   ├── test_target.py          # Target construction and tier boundaries
│   ├── test_leakage.py         # Leakage safeguards and SMOTE isolation
│   ├── test_training.py        # 4-model training and selection logic
│   ├── test_prediction.py      # Inference output schema and risk tiers
│   ├── test_shap.py            # Local/global SHAP and additive consistency
│   ├── test_intervention.py    # Rule matching and priority ranking
│   ├── test_database.py        # SQLAlchemy ORM transactions and SQLite
│   └── test_end_to_end.py      # Full integration pipeline and UI smoke test
└── docs/
    ├── system_architecture.md  # Architectural layout and data flow
    ├── methodology_mapping.md  # Direct mapping to 5-phase research methodology
    ├── research_gap_matrix.md  # 15-paper literature gap review and groundings
    ├── experimental_protocol.md# Protocols, splits, grids, and metrics
    ├── model_results.md        # Actual generated experimental evidence
    ├── limitations.md          # Methodological and ethical limitations
    ├── implementation_decisions.md # Architectural and design decisions
    └── reproducibility.md      # Exact commands to install, test, and run
```

---

## ⚡ Quickstart Guide

### 1. Installation
```bash
cd "edurisk-xai"
pip install -r requirements.txt
```

### 2. Run Test Suite
```bash
python -m pytest tests -v
```
*(All 25 unit and end-to-end integration tests execute and pass in ~60s).*

### 3. Run Training Experiment
```bash
python train_experiment.py
```
*(Trains all 4 models, applies in-fold SMOTE, executes GridSearchCV, logs to SQLite, evaluates on the holdout test set, and exports figures).*

### 4. Launch Streamlit Web Dashboard
```bash
streamlit run app.py
```
*Access the interface at `http://localhost:8501`.*

---

## ⚖️ Research Integrity & Ethical Statement
- **Non-Causality Principle**: SHAP values quantify feature contributions to the model's mathematical output; they do not establish causal mechanisms of academic failure.
- **Support, Not Punishment**: Risk tiers provide proactive decision support for academic advisors. The system must never be used for punitive disciplinary actions or tracking.
- **Human Oversight**: Automated suggestions require professional review by qualified educators.
