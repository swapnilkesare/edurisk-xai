from database.crud import SessionLocal
from database.models import InterventionRule

class InterventionEngine:
    def __init__(self):
        # We instantiate a session when needed
        pass

    def generate_interventions(self, risk_tier: str, shap_explanation: dict):
        """
        Maps risk-increasing SHAP factors to intervention recommendations.
        """
        if risk_tier == "LOW":
            return [] # No interventions needed

        risk_factors = shap_explanation.get("risk_increasing", [])
        if not risk_factors:
            return []

        interventions = []
        
        # Open DB session
        with SessionLocal() as db:
            active_rules = db.query(InterventionRule).filter(InterventionRule.is_active == True).all()
            
            # Create a lookup dictionary for active rules by feature name
            rule_map = {rule.feature_name: rule for rule in active_rules}
            
            for factor in risk_factors:
                feature_name = factor["feature"]
                # For SHAP, the factor already "contributes positively to risk"
                # which satisfies direction="shap_positive"
                
                if feature_name in rule_map:
                    rule = rule_map[feature_name]
                    # We can add severity, value, etc. logic here if threshold exists.
                    
                    interventions.append({
                        "priority": rule.priority,
                        "risk_factor": feature_name,
                        "evidence": f"Model contribution: Positive contribution toward predicted risk ({factor['value']:.4f}).",
                        "recommended_action": rule.intervention_action,
                        "status": "Pending"
                    })
            
            # Sort by priority
            interventions.sort(key=lambda x: x["priority"])
            
        return interventions
