# Explainable AI in Education: A Lightweight Web Dashboard

An Interpretable, SHAP-Driven Lightweight Framework for Transparent Student Risk Assessment and Pedagogical Intervention.

## Problem Statement & Research Motivation
Educational institutions frequently adopt opaque, computationally heavy models that leave non-technical educators unable to understand or trust predictions, hindering actionable interventions. This project solves that by integrating a classical ML pipeline with SHAP explainability and a rule-based intervention engine in a lightweight Streamlit interface.

## Methodology
The framework follows a 5-phase approach:
1. **Data Acquisition & Preprocessing**: Loading student data, mapping features, validating schemas, handling missing values, and executing a leakage-safe SMOTE on training folds.
2. **Predictive Modeling**: Evaluating four classical models (Decision Tree, SVC, Logistic Regression, Random Forest) via Stratified K-Fold CV.
3. **Explainable AI (SHAP)**: Providing local feature-level contributions to understand *why* a student is predicted to be at-risk.
4. **Interactive Dashboard**: A 11-page Streamlit application serving educators without requiring ML expertise.
5. **Rule-Based Intervention**: Mapping SHAP risk factors back to predefined, editable pedagogical remedies stored in SQLite.

## Technology Stack
- **Python 3.10+**
- **Machine Learning**: `scikit-learn`, `imbalanced-learn`, `pandas`, `numpy`
- **Explainability**: `shap`
- **Database**: `SQLite`, `SQLAlchemy`
- **Frontend**: `Streamlit`, `plotly`

## Installation and Execution
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Optional: Copy `.env.example` to `.env` and adjust settings.
4. Run the application: `streamlit run app.py`

## Features
- **Model Training UI**: Fully autonomous end-to-end model comparison and selection based on macro F1 and High-Risk recall.
- **Explainability UI**: Visual breakdown of prediction drivers using SHAP.
- **Intervention Engine**: Editable rules triggering targeted actions for at-risk students.
- **Student Tracking**: Longitudinal view of student risk trajectories.
- **Cohort Analytics**: Aggregated population risk monitoring.
- **Research Traceability**: Direct mapping between literature gaps and implemented prototype features.
