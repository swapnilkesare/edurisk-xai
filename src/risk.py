"""
Operational Risk Classification and Threshold Management for EduRisk XAI
"""
from typing import Dict, Any, List
from config.settings import HIGH_RISK_THRESHOLD, MODERATE_RISK_THRESHOLD

class RiskClassifier:
    """
    Translates raw model risk probabilities into actionable academic advising risk tiers.
    """
    def __init__(
        self,
        high_threshold: float = HIGH_RISK_THRESHOLD,
        moderate_threshold: float = MODERATE_RISK_THRESHOLD
    ):
        self.high_threshold = high_threshold
        self.moderate_threshold = moderate_threshold

    def classify_probability(self, probability: float) -> Dict[str, Any]:
        """
        Classifies a single risk probability into an operational tier.
        """
        p = float(probability)
        if p >= self.high_threshold:
            tier = "HIGH"
            urgency = "Immediate advisor consultation required."
            color = "#ef4444"  # Red
            badge_class = "risk-high"
        elif p >= self.moderate_threshold:
            tier = "MODERATE"
            urgency = "Proactive monitoring and targeted tutoring recommended."
            color = "#f59e0b"  # Amber
            badge_class = "risk-moderate"
        else:
            tier = "LOW"
            urgency = "Standard academic progression. On track."
            color = "#10b981"  # Emerald
            badge_class = "risk-low"

        return {
            "probability": round(p, 4),
            "percentage": round(p * 100, 1),
            "risk_tier": tier,
            "urgency": urgency,
            "color": color,
            "badge_class": badge_class,
            "thresholds_used": {
                "high": self.high_threshold,
                "moderate": self.moderate_threshold,
            }
        }

    def classify_batch(self, probabilities: List[float]) -> List[Dict[str, Any]]:
        return [self.classify_probability(p) for p in probabilities]
