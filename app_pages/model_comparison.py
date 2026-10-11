"""
Page: Model Comparison
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render_model_comparison(training_service, prediction_service):
    st.title("📊 Multi-Model Performance Comparison")
    st.markdown("Rigorous empirical comparison across all four candidate classifiers as specified in the research methodology.")

    meta = prediction_service.metadata
    models = meta.get("models", {})

    if not prediction_service.is_model_ready() or not models:
        st.warning("⚠️ No trained models available for comparison. Please execute training in the **Model Training** page first.")
        return

    selected_model = meta.get("selected_model", "")
    st.success(f"🏆 **Selected Optimal Model**: `{selected_model}` — Based on CV Macro F1 & High-Risk Recall.")

    # Comparative Summary Table
    rows = []
    for name, data in models.items():
        rows.append({
            "Model": name,
            "CV Macro F1": data.get("cv_macro_f1", 0.0),
            "Test Macro F1": data.get("test_macro_f1", 0.0),
            "Test Accuracy": data.get("test_accuracy", 0.0),
            "High-Risk Recall": data.get("test_high_risk_recall", 0.0),
            "ROC-AUC": data.get("test_roc_auc", "N/A"),
            "False Negatives": data.get("false_negatives", 0),
            "Training Time (s)": data.get("training_duration", 0.0),
            "Inference Latency (ms)": data.get("inference_latency_ms", 0.0),
            "Size (KB)": data.get("model_size_kb", 0.0),
        })

    df_comp = pd.DataFrame(rows)
    st.dataframe(
        df_comp.style.highlight_max(
            subset=["CV Macro F1", "Test Macro F1", "Test Accuracy", "High-Risk Recall"],
            color="#bbf7d0"
        ).highlight_min(
            subset=["False Negatives", "Inference Latency (ms)", "Training Time (s)"],
            color="#dbeafe"
        ),
        use_container_width=True
    )

    st.markdown("---")

    from config.theme import apply_dark_theme_to_plotly, COLOR_ACCENT_TEAL, COLOR_ACCENT_VIOLET, COLOR_RISK_HIGH, COLOR_RISK_MODERATE, COLOR_RISK_LOW

    # Interactive Visualizations
    col_v1, col_v2 = st.columns(2)

    with col_v1:
        st.subheader("Predictive Accuracy & High-Risk Recall")
        fig_bars = go.Figure()
        fig_bars.add_trace(go.Bar(
            x=df_comp["Model"], y=df_comp["CV Macro F1"],
            name="CV Macro F1", marker_color=COLOR_ACCENT_VIOLET
        ))
        fig_bars.add_trace(go.Bar(
            x=df_comp["Model"], y=df_comp["Test Macro F1"],
            name="Test Macro F1", marker_color=COLOR_ACCENT_TEAL
        ))
        fig_bars.add_trace(go.Bar(
            x=df_comp["Model"], y=df_comp["High-Risk Recall"],
            name="High-Risk Recall", marker_color=COLOR_RISK_MODERATE
        ))
        fig_bars.update_layout(
            barmode="group",
            yaxis=dict(range=[0, 1.05], title="Score"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=30, b=20)
        )
        fig_bars = apply_dark_theme_to_plotly(fig_bars)
        st.plotly_chart(fig_bars, use_container_width=True)

    with col_v2:
        st.subheader("Computational Overhead & Latency")
        fig_cost = go.Figure()
        fig_cost.add_trace(go.Bar(
            x=df_comp["Model"], y=df_comp["Inference Latency (ms)"],
            name="Inference (ms)", marker_color=COLOR_ACCENT_VIOLET
        ))
        fig_cost.update_layout(
            yaxis=dict(title="Latency (ms / sample)"),
            margin=dict(l=20, r=20, t=30, b=20)
        )
        fig_cost = apply_dark_theme_to_plotly(fig_cost)
        st.plotly_chart(fig_cost, use_container_width=True)

    st.markdown("---")

    # Detailed Confusion Matrices and Error Analysis
    st.subheader("🔍 Confusion Matrix & Error Analysis on Quarantined Test Set")

    cm_cols = st.columns(len(models))
    for idx, (name, data) in enumerate(models.items()):
        with cm_cols[idx]:
            st.markdown(f"**{name}**")
            # If raw results are available in session
            latest_exp = st.session_state.get("latest_experiment", {})
            raw_models = latest_exp.get("raw_training_output", {}).get("models", {})
            if name in raw_models and raw_models[name]["status"] == "SUCCESS":
                cm = raw_models[name]["test_metrics"]["confusion_matrix"]
                tn, fp = cm[0][0], cm[0][1]
                fn, tp = cm[1][0], cm[1][1]
                st.markdown(f"""
                - **True Negatives**: {tn}
                - **False Positives**: {fp}
                - **False Negatives**: {fn}
                - **True Positives**: {tp}
                """)
            else:
                st.markdown(f"False Negatives: `{data.get('false_negatives', 'N/A')}`")

    st.markdown("---")

    # Selection Policy Transparency
    st.subheader("📜 Model Selection Policy Transparency")
    st.markdown("""
    Model selection adheres strictly to **pre-registered criteria**:
    1. **Primary Metric**: Cross-Validation **Macro F1** on the training partition (prioritizing detection of minority at-risk students).
    2. **Safety Metric**: **High-Risk Recall** and **False Negative Rate** (minimizing missed at-risk interventions).
    3. **Parsimony Rule**: In the event of near-equal performance (within 0.015 Macro F1), prefer the structurally simpler, more explainable model (*Decision Tree* > *Logistic Regression* > *SVC* > *Random Forest*).
    4. **Zero Test Contamination**: The holdout test set is evaluated exclusively after model selection is finalized.
    """)
