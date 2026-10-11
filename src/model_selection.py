"""
Transparent Model Selection Policy for EduRisk XAI
"""
from typing import Dict, Any, Tuple

def select_best_model(training_results: Dict[str, Any]) -> Tuple[str, Any, str]:
    """
    Selects the winning model exclusively based on Cross-Validation evidence on training folds.
    The holdout test set is NEVER used for model selection.

    Policy:
    1. Filter models with SUCCESS status.
    2. Rank by CV Macro F1 score (prioritizing balanced class performance).
    3. In case of a performance tie (within 0.015 Macro F1):
       - Prefer lightweight/interpretable architecture (Decision Tree > Logistic Regression > SVC > Random Forest).
       - This directly implements Occam's Razor and the lightweight research constraint.

    Returns:
        (best_model_name, best_pipeline, selection_rationale)
    """
    models = training_results.get("models", {})
    successful_models = {
        name: data for name, data in models.items()
        if data.get("status") == "SUCCESS"
    }

    if not successful_models:
        raise ValueError("No candidate models trained successfully.")

    # Sort primarily by CV Macro F1 descending
    sorted_models = sorted(
        successful_models.items(),
        key=lambda item: item[1].get("cv_macro_f1_mean", 0.0),
        reverse=True
    )

    top_name, top_data = sorted_models[0]
    top_cv_f1 = top_data.get("cv_macro_f1_mean", 0.0)

    # Check for close competitors within threshold
    interpretability_priority = [
        "Decision Tree",
        "Logistic Regression",
        "Support Vector Classifier",
        "Random Forest"
    ]

    selected_name = top_name
    selected_data = top_data
    rationale = (
        f"Selected {top_name} based on highest Cross-Validation Macro F1 ({top_cv_f1:.4f}) "
        f"across {len(sorted_models)} evaluated candidate pipelines."
    )

    # Tie-breaking logic: If a more interpretable model is within 0.015 of the top score
    for simpler_model in interpretability_priority:
        if simpler_model in successful_models and simpler_model != top_name:
            simpler_score = successful_models[simpler_model].get("cv_macro_f1_mean", 0.0)
            if (top_cv_f1 - simpler_score) <= 0.015 and interpretability_priority.index(simpler_model) < interpretability_priority.index(top_name):
                selected_name = simpler_model
                selected_data = successful_models[simpler_model]
                rationale = (
                    f"Selected {simpler_model} (CV Macro F1: {simpler_score:.4f}) via lightweight parsimony rule. "
                    f"It scored within 0.015 of top-performing {top_name} ({top_cv_f1:.4f}) while offering superior "
                    f"architectural simplicity and immediate educator explainability."
                )
                break

    best_pipeline = selected_data["pipeline"]
    return selected_name, best_pipeline, rationale
