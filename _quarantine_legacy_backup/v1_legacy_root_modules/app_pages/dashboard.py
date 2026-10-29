import streamlit as st
from database.crud import SessionLocal
from database.models import Student, Prediction, Intervention
import pandas as pd

def app():
    st.title("EduRisk Dashboard")
    st.markdown("Overview of student academic risk and system status.")

    with SessionLocal() as db:
        total_students = db.query(Student).count()
        total_predictions = db.query(Prediction).count()
        
        high_risk = db.query(Prediction).filter(Prediction.risk_tier == "HIGH").count()
        mod_risk = db.query(Prediction).filter(Prediction.risk_tier == "MODERATE").count()
        low_risk = db.query(Prediction).filter(Prediction.risk_tier == "LOW").count()
        
        pending_interventions = db.query(Intervention).filter(Intervention.status == "Pending").count()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Students Tracked", total_students)
    col2.metric("Total Predictions", total_predictions)
    col3.metric("High Risk Assessments", high_risk)
    col4.metric("Pending Interventions", pending_interventions)
    
    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Risk Distribution")
        if total_predictions > 0:
            df = pd.DataFrame({
                "Tier": ["HIGH", "MODERATE", "LOW"],
                "Count": [high_risk, mod_risk, low_risk]
            })
            st.bar_chart(df.set_index("Tier"), color=["#ff4b4b"])
        else:
            st.info("No predictions recorded yet.")
            
    with col_b:
        st.subheader("Recent At-Risk Students")
        with SessionLocal() as db:
            recent = db.query(Prediction).filter(Prediction.risk_tier.in_(["HIGH", "MODERATE"])).order_by(Prediction.prediction_timestamp.desc()).limit(5).all()
            if recent:
                for r in recent:
                    st.write(f"**{r.student.name if r.student else 'Unknown'}** - {r.risk_tier} Risk ({r.prediction_timestamp.strftime('%Y-%m-%d')})")
            else:
                st.write("No recent at-risk students.")
                
    from ml.train import load_current_model
    artifact = load_current_model()
    if artifact:
        st.sidebar.success(f"Model Active: {artifact['model_name']} ({artifact['version']})")
    else:
        st.sidebar.warning("No Model Trained")
