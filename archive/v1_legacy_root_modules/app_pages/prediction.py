import streamlit as st
import pandas as pd
from services.prediction_service import PredictionService
import plotly.graph_objects as go
import time

def app():
    st.title("Predict Student Risk")
    st.markdown("Enter student metrics to predict academic risk using the SRC-RI framework.")

    try:
        service = PredictionService()
    except Exception as e:
        st.warning("No trained model available. Please go to Model Training first.")
        return

    with st.form("prediction_form"):
        st.subheader("Core Academic & Behavioral Metrics")
        
        col1, col2 = st.columns(2)
        with col1:
            attendance_rate = st.slider("Attendance Rate (%)", 0, 100, 85)
            study_hours = st.slider("Study Hours (per week)", 0.0, 20.0, 5.0)
            
        with col2:
            internal_test_score = st.slider("Internal Test Score (0-100)", 0, 100, 65)
            assignment_freq = st.slider("Assignment Submission Frequency (%)", 0, 100, 80)
            
        st.subheader("Additional Context")
        student_id = st.text_input("Student Identifier (optional, for tracking)")
        failures = st.selectbox("Previous Failures", [0, 1, 2, 3])
        sex = st.selectbox("Sex", ['F', 'M'])
        internet = st.selectbox("Internet Access at Home", ['yes', 'no'])

        submit = st.form_submit_button("PREDICT RISK")

    if submit:
        features = {
            "attendance_rate": attendance_rate,
            "study_hours": study_hours,
            "internal_test_score": internal_test_score,
            "assignment_submission_frequency": assignment_freq,
            "failures": failures,
            "sex": sex,
            "internet": internet
        }
        
        with st.spinner("Executing SRC-RI Pipeline..."):
            result = service.run_src_ri(features, student_identifier=student_id if student_id else None)
            time.sleep(0.5) # for UI effect
            
            st.markdown("---")
            st.header("Prediction Results")
            
            # 1. Risk Tier Display
            tier_color = {"HIGH": "red", "MODERATE": "orange", "LOW": "green"}[result['risk_tier']]
            st.markdown(f"### Predicted Risk Tier: <span style='color:{tier_color}'>{result['risk_tier']} RISK</span>", unsafe_allow_html=True)
            st.write(f"**Probability of being At-Risk:** {result['probability']:.1%}")
            
            st.markdown("---")
            
            col_a, col_b = st.columns(2)
            
            # 2. Risk Factors
            with col_a:
                st.subheader("Top Risk Factors")
                if result['risk_factors']:
                    for factor in result['risk_factors'][:3]:
                        st.write(f"- **{factor['feature']}** contributed positively to risk.")
                else:
                    st.write("No major risk-increasing factors found.")
                    
            # 3. Recommended Interventions
            with col_b:
                st.subheader("Recommended Interventions")
                if result['interventions']:
                    for r in result['interventions']:
                        st.info(f"**Action:** {r['recommended_action']}\n\n*Triggered by: {r['risk_factor']}*")
                else:
                    st.success("No interventions currently recommended.")

            # Store result in session state for Explainability page
            st.session_state['last_prediction'] = result
            st.session_state['last_features'] = features
            
            st.markdown("👉 **Go to 'Explainability' for a detailed SHAP visual breakdown.**")
