"""
EduRisk — Academic Risk Prediction, Explainability, and Decision Support Platform
Modular, accessible Streamlit application with horizontal top navigation, role-based access control,
and scoped institutional student risk intelligence.
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
from services.auth_service import seed_default_auth, authenticate_user, log_audit_event
from services.prediction_service import PredictionService
from services.training_service import TrainingService
from services.import_service import ImportService

# Page imports
from app_pages.dashboard import render_dashboard
from app_pages.predict_student import render_predict_student
from app_pages.students import render_students
from app_pages.reports import render_reports
from app_pages.data_import import render_data_import
from app_pages.model_training import render_model_training
from app_pages.model_comparison import render_model_comparison
from app_pages.explainability import render_explainability
from app_pages.interventions import render_interventions
from app_pages.analytics import render_analytics
from app_pages.research_traceability import render_research_traceability

# Page configuration
st.set_page_config(
    page_title="EduRisk — Student Academic Risk Assessment",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Adaptive Theme & High-Contrast CSS
st.markdown("""
<style>
    :root {
        --text-primary: #0f172a;
        --text-secondary: #334155;
        --text-muted: #64748b;
        --bg-surface: #ffffff;
        --bg-card: #f8fafc;
        --border-color: #cbd5e1;
        --brand-primary: #0284c7;
        --brand-primary-hover: #0369a1;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --text-primary: #f8fafc;
            --text-secondary: #cbd5e1;
            --text-muted: #94a3b8;
            --bg-surface: #0f172a;
            --bg-card: #1e293b;
            --border-color: #334155;
            --brand-primary: #38bdf8;
            --brand-primary-hover: #0ea5e9;
        }
    }

    /* Completely hide default left sidebar to enforce unified top navigation */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    div[data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    /* Typography & Container Spacing */
    .main {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    div.block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Button Polish */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.15s ease-in-out;
    }

    /* Navigation Bar Styling */
    .edurisk-top-bar {
        border-bottom: 2px solid var(--border-color, #e2e8f0);
        padding-bottom: 0.75rem;
        margin-bottom: 1.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize application database and services once
@st.cache_resource
def setup_services():
    init_db()
    db = SessionLocal()
    seed_default_rules_if_empty(db)
    seed_default_auth(db)
    db.close()

    pred_svc = PredictionService()
    train_svc = TrainingService()
    imp_svc = ImportService()
    return pred_svc, train_svc, imp_svc

prediction_service, training_service, import_service = setup_services()

# Session State Initialization
if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Home"


# ============================================================================
# 1. AUTHENTICATION & LOGIN GATEWAY
# ============================================================================
if st.session_state.current_user is None:
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 1.5rem 0;">
        <h1 style="color: var(--brand-primary, #0284c7); font-size: 2.8rem; font-weight: 800; margin-bottom: 0.25rem;">
            🎓 EduRisk
        </h1>
        <p style="color: var(--text-secondary, #475569); font-size: 1.2rem; margin-top: 0;">
            Student Academic Risk Assessment & Decision Support Platform
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_lspace, col_login, col_rspace = st.columns([1, 1.6, 1])
    with col_login:
        with st.container():
            st.markdown("""
            <div style="background-color: var(--bg-card, #f8fafc); border: 1px solid var(--border-color, #e2e8f0); border-radius: 12px; padding: 1.75rem; margin-bottom: 1.5rem;">
                <h3 style="color: var(--text-primary, #0f172a); margin-top: 0;">🔐 Sign In to Your Academic Account</h3>
                <p style="color: var(--text-muted, #64748b); font-size: 0.95rem;">
                    Access authorized student records, risk indicators, and intervention recommendations.
                </p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("login_form"):
                username_input = st.text_input("Username or Email", placeholder="e.g. teacher1")
                password_input = st.text_input("Password", type="password", placeholder="Enter your password")
                login_submit = st.form_submit_button("Sign In", type="primary", use_container_width=True)

                if login_submit:
                    if not username_input or not password_input:
                        st.error("Please enter both username/email and password.")
                    else:
                        db = SessionLocal()
                        user = authenticate_user(db, username_input, password_input)
                        db.close()
                        if user:
                            st.session_state.current_user = {
                                "id": user.id,
                                "username": user.username,
                                "full_name": user.full_name,
                                "role": user.role,
                                "organization_id": user.organization_id,
                                "organization_name": user.organization.name if user.organization else "Global System"
                            }
                            st.success(f"Welcome back, {user.full_name}!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials. Please verify your username and password.")

            st.markdown("<br>", unsafe_allow_html=True)

            # Quick Role Demonstration Access
            with st.expander("⚡ Quick Demonstration Role Access (Reviewer Logins)", expanded=True):
                st.caption("Select a pre-configured role to immediately test the platform:")
                q1, q2, q3 = st.columns(3)
                with q1:
                    if st.button("🧑‍🏫 Teacher", use_container_width=True, help="Teacher at Horizon High School"):
                        db = SessionLocal()
                        user = authenticate_user(db, "teacher1", "Teacher@123")
                        db.close()
                        if user:
                            st.session_state.current_user = {
                                "id": user.id,
                                "username": user.username,
                                "full_name": user.full_name,
                                "role": user.role,
                                "organization_id": user.organization_id,
                                "organization_name": user.organization.name if user.organization else "Global System"
                            }
                            st.rerun()
                with q2:
                    if st.button("🏫 Org Admin", use_container_width=True, help="Administrator at Horizon High School"):
                        db = SessionLocal()
                        user = authenticate_user(db, "orgadmin", "OrgAdmin@123")
                        db.close()
                        if user:
                            st.session_state.current_user = {
                                "id": user.id,
                                "username": user.username,
                                "full_name": user.full_name,
                                "role": user.role,
                                "organization_id": user.organization_id,
                                "organization_name": user.organization.name if user.organization else "Global System"
                            }
                            st.rerun()
                with q3:
                    if st.button("🔬 Researcher", use_container_width=True, help="Lead AI Researcher (Full Research Access)"):
                        db = SessionLocal()
                        user = authenticate_user(db, "researcher", "Research@123")
                        db.close()
                        if user:
                            st.session_state.current_user = {
                                "id": user.id,
                                "username": user.username,
                                "full_name": user.full_name,
                                "role": user.role,
                                "organization_id": user.organization_id,
                                "organization_name": "Global Research System"
                            }
                            st.rerun()

    st.stop()


# Convert user dictionary back to a light object helper
class CurrentUserProxy:
    def __init__(self, d):
        if d is None:
            d = {}
        self.id = d.get("id")
        self.username = d.get("username", "guest")
        self.full_name = d.get("full_name", "Guest Educator")
        self.role = d.get("role", "TEACHER")
        self.organization_id = d.get("organization_id")
        self.organization_name = d.get("organization_name", "EduRisk Academic Institution")
        # Dummy organization object for existing template lookups
        class Org:
            pass
        self.organization = Org()
        self.organization.name = self.organization_name

current_user = CurrentUserProxy(st.session_state.current_user)


# ============================================================================
# 2. HORIZONTAL TOP NAVIGATION BAR
# ============================================================================
st.markdown('<div class="edurisk-top-bar">', unsafe_allow_html=True)
top_cols = st.columns([1.8, 5.0, 2.2])

with top_cols[0]:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 8px; padding-top: 4px;">
        <span style="font-size: 1.5rem; font-weight: 800; color: var(--brand-primary, #0284c7);">🎓 EduRisk</span>
        <span style="font-size: 0.75rem; background-color: var(--bg-card, #f1f5f9); color: var(--text-muted, #64748b); padding: 2px 6px; border-radius: 6px; border: 1px solid var(--border-color, #cbd5e1);">
            {current_user.organization_name[:14]}
        </span>
    </div>
    """, unsafe_allow_html=True)

with top_cols[1]:
    # Determine visible navigation tabs based on user role
    nav_items = [
        ("🏠 Home", "🏠 Home"),
        ("🎯 Student Risk Assessment", "🎯 Risk Assessment"),
        ("👥 Students", "👥 Students"),
        ("📊 Reports", "📊 Reports"),
    ]
    if current_user.role == "SYSTEM_ADMIN":
        nav_items.append(("🛠️ Research & Admin Tools", "🛠️ Research & Admin"))

    btn_cols = st.columns(len(nav_items))
    for idx, (target_page, label) in enumerate(nav_items):
        with btn_cols[idx]:
            is_active = (st.session_state.current_page == target_page)
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"top_nav_btn_{idx}", type=btn_type, use_container_width=True):
                st.session_state.current_page = target_page
                st.rerun()

with top_cols[2]:
    user_col1, user_col2 = st.columns([2.5, 1.2])
    with user_col1:
        role_badge = {
            "TEACHER": "Educator",
            "ORG_ADMIN": "Org Admin",
            "SYSTEM_ADMIN": "Lead Researcher"
        }.get(current_user.role, current_user.role)
        st.markdown(f"""
        <div style="text-align: right; line-height: 1.2; padding-top: 4px;">
            <strong style="color: var(--text-primary, #0f172a); font-size: 0.85rem;">{current_user.full_name}</strong><br>
            <span style="color: var(--brand-primary, #0284c7); font-size: 0.75rem; font-weight: 600;">{role_badge}</span>
        </div>
        """, unsafe_allow_html=True)
    with user_col2:
        if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
            db = SessionLocal()
            log_audit_event(db, current_user.id, current_user.username, "LOGOUT", "SESSION", "User signed out")
            db.close()
            st.session_state.current_user = None
            st.session_state.current_page = "🏠 Home"
            st.session_state.pop("current_prediction", None)
            st.session_state.pop("selected_student_for_assessment", None)
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# 3. SECURE ROUTER WITH SERVER-SIDE PERMISSION ENFORCEMENT
# ============================================================================
curr_page = st.session_state.current_page

if curr_page == "🏠 Home":
    render_dashboard(prediction_service, training_service, current_user=current_user)

elif curr_page == "🎯 Student Risk Assessment":
    render_predict_student(prediction_service, current_user=current_user)

elif curr_page == "👥 Students":
    render_students(current_user=current_user)

elif curr_page == "📊 Reports":
    render_reports(current_user=current_user)

elif curr_page == "🛠️ Research & Admin Tools":
    # STRICT SERVER-SIDE AUTHORIZATION ENFORCEMENT
    if current_user.role != "SYSTEM_ADMIN":
        db = SessionLocal()
        log_audit_event(
            db, 
            current_user.id, 
            current_user.username, 
            "ACCESS_DENIED", 
            "RESEARCH_ADMIN_TOOLS", 
            f"Unauthorized attempt to access Research Tools by role {current_user.role}"
        )
        db.close()

        st.error("🚫 **Access Denied (403 Forbidden)**: You do not have permission to view Research & Administrator Tools.")
        st.info("This view is strictly restricted to Lead Researchers and System Administrators. Please return to the educator dashboard.")
        if st.button("← Return to Home", type="primary"):
            st.session_state.current_page = "🏠 Home"
            st.rerun()
        st.stop()

    # Authorized System Admin / Researcher Sub-Navigation
    st.markdown("""
    <div style="padding: 0.5rem 0 1rem 0;">
        <h1 style="color: var(--text-primary, #0f172a); font-size: 2rem; font-weight: 700; margin-bottom: 0.25rem;">
            🛠️ Research, Benchmarking & System Administration
        </h1>
        <p style="color: var(--text-secondary, #475569); font-size: 1.05rem;">
            Advanced algorithmic benchmarking, model re-training, SHAP validation, and research traceability.
        </p>
    </div>
    """, unsafe_allow_html=True)

    admin_views = [
        "📂 Data Management",
        "⚙️ Model Training",
        "📊 Model Benchmarking",
        "💡 Detailed SHAP Analysis",
        "📋 Intervention Rules Engine",
        "📈 Cohort Analytics",
        "📚 Research Traceability"
    ]

    selected_admin_tool = st.selectbox(
        "Select Research / Administrative Sub-View:",
        admin_views,
        index=0,
        key="admin_tool_sub_selector"
    )

    st.markdown("---")

    if selected_admin_tool == "📂 Data Management":
        render_data_import(import_service, training_service)
    elif selected_admin_tool == "⚙️ Model Training":
        render_model_training(training_service, prediction_service)
    elif selected_admin_tool == "📊 Model Benchmarking":
        render_model_comparison(training_service, prediction_service)
    elif selected_admin_tool == "💡 Detailed SHAP Analysis":
        render_explainability(prediction_service)
    elif selected_admin_tool == "📋 Intervention Rules Engine":
        render_interventions(prediction_service)
    elif selected_admin_tool == "📈 Cohort Analytics":
        render_analytics()
    elif selected_admin_tool == "📚 Research Traceability":
        render_research_traceability()

else:
    # Safe Fallback
    st.warning(f"Unknown page route '{curr_page}'. Returning to Home.")
    st.session_state.current_page = "🏠 Home"
    st.rerun()
