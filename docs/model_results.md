# Empirical Model Results & Performance Analysis

## 1. Experiment Overview
- **Experiment ID**: `exp_1791693461_a5bae9`
- **Execution Date**: 2026-10-11
- **Dataset**: UCI Student Performance (Portuguese Secondary Cohort, Cortez & Silva 2008, Augmented)
- **Dataset Fingerprint**: `396e1d5d8ecf1bc5`
- **Samples**: 649 Total (519 Training, 130 Quarantined Holdout Test)
- **Class Breakdown**: 110 Safe (0), 20 At-Risk (1) in test set.
- **Selected Optimal Model**: **Random Forest** (CV Macro F1 = **0.8787**)

---

## 2. Classifier Benchmark Matrix

The table below presents actual execution results on the independent holdout test set (130 students, 20 high-risk):

| Classifier | CV Macro F1 (Train) | Test Macro F1 | Test Accuracy | High-Risk Recall | False Negatives | ROC-AUC | Training Time (s) | Inference Latency (ms) | Artifact Size (KB) |
|---|---|---|---|---|---|---|---|---|---|
| **Random Forest** | **0.8787** ± 0.0515 | 0.8077 | 87.69% | **90.00%** | 2 | 0.9236 | 8.82s | 18.98ms | 288.54 KB |
| **Decision Tree** | 0.8522 ± 0.0517 | 0.8077 | 87.69% | **90.00%** | 2 | 0.9255 | 3.19s | 9.15ms | 27.95 KB |
| **Logistic Regression** | 0.8376 ± 0.0712 | **0.8467** | **90.77%** | **90.00%** | 2 | 0.9382 | **1.03s** | 9.21ms | **26.74 KB** |
| **Support Vector (SVC)** | 0.8256 ± 0.0442 | 0.8365 | 90.00% | **90.00%** | 2 | **0.9459** | 4.49s | **8.90ms** | 62.67 KB |

---

## 3. Analysis of Research Trade-offs

### 3.1 At-Risk Detection & Safety
- **Uniform High-Risk Recall**: All four models achieved **90.00% Recall** on the at-risk minority class in the holdout test set, identifying 18 out of 20 vulnerable students.
- **False Negative Analysis**: Each model incurred exactly **2 false negatives** (struggling students misclassified as low-risk). This represents an acceptable early-warning safety margin given that secondary assessments occur iteratively throughout the semester.

### 3.2 Predictive Consistency & Generalization
- **Random Forest** achieved the highest cross-validation Macro F1 on the training partition (0.8787), establishing superior stability across folds.
- **Logistic Regression** demonstrated exceptional out-of-fold generalization with a holdout test Macro F1 of 0.8467 and test accuracy of 90.77%, coupled with the fastest training time (1.03s) and smallest model footprint (26.74 KB).
- **Decision Tree** achieved comparable test Macro F1 (0.8077) with immediate white-box rule transparency, rendering it an outstanding candidate for resource-constrained institutional deployments.

### 3.3 Computational Efficiency on CPU
- Training durations spanned from **1.03s to 8.82s** across 5 folds and grid searches on consumer CPU.
- Inference latencies per sample averaged **8.9ms to 18.98ms**, satisfying real-time interactive requirements for educational dashboards.

---

## 4. Visual Evidence Artifacts
- **Figure 1**: Multi-Model Performance Comparison Bar Chart (`results/figures/figure_1_model_comparison.png`)
- **Figure 2**: Computational Overhead & Inference Latency (`results/figures/figure_2_computational_efficiency.png`)
- **Machine-Readable Payload**: `results/experiments/exp_1791693461_a5bae9.json`
- **Comparative CSV Export**: `results/experiments/exp_1791693461_a5bae9_comparison.csv`
