import streamlit as st
from database.crud import SessionLocal
from database.models import InterventionRule

def app():
    st.title("Intervention Engine Settings")
    st.markdown("Manage the rules that map predictive risk factors to actionable pedagogical remedies.")

    with SessionLocal() as db:
        rules = db.query(InterventionRule).all()
        
        st.subheader("Current Intervention Rules")
        if not rules:
            st.info("No rules configured.")
        else:
            for rule in rules:
                with st.expander(f"Rule: {rule.feature_name} ({rule.severity})"):
                    st.write(f"**Trigger:** When `{rule.feature_name}` contributes positively to risk (`{rule.direction}`).")
                    st.write(f"**Action:** {rule.intervention_action}")
                    st.write(f"**Priority:** {rule.priority}")
                    st.write(f"**Active:** {rule.is_active}")

        st.markdown("---")
        st.subheader("Add New Rule")
        with st.form("new_rule"):
            feature = st.text_input("Feature Name (e.g., attendance_rate)")
            severity = st.selectbox("Severity", ["High", "Medium", "Low"])
            action = st.text_input("Intervention Action")
            priority = st.number_input("Priority (lower is higher)", min_value=1, value=5)
            
            if st.form_submit_button("Add Rule"):
                new_rule = InterventionRule(
                    feature_name=feature,
                    direction="shap_positive",
                    severity=severity,
                    intervention_action=action,
                    priority=priority,
                    is_active=True
                )
                db.add(new_rule)
                db.commit()
                st.success("Rule added! Refresh page to see.")
