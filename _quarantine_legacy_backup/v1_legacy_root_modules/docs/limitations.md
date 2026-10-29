# Limitations

The proposed framework successfully integrates predictive modeling, explainability, and pedagogical interventions; however, several limitations remain:

1. **Synthetic Feature Augmentation**: The base UCI dataset lacks an `assignment_submission_frequency` feature. A synthetically generated feature was added to satisfy the four core methodology variables. Performance metrics reflect this augmented dataset.
2. **True Longitudinal Tracking**: The longitudinal capabilities provided in this prototype record temporal snapshots (predictions at different dates). It does not implement a true Spatio-Temporal Deep Learning sequence model (like an LSTM) due to the computational requirements of such architectures.
3. **Live API Integrations**: While the schema accommodates generic datasets, there is no live API integration with institutional LMS systems (e.g., Moodle or Canvas). Data must be provided via CSV import.
4. **Causality vs. Contribution**: SHAP values indicate a feature's contribution to the model's prediction, not strict causal evidence. For example, a high SHAP value for "low attendance" does not guarantee that simply forcing attendance will linearly improve the student's true comprehension.
5. **Categorical Calibration**: Rule thresholds mapping SHAP values to specific interventions are rule-based and derived conceptually. They have not been validated against empirical pedagogical outcome studies.
