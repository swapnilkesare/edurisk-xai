"""
SHAP Explainability Engine for EduRisk XAI
"""
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
import shap

from src.preprocessing import get_feature_names_out

class ExplainabilityEngine:
    """
    Computes local and global SHAP explanations for fitted pipelines,
    ensuring mathematical consistency, feature alignment, and educator-friendly plain English.
    """
    def __init__(self, pipeline: Any, background_data: Optional[pd.DataFrame] = None):
        self.pipeline = pipeline
        self.preprocessor = pipeline.named_steps.get("preprocessor")
        self.classifier = pipeline.named_steps.get("classifier")
        self.background_data = background_data
        self._explainer = None
        self._transformed_background = None
        self._feature_names = None

        self._initialize_explainer()

    def _initialize_explainer(self):
        """Builds the appropriate SHAP explainer based on classifier architecture."""
        if self.background_data is not None and self.preprocessor is not None:
            # Transform background data
            sample_bg = self.background_data.sample(
                min(len(self.background_data), 50), random_state=42
            )
            self._transformed_background = self.preprocessor.transform(sample_bg)
            try:
                self._feature_names = list(self.preprocessor.get_feature_names_out())
            except Exception:
                self._feature_names = [f"feature_{i}" for i in range(self._transformed_background.shape[1])]
        else:
            self._transformed_background = np.zeros((1, 4))
            self._feature_names = ["feature_0", "feature_1", "feature_2", "feature_3"]

        classifier_name = type(self.classifier).__name__

        try:
            if "Tree" in classifier_name or "Forest" in classifier_name:
                # TreeExplainer for Decision Tree / Random Forest
                self._explainer = shap.TreeExplainer(self.classifier)
            elif "LogisticRegression" in classifier_name:
                # LinearExplainer for Logistic Regression
                self._explainer = shap.LinearExplainer(
                    self.classifier, self._transformed_background
                )
            else:
                # KernelExplainer fallback for SVC or other models
                # Using predict_proba for risk class (1)
                predict_fn = lambda x: self.classifier.predict_proba(x)[:, 1]
                # Use small k-means or summary background to keep KernelExplainer fast
                bg_summary = shap.kmeans(self._transformed_background, min(10, len(self._transformed_background)))
                self._explainer = shap.KernelExplainer(predict_fn, bg_summary)
        except Exception as e:
            # Generic model-agnostic Explainer fallback
            print(f"[SHAP] Specific explainer failed, falling back to generic Explainer: {e}")
            try:
                self._explainer = shap.Explainer(self.classifier, self._transformed_background)
            except Exception as e2:
                print(f"[SHAP Error] Generic Explainer initialization failed: {e2}")
                self._explainer = None

    def explain_single_prediction(
        self,
        student_input: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Computes local SHAP explanation for a single student prediction.

        Returns:
            Dictionary with feature contributions, risk-increasing/protective factors,
            ranked impacts, and plain-language summary.
        """
        if self.preprocessor is None or self.classifier is None or self._explainer is None:
            return {
                "status": "UNAVAILABLE",
                "message": "SHAP explainer not available for this model.",
                "contributions": []
            }

        student_df = student_input.copy()
        if hasattr(self.preprocessor, "transformers_"):
            for trans_name, transformer, cols in self.preprocessor.transformers_:
                if trans_name != "remainder" and isinstance(cols, (list, tuple)):
                    for col in cols:
                        if col not in student_df.columns:
                            student_df[col] = 0.0 if trans_name == "num" else "no"

        # Transform single input row
        X_trans = self.preprocessor.transform(student_df)
        if hasattr(X_trans, "toarray"):
            X_trans = X_trans.toarray()


        feature_names = self._feature_names or [f"feat_{i}" for i in range(X_trans.shape[1])]

        try:
            raw_shap = self._explainer.shap_values(X_trans)

            # Extract SHAP values for positive class (at-risk)
            if isinstance(raw_shap, list):
                # Multiclass list: take class 1 (at-risk)
                vals = raw_shap[1][0] if len(raw_shap) > 1 else raw_shap[0][0]
            elif isinstance(raw_shap, np.ndarray):
                if raw_shap.ndim == 3:
                    # (n_samples, n_features, n_classes)
                    vals = raw_shap[0, :, 1] if raw_shap.shape[2] > 1 else raw_shap[0, :, 0]
                elif raw_shap.ndim == 2:
                    vals = raw_shap[0]
                else:
                    vals = raw_shap
            else:
                vals = np.array(raw_shap)

            # Base value
            base_val = getattr(self._explainer, "expected_value", 0.0)
            if isinstance(base_val, (list, np.ndarray)):
                base_val = float(base_val[1]) if len(base_val) > 1 else float(base_val[0])
            else:
                base_val = float(base_val)

        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"SHAP computation error: {str(e)}",
                "contributions": []
            }

        # Build feature contributions list
        contributions = []
        raw_input_dict = student_input.iloc[0].to_dict()

        for idx, name in enumerate(feature_names):
            val = float(vals[idx])
            # Match transformed feature name back to raw input value if available
            raw_val = raw_input_dict.get(name, None)
            if raw_val is None:
                # Check for one-hot encoded prefixes
                for k, v in raw_input_dict.items():
                    if name.startswith(k):
                        raw_val = v
                        break

            contributions.append({
                "feature": name,
                "raw_value": raw_val,
                "shap_value": round(val, 4),
                "abs_impact": round(abs(val), 4),
                "is_risk_increasing": bool(val > 0),
                "is_protective": bool(val < 0),
            })

        # Rank by absolute magnitude
        contributions_sorted = sorted(contributions, key=lambda x: x["abs_impact"], reverse=True)

        risk_increasing = [c for c in contributions_sorted if c["is_risk_increasing"]]
        protective = [c for c in contributions_sorted if c["is_protective"]]

        # Plain language narratives
        plain_language = []
        for c in risk_increasing[:3]:
            feat = c["feature"].replace("_", " ").title()
            val_str = f" ({c['raw_value']})" if c["raw_value"] is not None else ""
            plain_language.append(
                f"{feat}{val_str} elevated the student's predicted academic risk by +{c['shap_value']:.2f}."
            )
        for c in protective[:2]:
            feat = c["feature"].replace("_", " ").title()
            val_str = f" ({c['raw_value']})" if c["raw_value"] is not None else ""
            plain_language.append(
                f"{feat}{val_str} acted as a protective buffer, reducing risk by {c['shap_value']:.2f}."
            )

        return {
            "status": "SUCCESS",
            "base_value": round(base_val, 4),
            "contributions": contributions_sorted,
            "risk_increasing_factors": risk_increasing,
            "protective_factors": protective,
            "top_risk_factor": risk_increasing[0]["feature"] if risk_increasing else None,
            "plain_language_summary": plain_language,
            "additive_sum": round(float(np.sum(vals)), 4),
        }

    def compute_global_importance(
        self,
        cohort_df: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """
        Computes mean absolute SHAP feature importance across a cohort.
        """
        if self._explainer is None or self.preprocessor is None:
            return []

        sample_cohort = cohort_df.sample(min(len(cohort_df), 100), random_state=42).copy()

        # Align input features with preprocessor requirements
        if hasattr(self.preprocessor, "transformers_"):
            for trans_name, transformer, cols in self.preprocessor.transformers_:
                if trans_name != "remainder" and isinstance(cols, (list, tuple)):
                    for col in cols:
                        if col not in sample_cohort.columns:
                            sample_cohort[col] = 0.0 if trans_name == "num" else "no"

        try:
            X_trans = self.preprocessor.transform(sample_cohort)
            if hasattr(X_trans, "toarray"):
                X_trans = X_trans.toarray()

            feature_names = self._feature_names or [f"feat_{i}" for i in range(X_trans.shape[1])]
            raw_shap = self._explainer.shap_values(X_trans)
            if isinstance(raw_shap, list):
                vals = raw_shap[1] if len(raw_shap) > 1 else raw_shap[0]
            elif isinstance(raw_shap, np.ndarray) and raw_shap.ndim == 3:
                vals = raw_shap[:, :, 1] if raw_shap.shape[2] > 1 else raw_shap[:, :, 0]
            else:
                vals = raw_shap

            mean_abs = np.mean(np.abs(vals), axis=0)
            importance = [
                {
                    "feature": feature_names[i],
                    "mean_abs_shap": round(float(mean_abs[i]), 4)
                }
                for i in range(len(feature_names))
            ]
            return sorted(importance, key=lambda x: x["mean_abs_shap"], reverse=True)
        except Exception as e:
            print(f"[SHAP Error] Global importance computation failed: {e}")
            return []
