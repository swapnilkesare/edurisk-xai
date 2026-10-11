"""
Page: Explainability (SHAP Engine)
Interpretable local and global explanations powered by Shapley Additive Explanations (SHAP)
rendered in modern dark UI with accessible contrast tokens.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config.theme import (
    apply_dark_theme_to_plotly,
    COLOR_BG_CARD,
    COLOR_BG_SECONDARY,
    COLOR_ACCENT_TEAL,
    COLOR_ACCENT_VIOLET,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_BORDER,
    COLOR_RISK_HIGH,
    COLOR_RISK_LOW
)

def render_explainability(prediction_service):
    st.markdown(f"""
    <div style="padding: 0.25rem 0 0.75rem 0;">
        <h1 style="color: {COLOR_TEXT_PRIMARY}; font-size: 2rem; font-weight: 700; margin-bottom: 0.25rem;">
            💡 Explainable AI (SHAP Engine)
        </h1>
        <p style="color: {COLOR_TEXT_SECONDARY}; font-size: 1.05rem;">
            Interpretable local and global attributions powered by Shapley Additive Explanations (TreeSHAP).
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not prediction_service.is_model_ready():
        st.warning("⚠️ No trained model available. Please visit the **Model Training** page first.")
        return

    curr = st.session_state.get("current_prediction")
    if not curr:
        st.info("ℹ️ No recent student prediction in memory. Navigate to **Student Risk Assessment**, run an assessment, and return here for local explanations.")

    tab_local, tab_global = st.tabs(["🔍 Local Prediction Attribution", "🌐 Global Cohort Importance"])

    # TAB 1: Local Explanation
    with tab_local:
        if curr:
            pred = curr["prediction"]
            shap_info = curr["shap"]

            st.markdown(f"<h3 style='color: {COLOR_TEXT_PRIMARY}; font-size: 1.25rem;'>Local Attribution for Current Student</h3>", unsafe_allow_html=True)
            st.caption(f"Risk Tier: **{pred['risk_tier']}** | Probability: **{pred['risk_probability']:.2%}**")

            if shap_info.get("status") == "SUCCESS":
                contributions = shap_info.get("contributions", [])
                base_val = shap_info.get("base_value", 0.0)

                col_base, col_sum, col_model = st.columns(3)
                col_base.metric("Base Value (Expected Risk)", f"{base_val:.4f}")
                col_sum.metric("Sum of SHAP Attributions", f"{shap_info.get('additive_sum', 0.0):+.4f}")
                col_model.metric("Final Model Score", f"{base_val + shap_info.get('additive_sum', 0.0):.4f}")

                # Plain English Educator Summary
                st.markdown(f"<h4 style='color: {COLOR_ACCENT_VIOLET}; margin-top: 1rem;'>🗣️ Plain-Language Interpretation</h4>", unsafe_allow_html=True)
                for text in shap_info.get("plain_language_summary", []):
                    st.markdown(f"- <span style='color: {COLOR_TEXT_PRIMARY};'>{text}</span>", unsafe_allow_html=True)

                # Interactive SHAP Contribution Bar Chart
                st.markdown(f"<h4 style='color: {COLOR_TEXT_PRIMARY}; margin-top: 1rem;'>Feature Attribution Impact (SHAP Values)</h4>", unsafe_allow_html=True)
                df_shap = pd.DataFrame(contributions)
                if "raw_value" in df_shap.columns:
                    df_shap["raw_value"] = df_shap["raw_value"].astype(str)
                df_shap["Impact Direction"] = df_shap["shap_value"].apply(
                    lambda x: "Risk Increasing (+)" if x > 0 else "Protective (-)"
                )
                df_shap["Color"] = df_shap["shap_value"].apply(
                    lambda x: COLOR_RISK_HIGH if x > 0 else COLOR_RISK_LOW
                )

                fig_shap = go.Figure()
                fig_shap.add_trace(go.Bar(
                    y=df_shap["feature"],
                    x=df_shap["shap_value"],
                    orientation="h",
                    marker=dict(color=df_shap["Color"]),
                    text=df_shap["shap_value"].apply(lambda v: f"{v:+.3f}"),
                    textposition="auto"
                ))
                fig_shap.update_layout(
                    xaxis=dict(title="SHAP Value (Contribution toward Academic Risk)"),
                    yaxis=dict(autorange="reversed"),
                    height=max(350, len(df_shap) * 28),
                    margin=dict(l=20, r=20, t=20, b=20)
                )
                fig_shap = apply_dark_theme_to_plotly(fig_shap)
                st.plotly_chart(fig_shap, use_container_width=True)

                # Tabular breakdown
                with st.expander("🔬 View Mathematical SHAP Attribution Table"):
                    st.dataframe(df_shap[["feature", "raw_value", "shap_value", "Impact Direction"]], use_container_width=True)

            else:
                st.warning(f"SHAP explanation status: {shap_info.get('message', 'Not available')}")
        else:
            st.info("Run an assessment in **Student Risk Assessment** to view local attribution.")

    # TAB 2: Global Importance
    with tab_global:
        st.markdown(f"<h3 style='color: {COLOR_TEXT_PRIMARY}; font-size: 1.25rem;'>Global Cohort Feature Importance</h3>", unsafe_allow_html=True)
        st.markdown("Mean absolute SHAP value across the student population, showing overall feature influence.")

        if prediction_service.xai_engine and "active_df" in st.session_state and st.session_state.active_df is not None:
            with st.spinner("Computing cohort-wide SHAP distributions..."):
                global_imp = prediction_service.xai_engine.compute_global_importance(
                    st.session_state.active_df
                )

            if global_imp:
                df_glob = pd.DataFrame(global_imp)
                fig_glob = px.bar(
                    df_glob,
                    x="mean_abs_shap",
                    y="feature",
                    orientation="h",
                    labels={"mean_abs_shap": "Mean |SHAP Value|", "feature": "Operational Indicator"},
                    title="Global Feature Importance Ranking",
                    color="mean_abs_shap",
                    color_continuous_scale=[[0, COLOR_ACCENT_TEAL], [1, COLOR_ACCENT_VIOLET]]
                )
                fig_glob.update_layout(yaxis=dict(autorange="reversed"), height=400)
                fig_glob = apply_dark_theme_to_plotly(fig_glob)
                st.plotly_chart(fig_glob, use_container_width=True)
            else:
                st.info("Global importance calculation pending data transformation.")
        else:
            st.info("Ensure an active dataset and trained model are loaded to view global feature importance.")

    st.markdown(f"<hr style='border: none; border-top: 1px solid {COLOR_BORDER}; margin: 1.5rem 0;'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background-color: {COLOR_BG_CARD}; border: 1px solid {COLOR_BORDER}; border-left: 4px solid {COLOR_ACCENT_VIOLET}; border-radius: 8px; padding: 1rem 1.25rem;">
        <span style="color: {COLOR_ACCENT_VIOLET}; font-weight: 700;">💡 Non-Causality Principle:</span>
        <span style="color: {COLOR_TEXT_SECONDARY}; font-size: 0.95rem;">
            SHAP values indicate how each feature shifted the model's output score relative to the baseline. 
            They do not prove direct causal mechanisms. For instance, raising recorded attendance alone may not guarantee improved conceptual mastery if foundational gaps persist.
        </span>
    </div>
    """, unsafe_allow_html=True)
