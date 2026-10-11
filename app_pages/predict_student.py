"""
Page: Teacher-Facing Student Risk Prediction & Support Recommendations
Provides an intuitive, non-technical interface for teachers to assess student academic vulnerability,
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

def render_predict_student(prediction_service):
    st.markdown("""
    <div style="padding: 1rem 0 0.5rem 0;">
        <h1 style="color: #1e293b; font-size: 2rem; font-weight: 700; margin-bottom: 0.25rem;">
            🎯 Student Academic Risk Assessment
        </h1>
        <p style="color: #475569; font-size: 1.05rem;">
            Enter your student's current academic and attendance details to check if they may benefit from extra support.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Verify model readiness
    if not prediction_service.is_model_ready():
        st.error(
            "⚠️ **Assessment Engine Unavailable**: The prediction model is not currently loaded. "
            "Please contact your school administrator or check the Research & Admin section to train the baseline model."
        )
        return

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
            if st.button("🔄 Clear Form", use_container_width=True):
                st.session_state.pop("current_prediction", None)
                st.rerun()

        preset_vals = TEACHER_PROFILES.get(selected_profile) or {}

        # Section A: Student Information
        st.markdown("#### 1. Student Identification (Local Reference)")
        col_name, col_id = st.columns(2)
        with col_name:
            student_name = st.text_input(
                "Student Name or Alias (Optional)",
                value=preset_vals.get("student_name", "Alex J."),
                help="Used only to personalize the support plan. Never stored outside this local application."
            )
        with col_id:
            student_id = st.text_input(
                "Student Reference ID / Roll Number",
                value="STU-2026-042",
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
                format_func=lambda x: f"{x} prior failures" if x < 3 else "3 or more prior failures",
                help="Number of past courses or terms the student has failed."
            )

        st.markdown("---")

        # Section C: Attendance and Engagement
        st.markdown("#### 3. Attendance & Learning Habits")
        st.caption("Provide observations regarding attendance, assignment consistency, and independent study.")
        col_att1, col_att2, col_att3 = st.columns(3)
        with col_att1:
            attendance = st.slider(
                "Class Attendance Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(preset_vals.get("attendance_rate", 82.0)),
                step=1.0,
                help="Percentage of scheduled instructional classes attended this term."
            )
        with col_att2:
            assignment_sub = st.slider(
                "Assignment Submission Consistency (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(preset_vals.get("assignment_submission_frequency", 78.0)),
                step=1.0,
                help="Percentage of homework tasks and continuous assessments turned in on time."
            )
        with col_att3:
            study_hrs = st.slider(
                "Weekly Independent Study (Hours/Week)",
                min_value=0.0,
                max_value=25.0,
                value=float(preset_vals.get("study_hours", 4.0)),
                step=0.5,
                help="Estimated hours spent studying or doing coursework outside instructional time."
            )

        # Section D: Additional Context (Optional Expander)
        with st.expander("➕ Additional Background Context (Optional — Sensible Defaults Applied)"):
            st.caption("These additional factors provide nuanced context. Standard default assumptions are pre-filled.")
            col_ctx1, col_ctx2 = st.columns(2)
            with col_ctx1:
                school_support = st.selectbox("Receives Extra Institutional Tutoring / Support?", ["no", "yes"], index=0)
                family_support = st.selectbox("Receives Family Educational Support at Home?", ["yes", "no"], index=0)
                internet_access = st.selectbox("Reliable Internet Access for Study at Home?", ["yes", "no"], index=0)
            with col_ctx2:
                social_balance = st.slider("Weekly Peer Socializing Level (1: Low to 5: High)", 1, 5, 2,
                                           help="Time spent going out with friends.")
                weekend_balance = st.slider("Weekend Leisure/Socializing Level (1: Low to 5: High)", 1, 5, 2,
                                            help="Balance of weekend leisure activities.")

        # Construct complete feature payload matching model expectations
        student_data = {
            "attendance_rate": float(attendance),
            "internal_test_score": float(internal_test),
            "assignment_submission_frequency": float(assignment_sub),
            "study_hours": float(study_hrs),
            "failures": int(failures_opt),
            "schoolsup": school_support,
            "famsup": family_support,
            "internet": internet_access,
            "goout": social_balance,
            "Walc": weekend_balance,
            "Dalc": 1,
            "health": 3,
            "traveltime": 1,
            "age": 17,
            "sex": "F",
            "address": "U",
            "famsize": "GT3",
            "Pstatus": "T",
            "Medu": 3,
            "Fedu": 3,
            "activities": "yes",
            "romantic": "no",
        }

        st.markdown("<br>", unsafe_allow_html=True)
        predict_clicked = st.button(
            "🔍 Predict Student Risk & Generate Support Plan",
            type="primary",
            use_container_width=True,
            key="btn_run_prediction"
        )

        if predict_clicked:
            with st.spinner("Analyzing student indicators and matching supportive pedagogical interventions..."):
                try:
                    result = prediction_service.predict_and_explain(
                        student_data=student_data,
                        student_identifier=student_id or "STU-ANONYMOUS",
                        save_to_db=True
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
            banner_bg = "#fef2f2"
            banner_border = "#f87171"
            banner_title = "⚠️ May Need Additional Academic Support"
            badge_html = "<span style='background: #ef4444; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600; font-size: 0.9rem;'>Priority Support Recommended</span>"
            summary_desc = (
                f"Based on current marks and attendance patterns, <strong>{student_display_name}</strong> is showing "
                "strong indicators of academic vulnerability. Proactive, personalized assistance is advised to help them stay on track."
            )
        elif risk_tier == "MODERATE":
            banner_bg = "#fffbeb"
            banner_border = "#fbbf24"
            banner_title = "⚡ Keep Under Review (Moderate Risk)"
            badge_html = "<span style='background: #f59e0b; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600; font-size: 0.9rem;'>Monitoring Advised</span>"
            summary_desc = (
                f"<strong>{student_display_name}</strong> is currently in a borderline range. "
                "Early check-ins and light academic mentoring can prevent emerging learning gaps from compounding."
            )
        else:
            banner_bg = "#f0fdf4"
            banner_border = "#4ade80"
            banner_title = "✅ Lower Predicted Risk (On Track)"
            badge_html = "<span style='background: #10b981; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600; font-size: 0.9rem;'>On Track</span>"
            summary_desc = (
                f"<strong>{student_display_name}</strong> demonstrates healthy engagement and performance indicators. "
                "Continue standard instructional guidance and encourage their consistent study habits."
            )

        st.markdown(f"""
        <div style="background: {banner_bg}; border: 2px solid {banner_border}; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <h3 style="margin: 0; color: #1e293b;">{banner_title}</h3>
                {badge_html}
            </div>
            <p style="color: #334155; font-size: 1.05rem; margin-bottom: 0.5rem; line-height: 1.5;">
                {summary_desc}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # 2. Prediction Confidence & Overview Metrics
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

        # 3. Why Was This Result Produced? (Simple Plain-Language Explanation)
        st.markdown("### 🔍 Why Was This Result Produced?")
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
                    <div style="background: #fff1f2; border-left: 4px solid #f43f5e; padding: 10px 14px; border-radius: 6px; margin-bottom: 8px;">
                        <strong style="color: #9f1239;">{feat_name} {val_display}</strong><br>
                        <span style="color: #4c0519; font-size: 0.9rem;">Elevated predicted academic risk.</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: #f8fafc; padding: 10px 14px; border-radius: 6px; color: #64748b; font-size: 0.95rem;">
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
                    <div style="background: #f0fdf4; border-left: 4px solid #22c55e; padding: 10px 14px; border-radius: 6px; margin-bottom: 8px;">
                        <strong style="color: #14532d;">{feat_name} {val_display}</strong><br>
                        <span style="color: #166534; font-size: 0.9rem;">Acted as a positive buffer against academic difficulty.</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: #f8fafc; padding: 10px 14px; border-radius: 6px; color: #64748b; font-size: 0.95rem;">
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
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <h4 style="margin: 0; color: #1e293b;">📌 {item.get('action', 'Academic Support Action')}</h4>
                        <span style="background: {prio_color}; color: white; padding: 2px 8px; border-radius: 8px; font-size: 0.8rem; font-weight: 600;">
                            {prio} Priority
                        </span>
                    </div>
                    <p style="color: #475569; margin: 0.5rem 0 0.25rem 0; font-size: 0.95rem;">
                        <strong>Why this helps:</strong> {item.get('rationale', 'Assists student engagement and concept mastery.')}
                    </p>
                    <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;">
                        Targeted Indicator: <code>{item.get('feature', 'Engagement')}</code>
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("🎉 No immediate high-priority interventions required. Standard classroom engagement recommended.")

        st.markdown("<br>", unsafe_allow_html=True)

        # 5. Assess Another Student Action
        col_new, col_space = st.columns([1, 2])
        with col_new:
            if st.button("🔄 Assess Another Student", type="primary", use_container_width=True):
                st.session_state.pop("current_prediction", None)
                st.session_state.pop("current_student_name", None)
                st.rerun()

    st.markdown("<br><hr style='border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
    st.caption(
        "🔒 **Privacy & Ethical Safeguard**: All assessments are calculated locally in your session. "
        "Predictions provide formative decision support for educators and must be paired with compassionate human discussion."
    )
