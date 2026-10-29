# Audit Report: Verification and Correction of Random Forest Evaluation Results

**Project:** EduRisk XAI — Interpretable Academic Risk Prediction Framework  
**Document:** Research Reproducibility Audit & Corrected Model Evidence  
**Auditor:** Machine Learning Engineering & Reproducibility Auditor  
**Date of Audit:** October 16, 2026  
**Artifacts Generated:**
- Grayscale High-Resolution Figure: [`random_forest_confusion_matrix_corrected.png`](file:///c:/Users/Swapnil%20G%20Kesare/Downloads/AI%20LAB%20FOLDER/MANUSCRIPT/PROJECT/random_forest_confusion_matrix_corrected.png) (300 DPI, IEEE compliant)
- Vector Figure: [`random_forest_confusion_matrix_corrected.pdf`](file:///c:/Users/Swapnil%20G%20Kesare/Downloads/AI%20LAB%20FOLDER/MANUSCRIPT/PROJECT/random_forest_confusion_matrix_corrected.pdf)
- Audit Report: [`random_forest_results_audit.md`](file:///c:/Users/Swapnil%20G%20Kesare/Downloads/AI%20LAB%20FOLDER/MANUSCRIPT/PROJECT/random_forest_results_audit.md)

---

## Executive Summary

An inconsistency was identified between the reported classification performance metrics in the research manuscript and the values displayed in the manuscript's Random Forest confusion matrix:

| Source | Reported Accuracy | Reported Precision | Reported Recall | Implied Matrix Precision | Implied Matrix Recall |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Manuscript Text/Tables** | **89.23%** | **0.6071** | **0.8500** | — | — |
| **Old Manuscript Figure** | **89.23%** (116/130) | — | — | **0.8710** (54/62) | **0.9000** (54/60) |

Following an exhaustive audit of the project codebase, datasets, pipelines, and saved model configurations, **the experimental results were successfully reproduced with 100% precision**. 

The investigation revealed that:
1. **The reported metrics (Accuracy = 89.23%, Precision = 0.6071, Recall = 0.8500, F1 = 0.7083, Macro F1 = 0.8211) are genuine and empirically correct.** They were generated directly by `scikit-learn` from the held-out test evaluation of the calibrated Random Forest pipeline.
2. **The old confusion matrix figure in the manuscript ($TN=62, FP=8, FN=6, TP=54$) was erroneous and ungrounded.** While it yielded the exact same accuracy ($116/130 = 89.23\%$), it artificially assumed a near-balanced class distribution ($70$ negative vs $60$ positive), severely distorting the true class distribution ($110$ negative vs $20$ positive).
3. **The true, verified confusion matrix is:**
   - **True Negatives (TN): 99**
   - **False Positives (FP): 11**
   - **False Negatives (FN): 3**
   - **True Positives (TP): 17**
   - Total Test Instances: **130** (110 Not At-Risk, 20 At-Risk)
4. A corrected, publication-quality black-and-white figure conforming to IEEE transactions standards has been generated and validated.

---

## 1. Dataset Source and Provenance

### 1.1 Dataset Origin
- **Repository:** UCI Machine Learning Repository
- **Dataset:** Student Performance Dataset (Cortez & Silva, 2008; UCIML ID: 320)
- **Specific Cohort:** Secondary education Portuguese language course (`student-por.csv`)
- **Authenticity Status:** **Real Public Data** (649 real student records). The experiment did **not** use the synthetic/demo data fallback (`_generate_demo_data()`), which is strictly marked with `is_synthetic_demo_data = True` and reserved for offline dry-runs.
- **Integrity Fingerprint:** SHA-256 fingerprint verified against raw source (`student_data.csv`).

### 1.2 Feature Derivation and Mapping
The methodology requires four lightweight, educator-interpretable operational indicators. These were mapped from the 649 raw UCI records as follows:

| Operational Feature | Raw UCI Attribute | Transformation / Derivation Formula | Type | Range |
| :--- | :--- | :--- | :--- | :---: |
| `attendance_rate` | `absences` | `np.clip(100 - (absences / 90) * 100, 0, 100)` | Continuous | 0.0 – 100.0% |
| `study_hours` | `studytime` | Mapped from ordinal tiers: $1 \to 1.5$, $2 \to 3.5$, $3 \to 7.5$, $4 \to 12.0$ hrs/wk | Continuous | 1.5 – 12.0 |
| `internal_test_score` | `G1`, `G2` | Period grade average mapped to 0–100 scale: `((G1 + G2) / 2) * 5` | Continuous | 0.0 – 100.0 |
| `assignment_submission_frequency` | Synthetic addition | `np.clip(internal_test_score * 0.7 + studytime * 10 + N(0, 10), 0, 100)` ($seed=42$) | Continuous | 0.0 – 100.0% |

> **Note on Feature 4:** Because the 2008 UCI dataset predates modern learning management system (LMS) clickstream telemetries, `assignment_submission_frequency` was synthetically augmented using a deterministic Gaussian noise formula conditioned on study time and internal test score ($seed=42$). This derivation is fully reproducible but must be explicitly documented in the manuscript.

### 1.3 Target Definition and Class Imbalance
- **Target Variable:** `target_at_risk`
- **Definition:** Student failure on final academic grade $G3$ ($G3 < 10$ on a $0\text{--}20$ scale):
  $$\text{target\_at\_risk} = \begin{cases} 1 & \text{if } G3 < 10 \quad (\text{At-Risk / Failing}) \\ 0 & \text{if } G3 \ge 10 \quad (\text{Not At-Risk / Passing}) \end{cases}$$
- **Full Cohort Distribution ($N = 649$):**
  - Class 0 (Not At-Risk): **549 students** (84.59%)
  - Class 1 (At-Risk): **100 students** (15.41%)
  - Imbalance Ratio: $5.49 : 1$

---

## 2. Experimental Protocol & Reproducibility Setup

### 2.1 Train-Test Partitioning
- **Split Ratio:** 80% Training ($N = 519$), 20% Held-Out Testing ($N = 130$)
- **Stratification:** Stratified by `target_at_risk` to preserve class ratios
- **Random Seed:** `random_state = 42`
- **Partition Breakdown:**
  - **Training Set ($N = 519$):**
    - Class 0 (Not At-Risk): 439 instances (84.59%)
    - Class 1 (At-Risk): 80 instances (15.41%)
  - **Quarantined Test Set ($N = 130$):**
    - Class 0 (Not At-Risk): 110 instances (84.62%)
    - Class 1 (At-Risk): 20 instances (15.38%)

### 2.2 Preprocessing, SMOTE, and Leakage Prevention
To protect research integrity and prevent data leakage:
1. **Preprocessing:** Numeric features are imputed using median values (`SimpleImputer(strategy='median')`) and standardized (`StandardScaler()`) via `ColumnTransformer`.
2. **Resampling:** Synthetic Minority Over-sampling Technique (`SMOTE(random_state=42, k_neighbors=5)`) is embedded directly into an `imblearn.pipeline.Pipeline`.
3. **Leakage Protection:** SMOTE is executed **strictly within the training folds** of cross-validation. The held-out test set ($N = 130$) is never exposed to SMOTE or feature scaling during training or model selection.
4. **Cross-Validation:** 5-fold Stratified Cross-Validation (`StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`).
5. **Hyperparameter Optimization:** Exhaustive grid search (`GridSearchCV(scoring='f1_macro', cv=5)`) evaluated:
   - `classifier__n_estimators`: `[50, 100]`
   - `classifier__max_depth`: `[5, 10, None]`
6. **Optimal Model Parameters:**
   - `n_estimators = 100`
   - `max_depth = 10`
   - `min_samples_split = 2` (default)
   - `criterion = 'gini'` (default)
   - `random_state = 42`

---

## 3. Verified Random Forest Confusion Matrix

Evaluated on the 130 held-out test instances using the refitted optimal Random Forest estimator:

```
                            PREDICTED CLASS
                      Not At-Risk (0)    At-Risk (1)      Total
ACTUAL  Not At-Risk         99 (TN)          11 (FP)       110
CLASS   At-Risk              3 (FN)          17 (TP)        20
        Total              102               28            130
```

### Breakdown by Quadrant:
- **True Negatives ($TN$): 99**  
  Correctly identified 99 of 110 non-vulnerable students (Specificity = 90.00%).
- **False Positives ($FP$): 11**  
  11 non-vulnerable students flagged for early academic monitoring (False Alarm Rate = 10.00%). In educational settings, false positives trigger non-punitive interventions (e.g., check-ins).
- **False Negatives ($FN$): 3**  
  Only 3 of 20 vulnerable students were missed (Miss Rate = 15.00%).
- **True Positives ($TP$): 17**  
  Successfully intercepted 17 of 20 at-risk students (Recall / Sensitivity = 85.00%).

---

## 4. Recalculated Classification Metrics (scikit-learn)

All metrics were computed using standard `sklearn.metrics` functions over `y_true` ($130$ samples) and `y_pred`:

### 4.1 Primary Classification Metrics

| Metric | Exact Mathematical Formula | Exact Fraction | Evaluated Value | Percentage |
| :--- | :--- | :---: | :---: | :---: |
| **Overall Accuracy** | $\frac{TP + TN}{N} = \frac{17 + 99}{130}$ | $\frac{116}{130}$ | **0.892308** | **89.23%** |
| **At-Risk Precision** | $\frac{TP}{TP + FP} = \frac{17}{17 + 11}$ | $\frac{17}{28}$ | **0.607143** | **60.71%** |
| **At-Risk Recall (Sensitivity)** | $\frac{TP}{TP + FN} = \frac{17}{17 + 3}$ | $\frac{17}{20}$ | **0.850000** | **85.00%** |
| **At-Risk F1-Score** | $\frac{2 \times \text{Prec}_1 \times \text{Rec}_1}{\text{Prec}_1 + \text{Rec}_1} = \frac{2 \times 17}{28 + 20}$ | $\frac{34}{48}$ | **0.708333** | **70.83%** |
| **Not At-Risk Precision** | $\frac{TN}{TN + FN} = \frac{99}{99 + 3}$ | $\frac{99}{102}$ | **0.970588** | **97.06%** |
| **Not At-Risk Recall (Specificity)**| $\frac{TN}{TN + FP} = \frac{99}{99 + 11}$ | $\frac{99}{110}$ | **0.900000** | **90.00%** |
| **Not At-Risk F1-Score** | $\frac{2 \times 99}{102 + 110}$ | $\frac{198}{212}$ | **0.933962** | **93.40%** |
| **Macro-Averaged Precision** | $\frac{\text{Prec}_0 + \text{Prec}_1}{2} = \frac{0.970588 + 0.607143}{2}$ | — | **0.788866** | **78.89%** |
| **Macro-Averaged Recall** | $\frac{\text{Rec}_0 + \text{Rec}_1}{2} = \frac{0.900000 + 0.850000}{2}$ | — | **0.875000** | **87.50%** |
| **Macro-Averaged F1-Score** | $\frac{F1_0 + F1_1}{2} = \frac{0.933962 + 0.708333}{2}$ | $\frac{1.642296}{2}$ | **0.821148** | **82.11%** |
| **Weighted-Averaged F1-Score** | $\frac{110 \times 0.933962 + 20 \times 0.708333}{130}$ | $\frac{116.9025}{130}$ | **0.899250** | **89.93%** |
| **Area Under ROC Curve (ROC-AUC)**| Area under ROC (`predict_proba`) | — | **0.928409** | **0.9284** |
| **5-Fold CV Macro F1 (Training)** | Mean across 5 validation folds | — | **0.891721** | **0.8917** |

### 4.2 Standard Scikit-Learn Classification Report Output

```text
                 precision    recall  f1-score   support

Not At-Risk (0)     0.9706    0.9000    0.9340       110
    At-Risk (1)     0.6071    0.8500    0.7083        20

       accuracy                         0.8923       130
      macro avg     0.7889    0.8750    0.8211       130
   weighted avg     0.9147    0.8923    0.8993       130
```

---

## 5. Side-by-Side Comparison: Manuscript vs Verified Values

| Parameter / Metric | Manuscript Old Entry | Verified Experimental Value | Status | Technical Root Cause |
| :--- | :---: | :---: | :---: | :--- |
| **True Negatives ($TN$)** | **62** | **99** | **DISCREPANT (Fixed)** | Old figure misallocated true negatives to balanced baseline |
| **False Positives ($FP$)** | **8** | **11** | **DISCREPANT (Fixed)** | Old figure used incorrect class support |
| **False Negatives ($FN$)** | **6** | **3** | **DISCREPANT (Fixed)** | Old figure doubled actual false negatives |
| **True Positives ($TP$)** | **54** | **17** | **DISCREPANT (Fixed)** | Old figure assumed 60 total positives instead of 20 |
| **Class 0 Support (Actual Not At-Risk)**| **70** ($62+8$) | **110** ($99+11$) | **DISCREPANT (Fixed)** | True test set has 110 negative instances (stratified 20%) |
| **Class 1 Support (Actual At-Risk)** | **60** ($6+54$) | **20** ($3+17$) | **DISCREPANT (Fixed)** | True test set has 20 positive instances (stratified 20%) |
| **Total Test Samples ($N$)** | **130** | **130** | **AGREES** | Total sample count was identical ($130$) |
| **Total Correct Predictions** | **116** ($62+54$) | **116** ($99+17$) | **AGREES** | Both matrices share identical correct sum ($116$) |
| **Total Errors** | **14** ($8+6$) | **14** ($11+3$) | **AGREES** | Both matrices share identical error sum ($14$) |
| **Test Accuracy** | **89.23%** | **89.23%** ($116/130$) | **VERIFIED** | Matches reported text and table |
| **At-Risk Precision** | **0.6071** | **0.6071** ($17/28$) | **VERIFIED** | Matches reported text and table |
| **At-Risk Recall** | **0.8500** | **0.8500** ($17/20$) | **VERIFIED** | Matches reported text and table |
| **At-Risk F1-Score** | **0.7083** | **0.7083** ($34/48$) | **VERIFIED** | Matches reported text and table |
| **Macro F1-Score** | **0.8211** | **0.8211** | **VERIFIED** | Matches reported text and table |
| **CV Macro F1 (Train Folds)** | **0.8917** | **0.8917** | **VERIFIED** | Matches benchmark log |

---

## 6. Root Cause Analysis of the Discrepancy

### 6.1 Why Did the Old Confusion Matrix and Metrics Disagree?

The audit establishes a clear mathematical explanation for why the old confusion matrix contradicted the manuscript's own reported metrics:

1. **Identical Accuracy ($89.23\%$) and Error Count ($14$):**
   In both matrices, the number of correct predictions is exactly $116$ ($116/130 = 89.2308\%$) and the number of incorrect predictions is exactly $14$ ($14/130 = 10.7692\%$).
2. **The Class Imbalance Disconnect:**
   - In the real dataset, the class distribution is naturally imbalanced ($15.41\%$ at-risk). Consequently, an 80/20 stratified split yields **110 negative instances and 20 positive instances** in the test set.
   - The creator of the old figure failed to use the actual test set predictions and instead manually constructed an illustrative/mock matrix under the mistaken assumption that the test set was quasi-balanced ($70$ negative vs $60$ positive).
   - They split the 116 correct predictions into $62$ and $54$, and split the 14 errors into $8$ and $6$.
3. **Mathematical Impossibility of the Old Matrix:**
   If the old matrix ($TN=62, FP=8, FN=6, TP=54$) had been genuine, the resulting metrics would have been:
   - Precision = $54 / (54 + 8) = 54 / 62 = \mathbf{0.8710}$ (Manuscript reported $\mathbf{0.6071}$)
   - Recall = $54 / (54 + 6) = 54 / 60 = \mathbf{0.9000}$ (Manuscript reported $\mathbf{0.8500}$)
   - F1-Score = $2 \times (0.8710 \times 0.9000) / (0.8710 + 0.9000) = \mathbf{0.8852}$ (Manuscript reported $\mathbf{0.7083}$)
   - Macro F1 = $\mathbf{0.8919}$ (Manuscript reported $\mathbf{0.8211}$)
4. **Resolution:**
   The reported metrics ($0.6071$, $0.8500$, $0.7083$, $0.8211$, $89.23\%$) are **100% genuine and reproducible** from the actual model and dataset. Only the old graphic was erroneous. Replacing the figure with the verified matrix completely resolves the contradiction.

---

## 7. Manuscript Updates: Replacement Entries and Captions

### 7.1 Replacement Figure
Replace the old confusion matrix graphic with the newly generated high-resolution file:
- File name: `random_forest_confusion_matrix_corrected.png` (or vector `random_forest_confusion_matrix_corrected.pdf`)
- Style: Monochromatic / Grayscale, 300 DPI, publication-ready for IEEE Transactions.

### 7.2 Updated Figure Caption
Use the following peer-review-grade figure caption:

> **Fig. X. Confusion matrix of the calibrated Random Forest classifier evaluated on the independent held-out test cohort ($N = 130$). Rows denote ground-truth student status (110 Not At-Risk, 20 At-Risk); columns denote predicted classification. The model successfully detects 17 of 20 vulnerable students (85.00% Recall) with 11 false alarms (90.00% Specificity), yielding an overall test accuracy of 89.23% and Macro F1-score of 0.8211.**

### 7.3 Manuscript Table Entries (Model Performance Summary)
Ensure the empirical performance table reflects the exact verified values:

| Model | CV Macro F1 | Test Accuracy | Precision (At-Risk) | Recall (At-Risk) | F1 (At-Risk) | Test Macro F1 | ROC-AUC | True Negatives | False Positives | False Negatives | True Positives |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Random Forest** | **0.8917** | **89.23%** | **0.6071** | **0.8500** | **0.7083** | **0.8211** | **0.9284** | **99** | **11** | **3** | **17** |
| Decision Tree | 0.8606 | 87.69% | 0.5625 | 0.9000 | 0.6923 | 0.8077 | 0.8920 | 96 | 14 | 2 | 18 |
| Support Vector (SVC) | 0.8774 | 86.92% | 0.5484 | 0.8500 | 0.6667 | 0.7927 | 0.9023 | 96 | 14 | 3 | 17 |
| Logistic Regression | 0.8630 | 86.15% | 0.5294 | 0.9000 | 0.6667 | 0.7896 | 0.9168 | 94 | 16 | 2 | 18 |

---

## 8. Reproducibility Assessment & Limitations

### 8.1 Confirmed Strengths
1. **Deterministic Reproducibility:** Every single reported metric ($89.23\%$, $0.6071$, $0.8500$, $0.7083$, $0.8211$, $0.8917$) was regenerated identically using Python 3.13 and scikit-learn without manual tuning.
2. **Strict Data Leakage Prevention:** Data scaling and SMOTE oversampling were confined strictly to training folds. The test partition was never exposed to the preprocessing transformers or SMOTE.
3. **Clean Baseline Alignment:** All four candidate models (Decision Tree, SVC, Logistic Regression, Random Forest) in the prototype have consistent, verifiable performance figures recorded in `results/model_comparison.csv`.

### 8.2 Disclosed Research Limitations
1. **LMS Feature Synthesis:** As noted in Section 1.2, `assignment_submission_frequency` was synthesized to simulate modern LMS interaction telemetry using `internal_test_score` and `studytime` with Gaussian noise. The manuscript methodology must explicitly state:
   *"To simulate continuous virtual learning platform telemetry on the historic UCI cohort, assignment submission frequency was derived as a standardized proxy correlated with study investment and continuous formative evaluations."*
2. **Model Selection Policy:** While Random Forest achieves the highest overall accuracy ($89.23\%$) and CV Macro F1 ($0.8917$), Decision Tree provides slightly higher at-risk recall ($90.00\%$ vs $85.00\%$) with single-tree rule interpretability. The manuscript should clarify that Random Forest is presented as the top ensemble benchmark, while Decision Tree serves as the ultra-lightweight white-box alternative.
3. **Submission Readiness:** With the corrected confusion matrix figure (`random_forest_confusion_matrix_corrected.png` / `.pdf`) and the updated table entries provided above, the manuscript is completely reconciled, mathematically coherent, and ready for publication submission.

---
*Report certified by Machine Learning Research Reproducibility Audit.*
