# Phase 2: Explainable AI in Education Research Prototype

This directory contains the Phase 2 Research Demonstration Prototype for the manuscript:
**"Explainable AI in Education: A Lightweight Web Dashboard for Student Academic Performance Prediction and Intervention"**

## Purpose
This prototype is a completely isolated, standalone build designed to demonstrate the technical feasibility of the proposed methodology to faculty and project stakeholders. It proves that the four highlighted literature gaps can be addressed using a lightweight, transparent, and actionable architecture.

**The existing full project in the parent directory has not been modified and remains perfectly safe.**

## Features
- **4-Model Empirical Comparison**: Automatically trains and evaluates Decision Tree, SVC, Logistic Regression, and Random Forest using GridSearchCV and Stratified K-Fold.
- **Leakage-Safe SMOTE**: Prevents data leakage by applying SMOTE strictly inside the CV pipeline.
- **SHAP Integration**: Extracts local feature contributions using `TreeExplainer`/`LinearExplainer`.
- **Intervention Engine**: Translates SHAP mathematical values into pedagogical actions.
- **Teacher Dashboard**: An intuitive Streamlit interface to demonstrate the workflow.

## How to Run

### 1. Install Dependencies
Ensure you are in the `phase2_xai_student_risk_prototype` directory.
```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard
```bash
streamlit run app.py
```

### 3. Usage
1. Open the dashboard in your browser.
2. Click **Initialize & Train Models** on the Home page to generate the dataset and train the models.
3. Navigate to **Model Comparison** to view the metrics and selected model.
4. Navigate to **Predict Student Risk** to test inference, view SHAP explanations, and see recommended interventions.
5. Navigate to **Research Gap Demonstration** for a breakdown of how the prototype addresses the literature.

## Testing
The prototype includes an automated test suite verifying leakage safety, SHAP mappings, and end-to-end execution.
```bash
python tests/test_end_to_end.py
pytest tests/
```
