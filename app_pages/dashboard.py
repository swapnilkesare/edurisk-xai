"""
Page: Teacher-Friendly Welcome & Overview (Home)
Title: EduRisk — Student Academic Risk Assessment
Provides an accessible, high-contrast dashboard with live institutional indicators and immediate action routes.
"""
import streamlit as st
import pandas as pd

from database.database import SessionLocal
from database.models import Student, Prediction
from services.auth_service import get_scoped_students, get_scoped_predictions

def render_dashboard(prediction_service=None, training_service=None, current_user=None):
    # Retrieve scoped institutional data
    db = SessionLocal()
    try:
        students = get_scoped_students(db, current_user)
        preds = get_scoped_predictions(db, current_user, limit=50)
        org_name = current_user.organization.name if (current_user and current_user.organization) else "All Organizations (Global Admin)"
        user_name = current_user.full_name if current_user else "Educator"
    finally:
        db.close()

    # High-Contrast Brand Header
    st.markdown(f"""
    <div style="padding: 0.5rem 0 1rem 0;">
        <h1 style="color: var(--text-primary, #0f172a); font-size: 2.2rem; font-weight: 700; margin-bottom: 0.25rem;">
            🎓 EduRisk — Student Academic Risk Assessment
        </h1>
        <p style="color: var(--text-secondary, #475569); font-size: 1.15rem; margin-top: 0;">
            Identify students who may need additional academic support early in the term.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Hero Banner with High-Contrast Adaptive Styling
    st.markdown(f"""
    <div style="background-color: var(--bg-card, #f8fafc); 
                border: 1px solid var(--border-color, #e2e8f0); 
                border-left: 6px solid #0284c7; 
                border-radius: 12px; 
                padding: 1.5rem; 
                margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <h3 style="color: var(--text-primary, #0f172a); margin: 0; font-size: 1.3rem;">
                👋 Welcome, {user_name}
            </h3>
            <span style="background-color: #e0f2fe; color: #0369a1; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85rem;">
                {org_name}
            </span>
        </div>
        <p style="color: var(--text-secondary, #334155); font-size: 1.05rem; line-height: 1.6; margin-bottom: 0.5rem;">
            EduRisk helps you detect early warning signs of academic vulnerability. 
            By reviewing current attendance, submission consistency, and formative marks, you can quickly spot emerging 
            learning gaps and implement supportive pedagogical interventions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Primary Action Callout
    col_act, col_gap = st.columns([1, 2])
    with col_act:
        if st.button("🚀 Start Student Risk Assessment", type="primary", use_container_width=True, key="home_hero_assess_btn"):
            st.session_state.current_page = "🎯 Student Risk Assessment"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Real Institutional Data Metric Cards
    high_risk_count = sum(1 for p in preds if p.risk_tier == "HIGH")
    low_risk_count = sum(1 for p in preds if p.risk_tier == "LOW")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Enrolled Cohort", f"{len(students)} Students")
    with m2:
        st.metric("Completed Assessments", f"{len(preds)} Records")
    with m3:
        st.metric("Priority Support (High)", f"{high_risk_count}", delta_color="inverse")
    with m4:
        st.metric("On Track (Low)", f"{low_risk_count}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 3-Step Process Explanation
    st.markdown("### 📋 How It Works in 3 Simple Steps")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div style="background-color: var(--bg-card, #f8fafc); border: 1px solid var(--border-color, #e2e8f0); border-radius: 10px; padding: 1.25rem; height: 100%;">
            <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">📝</div>
            <h4 style="color: var(--text-primary, #0f172a); margin: 0 0 0.5rem 0;">1. Enter Details</h4>
            <p style="color: var(--text-secondary, #475569); font-size: 0.95rem; line-height: 1.5; margin: 0;">
                Provide the student's current attendance, test marks, and study hours using a simple form.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div style="background-color: var(--bg-card, #f8fafc); border: 1px solid var(--border-color, #e2e8f0); border-radius: 10px; padding: 1.25rem; height: 100%;">
            <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">⚡</div>
            <h4 style="color: var(--text-primary, #0f172a); margin: 0 0 0.5rem 0;">2. Check Predicted Risk</h4>
            <p style="color: var(--text-secondary, #475569); font-size: 0.95rem; line-height: 1.5; margin: 0;">
                Click one button to receive an easy-to-read assessment showing whether additional support is advised.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div style="background-color: var(--bg-card, #f8fafc); border: 1px solid var(--border-color, #e2e8f0); border-radius: 10px; padding: 1.25rem; height: 100%;">
            <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">🤝</div>
            <h4 style="color: var(--text-primary, #0f172a); margin: 0 0 0.5rem 0;">3. Support Your Student</h4>
            <p style="color: var(--text-secondary, #475569); font-size: 0.95rem; line-height: 1.5; margin: 0;">
                Review the key factors influencing the result and browse actionable, targeted pedagogical recommendations.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><hr style='border: none; border-top: 1px solid var(--border-color, #e2e8f0);'>", unsafe_allow_html=True)

    # Reassuring Educator Notice
    st.info(
        "💡 **Supportive Guidance Philosophy**: EduRisk provides early decision support to supplement your professional judgment. "
        "Predictions are indicative estimates of current vulnerability, not permanent labels or limits on student ability."
    )
