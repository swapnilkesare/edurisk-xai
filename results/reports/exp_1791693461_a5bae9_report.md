# EduRisk XAI — Experimental Evaluation Report

- **Experiment ID**: `exp_1791693461_a5bae9`
- **Execution Timestamp**: `2026-10-11 10:07:41`
- **Dataset**: UCI Student Performance (Augmented) (Fingerprint: `396e1d5d8ecf1bc5`)
- **Synthetic Flag**: Real Benchmark Data
- **Samples**: Train = 519, Test = 130
- **Selected Optimal Model**: **Random Forest**

### Selection Policy Rationale
> Selected Random Forest based on highest Cross-Validation Macro F1 (0.8787) across 4 evaluated candidate pipelines.

### Comparative Performance Matrix

| Model | CV Macro F1 | Test Macro F1 | Test Acc | High-Risk Recall | False Negatives | Train Time (s) | Latency (ms) |
|---|---|---|---|---|---|---|---|
| Decision Tree | 0.8522 | 0.8077 | 0.8769 | 0.9000 | 2 | 3.19s | 9.15ms |
| Support Vector Classifier | 0.8256 | 0.8365 | 0.9000 | 0.9000 | 2 | 4.49s | 8.90ms |
| Logistic Regression | 0.8376 | 0.8467 | 0.9077 | 0.9000 | 2 | 1.03s | 9.21ms |
| Random Forest | 0.8787 | 0.8077 | 0.8769 | 0.9000 | 2 | 8.82s | 18.98ms |

### Research Integrity Notes
1. **Holdout Independence**: The test set was strictly quarantined prior to preprocessing and SMOTE resampling.
2. **Resampling Isolation**: SMOTE was executed exclusively within training cross-validation folds.
3. **Lightweight Deployment**: All pipelines operated on consumer CPU without GPU dependencies.