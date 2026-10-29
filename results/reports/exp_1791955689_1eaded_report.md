# EduRisk XAI — Experimental Evaluation Report

- **Experiment ID**: `exp_1791955689_1eaded`
- **Execution Timestamp**: `2026-10-14 10:58:09`
- **Dataset**: UCI Student Performance (Augmented) (Fingerprint: `396e1d5d8ecf1bc5`)
- **Synthetic Flag**: Real Benchmark Data
- **Samples**: Train = 96, Test = 24
- **Selected Optimal Model**: **Decision Tree**

### Selection Policy Rationale
> Selected Decision Tree based on highest Cross-Validation Macro F1 (0.7864) across 4 evaluated candidate pipelines.

### Comparative Performance Matrix

| Model | CV Macro F1 | Test Macro F1 | Test Acc | High-Risk Recall | False Negatives | Train Time (s) | Latency (ms) |
|---|---|---|---|---|---|---|---|
| Decision Tree | 0.7864 | 0.8884 | 0.9583 | 0.6667 | 1 | 1.52s | 4.87ms |
| Support Vector Classifier | 0.6291 | 0.7491 | 0.8750 | 0.6667 | 1 | 0.96s | 4.88ms |
| Logistic Regression | 0.6453 | 0.7491 | 0.8750 | 0.6667 | 1 | 0.48s | 4.86ms |
| Random Forest | 0.5357 | 0.7273 | 0.9167 | 0.3333 | 2 | 3.72s | 9.03ms |

### Research Integrity Notes
1. **Holdout Independence**: The test set was strictly quarantined prior to preprocessing and SMOTE resampling.
2. **Resampling Isolation**: SMOTE was executed exclusively within training cross-validation folds.
3. **Lightweight Deployment**: All pipelines operated on consumer CPU without GPU dependencies.