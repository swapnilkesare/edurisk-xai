import streamlit as st
from database.crud import SessionLocal
from database.models import Prediction
import pandas as pd

def app():
    st.title("Cohort Analytics")
    st.markdown("Analyze risk across the student population.")

    with SessionLocal() as db:
        predictions = db.query(Prediction).all()
        
        if not predictions:
            st.info("No prediction data available for cohort analytics.")
            return
            
        df = pd.DataFrame([{
            "Date": p.prediction_timestamp,
            "Risk Tier": p.risk_tier,
            "Probability": p.probability
        } for p in predictions])
        
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        
        st.subheader("Risk Distribution")
        st.bar_chart(df['Risk Tier'].value_counts(), color=["#ff4b4b"])
        
        st.subheader("Average Risk Probability over Time")
        trend = df.groupby('Date')['Probability'].mean()
        st.line_chart(trend)
