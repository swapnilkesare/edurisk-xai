"""
Page: Teacher-Friendly Welcome & Overview (Home)
Title: EduRisk — Student Academic Risk Assessment
Modern, interactive dark UI with matte black canvas, electric teal primary accents, and soft violet insights.
"""
import streamlit as st
import pandas as pd

from config.theme import (
    COLOR_BG_CARD,
    COLOR_BG_SECONDARY,
    COLOR_ACCENT_TEAL,
    COLOR_ACCENT_VIOLET,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_BORDER,
    COLOR_RISK_HIGH,
    COLOR_RISK_LOW
)
from database.database import SessionLocal
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

    # Brand Title Header
    st.markdown(f"""
    <div style="padding: 0.25rem 0 1rem 0;">
        <h1 style="color: {COLOR_TEXT_PRIMARY}; font-size: 2.2rem; font-weight: 800; margin-bottom: 0.25rem; letter-spacing: -0.5px;">
            🎓 EduRisk — Student Academic Risk Assessment
        </h1>
        <p style="color: {COLOR_TEXT_SECONDARY}; font-size: 1.1rem; margin-top: 0;">
            Catch early indicators of academic difficulty and explore personalized pedagogical support.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Hero Banner in Matte Card with Electric Teal Left Bar
    st.markdown(f"""
    <div style="background-color: {COLOR_BG_CARD}; 
                border: 1px solid {COLOR_BORDER}; 
                border-left: 6px solid {COLOR_ACCENT_TEAL}; 
                border-radius: 12px; 
                padding: 1.5rem; 
                margin-bottom: 1.5rem;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <h3 style="color: {COLOR_TEXT_PRIMARY}; margin: 0; font-size: 1.3rem; font-weight: 700;">
                👋 Welcome, {user_name}
            </h3>
            <span style="background-color: {COLOR_BG_SECONDARY}; color: {COLOR_ACCENT_TEAL}; border: 1px solid {COLOR_BORDER}; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85rem;">
                {org_name}
            </span>
        </div>
        <p style="color: {COLOR_TEXT_SECONDARY}; font-size: 1.05rem; line-height: 1.6; margin-bottom: 0;">
            EduRisk empowers you to detect early warning signs of academic vulnerability before cumulative exams. 
            By reviewing attendance patterns, assignment consistency, and internal test performance, you can proactively guide students 
            with actionable, non-punitive interventions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Primary Action Callout Button
    col_act, col_gap = st.columns([1.2, 2.8])
    with col_act:
        if st.button("🚀 Assess Student Risk Now", type="primary", use_container_width=True, key="home_hero_assess_btn"):
            st.session_state.current_page = "🎯 Student Risk Assessment"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Real Institutional Metrics Display
    high_risk_count = sum(1 for p in preds if p.risk_tier == "HIGH")
    low_risk_count = sum(1 for p in preds if p.risk_tier == "LOW")

    st.markdown(f"### 📊 Institutional Status Overview — <span style='color: {COLOR_ACCENT_TEAL};'>{org_name}</span>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Enrolled Cohort", f"{len(students)} Students")
    with m2:
        st.metric("Evaluations Run", f"{len(preds)} Records")
    with m3:
        st.metric("Priority Support (High)", f"{high_risk_count}", delta=f"{high_risk_count/len(preds):.0%}" if preds else None, delta_color="inverse")
    with m4:
        st.metric("On Track (Low)", f"{low_risk_count}", delta=f"{low_risk_count/len(preds):.0%}" if preds else None)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3-Step Process Explanation in Dark Cards
    st.markdown("### 📋 How EduRisk Works in 3 Simple Steps")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div style="background-color: {COLOR_BG_CARD}; border: 1px solid {COLOR_BORDER}; border-radius: 12px; padding: 1.35rem; height: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
            <div style="font-size: 1.8rem; margin-bottom: 0.5rem; color: {COLOR_ACCENT_TEAL};">📝</div>
            <h4 style="color: {COLOR_TEXT_PRIMARY}; margin: 0 0 0.5rem 0; font-size: 1.15rem;">1. Enter Details</h4>
            <p style="color: {COLOR_TEXT_SECONDARY}; font-size: 0.95rem; line-height: 1.5; margin: 0;">
                Provide the student's current attendance, test marks, and study hours using a streamlined input form.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div style="background-color: {COLOR_BG_CARD}; border: 1px solid {COLOR_BORDER}; border-radius: 12px; padding: 1.35rem; height: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
            <div style="font-size: 1.8rem; margin-bottom: 0.5rem; color: {COLOR_ACCENT_TEAL};">⚡</div>
            <h4 style="color: {COLOR_TEXT_PRIMARY}; margin: 0 0 0.5rem 0; font-size: 1.15rem;">2. Check Predicted Risk</h4>
            <p style="color: {COLOR_TEXT_SECONDARY}; font-size: 0.95rem; line-height: 1.5; margin: 0;">
                Click one button to receive an easy-to-read assessment showing whether additional support is advised.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div style="background-color: {COLOR_BG_CARD}; border: 1px solid {COLOR_BORDER}; border-radius: 12px; padding: 1.35rem; height: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
            <div style="font-size: 1.8rem; margin-bottom: 0.5rem; color: {COLOR_ACCENT_VIOLET};">🤝</div>
            <h4 style="color: {COLOR_TEXT_PRIMARY}; margin: 0 0 0.5rem 0; font-size: 1.15rem;">3. Support Your Student</h4>
            <p style="color: {COLOR_TEXT_SECONDARY}; font-size: 0.95rem; line-height: 1.5; margin: 0;">
                Review the key factors influencing the result and browse actionable, targeted pedagogical recommendations.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"<br><hr style='border: none; border-top: 1px solid {COLOR_BORDER};'>", unsafe_allow_html=True)

    # Reassuring Educator Notice with Soft Violet Accent
    st.markdown(f"""
    <div style="background-color: {COLOR_BG_CARD}; border: 1px solid {COLOR_BORDER}; border-left: 4px solid {COLOR_ACCENT_VIOLET}; border-radius: 8px; padding: 1rem 1.25rem;">
        <span style="color: {COLOR_ACCENT_VIOLET}; font-weight: 700;">💡 Supportive Guidance Philosophy:</span>
        <span style="color: {COLOR_TEXT_SECONDARY}; font-size: 0.95rem;">
            EduRisk provides formative decision support to supplement your professional educator judgment. 
            Predictions are indicative estimates of current vulnerability, not permanent labels or limits on student ability.
        </span>
    </div>
    """, unsafe_allow_html=True)
