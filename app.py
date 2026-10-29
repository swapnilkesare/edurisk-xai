"""
EduRisk — Academic Risk Prediction, Explainability, and Decision Support Platform
Modular, accessible Streamlit application with modern interactive dark UI,
horizontal top navigation, role-based access control, and scoped institutional student risk intelligence.
"""
import sys
from pathlib import Path

# Add project root to path for clean imports
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from config.theme import (
    inject_custom_theme,
    COLOR_BG_MAIN,
    COLOR_BG_CARD,
    COLOR_BG_SECONDARY,
    COLOR_ACCENT_TEAL,
    COLOR_ACCENT_VIOLET,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_BORDER,
    COLOR_BORDER_SUBTLE
)
from database.database import init_db, SessionLocal
from database.crud import seed_default_rules_if_empty
from services.auth_service import (
    seed_default_auth,
    authenticate_user,
    log_audit_event,
    DEMO_ACCOUNTS
)
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

# Inject centralized modern dark UI theme
st.markdown(inject_custom_theme(), unsafe_allow_html=True)

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
# 1. AUTHENTICATION & LOGIN GATEWAY (DARK UI)
# ============================================================================
if st.session_state.current_user is None:
    st.markdown(f"""
    <div style="text-align: center; padding: 2.5rem 0 1.5rem 0;">
        <h1 style="color: {COLOR_ACCENT_TEAL}; font-size: 3rem; font-weight: 800; margin-bottom: 0.25rem; letter-spacing: -1px;">
            🎓 EduRisk
        </h1>
        <p style="color: {COLOR_TEXT_SECONDARY}; font-size: 1.15rem; margin-top: 0;">
            Student Academic Risk Assessment & Decision Support Platform
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_lspace, col_login, col_rspace = st.columns([1, 1.6, 1])
    with col_login:
        with st.container():
            st.markdown(f"""
            <div style="background-color: {COLOR_BG_CARD}; border: 1px solid {COLOR_BORDER}; border-radius: 12px; padding: 1.75rem; margin-bottom: 1.5rem; box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06);">
                <h3 style="color: {COLOR_TEXT_PRIMARY}; margin-top: 0; font-size: 1.3rem;">🔐 Sign In to Your Academic Account</h3>
                <p style="color: {COLOR_TEXT_SECONDARY}; font-size: 0.95rem; line-height: 1.5; margin-bottom: 0;">
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
                        try:
                            user = authenticate_user(db, username_input, password_input)
                            if user:
                                org_name = user.organization.name if user.organization else "Global System"
                                st.session_state.current_user = {
                                    "id": user.id,
                                    "username": user.username,
                                    "full_name": user.full_name,
                                    "role": user.role,
                                    "organization_id": user.organization_id,
                                    "organization_name": org_name
                                }
                                st.success(f"Welcome back, {user.full_name}!")
                                st.rerun()
                            else:
                                st.error("Invalid credentials. Please verify your username and password.")
                        finally:
                            db.close()

            st.markdown("<br>", unsafe_allow_html=True)

            # Quick Role Demonstration Access (All 4 Demo Accounts)
            with st.expander("⚡ Quick Demonstration Role Access (Reviewer Logins)", expanded=True):
                st.caption("Select a pre-configured role to immediately test the platform:")
                demo_cols = st.columns(len(DEMO_ACCOUNTS))
                for d_idx, demo_cfg in enumerate(DEMO_ACCOUNTS):
                    with demo_cols[d_idx]:
                        if st.button(demo_cfg["label"], key=f"demo_login_btn_{d_idx}", use_container_width=True, help=demo_cfg["scope"]):
                            db = SessionLocal()
                            try:
                                user = authenticate_user(db, demo_cfg["username"], demo_cfg["default_password"])
                                if user:
                                    org_name = user.organization.name if user.organization else (demo_cfg.get("org_name") or "Global System")
                                    st.session_state.current_user = {
                                        "id": user.id,
                                        "username": user.username,
                                        "full_name": user.full_name,
                                        "role": user.role,
                                        "organization_id": user.organization_id,
                                        "organization_name": org_name
                                    }
                                    st.rerun()
                            finally:
                                db.close()

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style="background-color: {COLOR_BG_SECONDARY}; border: 1px solid {COLOR_BORDER}; border-radius: 8px; padding: 0.85rem 1rem;">
                    <strong style="color: {COLOR_ACCENT_TEAL}; font-size: 0.9rem;">📋 Pre-Configured Test Credentials:</strong>
                    <table style="width: 100%; margin-top: 0.5rem; font-size: 0.82rem; color: {COLOR_TEXT_SECONDARY}; border-collapse: collapse;">
                        <tr style="border-bottom: 1px solid {COLOR_BORDER}; text-align: left; color: {COLOR_TEXT_PRIMARY};">
                            <th style="padding: 4px 6px;">Role</th>
                            <th style="padding: 4px 6px;">Username</th>
                            <th style="padding: 4px 6px;">Password</th>
                            <th style="padding: 4px 6px;">Institution</th>
                        </tr>
                        <tr style="border-bottom: 1px solid {COLOR_BORDER_SUBTLE};">
                            <td style="padding: 4px 6px;"><strong style="color: {COLOR_TEXT_PRIMARY};">Teacher 1</strong></td>
                            <td style="padding: 4px 6px;"><code>teacher1</code></td>
                            <td style="padding: 4px 6px;"><code>Teacher@123</code></td>
                            <td style="padding: 4px 6px;">Horizon High School</td>
                        </tr>
                        <tr style="border-bottom: 1px solid {COLOR_BORDER_SUBTLE};">
                            <td style="padding: 4px 6px;"><strong style="color: {COLOR_TEXT_PRIMARY};">Teacher 2</strong></td>
                            <td style="padding: 4px 6px;"><code>teacher2</code></td>
                            <td style="padding: 4px 6px;"><code>Teacher@123</code></td>
                            <td style="padding: 4px 6px;">Apex Academy</td>
                        </tr>
                        <tr style="border-bottom: 1px solid {COLOR_BORDER_SUBTLE};">
                            <td style="padding: 4px 6px;"><strong style="color: {COLOR_TEXT_PRIMARY};">Org Admin</strong></td>
                            <td style="padding: 4px 6px;"><code>orgadmin</code></td>
                            <td style="padding: 4px 6px;"><code>OrgAdmin@123</code></td>
                            <td style="padding: 4px 6px;">Horizon High School</td>
                        </tr>
                        <tr>
                            <td style="padding: 4px 6px;"><strong style="color: {COLOR_ACCENT_VIOLET};">Researcher</strong></td>
                            <td style="padding: 4px 6px;"><code>researcher</code></td>
                            <td style="padding: 4px 6px;"><code>Research@123</code></td>
                            <td style="padding: 4px 6px;">Global System</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)

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
        class Org:
            pass
        self.organization = Org()
        self.organization.name = self.organization_name

current_user = CurrentUserProxy(st.session_state.current_user)


# ============================================================================
# 2. HORIZONTAL TOP NAVIGATION BAR (MATTE BLACK / ELECTRIC TEAL)
# ============================================================================
st.markdown('<div class="edurisk-navbar-container">', unsafe_allow_html=True)
top_cols = st.columns([1.6, 5.4, 2.0])

with top_cols[0]:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 8px; padding-top: 4px; flex-wrap: wrap;">
        <span style="font-size: 1.55rem; font-weight: 800; color: {COLOR_ACCENT_TEAL}; letter-spacing: -0.5px; white-space: nowrap;">🎓 EduRisk</span>
        <span style="font-size: 0.75rem; background-color: {COLOR_BG_SECONDARY}; color: {COLOR_TEXT_SECONDARY}; padding: 3px 8px; border-radius: 6px; border: 1px solid {COLOR_BORDER}; font-weight: 500; white-space: nowrap; max-width: 140px; overflow: hidden; text-overflow: ellipsis;">
            {current_user.organization_name[:16]}
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
    user_col1, user_col2 = st.columns([2.0, 1.2])
    with user_col1:
        role_badge = {
            "TEACHER": "Educator",
            "ORG_ADMIN": "Org Admin",
            "SYSTEM_ADMIN": "Lead Researcher"
        }.get(current_user.role, current_user.role)
        st.markdown(f"""
        <div style="text-align: right; line-height: 1.2; padding-top: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
            <strong style="color: {COLOR_TEXT_PRIMARY}; font-size: 0.88rem;">{current_user.full_name}</strong><br>
            <span style="color: {COLOR_ACCENT_TEAL}; font-size: 0.75rem; font-weight: 600;">{role_badge}</span>
        </div>
        """, unsafe_allow_html=True)
    with user_col2:
        if st.button("🚪 Logout", key="logout_btn", type="secondary", use_container_width=True):
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
    st.markdown(f"""
    <div style="padding: 0.5rem 0 1rem 0;">
        <h1 style="color: {COLOR_TEXT_PRIMARY}; font-size: 2rem; font-weight: 700; margin-bottom: 0.25rem;">
            🛠️ Research, Benchmarking & System Administration
        </h1>
        <p style="color: {COLOR_TEXT_SECONDARY}; font-size: 1.05rem;">
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
