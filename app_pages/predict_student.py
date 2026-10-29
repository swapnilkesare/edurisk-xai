"""
Page: Teacher-Facing Student Risk Prediction & Support Recommendations
Provides an uncompressed, accessible, modern White UI interface for teachers to assess
student academic vulnerability using permanent roll numbers (PRN), understand key contributing
factors, and receive actionable, deterministic pedagogical interventions.
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from config.settings import CORE_FEATURES
from config.theme import (
    COLOR_BG_CARD,
    COLOR_BG_SECONDARY,
    COLOR_ACCENT_TEAL,
    COLOR_ACCENT_TEAL_SURFACE,
    COLOR_ACCENT_VIOLET,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_BODY,
    COLOR_TEXT_SECONDARY,
    COLOR_BORDER,
    COLOR_BORDER_SUBTLE,
    COLOR_RISK_HIGH,
    COLOR_RISK_HIGH_SURFACE,
    COLOR_RISK_MODERATE,
    COLOR_RISK_MODERATE_SURFACE,
    COLOR_RISK_LOW,
    COLOR_RISK_LOW_SURFACE
)
from database.database import SessionLocal
from database.crud import get_student_by_prn, normalize_prn, validate_prn

# Reassuring presets for teachers wanting a quick walkthrough
TEACHER_PROFILES = {
    "Custom Student Record": None,
    "Example 1: Student Falling Behind (Needs Prompt Support)": {
        "student_name": "Marcus Brody",
        "attendance_rate": 58.0,
        "internal_test_score": 28.0,
        "assignment_submission_frequency": 45.0,
        "study_hours": 1.5,
        "failures": 2,
    },
    "Example 2: Borderline Student (Needs Light Monitoring)": {
        "student_name": "Tariq Al-Mansoor",
        "attendance_rate": 74.0,
        "internal_test_score": 52.0,
        "assignment_submission_frequency": 70.0,
        "study_hours": 3.0,
        "failures": 0,
    },
    "Example 3: Student On Track (Standard Progress)": {
        "student_name": "Sofia Rodriguez",
        "attendance_rate": 96.0,
        "internal_test_score": 88.0,
        "assignment_submission_frequency": 95.0,
        "study_hours": 6.5,
        "failures": 0,
    }
}

def render_predict_student(prediction_service, current_user=None):
    # Top Header & Quick Return Home
    col_hdr_title, col_hdr_back = st.columns([3.8, 1.2])
    with col_hdr_title:
        st.markdown(f"""
        <div style="padding: 0.25rem 0 0.5rem 0;">
            <h1 style="color: {COLOR_TEXT_PRIMARY}; font-size: 2rem; font-weight: 700; margin-bottom: 0.25rem;">
                🎯 Student Academic Risk Assessment
            </h1>
            <p style="color: {COLOR_TEXT_SECONDARY}; font-size: 1.05rem; margin: 0;">
                Assess student academic indicators using their Permanent Roll Number (PRN) to receive transparent risk attributions and pedagogical guidance.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_hdr_back:
        st.markdown("<div style='padding-top: 1.2rem;'>", unsafe_allow_html=True)
        if st.button("🏠 Return to Home", use_container_width=True, key="top_back_to_home_btn", type="secondary"):
            st.session_state.current_page = "🏠 Home"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Verify model readiness
    if not prediction_service.is_model_ready():
        st.error(
            "⚠️ **Assessment Engine Unavailable**: The prediction model is not currently loaded. "
            "Please check the Research & Admin section to train the baseline model."
        )
        return

    # Check if a preselected student was dispatched from the Roster
    preselected = st.session_state.get("selected_student_for_assessment")

    # Check if a prediction result already exists in session state
    has_active_prediction = "current_prediction" in st.session_state and st.session_state.current_prediction is not None

    # ========================================================================
    # 1. INPUT FORM (COLLAPSIBLE WHEN PREDICTION IS ACTIVE)
    # ========================================================================
    with st.expander("📝 Student Information & Assessment Form", expanded=not has_active_prediction):
        
        # Display Banner for Pre-selected Roster Student
        if preselected:
            st.markdown(f"""
            <div style="background-color: {COLOR_ACCENT_TEAL_SURFACE}; border: 1px solid {COLOR_ACCENT_TEAL}; border-radius: 8px; padding: 0.85rem 1.15rem; margin-bottom: 1rem;">
                <strong style="color: {COLOR_ACCENT_TEAL};">🎓 Pre-Selected Student from Enrolled Roster:</strong><br>
                <span style="color: {COLOR_TEXT_PRIMARY}; font-size: 0.95rem;">
                    <strong>{preselected.get('student_name', 'Student')}</strong> • PRN: <code>{preselected.get('student_id', 'PRN-N/A')}</code> 
                    {f"• {preselected.get('course')} (Sem {preselected.get('semester')})" if preselected.get('course') else ''}
                </span>
            </div>
            """, unsafe_allow_html=True)

        col_preset, col_reset = st.columns([3, 1])
        with col_preset:
            selected_profile = st.selectbox(
                "Load benchmark demonstration profile (optional):",
                list(TEACHER_PROFILES.keys()),
                index=0,
                help="Select an example profile to test the assessment or choose Custom Student Record to enter custom values."
            )
        with col_reset:
            st.markdown("<div style='padding-top: 1.8rem;'>", unsafe_allow_html=True)
            if st.button("🔄 Clear Form", use_container_width=True, key="clear_assessment_form_btn", type="secondary"):
                st.session_state.pop("current_prediction", None)
                st.session_state.pop("selected_student_for_assessment", None)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        preset_vals = TEACHER_PROFILES.get(selected_profile) or {}

        # Default student name & PRN
        def_name = preselected["student_name"] if preselected else preset_vals.get("student_name", "Sarah Jenkins")
        def_prn = preselected["student_id"] if preselected else "PRN-2024-0042"

        # --- SECTION 1: PERMANENT ROLL NUMBER & IDENTIFICATION ---
        st.markdown(f"<h4 style='color: {COLOR_TEXT_PRIMARY}; margin-top: 0.5rem;'>1. Permanent Roll Number (PRN) & Student Profile</h4>", unsafe_allow_html=True)
        col_prn, col_name = st.columns(2)
        with col_prn:
            student_prn_input = st.text_input(
                "Permanent Roll Number (PRN)*",
                value=def_prn,
                help="Unique roll number or registration code. Used to associate multiple assessments to the same student over time."
            )
        with col_name:
            student_name_input = st.text_input(
                "Student Full Name / Alias",
                value=def_name,
                help="Used to personalize the support plan and export documentation."
            )

        # Quick DB check for PRN
        db = SessionLocal()
        matched_student = None
        try:
            norm_prn = normalize_prn(student_prn_input)
            org_id = current_user.organization_id if current_user else None
            if norm_prn:
                matched_student = get_student_by_prn(db, norm_prn, organization_id=org_id)
                if matched_student:
                    st.caption(f"✅ Verified Roster Match: **{matched_student.name}** ({matched_student.course}, Sem {matched_student.semester})")
                else:
                    st.caption(f"ℹ️ PRN `'{norm_prn}'` not yet in roster — will be automatically registered upon assessment completion.")
        finally:
            db.close()

        st.markdown(f"<hr style='border: none; border-top: 1px solid {COLOR_BORDER_SUBTLE}; margin: 1.25rem 0;'>", unsafe_allow_html=True)

        # --- SECTION 2: ACADEMIC PERFORMANCE INDICATORS ---
        st.markdown(f"<h4 style='color: {COLOR_TEXT_PRIMARY};'>2. Formative Academic Performance Indicators</h4>", unsafe_allow_html=True)
        col_acad1, col_acad2 = st.columns(2)
        with col_acad1:
            internal_test = st.slider(
                "Internal Test / Midterm Assessment Score (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(preset_vals.get("internal_test_score", 65.0)),
                step=1.0,
                help="Formative assessment or internal quiz average (0–100%)."
            )
        with col_acad2:
            failures_opt = st.selectbox(
                "Past Term Remediation / Backlog Credits",
                options=[0, 1, 2, 3],
                index=int(min(preset_vals.get("failures", 0), 3)),
                help="Number of previous subjects or terms where remedial support was needed."
            )

        st.markdown(f"<hr style='border: none; border-top: 1px solid {COLOR_BORDER_SUBTLE}; margin: 1.25rem 0;'>", unsafe_allow_html=True)

        # --- SECTION 3: CLASSROOM ENGAGEMENT & ATTENDANCE ---
        st.markdown(f"<h4 style='color: {COLOR_TEXT_PRIMARY};'>3. Classroom Engagement & Study Habits</h4>", unsafe_allow_html=True)
        col_att1, col_att2, col_att3 = st.columns(3)
        with col_att1:
            attendance = st.slider(
                "Course Attendance Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(preset_vals.get("attendance_rate", 82.0)),
                step=1.0,
                help="Percentage of scheduled lecture and laboratory sessions attended."
            )
        with col_att2:
            submission_freq = st.slider(
                "Assignment Submission Consistency (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(preset_vals.get("assignment_submission_frequency", 75.0)),
                step=1.0,
                help="Proportion of regular assignments submitted on time."
            )
        with col_att3:
            study_hrs = st.number_input(
                "Weekly Independent Study (Hours)",
                min_value=0.0,
                max_value=40.0,
                value=float(preset_vals.get("study_hours", 4.0)),
                step=0.5,
                help="Self-reported weekly hours dedicated to coursework outside scheduled classes."
            )

        st.markdown(f"<hr style='border: none; border-top: 1px solid {COLOR_BORDER_SUBTLE}; margin: 1.25rem 0;'>", unsafe_allow_html=True)

        # --- SECTION 4: CONTEXTUAL SOCIO-DEMOGRAPHIC FACTORS ---
        with st.expander("➕ Learning Environment Context (Support, Internet, Commute)", expanded=False):
            st.caption("Contextual factors calibrated against the validated UCI benchmark pipeline:")
            col_ctx1, col_ctx2 = st.columns(2)
            with col_ctx1:
                school_support = st.selectbox("Receiving institutional learning support / tutoring?", ["no", "yes"], index=0)
                family_support = st.selectbox("Academic encouragement at home?", ["yes", "no"], index=0)
                internet_access = st.selectbox("Reliable high-speed internet at home?", ["yes", "no"], index=0)
            with col_ctx2:
                extracurricular = st.selectbox("Participates in extracurricular / athletics?", ["yes", "no"], index=0)
                travel_time = st.selectbox(
                    "Commute time to campus",
                    ["< 15 minutes", "15 to 30 minutes", "30 to 60 minutes", "> 1 hour"],
                    index=0
                )
                travel_code = {"< 15 minutes": 1, "15 to 30 minutes": 2, "30 to 60 minutes": 3, "> 1 hour": 4}.get(travel_time, 1)

        # Assemble full input payload
        student_data = {
            "attendance_rate": float(attendance),
            "assignment_submission_frequency": float(submission_freq),
            "internal_test_score": float(internal_test),
            "study_hours": float(study_hrs),
            "failures": int(failures_opt),
            "schoolsup": school_support,
            "famsup": family_support,
            "internet": internet_access,
            "activities": extracurricular,
            "traveltime": travel_code,
            "school": "GP",
            "sex": "F",
            "age": 17,
            "address": "U",
            "famsize": "GT3",
            "Pstatus": "T",
            "Medu": 2,
            "Fedu": 2,
            "goout": 2,
            "Dalc": 1,
            "Walc": 1,
            "health": 4,
            "romantic": "no",
        }

        st.markdown("<br>", unsafe_allow_html=True)

        # Execute Prediction Button
        predict_clicked = st.button(
            "🚀 Run Student Academic Risk Assessment",
            type="primary",
            use_container_width=True,
            key="btn_run_student_risk_assessment"
        )

        if predict_clicked:
            clean_prn = normalize_prn(student_prn_input)
            is_valid_prn, prn_msg = validate_prn(clean_prn)

            if not is_valid_prn:
                st.error(f"Cannot run assessment: {prn_msg}")
            else:
                with st.spinner("Executing Random Forest pipeline, computing SHAP values, and matching pedagogical rules..."):
                    try:
                        org_id = current_user.organization_id if current_user else None
                        user_id = current_user.id if current_user else None

                        result = prediction_service.predict_and_explain(
                            student_data=student_data,
                            student_identifier=clean_prn,
                            save_to_db=True,
                            organization_id=org_id,
                            created_by_user_id=user_id
                        )

                        st.session_state.current_prediction = result
                        st.session_state.current_student_name = student_name_input or (matched_student.name if matched_student else f"Student {clean_prn}")
                        st.session_state.current_student_prn = clean_prn
                        st.success("✅ Assessment complete! Review the evidence-grounded results below.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not complete assessment: {str(e)}")

    # ========================================================================
    # 2. ASSESSMENT OUTCOME & RECOMMENDATIONS SECTION (UNCOMPRESSED LAYOUT)
    # ========================================================================
    if has_active_prediction:
        result = st.session_state.current_prediction
        pred = result["prediction"]
        shap_res = result.get("shap", {})
        interventions = result.get("interventions", [])
        student_display_name = st.session_state.get("current_student_name", "Student")
        student_display_prn = st.session_state.get("current_student_prn", "PRN-N/A")

        st.markdown(f"<hr style='border: none; border-top: 1px solid {COLOR_BORDER}; margin: 2rem 0 1.5rem 0;'>", unsafe_allow_html=True)

        # Page-Level Title with PRN pill
        st.markdown(f"""
        <div style="display: flex; align-items: baseline; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1.25rem;">
            <h2 style="color: {COLOR_TEXT_PRIMARY}; font-size: 1.75rem; font-weight: 700; margin: 0;">
                Assessment Results for {student_display_name}
            </h2>
            <span style="background-color: {COLOR_BG_SECONDARY}; color: {COLOR_TEXT_SECONDARY}; padding: 3px 10px; border-radius: 6px; border: 1px solid {COLOR_BORDER}; font-size: 0.85rem; font-weight: 600;">
                PRN: <code>{student_display_prn}</code>
            </span>
        </div>
        """, unsafe_allow_html=True)

        # 1. Prominent Plain-Language Risk Tier Banner
        risk_tier = pred.get("risk_tier", "LOW").upper()
        prob_val = pred.get("risk_probability", 0.0)

        if risk_tier == "HIGH":
            banner_bg = COLOR_RISK_HIGH_SURFACE
            banner_border = COLOR_RISK_HIGH
            banner_title = "⚠️ Priority Support Recommended (High Academic Vulnerability)"
            badge_html = f"<span style='background-color: {COLOR_RISK_HIGH}; color: #FFFFFF; padding: 5px 14px; border-radius: 20px; font-weight: 700; font-size: 0.85rem;'>High Risk Band</span>"
            summary_desc = (
                f"Based on current marks ({student_data.get('internal_test_score', 0):.0f}%) and attendance ({student_data.get('attendance_rate', 0):.0f}%), "
                f"<strong>{student_display_name}</strong> is exhibiting strong indicators of academic vulnerability. "
                "Immediate, collaborative faculty and advisor support is recommended to prevent compounding learning deficits."
            )
        elif risk_tier == "MODERATE":
            banner_bg = COLOR_RISK_MODERATE_SURFACE
            banner_border = COLOR_RISK_MODERATE
            banner_title = "⚡ Monitoring Advised (Moderate Risk / Borderline Indicators)"
            badge_html = f"<span style='background-color: {COLOR_RISK_MODERATE}; color: #FFFFFF; padding: 5px 14px; border-radius: 20px; font-weight: 700; font-size: 0.85rem;'>Moderate Risk Band</span>"
            summary_desc = (
                f"<strong>{student_display_name}</strong> is performing within a borderline academic range. "
                "Targeted formative check-ins, study habit consultations, and homework review can solidify their foundation."
            )
        else:
            banner_bg = COLOR_RISK_LOW_SURFACE
            banner_border = COLOR_RISK_LOW
            banner_title = "✅ On Track (Low Predicted Risk)"
            badge_html = f"<span style='background-color: {COLOR_RISK_LOW}; color: #FFFFFF; padding: 5px 14px; border-radius: 20px; font-weight: 700; font-size: 0.85rem;'>Low Risk Band</span>"
            summary_desc = (
                f"<strong>{student_display_name}</strong> demonstrates healthy engagement and academic consistency. "
                "Continue standard curriculum guidance and provide positive reinforcement for their independent study habits."
            )

        st.markdown(f"""
        <div style="background-color: {banner_bg}; 
                    border: 1px solid {banner_border}; 
                    border-left: 6px solid {banner_border}; 
                    border-radius: 12px; 
                    padding: 1.5rem 1.75rem; 
                    margin-bottom: 1.5rem;
                    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.5rem;">
                <h3 style="margin: 0; color: {COLOR_TEXT_PRIMARY}; font-size: 1.25rem; font-weight: 700;">{banner_title}</h3>
                {badge_html}
            </div>
            <p style="color: {COLOR_TEXT_BODY}; font-size: 1.02rem; margin-bottom: 0; line-height: 1.55;">
                {summary_desc}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # 2. Key Quantitative Summary Cards (Uncompressed Widths)
        col_m1, col_m2, col_m3 = st.columns([1.2, 1.2, 1.2])
        with col_m1:
            st.metric(
                label="Estimated Risk Probability",
                value=f"{prob_val:.1%}",
                help="Model-estimated probability that the student requires proactive pedagogical remediation."
            )
        with col_m2:
            st.metric(
                label="Action Urgency",
                value=pred.get("urgency", "Standard Guidance")
            )
        with col_m3:
            st.metric(
                label="Recommended Action Items",
                value=f"{len(interventions)} Action Items"
            )

        st.caption(
            "ℹ️ *Ethical Guidance: This probability estimate is derived from statistical machine learning patterns on student indicators. "
            "It is not a guarantee or fixed label, but an advisory signal to guide constructive educator discussions.*"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # 3. Main Contributing Factors (SHAP Local Explainability)
        st.markdown(f"""
        <div style="border-bottom: 1px solid {COLOR_BORDER}; padding-bottom: 0.5rem; margin-bottom: 1rem;">
            <h3 style="color: {COLOR_TEXT_PRIMARY}; font-size: 1.3rem; margin: 0 0 0.25rem 0;">
                🔍 Evidence-Based Contributing Factors (SHAP Explainability)
            </h3>
            <p style="color: {COLOR_TEXT_SECONDARY}; font-size: 0.95rem; margin: 0;">
                Feature attributions decompose the exact positive and negative drivers influencing this student's assessment score.
            </p>
        </div>
        """, unsafe_allow_html=True)

        risk_increasing = shap_res.get("risk_increasing_factors", [])
        protective_factors = shap_res.get("protective_factors", [])

        col_factors1, col_factors2 = st.columns([1, 1])

        with col_factors1:
            st.markdown(f"<h4 style='color: {COLOR_RISK_HIGH}; font-size: 1.05rem;'>🔻 Factors Increasing Academic Concern</h4>", unsafe_allow_html=True)
            if risk_increasing:
                for item in risk_increasing[:3]:
                    feat_name = item["feature"].replace("_", " ").title()
                    raw_v = item.get("raw_value")
                    val_display = f": <strong>{raw_v}</strong>" if raw_v is not None else ""
                    st.markdown(f"""
                    <div style="background-color: {COLOR_BG_CARD}; border-left: 4px solid {COLOR_RISK_HIGH}; border: 1px solid {COLOR_BORDER}; padding: 12px 14px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
                        <strong style="color: {COLOR_RISK_HIGH}; font-size: 0.98rem;">{feat_name}</strong> {val_display}<br>
                        <span style="color: {COLOR_TEXT_SECONDARY}; font-size: 0.88rem;">Contributed positively toward academic vulnerability signal (SHAP = +{item['shap_value']:.3f}).</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: {COLOR_BG_CARD}; border: 1px solid {COLOR_BORDER}; padding: 12px 14px; border-radius: 8px; color: {COLOR_TEXT_SECONDARY}; font-size: 0.95rem;">
                    No critical risk-increasing factors detected.
                </div>
                """, unsafe_allow_html=True)

        with col_factors2:
            st.markdown(f"<h4 style='color: {COLOR_RISK_LOW}; font-size: 1.05rem;'>🛡️ Protective Factors Supporting Resilience</h4>", unsafe_allow_html=True)
            if protective_factors:
                for item in protective_factors[:3]:
                    feat_name = item["feature"].replace("_", " ").title()
                    raw_v = item.get("raw_value")
                    val_display = f": <strong>{raw_v}</strong>" if raw_v is not None else ""
                    st.markdown(f"""
                    <div style="background-color: {COLOR_BG_CARD}; border-left: 4px solid {COLOR_RISK_LOW}; border: 1px solid {COLOR_BORDER}; padding: 12px 14px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
                        <strong style="color: {COLOR_RISK_LOW}; font-size: 0.98rem;">{feat_name}</strong> {val_display}<br>
                        <span style="color: {COLOR_TEXT_SECONDARY}; font-size: 0.88rem;">Buffer preventing further academic vulnerability (SHAP = {item['shap_value']:.3f}).</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: {COLOR_BG_CARD}; border: 1px solid {COLOR_BORDER}; padding: 12px 14px; border-radius: 8px; color: {COLOR_TEXT_SECONDARY}; font-size: 0.95rem;">
                    No notable protective buffers identified.
                </div>
                """, unsafe_allow_html=True)

        # AI Plain-Language Synthesis Summary
        if shap_res.get("plain_language_summary"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background-color: {COLOR_BG_CARD}; border: 1px solid {COLOR_BORDER}; border-left: 4px solid {COLOR_ACCENT_VIOLET}; border-radius: 8px; padding: 1.15rem 1.35rem; box-shadow: 0 1px 2px rgba(15,23,42,0.04);">
                <strong style="color: {COLOR_ACCENT_VIOLET}; font-size: 1rem;">💡 AI Synthesis Summary:</strong>
                <ul style="margin: 0.5rem 0 0 0; padding-left: 1.25rem; color: {COLOR_TEXT_BODY}; font-size: 0.94rem; line-height: 1.6;">
                    {''.join([f"<li>{s}</li>" for s in shap_res['plain_language_summary'][:3]])}
                </ul>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 4. Recommended Pedagogical Interventions (Full-Width Uncompressed Cards)
        st.markdown(f"""
        <div style="border-bottom: 1px solid {COLOR_BORDER}; padding-bottom: 0.5rem; margin-bottom: 1rem;">
            <h3 style="color: {COLOR_TEXT_PRIMARY}; font-size: 1.3rem; margin: 0 0 0.25rem 0;">
                🤝 Recommended Pedagogical Interventions
            </h3>
            <p style="color: {COLOR_TEXT_SECONDARY}; font-size: 0.95rem; margin: 0;">
                Deterministic, rule-based support strategies linked directly to the student's identified risk factors:
            </p>
        </div>
        """, unsafe_allow_html=True)

        if interventions:
            for idx, item in enumerate(interventions):
                prio = item.get("priority", "MEDIUM")
                prio_color = {"HIGH": COLOR_RISK_HIGH, "MEDIUM": COLOR_RISK_MODERATE, "LOW": COLOR_RISK_LOW}.get(prio, COLOR_ACCENT_TEAL)
                prio_bg = {"HIGH": COLOR_RISK_HIGH_SURFACE, "MEDIUM": COLOR_RISK_MODERATE_SURFACE, "LOW": COLOR_RISK_LOW_SURFACE}.get(prio, COLOR_ACCENT_TEAL_SURFACE)
                
                st.markdown(f"""
                <div style="background-color: {COLOR_BG_CARD}; 
                            border: 1px solid {COLOR_BORDER}; 
                            border-left: 5px solid {prio_color}; 
                            border-radius: 10px; 
                            padding: 1.25rem 1.5rem; 
                            margin-bottom: 1rem; 
                            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem; flex-wrap: wrap; gap: 0.5rem;">
                        <h4 style="margin: 0; color: {COLOR_TEXT_PRIMARY}; font-size: 1.12rem; font-weight: 700;">📌 {item.get('action', 'Academic Support Action')}</h4>
                        <span style="background-color: {prio_bg}; color: {prio_color}; border: 1px solid {prio_color}; padding: 3px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: 700;">
                            {prio} Priority Action
                        </span>
                    </div>
                    <p style="color: {COLOR_TEXT_BODY}; margin: 0.4rem 0 0.5rem 0; font-size: 0.96rem; line-height: 1.55;">
                        <strong style="color: {COLOR_TEXT_PRIMARY};">Educational Rationale:</strong> {item.get('rationale', 'Assists student engagement and concept mastery.')}
                    </p>
                    <div style="font-size: 0.86rem; color: {COLOR_TEXT_SECONDARY};">
                        Targeted Indicator: <code style="background-color: {COLOR_BG_SECONDARY}; color: {COLOR_ACCENT_TEAL}; padding: 2px 7px; border-radius: 4px; border: 1px solid {COLOR_BORDER}; font-weight: 600;">{item.get('feature', 'Engagement')}</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("🎉 No high-priority remediation rules triggered. Student is progressing smoothly under standard guidance.")

        st.markdown("<br>", unsafe_allow_html=True)

        # 5. Technical Decomposition Expander (Audit & Verification)
        with st.expander("🔬 Technical Verification & SHAP Value Matrix (For Data Specialists)"):
            st.caption("Underlying mathematical model values decomposed into exact Shapley attributions:")
            st.write(f"**Base Risk Expectation (Prior):** `{shap_res.get('base_value', 0.5):.4f}`")
            if shap_res.get("contributions"):
                df_shap = pd.DataFrame(shap_res["contributions"])
                if "raw_value" in df_shap.columns:
                    df_shap["raw_value"] = df_shap["raw_value"].astype(str)
                st.dataframe(
                    df_shap[["feature", "raw_value", "shap_value", "is_risk_increasing"]],
                    use_container_width=True
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # 6. Responsive Bottom Action Bar
        col_new, col_home_bot, col_export = st.columns([1.3, 1.3, 1.4])
        with col_new:
            if st.button("🔄 Assess Another Student", type="primary", use_container_width=True, key="assess_another_student_btn"):
                st.session_state.pop("current_prediction", None)
                st.session_state.pop("current_student_name", None)
                st.session_state.pop("current_student_prn", None)
                st.session_state.pop("selected_student_for_assessment", None)
                st.rerun()
        with col_home_bot:
            if st.button("🏠 Return to Home Dashboard", use_container_width=True, key="bottom_return_home_btn", type="secondary"):
                st.session_state.pop("selected_student_for_assessment", None)
                st.session_state.current_page = "🏠 Home"
                st.rerun()
        with col_export:
            if st.button("👥 View Roster & Past History", use_container_width=True, key="view_roster_history_btn", type="secondary"):
                st.session_state.current_page = "👥 Students"
                st.rerun()

    st.markdown(f"<br><hr style='border: none; border-top: 1px solid {COLOR_BORDER};'>", unsafe_allow_html=True)
    st.caption(
        "🔒 **Privacy & Tenancy Protection**: All predictions and student PRN mappings are stored securely in your scoped institutional database. "
        "Predictions provide formative decision support for educators and must be paired with compassionate human discussion."
    )
