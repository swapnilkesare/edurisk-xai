"""
Page: Data Management and Ingestion
"""
import streamlit as st
import pandas as pd
from src.data_loader import load_dataset, generate_synthetic_demo_data
from services.import_service import ImportService
from config.settings import CORE_FEATURES, TARGET_COLUMN

def render_data_import(import_service, training_service):
    st.title("📂 Data Management & Ingestion")
    st.markdown("Inspect, validate, and manage educational cohorts used for training and inference.")

    tab1, tab2, tab3 = st.tabs(["📁 Active Dataset", "⬆️ Upload Custom CSV", "🧪 Synthetic Demo Generator"])

    # TAB 1: Active Dataset Preview
    with tab1:
        st.subheader("Current Dataset in Memory")
        if "active_df" not in st.session_state or st.session_state.active_df is None:
            df, prov = load_dataset(fallback_to_synthetic=True)
            st.session_state.active_df = df
            st.session_state.active_provenance = prov

        df = st.session_state.active_df
        prov = st.session_state.active_provenance

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Dataset Name", prov.name[:25])
        col2.metric("Total Records", len(df))
        col3.metric("Features", len(df.columns) - 1)
        col4.metric("Dataset Type", "Synthetic" if prov.is_synthetic else "Real Benchmark")

        if prov.is_synthetic:
            st.warning("⚠️ This dataset is flagged as **SYNTHETIC / DEMO DATA**. Real-world performance claims must not be derived from it.")

        st.markdown("#### Sample Records Preview")
        st.dataframe(df.head(10), use_container_width=True)

        st.markdown("#### Feature Summary & Target Distribution")
        col_summary1, col_summary2 = st.columns(2)

        with col_summary1:
            st.markdown("**Numeric Indicators Summary**")
            st.dataframe(df[CORE_FEATURES].describe().round(2))

        with col_summary2:
            st.markdown(f"**Target Distribution (`{TARGET_COLUMN}`)**")
            if TARGET_COLUMN in df.columns:
                target_counts = df[TARGET_COLUMN].value_counts().reset_index()
                target_counts.columns = ["Target Class", "Count"]
                target_counts["Label"] = target_counts["Target Class"].map({0: "Low-Risk / Safe (0)", 1: "At-Risk (1)"})
                target_counts["Percentage"] = (target_counts["Count"] / len(df) * 100).round(1)
                st.dataframe(target_counts[["Label", "Count", "Percentage"]])

    # TAB 2: Upload Custom CSV
    with tab2:
        st.subheader("Upload Educational Dataset (CSV)")
        st.markdown("""
        Ensure your CSV contains the **four core features**:
        - `attendance_rate` (0.0 - 100.0)
        - `internal_test_score` (0.0 - 100.0)
        - `assignment_submission_frequency` (0.0 - 100.0)
        - `study_hours` (0.0 - 40.0)
        - `target_at_risk` (0 or 1 binary target)
        """)

        uploaded_file = st.file_uploader("Choose CSV file", type=["csv"])

        if uploaded_file is not None:
            if st.button("Validate & Ingest Dataset", type="primary"):
                with st.spinner("Validating schema and leakage safeguards..."):
                    success, df_up, prov_up, report = import_service.validate_and_ingest_csv(
                        uploaded_file, uploaded_file.name
                    )

                if success:
                    st.success(f"✅ Successfully ingested {len(df_up)} records! Dataset saved and verified.")
                    st.session_state.active_df = df_up
                    st.session_state.active_provenance = prov_up
                    st.rerun()
                else:
                    st.error("❌ Dataset Validation Failed:")
                    for err in report.get("errors", []):
                        st.markdown(f"- 🔴 {err}")
                    if report.get("warnings"):
                        st.warning("Warnings:")
                        for w in report["warnings"]:
                            st.markdown(f"- ⚠️ {w}")

    # TAB 3: Synthetic Demo Generator
    with tab3:
        st.subheader("Generate Controlled Synthetic Demonstration Cohort")
        st.markdown("""
        Generate a synthetic cohort for pipeline testing and UI demonstration. 
        All generated records are tagged with **`[SYNTHETIC / DEMO DATA]`**.
        """)

        col_syn1, col_syn2 = st.columns(2)
        with col_syn1:
            sample_size = st.slider("Cohort Sample Size", min_value=100, max_value=1000, value=300, step=50)
        with col_syn2:
            seed_val = st.number_input("Random Seed", value=42, step=1)

        if st.button("Generate Synthetic Cohort", type="secondary"):
            with st.spinner("Synthesizing realistic educational cohort..."):
                df_syn, prov_syn = generate_synthetic_demo_data(n_samples=sample_size, random_state=seed_val)
                st.session_state.active_df = df_syn
                st.session_state.active_provenance = prov_syn

            st.success(f"Generated {len(df_syn)} synthetic student records (Seed: {seed_val}).")
            st.rerun()
