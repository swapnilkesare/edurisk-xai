"""
EduRisk XAI — Teacher-Friendly Student Risk Prediction & Decision Support System
A streamlined, non-technical dashboard for teachers to identify students needing academic support.
"""
import sys
from pathlib import Path

# Add project root to path for clean imports
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from database.database import init_db, SessionLocal
from database.crud import seed_default_rules_if_empty
from services.prediction_service import PredictionService
from services.training_service import TrainingService
from services.import_service import ImportService

# Page imports
from app_pages.dashboard import render_dashboard
from app_pages.data_import import render_data_import
from app_pages.model_training import render_model_training
from app_pages.model_comparison import render_model_comparison
from app_pages.predict_student import render_predict_student
from app_pages.explainability import render_explainability
from app_pages.interventions import render_interventions
from app_pages.analytics import render_analytics
from app_pages.research_traceability import render_research_traceability

# Configure Streamlit page
st.set_page_config(
    page_title="EduRisk — Student Risk Assessment",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Teacher-Friendly Clean Styling
st.markdown("""
<style>
    .main {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    div[data-testid="stSidebarNav"] {
        display: none;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
    }
    div.block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize services once
@st.cache_resource
def setup_services():
    init_db()
    db = SessionLocal()
    seed_default_rules_if_empty(db)
    db.close()

    pred_svc = PredictionService()
    train_svc = TrainingService()
    imp_svc = ImportService()
    return pred_svc, train_svc, imp_svc

prediction_service, training_service, import_service = setup_services()

# Manage Teacher Navigation state
if "teacher_nav" not in st.session_state:
    st.session_state.teacher_nav = "🏠 Home"

# Sidebar Navigation
with st.sidebar:
    st.markdown("""
    <div style="padding-bottom: 0.5rem;">
        <h2 style="margin: 0; color: #1e293b; font-size: 1.5rem;">🎓 <strong>EduRisk</strong></h2>
        <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Student Risk Assessment</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # Primary Teacher Navigation (Strictly 3 clean sections)
    primary_options = [
        "🏠 Home",
        "🎯 Predict Student Risk",
        "📋 Results & Support"
    ]

    current_idx = 0
    if st.session_state.teacher_nav in primary_options:
        current_idx = primary_options.index(st.session_state.teacher_nav)

    # Synchronize radio widget state if teacher_nav was updated programmatically (e.g. via action buttons)
    if "teacher_nav_radio" in st.session_state and st.session_state.teacher_nav_radio != st.session_state.teacher_nav:
        st.session_state.teacher_nav_radio = st.session_state.teacher_nav

    selected_nav = st.radio(
        "Teacher Menu",
        primary_options,
        index=current_idx,
        key="teacher_nav_radio"
    )

    # Sync navigation state when radio selection changes directly
    if selected_nav != st.session_state.teacher_nav:
        st.session_state.teacher_nav = selected_nav

    st.markdown("---")

    # Secondary Research / Admin Tools (Collapsed by default so teachers are not overwhelmed)
    with st.expander("🛠️ Research & Admin Tools", expanded=False):
        st.caption("Advanced tools for ML model configuration, benchmarking, and research traceability.")
        admin_choice = st.selectbox(
            "Select Admin View",
            [
                "None (Teacher Mode)",
                "📂 Data Management",
                "⚙️ Model Training",
                "📊 Model Benchmarking",
                "💡 Detailed SHAP Analysis",
                "📋 Intervention Rules Engine",
                "📈 Cohort Analytics",
                "📚 Research Traceability"
            ],
            index=0,
            key="admin_tool_selector"
        )

    st.markdown("---")
    st.caption("⚖️ *EduRisk Decision Support System. Formative Guidance Only.*")

# Application Router
# If an administrator tool is active, display that view; otherwise show the teacher-friendly page
if admin_choice != "None (Teacher Mode)":
    col_adm_hdr, col_adm_ret = st.columns([3, 1])
    with col_adm_hdr:
        st.info(f"🛠️ Administrator / Research View: **{admin_choice}**")
    with col_adm_ret:
        if st.button("← Return to Teacher Mode", use_container_width=True):
            st.session_state.admin_tool_selector = "None (Teacher Mode)"
            st.rerun()

    if admin_choice == "📂 Data Management":
        render_data_import(import_service, training_service)
    elif admin_choice == "⚙️ Model Training":
        render_model_training(training_service, prediction_service)
    elif admin_choice == "📊 Model Benchmarking":
        render_model_comparison(training_service, prediction_service)
    elif admin_choice == "💡 Detailed SHAP Analysis":
        render_explainability(prediction_service)
    elif admin_choice == "📋 Intervention Rules Engine":
        render_interventions(prediction_service)
    elif admin_choice == "📈 Cohort Analytics":
        render_analytics()
    elif admin_choice == "📚 Research Traceability":
        render_research_traceability()
else:
    # Teacher-Facing Flow
    if st.session_state.teacher_nav == "🏠 Home":
        render_dashboard(prediction_service, training_service)

    elif st.session_state.teacher_nav == "🎯 Predict Student Risk":
        render_predict_student(prediction_service)

    elif st.session_state.teacher_nav == "📋 Results & Support":
        if "current_prediction" in st.session_state and st.session_state.current_prediction is not None:
            render_predict_student(prediction_service)
        else:
            st.markdown("""
            <div style="padding: 1rem 0;">
                <h2 style="color: #1e293b;">📋 Assessment Results & Support</h2>
                <p style="color: #64748b;">No active student assessment found in this session yet.</p>
            </div>
            """, unsafe_allow_html=True)
            st.info("👋 To view results and personalized pedagogical support, please assess a student first.")
            if st.button("🚀 Start a Student Assessment Now", type="primary"):
                st.session_state.teacher_nav = "🎯 Predict Student Risk"
                st.rerun()
