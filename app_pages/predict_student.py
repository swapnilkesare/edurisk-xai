"""
Page: Teacher-Facing Student Risk Prediction & Support Recommendations
Provides an accessible, intuitive interface for teachers to assess student academic vulnerability,
understand key contributing factors, and receive practical pedagogical interventions.
"""
import streamlit as st
import pandas as pd
from config.settings import CORE_FEATURES

# Reassuring presets for teachers wanting a quick walkthrough
TEACHER_PROFILES = {
    "Custom Student Record": None,
    "Example 1: Student Falling Behind (Needs Prompt Support)": {
        "student_name": "Student A",
        "attendance_rate": 58.0,
        "internal_test_score": 28.0,
        "assignment_submission_frequency": 45.0,
        "study_hours": 1.5,
        "failures": 2,
    },
    "Example 2: Borderline Student (Needs Light Monitoring)": {
        "student_name": "Student B",
        "attendance_rate": 74.0,
        "internal_test_score": 52.0,
        "assignment_submission_frequency": 70.0,
        "study_hours": 3.0,
        "failures": 0,
    },
    "Example 3: Student On Track (Standard Progress)": {
        "student_name": "Student C",
        "attendance_rate": 96.0,
        "internal_test_score": 88.0,
        "assignment_submission_frequency": 95.0,
        "study_hours": 6.5,
        "failures": 0,
    }
}

def render_predict_student(prediction_service, current_user=None):
    # Top Header & Navigation Bar Action
    col_hdr_title, col_hdr_back = st.columns([4, 1])
    with col_hdr_title:
        st.markdown("""
        <div style="padding: 0.5rem 0 0.5rem 0;">
            <h1 style="color: var(--text-primary, #0f172a); font-size: 2rem; font-weight: 700; margin-bottom: 0.25rem;">
                🎯 Student Academic Risk Assessment
            </h1>
            <p style="color: var(--text-secondary, #475569); font-size: 1.05rem; margin: 0;">
                Enter student indicators to assess support needs and review tailored pedagogical actions.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_hdr_back:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🏠 Return to Home", use_container_width=True, key="top_back_to_home_btn"):
            st.session_state.current_page = "🏠 Home"
            st.rerun()

    # Verify model readiness
    if not prediction_service.is_model_ready():
        st.error(
            "⚠️ **Assessment Engine Unavailable**: The prediction model is not currently loaded. "
            "Please contact your school administrator or check the Research & Admin section to train the baseline model."
        )
        return

    # Check if a preselected student was dispatched from the Roster
    preselected = st.session_state.get("selected_student_for_assessment")

    # Check if a prediction result already exists in session state
    has_active_prediction = "current_prediction" in st.session_state and st.session_state.current_prediction is not None

    # Step 1 & 2: Assessment Input Form
    with st.expander("📝 Student Information & Assessment Form", expanded=not has_active_prediction):
        # Profile preset selector
        col_preset, col_reset = st.columns([3, 1])
        with col_preset:
            selected_profile = st.selectbox(
                "Load a sample student profile (optional):",
                list(TEACHER_PROFILES.keys()),
                index=0,
                help="Select an example profile to test the assessment or choose Custom Student Record to enter your own."
            )
        with col_reset:
            if st.button("🔄 Clear Form", use_container_width=True, key="clear_assessment_form_btn"):
                st.session_state.pop("current_prediction", None)
                st.session_state.pop("selected_student_for_assessment", None)
                st.rerun()

        preset_vals = TEACHER_PROFILES.get(selected_profile) or {}

        # Default student name & ID
        def_name = preselected["student_name"] if preselected else preset_vals.get("student_name", "Alex J.")
        def_id = preselected["student_id"] if preselected else "STU-2026-042"

        # Section A: Student Information
        st.markdown("#### 1. Student Identification (Local Reference)")
        col_name, col_id = st.columns(2)
        with col_name:
            student_name = st.text_input(
                "Student Name or Alias (Optional)",
                value=def_name,
                help="Used only to personalize the support plan. Never stored outside this local application."
            )
        with col_id:
            student_id = st.text_input(
                "Student Reference ID / Roll Number",
                value=def_id,
                help="A unique reference code for keeping records organized."
            )

        st.markdown("---")

        # Section B: Academic Performance
        st.markdown("#### 2. Academic Performance")
        st.caption("Provide current grades and formative exam results.")
        col_acad1, col_acad2 = st.columns(2)
        with col_acad1:
            internal_test = st.slider(
                "Internal Assessment / Midterm Score (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(preset_vals.get("internal_test_score", 65.0)),
                step=1.0,
                help="Student's most recent formative test or internal exam score (0-100%)."
            )
        with col_acad2:
            failures_opt = st.selectbox(
                "Prior Course Difficulties / Past Incomplete Terms",
                options=[0, 1, 2, 3],
                index=int(min(preset_vals.get("failures", 0), 3)),
                help="Number of previous terms where remediation or credit retrieval was required (0 to 3+)."
            )

        st.markdown("---")

        # Section C: Engagement & Attendance
        st.markdown("#### 3. Classroom Engagement & Attendance")
        st.caption("Provide attendance consistency, assignment completion, and study time.")
        col_att1, col_att2, col_att3 = st.columns(3)
        with col_att1:
            attendance = st.slider(
                "Course Attendance Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(preset_vals.get("attendance_rate", 82.0)),
                step=1.0,
                help="Percentage of scheduled class periods attended so far this term."
            )
        with col_att2:
            submission_freq = st.slider(
                "Assignment Submission Consistency (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(preset_vals.get("assignment_submission_frequency", 75.0)),
                step=1.0,
                help="Proportion of regular homework assignments and lab reports turned in on time."
            )
        with col_att3:
            study_hrs = st.number_input(
                "Self-Directed Study Hours (Per Week)",
                min_value=0.0,
                max_value=40.0,
                value=float(preset_vals.get("study_hours", 3.5)),
                step=0.5,
                help="Estimated hours spent studying and doing coursework independently each week."
            )

        st.markdown("---")

        # Section D: Contextual Factors (Optional Expander)
        with st.expander("➕ Additional Learning Context (Family Support, Activities, Internet Access)", expanded=False):
            st.caption("These non-academic factors help the underlying AI system build an equitable, balanced assessment.")
            col_ctx1, col_ctx2 = st.columns(2)
            with col_ctx1:
                school_support = st.selectbox("Currently receiving school learning support / tutoring?", ["no", "yes"], index=0)
                family_support = st.selectbox("Receives academic encouragement at home?", ["yes", "no"], index=0)
                internet_access = st.selectbox("Reliable internet connectivity at home?", ["yes", "no"], index=0)
            with col_ctx2:
                extracurricular = st.selectbox("Participates in extracurricular activities / sports?", ["yes", "no"], index=0)
                travel_time = st.selectbox(
                    "Commute time to institution",
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

        # Primary Single Action Button
        predict_clicked = st.button(
            "🔮 Assess Student Risk",
            type="primary",
            use_container_width=True,
            key="btn_run_student_risk_assessment"
        )

        if predict_clicked:
            with st.spinner("Analyzing student indicators and matching supportive pedagogical interventions..."):
                try:
                    org_id = current_user.organization_id if current_user else None
                    user_id = current_user.id if current_user else None

                    result = prediction_service.predict_and_explain(
                        student_data=student_data,
                        student_identifier=student_id or "STU-ANONYMOUS",
                        save_to_db=True,
                        organization_id=org_id,
                        created_by_user_id=user_id
                    )
                    st.session_state.current_prediction = result
                    st.session_state.current_student_name = student_name or "This student"
                    st.success("✅ Assessment complete! Review the results and recommendations below.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not complete assessment: {e}")

    # Step 3: Results and Support Section
    if has_active_prediction:
        result = st.session_state.current_prediction
        pred = result["prediction"]
        shap_res = result.get("shap", {})
        interventions = result.get("interventions", [])
        student_display_name = st.session_state.get("current_student_name", "This student")

        st.markdown("---")
        st.markdown(f"## 📊 Assessment Results for **{student_display_name}**")

        # 1. Plain-Language Risk Assessment Header Card
        risk_tier = pred.get("risk_tier", "LOW").upper()
        prob_val = pred.get("risk_probability", 0.0)

        if risk_tier == "HIGH":
            banner_border = "#ef4444"
            banner_title = "⚠️ Priority Support Recommended (High Academic Risk)"
            badge_html = "<span style='background-color: #ef4444; color: #ffffff; padding: 4px 12px; border-radius: 12px; font-weight: 600; font-size: 0.9rem;'>Priority Support</span>"
            summary_desc = (
                f"Based on current marks and attendance patterns, <strong>{student_display_name}</strong> is showing "
                "strong indicators of academic vulnerability. Proactive, personalized assistance is advised to help them stay on track."
            )
        elif risk_tier == "MODERATE":
            banner_border = "#f59e0b"
            banner_title = "⚡ Monitoring Advised (Moderate Risk)"
            badge_html = "<span style='background-color: #f59e0b; color: #ffffff; padding: 4px 12px; border-radius: 12px; font-weight: 600; font-size: 0.9rem;'>Monitoring Advised</span>"
            summary_desc = (
                f"<strong>{student_display_name}</strong> is currently in a borderline range. "
                "Early check-ins and light academic mentoring can prevent emerging learning gaps from compounding."
            )
        else:
            banner_border = "#10b981"
            banner_title = "✅ On Track (Lower Predicted Risk)"
            badge_html = "<span style='background-color: #10b981; color: #ffffff; padding: 4px 12px; border-radius: 12px; font-weight: 600; font-size: 0.9rem;'>On Track</span>"
            summary_desc = (
                f"<strong>{student_display_name}</strong> demonstrates healthy engagement and performance indicators. "
                "Continue standard instructional guidance and encourage their consistent study habits."
            )

        st.markdown(f"""
        <div style="background-color: var(--bg-card, #f8fafc); 
                    border: 2px solid {banner_border}; 
                    border-radius: 12px; 
                    padding: 1.5rem; 
                    margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <h3 style="margin: 0; color: var(--text-primary, #0f172a); font-size: 1.25rem;">{banner_title}</h3>
                {badge_html}
            </div>
            <p style="color: var(--text-secondary, #334155); font-size: 1.05rem; margin-bottom: 0; line-height: 1.5;">
                {summary_desc}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # 2. Prediction Metrics
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric(
                label="Estimated Risk Probability",
                value=f"{prob_val:.1%}",
                help="Algorithmic probability that the student will require remediation under current conditions."
            )
        with col_m2:
            st.metric(
                label="Action Urgency",
                value=pred.get("urgency", "Standard Guidance")
            )
        with col_m3:
            st.metric(
                label="Identified Support Opportunities",
                value=f"{len(interventions)} Action Items"
            )

        st.caption(
            "ℹ️ *Note: This probability represents an algorithmic estimate based on historical student patterns, "
            "not a fixed prediction or guarantee of future performance. Use it as an early heads-up to guide supportive conversations.*"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # 3. Main Contributing Factors
        st.markdown("### 🔍 Main Contributing Factors")
        st.caption("Here are the main student indicators influencing this assessment:")

        risk_increasing = shap_res.get("risk_increasing_factors", [])
        protective_factors = shap_res.get("protective_factors", [])

        col_factors1, col_factors2 = st.columns(2)

        with col_factors1:
            st.markdown("#### 🔻 Factors Increasing Academic Concern")
            if risk_increasing:
                for item in risk_increasing[:3]:
                    feat_name = item["feature"].replace("_", " ").title()
                    raw_v = item.get("raw_value")
                    val_display = f"({raw_v})" if raw_v is not None else ""
                    st.markdown(f"""
                    <div style="background-color: var(--bg-card, #fff1f2); border-left: 4px solid #ef4444; border: 1px solid var(--border-color, #fecdd3); padding: 10px 14px; border-radius: 6px; margin-bottom: 8px;">
                        <strong style="color: #ef4444;">{feat_name} {val_display}</strong><br>
                        <span style="color: var(--text-secondary, #4c0519); font-size: 0.9rem;">Elevated predicted academic risk.</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: var(--bg-card, #f8fafc); border: 1px solid var(--border-color, #e2e8f0); padding: 10px 14px; border-radius: 6px; color: var(--text-muted, #64748b); font-size: 0.95rem;">
                    No critical risk-increasing factors detected.
                </div>
                """, unsafe_allow_html=True)

        with col_factors2:
            st.markdown("#### 🛡️ Protective Factors Supporting Stability")
            if protective_factors:
                for item in protective_factors[:3]:
                    feat_name = item["feature"].replace("_", " ").title()
                    raw_v = item.get("raw_value")
                    val_display = f"({raw_v})" if raw_v is not None else ""
                    st.markdown(f"""
                    <div style="background-color: var(--bg-card, #f0fdf4); border-left: 4px solid #10b981; border: 1px solid var(--border-color, #bbf7d0); padding: 10px 14px; border-radius: 6px; margin-bottom: 8px;">
                        <strong style="color: #10b981;">{feat_name} {val_display}</strong><br>
                        <span style="color: var(--text-secondary, #14532d); font-size: 0.9rem;">Acted as a positive buffer against academic difficulty.</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: var(--bg-card, #f8fafc); border: 1px solid var(--border-color, #e2e8f0); padding: 10px 14px; border-radius: 6px; color: var(--text-muted, #64748b); font-size: 0.95rem;">
                    No notable protective buffers identified.
                </div>
                """, unsafe_allow_html=True)

        # Plain language summary sentences if available
        if shap_res.get("plain_language_summary"):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Plain Language Summary:**")
            for sentence in shap_res["plain_language_summary"][:3]:
                st.write(f"• {sentence}")

        # Secondary Technical Explanation Expander (kept for researchers / audit)
        with st.expander("🔬 View Technical Explanation (For Data Specialists & Researchers)"):
            st.caption("Detailed SHAP (SHapley Additive exPlanations) values decompose the underlying model score.")
            st.write(f"**Baseline Average Risk:** {shap_res.get('base_value', 0.5):.4f}")
            if shap_res.get("contributions"):
                df_shap = pd.DataFrame(shap_res["contributions"])
                if "raw_value" in df_shap.columns:
                    df_shap["raw_value"] = df_shap["raw_value"].astype(str)
                st.dataframe(
                    df_shap[["feature", "raw_value", "shap_value", "is_risk_increasing"]],
                    use_container_width=True
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # 4. Recommended Support (Pedagogical Interventions)
        st.markdown("### 🤝 Recommended Pedagogical Support Actions")
        st.caption("Targeted, non-judgmental support strategies based on the identified risk drivers:")

        if interventions:
            for idx, item in enumerate(interventions):
                prio = item.get("priority", "MEDIUM")
                prio_color = {"HIGH": "#ef4444", "MEDIUM": "#f59e0b", "LOW": "#10b981"}.get(prio, "#64748b")
                
                st.markdown(f"""
                <div style="background-color: var(--bg-card, #f8fafc); border: 1px solid var(--border-color, #e2e8f0); border-left: 5px solid {prio_color}; border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <h4 style="margin: 0; color: var(--text-primary, #0f172a);">📌 {item.get('action', 'Academic Support Action')}</h4>
                        <span style="background-color: {prio_color}; color: #ffffff; padding: 2px 8px; border-radius: 8px; font-size: 0.8rem; font-weight: 600;">
                            {prio} Priority
                        </span>
                    </div>
                    <p style="color: var(--text-secondary, #475569); margin: 0.5rem 0 0.25rem 0; font-size: 0.95rem;">
                        <strong>Why this helps:</strong> {item.get('rationale', 'Assists student engagement and concept mastery.')}
                    </p>
                    <p style="color: var(--text-muted, #94a3b8); font-size: 0.85rem; margin: 0;">
                        Targeted Indicator: <code>{item.get('feature', 'Engagement')}</code>
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("🎉 No immediate high-priority interventions required. Standard classroom engagement recommended.")

        st.markdown("<br>", unsafe_allow_html=True)

        # 5. Bottom Navigation & Action Buttons
        col_new, col_home_bot, col_space = st.columns([1, 1, 2])
        with col_new:
            if st.button("🔄 Assess Another Student", type="primary", use_container_width=True, key="assess_another_student_btn"):
                st.session_state.pop("current_prediction", None)
                st.session_state.pop("current_student_name", None)
                st.session_state.pop("selected_student_for_assessment", None)
                st.rerun()
        with col_home_bot:
            if st.button("🏠 Return to Home", use_container_width=True, key="bottom_return_home_btn"):
                st.session_state.pop("selected_student_for_assessment", None)
                st.session_state.current_page = "🏠 Home"
                st.rerun()

    st.markdown("<br><hr style='border: none; border-top: 1px solid var(--border-color, #e2e8f0);'>", unsafe_allow_html=True)
    st.caption(
        "🔒 **Privacy & Ethical Safeguard**: All assessments are calculated locally in your session. "
        "Predictions provide formative decision support for educators and must be paired with compassionate human discussion."
    )
