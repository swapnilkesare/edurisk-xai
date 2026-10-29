import streamlit as st
import pandas as pd
from database.crud import SessionLocal
from database.models import Student, Prediction

def app():
    st.title("Student Tracking")
    st.markdown("Longitudinal monitoring of student academic risk.")

    with SessionLocal() as db:
        students = db.query(Student).all()
        
        if not students:
            st.info("No students found in the database. Run predictions with a Student Identifier to populate this list.")
            return

        student_ids = [s.student_identifier for s in students]
        selected_id = st.selectbox("Select a Student", student_ids)
        
        if selected_id:
            student = db.query(Student).filter(Student.student_identifier == selected_id).first()
            st.subheader(f"History for {student.name}")
            
            predictions = db.query(Prediction).filter(Prediction.student_id == student.id).order_by(Prediction.prediction_timestamp).all()
            
            if predictions:
                df = pd.DataFrame([{
                    "Date": p.prediction_timestamp.strftime("%Y-%m-%d %H:%M"),
                    "Risk Tier": p.risk_tier,
                    "Probability": p.probability
                } for p in predictions])
                
                st.table(df)
                
                # Plot trajectory
                st.line_chart(df.set_index("Date")["Probability"])
            else:
                st.write("No predictions found for this student.")
