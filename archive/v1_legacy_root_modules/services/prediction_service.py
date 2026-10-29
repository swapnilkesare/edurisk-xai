import pandas as pd
import logging
from datetime import datetime
from ml.train import load_current_model
from ml.explain import SHAPExplainer
from ml.intervention import InterventionEngine
from config.settings import RISK_THRESHOLD_HIGH, RISK_THRESHOLD_MODERATE
from database.crud import SessionLocal
from database.models import Student, Prediction, SHAPExplanation, Intervention, BehaviorRecord

logger = logging.getLogger(__name__)

class PredictionService:
    def __init__(self):
        self.artifact = load_current_model()
        if self.artifact:
            # SHAP explainer requires the background data or we can pass None if TreeExplainer
            self.explainer = SHAPExplainer(self.artifact, background_data=None)
            self.intervention_engine = InterventionEngine()
        else:
            self.explainer = None
            self.intervention_engine = None

    def get_risk_tier(self, probability: float) -> str:
        if probability >= RISK_THRESHOLD_HIGH:
            return "HIGH"
        elif probability >= RISK_THRESHOLD_MODERATE:
            return "MODERATE"
        else:
            return "LOW"

    def run_src_ri(self, student_features: dict, student_identifier: str = None):
        """
        Executes the SHAP-Based Risk Classification and Rule-Mapped Intervention (SRC-RI) Algorithm.
        """
        if not self.artifact:
            raise Exception("No trained model found. Please train a model first.")

        # Ensure single row dataframe
        df = pd.DataFrame([student_features])
        
        # 1. Preprocess & 2. Predict Probability
        pipeline = self.artifact['model']
        
        # predict_proba returns [prob_class_0, prob_class_1]
        try:
            proba = pipeline.predict_proba(df)[0][1]
        except AttributeError:
            # If the model doesn't support predict_proba (shouldn't happen with our setup)
            pred = pipeline.predict(df)[0]
            proba = 1.0 if pred == 1 else 0.0

        # 3. Assign Risk Tier
        risk_tier = self.get_risk_tier(proba)
        
        # 4 & 5. Compute Local SHAP Explanation and Rank Factors
        shap_result = self.explainer.explain_prediction(df)
        
        # 6. Map Contributors to Interventions
        interventions = self.intervention_engine.generate_interventions(risk_tier, shap_result)
        
        # 8. Log prediction (if student_identifier is provided)
        if student_identifier:
            self._log_prediction(student_identifier, student_features, proba, risk_tier, shap_result, interventions)

        # 9. Return structured result
        return {
            "risk_tier": risk_tier,
            "probability": proba,
            "prediction": 1 if risk_tier in ["HIGH", "MODERATE"] else 0,
            "shap_values": shap_result.get("shap_values", []),
            "risk_factors": shap_result.get("risk_increasing", []),
            "protective_factors": shap_result.get("risk_decreasing", []),
            "interventions": interventions,
            "model_version": self.artifact.get("version"),
            "timestamp": datetime.now().isoformat()
        }

    def _log_prediction(self, student_identifier, features, probability, risk_tier, shap_result, interventions):
        """Logs the entire prediction trace to the database for longitudinal tracking."""
        with SessionLocal() as db:
            # 1. Find or create student
            student = db.query(Student).filter(Student.student_identifier == student_identifier).first()
            if not student:
                student = Student(student_identifier=student_identifier, name=f"Student {student_identifier}")
                db.add(student)
                db.commit()
                db.refresh(student)
                
            # 2. Log behavior snapshot
            behavior = BehaviorRecord(
                student_id=student.id,
                attendance=features.get('attendance_rate'),
                study_hours=features.get('study_hours'),
                assignment_submission_rate=features.get('assignment_submission_frequency'),
                record_date=datetime.utcnow()
            )
            db.add(behavior)
            
            # 3. Log prediction
            prediction = Prediction(
                student_id=student.id,
                model_version=self.artifact.get('version'),
                predicted_class=1 if risk_tier in ["HIGH", "MODERATE"] else 0,
                risk_tier=risk_tier,
                probability=probability
            )
            db.add(prediction)
            db.commit()
            db.refresh(prediction)
            
            # 4. Log SHAP
            if shap_result and "risk_increasing" in shap_result:
                for idx, factor in enumerate(shap_result["risk_increasing"]):
                    sh = SHAPExplanation(
                        prediction_id=prediction.id,
                        feature_name=factor["feature"],
                        feature_value=features.get(factor["feature"], 0.0),
                        shap_value=factor["value"],
                        direction="positive",
                        rank=idx + 1
                    )
                    db.add(sh)
            if shap_result and "risk_decreasing" in shap_result:
                for idx, factor in enumerate(shap_result["risk_decreasing"]):
                    sh = SHAPExplanation(
                        prediction_id=prediction.id,
                        feature_name=factor["feature"],
                        feature_value=features.get(factor["feature"], 0.0),
                        shap_value=factor["value"],
                        direction="negative",
                        rank=idx + 1
                    )
                    db.add(sh)
            
            # 5. Log Interventions
            for rec in interventions:
                interv = Intervention(
                    student_id=student.id,
                    prediction_id=prediction.id,
                    risk_factor=rec["risk_factor"],
                    intervention_action=rec["recommended_action"],
                    priority=rec["priority"],
                    status="Pending"
                )
                db.add(interv)
                
            db.commit()
