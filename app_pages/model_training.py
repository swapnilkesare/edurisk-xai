"""
Page: Model Training
"""
import streamlit as st
import time
from services.training_service import TrainingService

def render_model_training(training_service, prediction_service):
    st.title("⚙️ Model Training & Pipeline Execution")
    st.markdown("Execute the data-leakage safe training pipeline across all four candidate classifiers.")

    # Check active dataset in memory
    if "active_df" not in st.session_state or st.session_state.active_df is None:
        from src.data_loader import load_dataset
        df, prov = load_dataset(fallback_to_synthetic=True)
        st.session_state.active_df = df
        st.session_state.active_provenance = prov

    df = st.session_state.active_df
    prov = st.session_state.active_provenance

    st.info(f"Target Dataset: **{prov.name}** ({len(df)} samples, {len(df.columns)-1} features) — Fingerprint: `{prov.fingerprint}`")

    if prov.is_synthetic:
        st.warning("⚠️ **Active dataset is labeled as [SYNTHETIC / DEMO DATA]**. Model metrics will reflect synthetic demonstration data.")

    # Training Configuration Panel
    with st.expander("🛠️ Pipeline & Resampling Configuration", expanded=True):
        col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
        with col_cfg1:
            use_smote = st.checkbox("Apply In-Fold SMOTE", value=True, help="Oversamples the minority risk class strictly within training folds.")
        with col_cfg2:
            st.markdown("**Split Protocol:** 80% Train, 20% Holdout Test")
        with col_cfg3:
            st.markdown("**Cross-Validation:** 5-Fold Stratified K-Fold")

    # Start Training Button
    train_button = st.button("🚀 Train All 4 Candidate Classifiers", type="primary", use_container_width=True)

    if train_button:
        progress_bar = st.progress(0, text="Initializing training pipeline...")
        status_box = st.empty()

        start_time = time.time()
        try:
            status_box.info("Step 1/4: Partitioning quarantined test set & setting up in-fold pipelines...")
            progress_bar.progress(25, text="Building GridSearch cross-validators...")

            status_box.info("Step 2/4: Optimizing Decision Tree and Support Vector Classifier...")
            progress_bar.progress(50, text="Evaluating tree and kernel models...")

            status_box.info("Step 3/4: Optimizing Logistic Regression and Random Forest...")
            progress_bar.progress(75, text="Tuning ensemble and linear models...")

            # Run full training via service
            experiment_record = training_service.run_full_training(
                df=df,
                provenance=prov,
                use_smote=use_smote
            )

            progress_bar.progress(100, text="Training complete! Artifacts serialized.")
            status_box.success(f"🎉 Training pipeline executed successfully in {time.time() - start_time:.2f}s!")

            # Refresh prediction service model state
            prediction_service._load_active_model()
            st.session_state.latest_experiment = experiment_record

        except Exception as e:
            status_box.error(f"❌ Training failed: {str(e)}")
            progress_bar.empty()
            return

    # Display Current Model Artifact Information
    st.markdown("---")
    st.subheader("Active Model Artifact Status")

    meta = prediction_service.metadata
    if prediction_service.is_model_ready() and meta:
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Selected Model", meta.get("selected_model", "Unknown"))
        col_m2.metric("Experiment ID", meta.get("experiment_id", "Unknown"))
        col_m3.metric("Model Version", meta.get("model_version", "v1.0"))

        st.markdown(f"**Selection Rationale:** {meta.get('selection_rationale', '')}")

        st.markdown("#### Hyperparameters of Selected Model")
        sel_name = meta.get("selected_model")
        if sel_name and "models" in meta and sel_name in meta["models"]:
            st.json(meta["models"][sel_name].get("best_params", {}))
    else:
        st.info("No trained model currently active in memory. Click the button above to train models.")
