"""
Prediction and Explainability Service for EduRisk XAI
"""
from typing import Dict, Any, Optional, Union
from pathlib import Path
import json
import joblib
import pandas as pd

from config.settings import ARTIFACTS_DIR, RAW_DATA_PATH
from src.predict import predict_single_student
from src.explain import ExplainabilityEngine
from src.intervention import InterventionEngine
from src.risk import RiskClassifier
from src.data_loader import load_dataset
from database.database import SessionLocal
from database.crud import save_prediction_and_xai, get_all_rules

class PredictionService:
    """
    Coordinates end-to-end inference: Prediction -> SHAP -> Intervention -> Persistence.
    """
    def __init__(self):
        self.artifact_path = ARTIFACTS_DIR / "best_model.pkl"
        self.metadata_path = ARTIFACTS_DIR / "model_metadata.json"
        self.pipeline = None
        self.metadata = {}
        self.xai_engine = None
        self.risk_classifier = RiskClassifier()
        self.intervention_engine = None

        self._load_active_model()

    def _load_active_model(self):
        """Loads fitted pipeline and initializes SHAP explainability engine."""
        if self.artifact_path.exists():
            try:
                self.pipeline = joblib.load(self.artifact_path)
            except Exception as e:
                print(f"[Warning] Failed to load model artifact: {e}")
                self.pipeline = None

        if self.metadata_path.exists():
            try:
                with open(self.metadata_path, "r") as f:
                    self.metadata = json.load(f)
            except Exception:
                self.metadata = {}

        if self.pipeline is not None:
            # Load background data for SHAP
            bg_df = None
            try:
                raw_df, _ = load_dataset(fallback_to_synthetic=True)
                bg_df = raw_df
            except Exception:
                pass
            self.xai_engine = ExplainabilityEngine(self.pipeline, background_data=bg_df)

        # Load intervention rules from DB if available, else defaults
        rules = []
        try:
            db = SessionLocal()
            db_rules = get_all_rules(db, active_only=True)
            for r in db_rules:
                rules.append({
                    "feature": r.feature,
                    "threshold": r.threshold,
                    "direction": r.direction,
                    "severity": r.severity,
                    "action": r.action,
                    "rationale": r.rationale,
                })
            db.close()
        except Exception:
            pass

        self.intervention_engine = InterventionEngine(rules=rules if rules else None)

    def is_model_ready(self) -> bool:
        return self.pipeline is not None

    def predict_and_explain(
        self,
        student_data: Union[Dict[str, Any], pd.DataFrame],
        student_identifier: Optional[str] = None,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Executes complete inference workflow for a student.
        """
        if not self.is_model_ready():
            raise RuntimeError("No trained model available. Please train a model first.")

        if isinstance(student_data, dict):
            df_input = pd.DataFrame([student_data])
        else:
            df_input = student_data.copy()

        # 1. Prediction & Risk Classification
        pred_res = predict_single_student(
            pipeline=self.pipeline,
            student_data=df_input,
            risk_classifier=self.risk_classifier
        )

        # 2. SHAP Explainability
        shap_res = {}
        if self.xai_engine is not None:
            shap_res = self.xai_engine.explain_single_prediction(
                pd.DataFrame([pred_res["input_features"]])
            )


        # 3. Deterministic Pedagogical Interventions
        interventions = self.intervention_engine.evaluate_interventions(
            student_features=pred_res["input_features"],
            shap_explanation=shap_res,
            risk_tier=pred_res["risk_tier"]
        )

        # 4. Persistence to SQLite
        db_id = None
        if save_to_db:
            try:
                db = SessionLocal()
                pred_row = save_prediction_and_xai(
                    db=db,
                    student_identifier=student_identifier,
                    model_version=self.metadata.get("model_version", "v1.0"),
                    model_name=self.metadata.get("selected_model", "Selected Model"),
                    predicted_class=pred_res["predicted_class"],
                    risk_tier=pred_res["risk_tier"],
                    probability=pred_res["risk_probability"],
                    input_data=pred_res["input_features"],
                    shap_explanation=shap_res,
                    interventions=interventions,
                )
                db_id = pred_row.id
                db.close()
            except Exception as e:
                print(f"[Database Warning] Could not save prediction to DB: {e}")

        return {
            "prediction_id": db_id,
            "prediction": pred_res,
            "shap": shap_res,
            "interventions": interventions,
            "model_metadata": self.metadata,
        }
