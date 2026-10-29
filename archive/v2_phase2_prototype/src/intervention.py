class InterventionEngine:
    def __init__(self):
        # Hardcoded rule mapping for the prototype as requested in Phase 2
        self.rules = {
            "attendance_rate": "Schedule attendance follow-up with the student.",
            "internal_test_score": "Recommend targeted revision or peer tutoring.",
            "assignment_submission_frequency": "Recommend assignment planning/support.",
            "study_hours": "Recommend study schedule support."
        }
        
    def generate_recommendations(self, shap_contributions: list) -> list:
        """
        Takes the SHAP contributions list from the Explainer and maps the top risk factors
        to actionable interventions.
        """
        recommendations = []
        for factor in shap_contributions:
            if factor['type'] == 'risk' and factor['value'] > 0: # Only map factors that actively pushed risk higher
                feature_name = factor['feature']
                if feature_name in self.rules:
                    recommendations.append({
                        "risk_factor": feature_name,
                        "action": self.rules[feature_name]
                    })
                    
        return recommendations
