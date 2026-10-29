import streamlit as st
import os

# Configure the main page
st.set_page_config(
    page_title="Explainable AI in Education",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Navigation setup
from app_pages import (
    dashboard, students, prediction, explainability, 
    interventions, analytics, model_training, 
    model_performance, data_import, research_traceability, settings
)

# Sidebar Navigation
st.sidebar.title("🎓 EduRisk XAI")
st.sidebar.markdown("---")

PAGES = {
    "Dashboard": dashboard,
    "Predict Risk": prediction,
    "Explainability": explainability,
    "Interventions": interventions,
    "Students": students,
    "Cohort Analytics": analytics,
    "Model Training": model_training,
    "Model Performance": model_performance,
    "Data Import": data_import,
    "Research Traceability": research_traceability,
    "Settings": settings
}

selection = st.sidebar.radio("Navigation", list(PAGES.keys()))

st.sidebar.markdown("---")
st.sidebar.info(
    "**Responsible AI Notice:**\n"
    "This system provides AI-assisted academic risk estimates for educator decision support. "
    "Predictions should not be treated as definitive judgments about a student's ability."
)

# Load the selected page
page = PAGES[selection]
page.app()
