import joblib
import pandas as pd
import numpy as np

class Predictor:
    def __init__(self, model_path='models/artifacts/best_model.pkl'):
        self.pipeline = joblib.load(model_path)
        
    def predict(self, student_data: dict) -> dict:
        """
        Takes a dictionary of the 4 core features, returns risk tier and probability.
        """
        df = pd.DataFrame([student_data])
        
        # Ensure ordered columns match training
        cols = ['attendance_rate', 'study_hours', 'internal_test_score', 'assignment_submission_frequency']
        df = df[cols]
        
        prob = self.pipeline.predict_proba(df)[0][1] # Probability of Class 1 (At-Risk)
        
        # Risk Tier Logic (as specified in methodology)
        if prob >= 0.66:
            tier = "HIGH"
        elif prob >= 0.33:
            tier = "MODERATE"
        else:
            tier = "LOW"
            
        return {
            "probability": float(prob),
            "risk_tier": tier,
            "input_df": df
        }
