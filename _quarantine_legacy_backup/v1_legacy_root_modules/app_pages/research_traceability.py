import streamlit as st

def app():
    st.title("Research Traceability")
    st.markdown("Mapping the implementation back to the literature gaps.")
    
    gaps = [
        {"Gap": "No consensus on best model", "Response": "4-model evaluation pipeline", "Evidence": "Model Training Page", "Status": "FULLY ADDRESSED"},
        {"Gap": "Black-box opacity", "Response": "SHAP local/global explanations", "Evidence": "Explainability Page", "Status": "FULLY ADDRESSED"},
        {"Gap": "High computational cost", "Response": "Lightweight scikit-learn models", "Evidence": "Model Performance Page (Train time)", "Status": "FULLY ADDRESSED"},
        {"Gap": "Static data over-reliance", "Response": "Longitudinal SQLite tracking", "Evidence": "Student Tracking Page", "Status": "PARTIALLY ADDRESSED"},
        {"Gap": "Live LMS underutilization", "Response": "LMS-compatible schema + CSV Import", "Evidence": "Data Import Page", "Status": "PARTIALLY ADDRESSED"}
    ]
    
    st.table(gaps)
    
    st.markdown("### Remaining Limitations")
    st.info("- No live institutional LMS (Moodle/Canvas) credentials available. \n- Longitudinal features rely on repeated manual predictions rather than deep spatial-temporal sequences.")
