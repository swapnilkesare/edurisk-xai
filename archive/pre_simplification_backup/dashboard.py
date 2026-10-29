"""
Page: Home / Research Overview
"""
import streamlit as st
from config.settings import ARTIFACTS_DIR, RAW_DATA_PATH
import json

def render_dashboard(prediction_service, training_service):
    st.title("🎓 EduRisk XAI")
    st.subheader("Research-Grade Student Academic Risk Prediction, Explainability, and Intervention Framework")

    st.markdown("""
    **EduRisk XAI** is a transparent, lightweight machine-learning decision support system engineered for secondary and post-secondary educational institutions. 
    It identifies academically vulnerable students early in the term, produces model-faithful **SHAP explanations**, and maps verified risk factors to **deterministic pedagogical interventions**.
    """)

    # High-level Metric Badges
    col1, col2, col3, col4 = st.columns(4)

    is_model_ready = prediction_service.is_model_ready()
    meta = prediction_service.metadata

    with col1:
        st.metric(
            label="Model Status",
            value="Active & Fitted" if is_model_ready else "Untrained",
            delta="Ready for Inference" if is_model_ready else "Train Model First"
        )
    with col2:
        selected_model = meta.get("selected_model", "None")
        st.metric(label="Selected Model", value=selected_model)
    with col3:
        best_cv_f1 = "N/A"
        if is_model_ready and "models" in meta and selected_model in meta["models"]:
            best_cv_f1 = f"{meta['models'][selected_model].get('cv_macro_f1', 0):.4f}"
        st.metric(label="CV Macro F1", value=best_cv_f1)
    with col4:
        data_source = meta.get("dataset", {}).get("name", "UCI Portuguese Cohort")
        is_syn = meta.get("dataset", {}).get("is_synthetic", False)
        st.metric(
            label="Dataset Mode",
            value="Synthetic Demo" if is_syn else "Benchmark Public",
            delta="[DEMO DATA]" if is_syn else "Cortez & Silva (2008)"
        )

    if is_syn:
        st.warning("⚠️ **Active dataset is labeled as [SYNTHETIC / DEMO DATA]**. Demonstrations using synthetic data do not constitute empirical evidence of real-world academic risk.")

    st.markdown("---")

    # Five-Phase Methodology
    st.markdown("### 🔬 Five-Phase Research Methodology")

    phase_cols = st.columns(5)

    with phase_cols[0]:
        st.markdown("""
        **Phase 1: Acquisition**
        - Schema validation
        - Core 4 features
        - Stratified 80/20 split
        - In-fold SMOTE
        """)

    with phase_cols[1]:
        st.markdown("""
        **Phase 2: Modeling**
        - Decision Tree
        - Support Vector (SVC)
        - Logistic Regression
        - Random Forest
        """)

    with phase_cols[2]:
        st.markdown("""
        **Phase 3: Explainability**
        - Local SHAP values
        - Directional factors
        - Global feature importance
        - Additive consistency
        """)

    with phase_cols[3]:
        st.markdown("""
        **Phase 4: Dashboard**
        - Educator UI
        - Zero code required
        - Audited persistence
        - Longitudinal trends
        """)

    with phase_cols[4]:
        st.markdown("""
        **Phase 5: Intervention**
        - Deterministic rules
        - Priority ranking
        - Teacher review
        - Actionable support
        """)

    st.markdown("---")

    # Research Integrity & Non-Causality Disclaimers
    st.markdown("### ⚖️ Research Integrity & Responsible AI Disclaimers")
    col_disc1, col_disc2 = st.columns(2)

    with col_disc1:
        st.info("""
        **Decision Support, Not Determinism**  
        EduRisk XAI produces probabilistic risk categorizations to assist educational advisors. It is not an automated decision-maker and must never be utilized to enact punitive sanctions or restrict student opportunities.
        """)

    with col_disc2:
        st.info("""
        **Attribution vs. Causality**  
        SHAP values illustrate how input attributes altered the model's mathematical prediction score. SHAP attributions do not prove causal relationships. Remedying an isolated risk indicator does not automatically guarantee student success.
        """)
