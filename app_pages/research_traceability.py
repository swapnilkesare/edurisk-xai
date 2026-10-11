"""
Page: Research Traceability Matrix
"""
import streamlit as st
import pandas as pd

# The 15-paper literature gap matrix grounded in supplied research materials
LITERATURE_GAP_DATA = [
    {
        "Paper": "Pan, J. et al. [1]",
        "Year": 2025,
        "Method": "Literature Survey",
        "Main Result": "Benchmarked ML models",
        "Identified Gap": "No consensus on best model",
        "Prototype Response": "Four-model parallel pipeline with transparent CV selection",
        "Status": "FULLY ADDRESSED",
        "Evidence": "src/train.py, app_pages/model_comparison.py",
        "Remaining Limitation": "Selected model may be dataset specific"
    },
    {
        "Paper": "Jha, M. K. et al. [2]",
        "Year": 2025,
        "Method": "XGNN-AP Framework",
        "Main Result": "99.71% Acc, F1: 1.00",
        "Identified Gap": "Deep models lack transparency",
        "Prototype Response": "Integration of SHAP TreeExplainer/LinearExplainer/KernelExplainer",
        "Status": "FULLY ADDRESSED",
        "Evidence": "src/explain.py, app_pages/explainability.py",
        "Remaining Limitation": "SHAP explains model behavior, not causality"
    },
    {
        "Paper": "Kalita, E. et al. [3]",
        "Year": 2025,
        "Method": "Time-Series DL",
        "Main Result": "88.23% Accuracy",
        "Identified Gap": "High compute; opaque network",
        "Prototype Response": "Pure scikit-learn pipeline (CPU deployable)",
        "Status": "FULLY ADDRESSED",
        "Evidence": "requirements.txt, CPU benchmark in train.py",
        "Remaining Limitation": "Lower sequence awareness than recurrent deep networks"
    },
    {
        "Paper": "Angeioplastis, A. et al. [4]",
        "Year": 2025,
        "Method": "Classification",
        "Main Result": "F1-Score > 0.80",
        "Identified Gap": "Ignores student dynamics",
        "Prototype Response": "Longitudinal SQLite tracking of multi-period predictions",
        "Status": "PARTIALLY ADDRESSED",
        "Evidence": "database/models.py, app_pages/analytics.py",
        "Remaining Limitation": "Evaluates discrete snapshots rather than continuous spatio-temporal graphs"
    },
    {
        "Paper": "Gonzales, W. et al. [5]",
        "Year": 2025,
        "Method": "Hybrid ML-DL",
        "Main Result": "Superior sensitivity",
        "Identified Gap": "Few models for basic school",
        "Prototype Response": "UI abstraction removing programming requirements for educators",
        "Status": "FULLY ADDRESSED",
        "Evidence": "app.py, Streamlit framework",
        "Remaining Limitation": "Requires institutional device access"
    },
    {
        "Paper": "Johora, F. T. & Hasan, M. N. [6]",
        "Year": 2025,
        "Method": "Voting Ensemble",
        "Main Result": "86.38% Accuracy",
        "Identified Gap": "Black-box trust barrier",
        "Prototype Response": "Plain-English explanations + SHAP attribution breakdown",
        "Status": "FULLY ADDRESSED",
        "Evidence": "src/explain.py, app_pages/explainability.py",
        "Remaining Limitation": "Formal educator trust user study not yet conducted"
    },
    {
        "Paper": "Paul, R. et al. [7]",
        "Year": 2025,
        "Method": "Regression & ML",
        "Main Result": "Forecasted 1st Sem GPA",
        "Identified Gap": "Late at-risk detection",
        "Prototype Response": "Early-semester indicators used (attendance, formative assessments)",
        "Status": "FULLY ADDRESSED",
        "Evidence": "config/settings.py, src/schema.py",
        "Remaining Limitation": "Requires early recording of formative assignments"
    },
    {
        "Paper": "Lu, J. et al. [8]",
        "Year": 2024,
        "Method": "Survey & Stats",
        "Main Result": "Motivation impacts GPA",
        "Identified Gap": "Overlooked behavioral traits",
        "Prototype Response": "Behavioral indicators mapped into feature schema and database",
        "Status": "FULLY ADDRESSED",
        "Evidence": "database/models.py, src/schema.py",
        "Remaining Limitation": "Self-reported motivation exhibits subjective bias"
    },
    {
        "Paper": "Luo, Z. et al. [9]",
        "Year": 2024,
        "Method": "Spatio-Temporal",
        "Main Result": "High trajectory precision",
        "Identified Gap": "Static data over-reliance",
        "Prototype Response": "Temporal multi-point auditing in SQLite",
        "Status": "PARTIALLY ADDRESSED",
        "Evidence": "database/crud.py, app_pages/analytics.py",
        "Remaining Limitation": "Snapshot intervals depend on manual or periodic import"
    },
    {
        "Paper": "Pires, J. P. J. et al. [10]",
        "Year": 2024,
        "Method": "Supervised ML",
        "Main Result": "Forecasted coding risk",
        "Identified Gap": "Needs domain-tailored tool",
        "Prototype Response": "Retrainable pipeline with dynamic feature configuration",
        "Status": "FULLY ADDRESSED",
        "Evidence": "src/train.py, services/training_service.py",
        "Remaining Limitation": "Retraining required per specialized academic department"
    },
    {
        "Paper": "Akbar, S. [11]",
        "Year": 2024,
        "Method": "Rule Mining",
        "Main Result": "Rule-based pathways",
        "Identified Gap": "Lacks accessible pipeline",
        "Prototype Response": "One-click browser-based training and inference pipeline",
        "Status": "FULLY ADDRESSED",
        "Evidence": "app_pages/model_training.py",
        "Remaining Limitation": "Requires local or private server execution"
    },
    {
        "Paper": "Liu, Y. et al. [12]",
        "Year": 2023,
        "Method": "Log Mining",
        "Main Result": "Linked logs to exam marks",
        "Identified Gap": "Underutilized LMS logs",
        "Prototype Response": "Generic CSV/schema ingestion supporting clickstream and activity",
        "Status": "PARTIALLY ADDRESSED",
        "Evidence": "services/import_service.py, src/schema.py",
        "Remaining Limitation": "No live OAuth API to Canvas/Moodle implemented (Future)"
    },
    {
        "Paper": "Feng, G. & Fan, M. [13]",
        "Year": 2022,
        "Method": "Data Cleaning",
        "Main Result": "Mitigated overfitting",
        "Identified Gap": "Poor data curation/noise",
        "Prototype Response": "Leakage-safe ColumnTransformer with in-fold SMOTE and scaling",
        "Status": "FULLY ADDRESSED",
        "Evidence": "src/preprocessing.py, src/train.py, tests/test_leakage.py",
        "Remaining Limitation": "Severe systemic missingness cannot be entirely imputed"
    },
    {
        "Paper": "Zhang, Y. et al. [14]",
        "Year": 2021,
        "Method": "Comparative Analysis",
        "Main Result": "Accuracy-compute trade-off",
        "Identified Gap": "Hardware selection limits",
        "Prototype Response": "Lightweight Python stack running entirely on commodity CPU",
        "Status": "FULLY ADDRESSED",
        "Evidence": "requirements.txt, src/train.py",
        "Remaining Limitation": "In-memory training limits cohort scalability to ~100k rows"
    },
    {
        "Paper": "Alshanqiti, A. & Namoun, A. [15]",
        "Year": 2020,
        "Method": "Multi-Label Reg",
        "Main Result": "Granular grade tiers",
        "Identified Gap": "Binary pass/fail is coarse",
        "Prototype Response": "Probabilistic thresholding into LOW, MODERATE, HIGH risk tiers",
        "Status": "FULLY ADDRESSED",
        "Evidence": "src/target.py, src/risk.py, app_pages/predict_student.py",
        "Remaining Limitation": "Threshold calibration requires domain agreement"
    }
]

def render_research_traceability():
    st.title("📚 Research Gap Traceability Matrix")
    st.markdown("Grounding prototype capabilities against the **15-paper literature review** from the project manuscript.")

    df_gaps = pd.DataFrame(LITERATURE_GAP_DATA)

    # Status KPI Cards
    status_counts = df_gaps["Status"].value_counts().to_dict()
    col1, col2, col3 = st.columns(3)
    col1.metric("Fully Addressed", status_counts.get("FULLY ADDRESSED", 0), "Implemented in Prototype")
    col2.metric("Partially Addressed", status_counts.get("PARTIALLY ADDRESSED", 0), "Lightweight Prototype Scope")
    col3.metric("Future Work", status_counts.get("FUTURE", 0), "Requires External APIs")

    st.markdown("---")

    # Filter by Status
    st.subheader("Literature Mapping Matrix")
    filter_status = st.multiselect(
        "Filter by Implementation Status:",
        ["FULLY ADDRESSED", "PARTIALLY ADDRESSED", "FUTURE"],
        default=["FULLY ADDRESSED", "PARTIALLY ADDRESSED", "FUTURE"]
    )

    df_filtered = df_gaps[df_gaps["Status"].isin(filter_status)]

    st.dataframe(
        df_filtered[["Paper", "Identified Gap", "Prototype Response", "Status", "Evidence", "Remaining Limitation"]],
        use_container_width=True
    )

    st.markdown("---")
    st.markdown("""
    ### 🔬 Research Grounding Statement
    Gaps marked **FULLY ADDRESSED** have verified executable code and automated unit tests. 
    Gaps marked **PARTIALLY ADDRESSED** (such as longitudinal dynamics and LMS clickstream) are addressed at the prototype architecture level (SQLite snapshot logging, CSV schema support) without overclaiming deep temporal neural modeling or live cloud API synchronization.
    """)
