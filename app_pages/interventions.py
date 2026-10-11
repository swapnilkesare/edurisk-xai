"""
Page: Recommended Support & Pedagogical Interventions
"""
import streamlit as st
import pandas as pd
from database.database import SessionLocal
from database.crud import get_all_rules, get_all_interventions, update_intervention_status
from database.models import InterventionRule

def render_interventions(prediction_service):
    st.title("🎯 Pedagogical Support & Intervention Engine")
    st.markdown("Deterministic, transparent intervention recommendations mapped from verified SHAP risk factors.")

    tab_current, tab_history, tab_rules = st.tabs([
        "⚡ Current Student Recommendations",
        "📋 Intervention Tracking Log",
        "⚙️ Teacher Rule Management"
    ])

    # TAB 1: Current Recommendations
    with tab_current:
        curr = st.session_state.get("current_prediction")
        if not curr:
            st.info("ℹ️ No active student prediction loaded. Run an inference in **Predict Student Risk** to view personalized recommendations.")
        else:
            interventions = curr.get("interventions", [])
            pred = curr["prediction"]

            st.subheader(f"Recommended Actions for Risk Tier: {pred['risk_tier']}")

            if not interventions:
                st.success("🎉 No active pedagogical interventions triggered. Student metrics satisfy established performance baselines.")
            else:
                for idx, item in enumerate(interventions):
                    p_color = "#ef4444" if item["priority"] == "HIGH" else "#f59e0b"
                    with st.container():
                        st.markdown(f"""
                        #### <span style='color:{p_color};'>[{item['priority']} PRIORITY]</span> Action: {item['action']}
                        """, unsafe_allow_html=True)

                        col_f1, col_f2, col_f3 = st.columns(3)
                        col_f1.markdown(f"**Triggering Feature**: `{item['feature']}`")
                        col_f2.markdown(f"**Observed Value**: `{item['observed_value']}` (Threshold: `{item['direction']} {item['threshold']}`)")
                        col_f3.markdown(f"**SHAP Attribution Verified**: `{'Yes (+Risk)' if item['shap_verified'] else 'Rule-Based Only'}`")

                        st.markdown(f"**Educational Rationale**: {item['rationale']}")
                        st.caption(f"⚠️ *{item['disclaimer']}*")
                        st.markdown("---")

    # TAB 2: Tracking Log from SQLite
    with tab_history:
        st.subheader("Audited Intervention Management Log")
        st.markdown("Track and update intervention execution status across all enrolled students.")

        try:
            db = SessionLocal()
            records = get_all_interventions(db, limit=50)
            db.close()

            if records:
                for rec in records:
                    col_info, col_status = st.columns([3, 1])
                    with col_info:
                        st.markdown(f"**Intervention #{rec.id}** — `{rec.risk_factor}`: {rec.intervention}")
                        st.caption(f"Priority: {rec.priority} | Logged: {rec.created_at.strftime('%Y-%m-%d %H:%M')}")
                    with col_status:
                        new_st = st.selectbox(
                            "Status",
                            ["Pending", "In Progress", "Completed", "Dismissed"],
                            index=["Pending", "In Progress", "Completed", "Dismissed"].index(rec.status),
                            key=f"interv_status_{rec.id}"
                        )
                        if new_st != rec.status:
                            db_up = SessionLocal()
                            update_intervention_status(db_up, rec.id, new_st)
                            db_up.close()
                            st.success(f"Updated #{rec.id} to {new_st}")
                            st.rerun()
                    st.markdown("---")
            else:
                st.info("No recorded interventions in the database yet.")
        except Exception as e:
            st.warning(f"Unable to query database log: {e}")

    # TAB 3: Teacher Rule Management
    with tab_rules:
        st.subheader("Configurable Pedagogical Rule Set")
        st.markdown("Instructors can inspect and customize deterministic intervention criteria.")

        try:
            db = SessionLocal()
            rules = get_all_rules(db, active_only=False)
            db.close()

            if rules:
                rule_table = [
                    {
                        "ID": r.id,
                        "Feature": r.feature,
                        "Condition": f"{r.direction} {r.threshold}",
                        "Severity": r.severity,
                        "Action": r.action,
                        "Active": r.is_active
                    }
                    for r in rules
                ]
                st.dataframe(pd.DataFrame(rule_table), use_container_width=True)

            # Form to add a new rule
            with st.expander("➕ Define New Pedagogical Rule"):
                with st.form("new_rule_form"):
                    f_name = st.selectbox("Feature", ["attendance_rate", "internal_test_score", "assignment_submission_frequency", "study_hours", "failures"])
                    f_dir = st.selectbox("Condition Direction", ["below", "above", "equals"])
                    f_thresh = st.number_input("Threshold Value", value=70.0, step=1.0)
                    f_sev = st.selectbox("Severity", ["HIGH", "MEDIUM", "LOW"])
                    f_action = st.text_input("Recommended Action", value="Faculty academic advising session.")
                    f_rat = st.text_area("Pedagogical Rationale", value="Metric deviated from established departmental baseline.")

                    if st.form_submit_button("Save Rule to Database"):
                        db_new = SessionLocal()
                        new_rule = InterventionRule(
                            feature=f_name,
                            threshold=f_thresh,
                            direction=f_dir,
                            severity=f_sev,
                            action=f_action,
                            rationale=f_rat,
                            is_active=True
                        )
                        db_new.add(new_rule)
                        db_new.commit()
                        db_new.close()
                        prediction_service._load_active_model()
                        st.success("New rule saved and loaded into intervention engine!")
                        st.rerun()

        except Exception as e:
            st.error(f"Rule management error: {e}")
