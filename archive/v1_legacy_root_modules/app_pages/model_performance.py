import streamlit as st
from ml.train import load_current_model
import pandas as pd

def app():
    st.title("Model Performance")
    
    artifact = load_current_model()
    
    if not artifact:
        st.warning("No model has been trained yet.")
        return
        
    st.subheader(f"Current Active Model: {artifact['model_name']} ({artifact['version']})")
    st.write(f"**Trained on:** {artifact['timestamp']}")
    
    st.markdown("### Metrics on Independent Test Set")
    metrics = artifact['metrics']
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Macro F1", f"{metrics.get('Macro F1', 0):.4f}")
    col2.metric("High-Risk Recall", f"{metrics.get('Recall (High-Risk)', 0):.4f}")
    col3.metric("Accuracy", f"{metrics.get('Accuracy', 0):.4f}")
    
    st.markdown("### Confusion Matrix")
    cm = metrics.get('Confusion Matrix', [[0,0],[0,0]])
    st.write(pd.DataFrame(cm, index=["Actual Not At-Risk", "Actual At-Risk"], columns=["Pred Not At-Risk", "Pred At-Risk"]))
    
    st.markdown("---")
    st.write("**Features Used:**", ", ".join(artifact['feature_names']))
