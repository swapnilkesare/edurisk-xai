"""
Page: Reports & Cohort Summary Analytics
Generates aggregated academic vulnerability reports and pedagogical intervention summaries.
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
    COLOR_RISK_MODERATE,
    COLOR_RISK_LOW
)
from database.database import SessionLocal
from database.models import Prediction, Intervention
from services.auth_service import get_scoped_predictions

def render_reports(current_user=None):
    st.markdown(f"""
    <div style="padding: 0.25rem 0 0.75rem 0;">
        <h1 style="color: {COLOR_TEXT_PRIMARY}; font-size: 2rem; font-weight: 700; margin-bottom: 0.25rem;">
            📊 Academic Risk & Intervention Reports
        </h1>
        <p style="color: {COLOR_TEXT_SECONDARY}; font-size: 1.05rem;">
            Aggregated institutional summaries to inform student advisory and academic support planning.
        </p>
    </div>
    """, unsafe_allow_html=True)

    db = SessionLocal()
    try:
        preds = get_scoped_predictions(db, current_user, limit=200)
        org_name = current_user.organization.name if (current_user and current_user.organization) else "All Organizations (Global Admin)"

        st.caption(f"🏫 Reporting Scope: **{org_name}** | Recent Evaluations Analyzed: **{len(preds)}**")

        if not preds:
            st.info("No assessment records found for this organization yet. Run student risk assessments to populate this report.")
            return

        # Tier counts
        tiers = [p.risk_tier.upper() for p in preds]
        high_cnt = tiers.count("HIGH")
        mod_cnt = tiers.count("MODERATE")
        low_cnt = tiers.count("LOW")
        total = len(tiers)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Assessments", total)
        with col2:
            st.metric("Priority Support (High)", f"{high_cnt} ({high_cnt/total:.0%})", delta_color="inverse")
        with col3:
            st.metric("Monitoring Advised (Moderate)", f"{mod_cnt} ({mod_cnt/total:.0%})")
        with col4:
            st.metric("On Track (Low)", f"{low_cnt} ({low_cnt/total:.0%})")

        st.markdown("<br>", unsafe_allow_html=True)

        # Visualizations
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.markdown(f"<h4 style='color: {COLOR_TEXT_PRIMARY}; font-size: 1.15rem;'>🎯 Student Risk Tier Distribution</h4>", unsafe_allow_html=True)
            df_pie = pd.DataFrame({
                "Risk Tier": ["Priority Support (High)", "Monitoring Advised (Mod)", "On Track (Low)"],
                "Count": [high_cnt, mod_cnt, low_cnt],
            })
            fig_pie = px.pie(
                df_pie,
                names="Risk Tier",
                values="Count",
                color="Risk Tier",
                color_discrete_map={
                    "Priority Support (High)": COLOR_RISK_HIGH,
                    "Monitoring Advised (Mod)": COLOR_RISK_MODERATE,
                    "On Track (Low)": COLOR_RISK_LOW
                },
                hole=0.48
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=320)
            fig_pie = apply_dark_theme_to_plotly(fig_pie)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_chart2:
            st.markdown(f"<h4 style='color: {COLOR_TEXT_PRIMARY}; font-size: 1.15rem;'>📈 Predicted Probability Histogram</h4>", unsafe_allow_html=True)
            probs = [p.probability for p in preds]
            fig_hist = px.histogram(
                x=probs,
                nbins=10,
                labels={"x": "Estimated Risk Probability", "y": "Student Count"},
                color_discrete_sequence=[COLOR_ACCENT_TEAL]
            )
            fig_hist.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                height=320,
                xaxis=dict(tickformat=".0%")
            )
            fig_hist = apply_dark_theme_to_plotly(fig_hist)
            st.plotly_chart(fig_hist, use_container_width=True)

        st.markdown(f"<hr style='border: none; border-top: 1px solid {COLOR_BORDER}; margin: 1.5rem 0;'>", unsafe_allow_html=True)

        # Recent Evaluation Records Table
        st.markdown(f"<h3 style='color: {COLOR_TEXT_PRIMARY}; font-size: 1.25rem;'>📋 Recent Evaluation Logs</h3>", unsafe_allow_html=True)
        table_rows = []
        for p in preds[:30]:
            table_rows.append({
                "Evaluation Date": p.prediction_timestamp.strftime("%Y-%m-%d %H:%M"),
                "Student Reference": p.student_identifier or "ANONYMOUS",
                "Risk Category": p.risk_tier,
                "Probability Score": f"{p.probability:.1%}",
                "Evaluated Model": p.model_name,
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    finally:
        db.close()
