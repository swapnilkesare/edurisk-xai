"""
Page: Cohort Analytics & Longitudinal Trajectories
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.database import SessionLocal
from database.crud import get_student_history, get_recent_predictions
from config.settings import CORE_FEATURES, TARGET_COLUMN

def render_analytics():
    st.title("📈 Cohort Analytics & Longitudinal Trajectories")
    st.markdown("Cohort-level risk analytics and longitudinal student trajectory tracking.")

    tab_cohort, tab_trajectory = st.tabs(["📊 Cohort-Wide Overview", "📈 Longitudinal Student Trajectory"])

    # TAB 1: Cohort Overview
    with tab_cohort:
        if "active_df" not in st.session_state or st.session_state.active_df is None:
            from src.data_loader import load_dataset
            df, prov = load_dataset(fallback_to_synthetic=True)
            st.session_state.active_df = df
            st.session_state.active_provenance = prov

        df = st.session_state.active_df
        prov = st.session_state.active_provenance

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Cohort Size", f"{len(df)} Students")
        if TARGET_COLUMN in df.columns:
            at_risk_cnt = int(df[TARGET_COLUMN].sum())
            safe_cnt = len(df) - at_risk_cnt
            pct_risk = (at_risk_cnt / len(df)) * 100
            col2.metric("At-Risk Students", f"{at_risk_cnt} ({pct_risk:.1f}%)")
            col3.metric("On-Track Students", f"{safe_cnt} ({100-pct_risk:.1f}%)")
        col4.metric("Dataset Provenance", "Synthetic Demo" if prov.is_synthetic else "Benchmark Dataset")

        col_c1, col_c2 = st.columns(2)

        from config.theme import apply_dark_theme_to_plotly, COLOR_RISK_HIGH, COLOR_RISK_LOW, COLOR_ACCENT_TEAL, COLOR_BORDER

        with col_c1:
            st.subheader("Attendance vs. Internal Assessment")
            if "attendance_rate" in df.columns and "internal_test_score" in df.columns:
                fig_scatter = px.scatter(
                    df,
                    x="attendance_rate",
                    y="internal_test_score",
                    color=df[TARGET_COLUMN].map({0: "On-Track", 1: "At-Risk"}) if TARGET_COLUMN in df.columns else None,
                    color_discrete_map={"On-Track": COLOR_RISK_LOW, "At-Risk": COLOR_RISK_HIGH},
                    labels={"attendance_rate": "Attendance Rate (%)", "internal_test_score": "Internal Test Score (%)"},
                    title="Attendance vs. Assessment Performance"
                )
                fig_scatter.update_layout(margin=dict(l=20, r=20, t=30, b=20))
                fig_scatter = apply_dark_theme_to_plotly(fig_scatter)
                st.plotly_chart(fig_scatter, use_container_width=True)

        with col_c2:
            st.subheader("Weekly Study Hours Distribution")
            if "study_hours" in df.columns:
                fig_hist = px.histogram(
                    df,
                    x="study_hours",
                    nbins=20,
                    color=df[TARGET_COLUMN].map({0: "On-Track", 1: "At-Risk"}) if TARGET_COLUMN in df.columns else None,
                    color_discrete_map={"On-Track": COLOR_RISK_LOW, "At-Risk": COLOR_RISK_HIGH},
                    labels={"study_hours": "Study Hours / Week"},
                    title="Study Hours Distribution Across Risk Classes"
                )
                fig_hist.update_layout(margin=dict(l=20, r=20, t=30, b=20))
                fig_hist = apply_dark_theme_to_plotly(fig_hist)
                st.plotly_chart(fig_hist, use_container_width=True)

    # TAB 2: Longitudinal Trajectory
    with tab_trajectory:
        st.subheader("Individual Student Longitudinal Monitoring")
        st.markdown("Track prediction trajectory across multi-period assessments to observe risk escalation or recovery.")

        stu_search = st.text_input("Enter Student Identifier to Inspect History:", value="STU-2026-081")

        if stu_search:
            try:
                db = SessionLocal()
                history = get_student_history(db, stu_search)
                db.close()

                if history:
                    st.markdown(f"Found **{len(history)}** historical evaluation snapshots for student `{stu_search}`.")

                    h_records = [
                        {
                            "Timestamp": h.prediction_timestamp.strftime("%Y-%m-%d %H:%M"),
                            "Risk Tier": h.risk_tier,
                            "Probability": f"{h.probability:.2%}",
                            "Model Version": h.model_version,
                            "Raw Prob": h.probability
                        }
                        for h in history
                    ]
                    df_h = pd.DataFrame(h_records)

                    fig_trend = px.line(
                        df_h,
                        x="Timestamp",
                        y="Raw Prob",
                        markers=True,
                        labels={"Raw Prob": "Predicted Failure Probability", "Timestamp": "Evaluation Date"},
                        title=f"Risk Trajectory for {stu_search}",
                        color_discrete_sequence=[COLOR_ACCENT_TEAL]
                    )
                    fig_trend.add_hline(y=0.66, line_dash="dash", line_color=COLOR_RISK_HIGH, annotation_text="High Risk Threshold (0.66)")
                    fig_trend.add_hline(y=0.33, line_dash="dash", line_color="#FFB238", annotation_text="Moderate Risk Threshold (0.33)")
                    fig_trend.update_layout(yaxis=dict(range=[0, 1.05]))
                    fig_trend = apply_dark_theme_to_plotly(fig_trend)
                    st.plotly_chart(fig_trend, use_container_width=True)

                    st.dataframe(df_h[["Timestamp", "Risk Tier", "Probability", "Model Version"]], use_container_width=True)

                else:
                    st.info(f"No previous prediction records found in SQLite database for identifier `{stu_search}`. Run predictions in **Predict Student Risk** to create historical snapshots.")
            except Exception as e:
                st.warning(f"Could not load student history: {e}")
