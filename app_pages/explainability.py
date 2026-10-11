"""
Page: Explainability (SHAP Engine)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render_explainability(prediction_service):
    st.title("💡 Explainable AI (SHAP Engine)")
    st.markdown("Interpretable local and global explanations powered by Shapley Additive Explanations (SHAP).")

    if not prediction_service.is_model_ready():
        st.warning("⚠️ No trained model available. Please visit the **Model Training** page first.")
        return

    curr = st.session_state.get("current_prediction")
    if not curr:
        st.info("ℹ️ No recent student prediction in memory. Navigate to **Predict Student Risk**, run an inference, and return here for local explanations.")

    tab_local, tab_global = st.tabs(["🔍 Local Prediction Explanation", "🌐 Global Cohort Importance"])

    # TAB 1: Local Explanation
    with tab_local:
        if curr:
            pred = curr["prediction"]
            shap_info = curr["shap"]

            st.subheader("Local Attribution for Current Student")
            st.caption(f"Risk Tier: **{pred['risk_tier']}** | Probability: **{pred['risk_probability']:.2%}**")

            if shap_info.get("status") == "SUCCESS":
                contributions = shap_info.get("contributions", [])
                base_val = shap_info.get("base_value", 0.0)

                col_base, col_sum, col_model = st.columns(3)
                col_base.metric("Base Value (Expected Risk)", f"{base_val:.4f}")
                col_sum.metric("Sum of SHAP Attributions", f"{shap_info.get('additive_sum', 0.0):+.4f}")
                col_model.metric("Final Model Score", f"{base_val + shap_info.get('additive_sum', 0.0):.4f}")

                # Plain English Educator Summary
                st.markdown("#### 🗣️ Plain-Language Interpretation")
                for text in shap_info.get("plain_language_summary", []):
                    st.markdown(f"- {text}")

                # Interactive SHAP Contribution Bar Chart
                st.markdown("#### Feature Attribution Impact (SHAP Values)")
                df_shap = pd.DataFrame(contributions)
                if "raw_value" in df_shap.columns:
                    df_shap["raw_value"] = df_shap["raw_value"].astype(str)
                df_shap["Impact Direction"] = df_shap["shap_value"].apply(
                    lambda x: "Risk Increasing (+)" if x > 0 else "Protective (-)"
                )
                df_shap["Color"] = df_shap["shap_value"].apply(
                    lambda x: "#ef4444" if x > 0 else "#10b981"
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
                st.plotly_chart(fig_shap, use_container_width=True)

                # Tabular breakdown
                with st.expander("🔬 View Mathematical SHAP Attribution Table"):
                    st.dataframe(df_shap[["feature", "raw_value", "shap_value", "Impact Direction"]], use_container_width=True)

            else:
                st.warning(f"SHAP explanation status: {shap_info.get('message', 'Not available')}")
        else:
            st.info("Run a prediction in **Predict Student Risk** to view local attribution.")

    # TAB 2: Global Importance
    with tab_global:
        st.subheader("Global Cohort Feature Importance")
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
                    color_continuous_scale="Blues"
                )
                fig_glob.update_layout(yaxis=dict(autorange="reversed"), height=400)
                st.plotly_chart(fig_glob, use_container_width=True)
            else:
                st.info("Global importance calculation pending data transformation.")
        else:
            st.info("Ensure an active dataset and trained model are loaded to view global feature importance.")

    st.markdown("---")
    st.info("""
    **Non-Causality Principle**: SHAP values indicate how each feature shifted the model's output score relative to the baseline. 
    They do not demonstrate causal mechanisms. For instance, raising attendance alone may not guarantee improved comprehension if foundational knowledge gaps persist.
    """)
