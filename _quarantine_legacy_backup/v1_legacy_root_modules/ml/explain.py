import shap
import pandas as pd
import numpy as np
import logging
from ml.preprocessing import get_feature_names

logger = logging.getLogger(__name__)

class SHAPExplainer:
    def __init__(self, model_artifact, background_data=None):
        """
        Initializes the SHAP Explainer.
        model_artifact is the dictionary returned by train.py/load_current_model().
        background_data is the raw DataFrame (without target) used to fit the explainer if needed.
        """
        self.artifact = model_artifact
        self.pipeline = self.artifact['model']
        self.model_name = self.artifact['model_name']
        self.classifier = self.pipeline.named_steps['classifier']
        self.preprocessor = self.pipeline.named_steps['preprocessor']
        self.feature_names = self.artifact['feature_names']
        
        self.explainer = None
        self.expected_value = None
        self._initialize_explainer(background_data)

    def _initialize_explainer(self, background_data):
        try:
            # We need the preprocessed background data for the explainer
            if background_data is not None:
                # Remove target if present
                if 'target_at_risk' in background_data.columns:
                    background_data = background_data.drop(columns=['target_at_risk'])
                if 'is_synthetic_demo_data' in background_data.columns:
                    background_data = background_data.drop(columns=['is_synthetic_demo_data'])
                
                # Preprocess background data
                X_background = self.preprocessor.transform(background_data)
                
                # Sample background data for performance if it's too large
                if X_background.shape[0] > 100:
                    idx = np.random.choice(X_background.shape[0], 100, replace=False)
                    X_background = X_background[idx]
            else:
                X_background = None

            # Choose the appropriate explainer
            if self.model_name in ['Decision Tree', 'Random Forest']:
                self.explainer = shap.TreeExplainer(self.classifier)
                self.expected_value = self.explainer.expected_value
            elif self.model_name in ['Logistic Regression', 'SVC']:
                if X_background is not None:
                    # Use LinearExplainer for Logistic Regression, KernelExplainer for SVC
                    if self.model_name == 'Logistic Regression':
                        self.explainer = shap.LinearExplainer(self.classifier, X_background)
                    else:
                        # SVM with RBF requires KernelExplainer or sampling
                        # predict_proba for probabilities if SVC probability=True
                        self.explainer = shap.KernelExplainer(self.classifier.predict_proba, X_background)
                    self.expected_value = self.explainer.expected_value
                else:
                    logger.warning("Background data required for Linear/Kernel explainer. SHAP might fail.")
            
            logger.info(f"Initialized SHAP Explainer for {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize SHAP explainer: {e}")

    def explain_prediction(self, raw_input_df: pd.DataFrame):
        """
        Returns SHAP explanation for a single raw prediction.
        """
        if self.explainer is None:
            return None

        try:
            # Preprocess the single input
            X_transformed = self.preprocessor.transform(raw_input_df)
            
            # Compute SHAP values
            shap_values = self.explainer.shap_values(X_transformed)
            
            # Extract values for the 'At-Risk' class (Class 1)
            if isinstance(shap_values, list):
                # TreeExplainer for classification returns a list
                class_1_shap = shap_values[1][0]
            elif len(shap_values.shape) == 3:
                # Depending on SHAP version / explainer
                class_1_shap = shap_values[0, :, 1]
            else:
                # Kernel / Linear explainer might return just the target class if we pass predict_proba[:,1],
                # but if we passed predict_proba it returns for all classes.
                # Let's handle the typical 2D array output safely
                if len(shap_values.shape) == 2 and shap_values.shape[0] == 1:
                    class_1_shap = shap_values[0]
                else:
                    class_1_shap = shap_values[1][0] if isinstance(shap_values, list) else shap_values[0]
            
            # Map to feature names (using the preprocessor feature names out)
            num_features = raw_input_df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
            cat_features = raw_input_df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
            feature_names = get_feature_names(self.preprocessor, num_features, cat_features)
            
            # Create a dictionary of feature -> SHAP value
            shap_dict = {feature_names[i]: float(class_1_shap[i]) for i in range(len(feature_names))}
            
            # Sort by absolute contribution
            sorted_shap = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)
            
            risk_increasing = [{"feature": k, "value": v} for k, v in sorted_shap if v > 0]
            risk_decreasing = [{"feature": k, "value": v} for k, v in sorted_shap if v < 0]
            
            return {
                "shap_values": class_1_shap.tolist(),
                "feature_names": feature_names,
                "expected_value": float(self.expected_value[1] if isinstance(self.expected_value, (list, np.ndarray)) else self.expected_value),
                "risk_increasing": risk_increasing,
                "risk_decreasing": risk_decreasing,
                "transformed_input": X_transformed[0].tolist()
            }
        except Exception as e:
            logger.error(f"Error during SHAP explanation generation: {e}")
            return None
