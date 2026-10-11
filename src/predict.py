"""
Inference Engine and Risk Prediction Interface for EduRisk XAI
"""
from typing import Dict, Any, Union
import pandas as pd
import numpy as np

from src.risk import RiskClassifier

def predict_single_student(
    pipeline: Any,
    student_data: Union[Dict[str, Any], pd.DataFrame],
    risk_classifier: RiskClassifier = None,
) -> Dict[str, Any]:
    """
    Executes inference for a single student record using a trained pipeline.

    Returns:
        Dictionary containing predicted class, continuous risk probability,
        operational risk tier, and feature values.
    """
    if risk_classifier is None:
        risk_classifier = RiskClassifier()

    if isinstance(student_data, dict):
        df_input = pd.DataFrame([student_data])
    elif isinstance(student_data, pd.DataFrame):
        df_input = student_data.iloc[[0]].copy()
    else:
        raise TypeError("student_data must be a dict or a pandas DataFrame.")


    # Align input features with pipeline requirements
    if hasattr(pipeline, "named_steps") and "preprocessor" in pipeline.named_steps:
        preprocessor = pipeline.named_steps["preprocessor"]
        if hasattr(preprocessor, "transformers_"):
            for trans_name, transformer, cols in preprocessor.transformers_:
                if trans_name != "remainder" and isinstance(cols, (list, tuple)):
                    for col in cols:
                        if col not in df_input.columns:
                            df_input[col] = 0.0 if trans_name == "num" else "no"


    # Execute prediction
    try:
        predicted_class = int(pipeline.predict(df_input)[0])

        probabilities = pipeline.predict_proba(df_input)[0]

        # Probability of at-risk (class 1)
        risk_prob = float(probabilities[1]) if len(probabilities) > 1 else float(probabilities[0])
    except Exception as e:
        raise RuntimeError(f"Prediction failed on input: {e}")

    risk_info = risk_classifier.classify_probability(risk_prob)

    return {
        "predicted_class": predicted_class,
        "is_at_risk": bool(predicted_class == 1),
        "risk_probability": round(risk_prob, 4),
        "risk_percentage": risk_info["percentage"],
        "risk_tier": risk_info["risk_tier"],
        "urgency": risk_info["urgency"],
        "tier_color": risk_info["color"],
        "input_features": df_input.to_dict(orient="records")[0],
    }
