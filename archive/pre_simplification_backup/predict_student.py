"""
Page: Predict Student Risk
"""
import streamlit as st
import pandas as pd
from config.settings import CORE_FEATURES

DEMO_SCENARIOS = {
    "Custom Input": None,
    "[DEMO] Academically Vulnerable Student": {
        "attendance_rate": 55.0,
        "internal_test_score": 38.0,
        "assignment_submission_frequency": 45.0,
        "study_hours": 1.5,
        "failures": 2,
    },
    "[DEMO] Borderline / Moderate-Risk Student": {
        "attendance_rate": 72.0,
        "internal_test_score": 52.0,
        "assignment_submission_frequency": 68.0,
        "study_hours": 2.5,
        "failures": 0,
    },
    "[DEMO] High-Performing / Low-Risk Student": {
        "attendance_rate": 96.0,
        "internal_test_score": 88.0,
        "assignment_submission_frequency": 95.0,
        "study_hours": 7.5,
        "failures": 0,
    }
}

def render_predict_student(prediction_service):
    st.title("🎯 Predict Student Academic Risk")
    st.markdown("Evaluate student vulnerability using the active trained model pipeline.")

    if not prediction_service.is_model_ready():
        st.warning("⚠️ No trained model available. Please visit the **Model Training** page first to train the classifiers.")
        return

    meta = prediction_service.metadata
    st.caption(f"Active Model: **{meta.get('selected_model', 'N/A')}** ({meta.get('model_version', 'v1.0')})")

    # Scenario Selection
    col_scen, col_id = st.columns([2, 1])
    with col_scen:
        selected_scenario = st.selectbox("Load Example Demonstration Profile:", list(DEMO_SCENARIOS.keys()))
    with col_id:
        student_id = st.text_input("Student Identifier / Roll No.", value="STU-2026-081")

    scenario_vals = DEMO_SCENARIOS.get(selected_scenario) or {}

    st.markdown("#### Input Academic & Behavioral Indicators")
    col1, col2 = st.columns(2)

    with col1:
        att = st.slider(
            "Attendance Rate (%)",
            min_value=0.0, max_value=100.0,
            value=float(scenario_vals.get("attendance_rate", 75.0)),
            step=1.0, help="Percentage of instructional class sessions attended."
        )
        test_score = st.slider(
            "Internal Test Score (%)",
            min_value=0.0, max_value=100.0,
            value=float(scenario_vals.get("internal_test_score", 60.0)),
            step=1.0, help="Formative internal assessment / midterm score."
        )

    with col2:
        assign_sub = st.slider(
            "Assignment Submission Rate (%)",
            min_value=0.0, max_value=100.0,
            value=float(scenario_vals.get("assignment_submission_frequency", 80.0)),
            step=1.0, help="Frequency of timely coursework submissions."
        )
        study_hrs = st.slider(
            "Weekly Independent Study Hours (hrs/wk)",
            min_value=0.0, max_value=30.0,
            value=float(scenario_vals.get("study_hours", 4.0)),
            step=0.5, help="Estimated self-study hours outside class."
        )

    # Contextual features if supported by active model
    features_in_model = meta.get("feature_columns", CORE_FEATURES)
    student_dict = {
        "attendance_rate": att,
        "internal_test_score": test_score,
        "assignment_submission_frequency": assign_sub,
        "study_hours": study_hrs,
    }

    # Add defaults for extended features if the pipeline requires them
    for feat in features_in_model:
        if feat not in student_dict:
            if feat == "failures":
                student_dict[feat] = scenario_vals.get("failures", 0)
            elif feat in ["Medu", "Fedu"]:
                student_dict[feat] = 3
            elif feat in ["Dalc", "Walc", "health", "goout", "traveltime"]:
                student_dict[feat] = 2
            elif feat in ["age"]:
                student_dict[feat] = 17
            elif feat in ["sex"]:
                student_dict[feat] = "F"
            elif feat in ["address"]:
                student_dict[feat] = "U"
            elif feat in ["famsize"]:
                student_dict[feat] = "GT3"
            elif feat in ["Pstatus"]:
                student_dict[feat] = "T"
            else:
                student_dict[feat] = "no"

    st.markdown("---")

    predict_btn = st.button("🔮 Run Academic Risk Inference", type="primary", use_container_width=True)

    if predict_btn:
        with st.spinner("Executing pipeline inference, SHAP attribution, and intervention matching..."):
            inference_result = prediction_service.predict_and_explain(
                student_data=student_dict,
                student_identifier=student_id,
                save_to_db=True
            )

        st.session_state.current_prediction = inference_result
        pred = inference_result["prediction"]

        st.markdown("### 📋 Prediction Outcome")
        col_res1, col_res2, col_res3 = st.columns(3)

        with col_res1:
            tier = pred["risk_tier"]
            color_map = {"HIGH": "🔴", "MODERATE": "🟡", "LOW": "🟢"}
            st.metric("Operational Risk Tier", f"{color_map.get(tier, '')} {tier} RISK")

        with col_res2:
            st.metric("Predicted Failure Probability", f"{pred['risk_probability']:.2%}")

        with col_res3:
            st.metric("Classification Output", "At-Risk (1)" if pred["is_at_risk"] else "On-Track (0)")

        # Urgency recommendation alert
        if tier == "HIGH":
            st.error(f"🚨 **High Risk Advisory**: {pred['urgency']}")
        elif tier == "MODERATE":
            st.warning(f"⚠️ **Moderate Risk Advisory**: {pred['urgency']}")
        else:
            st.success(f"✅ **Low Risk Advisory**: {pred['urgency']}")

        st.info("💡 SHAP feature attributions and deterministic interventions have been generated. Inspect them in the **Explainability** and **Recommended Support** pages.")

    st.markdown("---")
    st.caption("🔒 **Privacy & Ethical Disclaimer**: Predictions represent automated advisory indicators for faculty mentoring. Institutional deployment requires privacy protocols, access control, and human oversight.")
