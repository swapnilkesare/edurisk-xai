import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px

# Check if model exists
MODEL_READY = os.path.exists('models/artifacts/best_model.pkl')

if MODEL_READY:
    from src.predict import Predictor
    from src.explain import Explainer
    from src.intervention import InterventionEngine

st.set_page_config(page_title="Phase 2 Research Prototype", layout="wide")

st.sidebar.title("EduRisk XAI")
page = st.sidebar.radio("Navigation", [
    "Home / Overview",
    "Model Comparison",
    "Predict Student Risk",
    "Research Gap Demonstration"
])

st.sidebar.markdown("---")
st.sidebar.info("Phase 2 — Research Demonstration Prototype")

if page == "Home / Overview":
    st.title("Understand student risk — not just predict it.")
    st.write("Existing student prediction systems may be accurate but can be difficult for educators to understand and deploy.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("FOUR RESEARCH GAPS")
        st.markdown("""
        - ❌ No consensus on best model
        - ❌ Deep models lack transparency
        - ❌ High computational cost
        - ❌ Black-box trust barrier
        """)
    with col2:
        st.subheader("How our prototype responds")
        st.markdown("""
        - ✅ Four-model comparison
        - ✅ Lightweight CPU-based ML
        - ✅ SHAP explanations
        - ✅ Teacher-friendly reasoning
        """)
        
    if st.button("Initialize & Train Models (Run Demonstration Setup)"):
        with st.spinner("Executing pipeline (Download Data -> Preprocess -> SMOTE -> Train 4 Models -> Evaluate -> Select)..."):
            from src.data_loader import DataLoader
            from src.train import ModelTrainer
            loader = DataLoader()
            df = loader.load_data()
            trainer = ModelTrainer(df)
            trainer.run_training_pipeline()
            st.success("Pipeline executed successfully. Please navigate to Model Comparison.")

elif page == "Model Comparison":
    st.title("Four-Model Comparison")
    st.write("Results from the Stratified K-Fold CV GridSearch.")
    
    if not os.path.exists('results/model_comparison.json'):
        st.warning("No metrics found. Please run the training pipeline on the Home page.")
    else:
        with open('results/model_comparison.json', 'r') as f:
            data = json.load(f)
            
        metrics_df = pd.DataFrame(data['metrics'])
        st.dataframe(metrics_df[['Model', 'CV Macro F1', 'Test Accuracy', 'Test Recall', 'Training Time (s)', 'Inference Time (ms)']])
        
        st.markdown("---")
        st.subheader(f"SELECTED MODEL: {data['selected_model']}")
        st.info(f"**SELECTION REASON:** {data['selection_reason']}")
        
        # Load runtimes
        if os.path.exists('results/runtime_metrics.json'):
            with open('results/runtime_metrics.json', 'r') as f:
                runtimes = json.load(f)
            st.write(f"**Actual Training Time:** {runtimes['Training Time (s)']:.2f} seconds")
            st.write(f"**Actual Inference Time:** {runtimes['Inference Time (ms/sample)']:.4f} milliseconds")
            st.write(f"**Actual Model Size:** {runtimes['Model Size (KB)']:.1f} KB")

elif page == "Predict Student Risk":
    st.title("Student Risk Assessment")
    
    if not MODEL_READY:
        st.warning("Model not ready. Go to Home and Initialize.")
        st.stop()
        
    st.write("Demonstration Scenarios:")
    colA, colB, colC = st.columns(3)
    if colA.button("DEMO STUDENT A (Healthy)"):
        st.session_state['att'] = 95
        st.session_state['ass'] = 90
        st.session_state['test'] = 80
        st.session_state['study'] = 12.0
    if colB.button("DEMO STUDENT B (Borderline)"):
        st.session_state['att'] = 75
        st.session_state['ass'] = 65
        st.session_state['test'] = 55
        st.session_state['study'] = 5.0
    if colC.button("DEMO STUDENT C (At-Risk)"):
        st.session_state['att'] = 45
        st.session_state['ass'] = 30
        st.session_state['test'] = 30
        st.session_state['study'] = 2.0
        
    st.markdown("---")
    
    att = st.slider("Attendance Rate %", 0, 100, st.session_state.get('att', 85))
    ass = st.slider("Assignment Submission Frequency %", 0, 100, st.session_state.get('ass', 80))
    test = st.slider("Internal Test Score", 0, 100, st.session_state.get('test', 65))
    study = st.slider("Study Hours (weekly)", 0.0, 20.0, st.session_state.get('study', 5.0))
    
    if st.button("PREDICT RISK", type="primary"):
        predictor = Predictor()
        student_data = {
            'attendance_rate': att,
            'study_hours': study,
            'internal_test_score': test,
            'assignment_submission_frequency': ass
        }
        
        result = predictor.predict(student_data)
        st.session_state['pred_result'] = result
        st.session_state['input_df'] = result['input_df']
        
    if 'pred_result' in st.session_state:
        res = st.session_state['pred_result']
        color = "red" if res['risk_tier'] == "HIGH" else "orange" if res['risk_tier'] == "MODERATE" else "green"
        
        st.markdown(f"### Risk: <span style='color:{color}'>{res['risk_tier']} RISK</span>", unsafe_allow_html=True)
        st.write(f"**Predicted Risk Probability:** {res['probability']:.1%}")
        st.caption("Model-based decision-support estimate. Not real student data.")
        
        st.markdown("---")
        
        if st.button("WHY? (Generate Explanation)"):
            explainer = Explainer()
            shap_res = explainer.explain(st.session_state['input_df'])
            
            st.subheader("WHY WAS THIS STUDENT FLAGGED?")
            for c in shap_res['contributions']:
                arrow = "↑" if c['type'] == 'risk' else "↓"
                text = "Increased predicted risk" if c['type'] == 'risk' else "Reduced predicted risk"
                st.write(f"**{c['feature']}**\n\n{arrow} {text}")
                
            st.subheader("PLAIN-ENGLISH EXPLANATION")
            risk_factors = [c['feature'] for c in shap_res['contributions'] if c['type'] == 'risk' and c['value'] > 0]
            if risk_factors:
                st.write(f"The strongest model contributions toward the predicted risk were {', '.join(risk_factors)}.")
            else:
                st.write("The model did not identify strong risk factors.")
                
            st.subheader("RECOMMENDED ACTION")
            engine = InterventionEngine()
            actions = engine.generate_recommendations(shap_res['contributions'])
            if actions:
                for a in actions:
                    st.success(f"**Risk Factor:** {a['risk_factor']}\n\n**Suggested Action:** {a['action']}")
            else:
                st.info("No targeted interventions required.")

elif page == "Research Gap Demonstration":
    st.title("Research Gap → Implemented Response")
    
    st.markdown("### Gap 1: No consensus on best model")
    st.write("**Response:** Four-model empirical comparison (See Model Comparison page)")
    
    st.markdown("### Gap 2: Deep models lack transparency")
    st.write("**Response:** Lightweight ML + SHAP (See Predict Student Risk page > WHY?)")
    
    st.markdown("### Gap 3: High compute / opaque network")
    st.write("**Response:** CPU-based lightweight models with measured runtime (See Model Comparison page metrics)")
    
    st.markdown("### Gap 4: Black-box trust barrier")
    st.write("**Response:** Teacher-readable feature-level explanations and recommended support actions.")
