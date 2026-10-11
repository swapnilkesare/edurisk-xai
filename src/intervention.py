"""
Deterministic Rule-Based Pedagogical Intervention Engine for EduRisk XAI
"""
from typing import Dict, Any, List, Optional
from config.settings import DEFAULT_INTERVENTION_RULES

class InterventionEngine:
    """
    Translates SHAP risk-increasing factors and student metrics into transparent,
    deterministic educational support actions.
    """
    def __init__(self, rules: Optional[List[Dict[str, Any]]] = None):
        self.rules = rules or DEFAULT_INTERVENTION_RULES

    def evaluate_interventions(
        self,
        student_features: Dict[str, Any],
        shap_explanation: Optional[Dict[str, Any]] = None,
        risk_tier: str = "LOW"
    ) -> List[Dict[str, Any]]:
        """
        Generates prioritized, rule-based interventions based on feature values and SHAP risk contributions.

        Returns:
            List of recommendation dicts sorted by priority.
        """
        recommendations: List[Dict[str, Any]] = []

        # Extract risk-increasing feature names and shap values if available
        shap_risk_map = {}
        if shap_explanation and shap_explanation.get("status") == "SUCCESS":
            for item in shap_explanation.get("risk_increasing_factors", []):
                shap_risk_map[item["feature"]] = item["shap_value"]

        for rule in self.rules:
            feat = rule["feature"]
            val = student_features.get(feat, None)

            if val is None or not isinstance(val, (int, float)):
                continue

            threshold = float(rule["threshold"])
            direction = rule.get("direction", "below")
            triggered = False

            if direction == "below" and val < threshold:
                triggered = True
            elif direction == "above" and val > threshold:
                triggered = True
            elif direction == "equals" and val == threshold:
                triggered = True

            if triggered:
                # Check if this feature also contributed positively to risk according to SHAP
                has_shap_support = feat in shap_risk_map
                shap_val = shap_risk_map.get(feat, None)

                # Severity boost if student is in HIGH risk tier
                priority_label = rule.get("severity", "MEDIUM")
                if risk_tier == "HIGH" and priority_label != "HIGH":
                    priority_label = "HIGH"

                recommendations.append({
                    "feature": feat,
                    "observed_value": val,
                    "threshold": threshold,
                    "direction": direction,
                    "priority": priority_label,
                    "action": rule["action"],
                    "rationale": rule["rationale"],
                    "shap_contribution": round(shap_val, 4) if shap_val is not None else None,
                    "shap_verified": has_shap_support,
                    "status": "Pending",
                    "disclaimer": "This intervention recommendation represents automated decision support and requires educator clinical judgment."
                })

        # Rank recommendations: HIGH priority first, then by SHAP contribution magnitude
        priority_rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        recommendations.sort(
            key=lambda x: (
                priority_rank.get(x["priority"], 1),
                x["shap_contribution"] if x["shap_contribution"] is not None else 0.0
            ),
            reverse=True
        )

        return recommendations
