"""
Page: Reports & Cohort Summary Analytics
Generates aggregated academic vulnerability reports and pedagogical intervention summaries.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from database.database import SessionLocal
from database.models import Prediction, Intervention
from services.auth_service import get_scoped_predictions

def render_reports(current_user=None):
    st.markdown("""
    <div style="padding: 0.5rem 0 1rem 0;">
        <h1 style="color: var(--text-primary, #0f172a); font-size: 2rem; font-weight: 700; margin-bottom: 0.25rem;">
            📊 Academic Risk & Intervention Reports
        </h1>
        <p style="color: var(--text-secondary, #475569); font-size: 1.05rem;">
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
            st.markdown("#### 🎯 Student Risk Tier Distribution")
            df_pie = pd.DataFrame({
                "Risk Tier": ["Priority Support (High)", "Monitoring Advised (Mod)", "On Track (Low)"],
                "Count": [high_cnt, mod_cnt, low_cnt],
                "Color": ["#ef4444", "#f59e0b", "#10b981"]
            })
            fig_pie = px.pie(
                df_pie,
                names="Risk Tier",
                values="Count",
                color="Risk Tier",
                color_discrete_map={
                    "Priority Support (High)": "#ef4444",
                    "Monitoring Advised (Mod)": "#f59e0b",
                    "On Track (Low)": "#10b981"
                },
                hole=0.45
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=320)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_chart2:
            st.markdown("#### 📈 Predicted Probability Histogram")
            probs = [p.probability for p in preds]
            fig_hist = px.histogram(
                x=probs,
                nbins=10,
                labels={"x": "Estimated Risk Probability", "y": "Student Count"},
                color_discrete_sequence=["#0284c7"]
            )
            fig_hist.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                height=320,
                xaxis=dict(tickformat=".0%")
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        st.markdown("---")

        # Recent Evaluation Records Table
        st.markdown("### 📋 Recent Evaluation Logs")
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
