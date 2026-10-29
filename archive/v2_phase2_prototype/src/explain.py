import shap
import pandas as pd
import joblib
import numpy as np

class Explainer:
    def __init__(self, model_path='models/artifacts/best_model.pkl'):
        self.pipeline = joblib.load(model_path)
        self.classifier = self.pipeline.named_steps['classifier']
        self.preprocessor = self.pipeline.named_steps['preprocessor']
        self.model_name = self.classifier.__class__.__name__
        
    def explain(self, input_df: pd.DataFrame) -> dict:
        """
        Generates local SHAP explanations for the given student data.
        """
        # Transform the input using the pipeline's preprocessor
        X_transformed = self.preprocessor.transform(input_df)
        
        # Get feature names from the preprocessor
        feature_names = input_df.columns.tolist()
        
        # Select appropriate explainer
        if 'Tree' in self.model_name or 'Forest' in self.model_name:
            explainer = shap.TreeExplainer(self.classifier)
            shap_values = explainer.shap_values(X_transformed)
            # TreeExplainer for classification returns a list of arrays (one per class)
            # Or a single array for binary classification in some sklearn versions
            if isinstance(shap_values, list):
                shap_values_class_1 = shap_values[1][0]
            elif len(shap_values.shape) == 3: # (samples, features, classes)
                shap_values_class_1 = shap_values[0, :, 1]
            elif len(shap_values.shape) == 2: # (samples, features)
                shap_values_class_1 = shap_values[0]
            else:
                shap_values_class_1 = shap_values
                
            expected_value = explainer.expected_value
            if isinstance(expected_value, (list, np.ndarray)):
                expected_value = expected_value[-1]
                
        elif 'Logistic' in self.model_name or 'SVC' in self.model_name:
            # Fallback to LinearExplainer for Logistic, or KernelExplainer for SVC if needed
            # For phase 2 prototype with scaled data, LinearExplainer is fast
            if 'Logistic' in self.model_name:
                explainer = shap.LinearExplainer(self.classifier, self.preprocessor.transform(pd.DataFrame(columns=feature_names))) # dummy background not strictly needed for LinearExplainer if independent=False
                shap_values = explainer.shap_values(X_transformed)[0]
                expected_value = explainer.expected_value
            else:
                # SVC is tricky without a background dataset. We will use an approximation or just KernelExplainer with a zero background
                background = pd.DataFrame(0, index=np.arange(1), columns=range(X_transformed.shape[1]))
                explainer = shap.KernelExplainer(self.classifier.predict_proba, background)
                shap_values = explainer.shap_values(X_transformed)[1][0]
                expected_value = explainer.expected_value[1]
        else:
            raise ValueError(f"Unsupported model for prototype explainer: {self.model_name}")

        # Map to feature names
        contributions = []
        for i, feat in enumerate(feature_names):
            val = float(shap_values_class_1[i])
            contributions.append({
                "feature": feat,
                "value": val,
                "type": "risk" if val > 0 else "protective"
            })
            
        contributions = sorted(contributions, key=lambda x: abs(x['value']), reverse=True)
        
        return {
            "expected_value": float(expected_value),
            "contributions": contributions
        }
