"""
EduRisk XAI — Main Streamlit Application
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
    page_title="EduRisk XAI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .metric-card {
        background: #f8fafc;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #e2e8f0;
    }
    .risk-high {
        color: #ef4444;
        font-weight: bold;
    }
    .risk-moderate {
        color: #f59e0b;
        font-weight: bold;
    }
    .risk-low {
        color: #10b981;
        font-weight: bold;
    }
    div[data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database and default rules once
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

# Sidebar Navigation
with st.sidebar:
    st.markdown("## 🎓 **EduRisk XAI**")
    st.caption("Explainable Student Risk Assessment")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "🏠 Home / Overview",
            "📂 Data Management",
            "⚙️ Model Training",
            "📊 Model Comparison",
            "🎯 Predict Student Risk",
            "💡 Explainability (SHAP)",
            "📋 Recommended Support",
            "📈 Cohort Analytics",
            "📚 Research Traceability"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("### 🖥️ System Status")
    is_ready = prediction_service.is_model_ready()
    if is_ready:
        meta = prediction_service.metadata
        st.success(f"Model: **{meta.get('selected_model', 'Fitted')}**")
        st.caption(f"Ver: `{meta.get('model_version', 'v1.0')}`")
    else:
        st.warning("Model: **Untrained**")

    st.markdown("---")
    st.caption("⚖️ *EduRisk XAI Research Prototype. Decision Support Only.*")

# Route to selected page
if page == "🏠 Home / Overview":
    render_dashboard(prediction_service, training_service)
elif page == "📂 Data Management":
    render_data_import(import_service, training_service)
elif page == "⚙️ Model Training":
    render_model_training(training_service, prediction_service)
elif page == "📊 Model Comparison":
    render_model_comparison(training_service, prediction_service)
elif page == "🎯 Predict Student Risk":
    render_predict_student(prediction_service)
elif page == "💡 Explainability (SHAP)":
    render_explainability(prediction_service)
elif page == "📋 Recommended Support":
    render_interventions(prediction_service)
elif page == "📈 Cohort Analytics":
    render_analytics()
elif page == "📚 Research Traceability":
    render_research_traceability()
