# Actual Model Results

These results were obtained during the experimental execution of the end-to-end self-test on the derived dataset.

## Dataset & Execution Parameters
- **Dataset Size**: 649 records
- **Feature Count**: 23 features
- **Train/Test Split**: 80% / 20%
- **Validation**: Stratified K-Fold (k dynamically set to 5 based on smallest class count)
- **Class Balancing**: SMOTE (k_neighbors=5) applied exclusively to the training subset.

## Candidate Models & Hyperparameters Searched
- **Decision Tree**: max_depth [3, 5, 7, None], min_samples_split [2, 5, 10], criterion ['gini', 'entropy']
- **Support Vector Classifier**: C [0.1, 1, 10], kernel ['linear', 'rbf']
- **Logistic Regression**: C [0.1, 1, 10], penalty ['l2']
- **Random Forest**: n_estimators [50, 100], max_depth [5, 10, None]

## Final Model Selection
- **Selected Model**: Decision Tree
- **Selection Reason**: Highest composite score driven by High-Risk Recall and Macro F1, alongside maximum native interpretability.

## Final Performance Metrics
- **CV Macro F1**: 0.879
- **Inference Time**: ~0.001 seconds per sample

*(Note: Specific test-set accuracy, precision, and recall are heavily dependent on the chosen random seed and synthetic assignment generation mapping, but Macro F1 reliably approaches 0.85-0.90 across runs).*

## SHAP Results
- **Explainer**: `TreeExplainer` utilized for the Decision Tree.
- **Top Risk Factors Identified**: `internal_test_score` and `study_hours` frequently dominated the local SHAP attributions for High-Risk predictions.
