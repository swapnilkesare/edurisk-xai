# EduRisk — Specification & Integration Roadmap for Additional Student Information

**Document:** `docs/additional_student_information_plan.md`  
**Status:** Architectural Specification & Research Guidance  
**Scope:** Evaluates potential future data dimensions, collection methodologies, validation constraints, privacy/equity safeguards, and model-safety protocols.

---

## 1. Executive Summary & Leakage Prevention Principles

Educational data science models are prone to subtle methodological traps, especially **target leakage** (using outcome-correlated information collected after the prediction horizon) and **proxy discrimination** (using demographic or socio-economic indicators that reinforce historical disparities).

This document evaluates six proposed candidate feature categories for future expansion in EduRisk. Each dimension is strictly categorized as either:
1. **Model-Suitable (Predictive Indicator):** Time-bounded, formative, operational data collected *strictly before* the target observation window.
2. **Pedagogical Support Planning Only (Contextual Indicator):** Information that must NOT enter the automated machine-learning pipeline to prevent bias, overfitting, or privacy violations, but serves educators during human-led advising and intervention design.

---

## 2. Detailed Dimension Evaluation

### Dimension 1: Subject-Wise Formative Marks & Continuous Assessment Scores
* **Intended Use:** Detect domain-specific learning gaps (e.g., student struggling specifically in Mathematics or Programming while excelling in Humanities), enabling targeted subject tutoring rather than generic warnings.
* **Current Status in Schema:** Partially exists as an aggregated single indicator (`internal_test_score`). Granular per-subject fields exist in relational table `academic_records` (`internal_test_score`, `assignment_score`), but the ML model consumes a unified 0–100% score.
* **Collection & Validation:**
  - Ingested via LMS gradebook API or instructor CSV upload.
  - Range validation: strictly bounded between `0.0` and `100.0%`.
  - Normalization: Z-score standardisation within section/course to control for exam difficulty variance across instructors.
* **Suitability:** **Model-Suitable**.
  - Formative midterm/quiz marks recorded in weeks 1–6 are strong, legitimate predictors of semester-end outcome without target leakage.
* **Privacy & Fairness:** High utility, low fairness risk. Objective assessment of demonstrated syllabus mastery.
* **Evaluation Protocol:** Evaluate incremental F1-score improvement using nested Cross-Validation; verify that adding subject-specific vectors does not induce dimensional sparsity on smaller cohorts.

---

### Dimension 2: Assignment Submission Timing & Completion Velocity
* **Intended Use:** Measure self-regulation, time management, and academic engagement before exam marks are available.
* **Current Status in Schema:** Exists in current model as `assignment_submission_frequency` (proportion of assignments submitted on time).
* **Collection & Validation:**
  - Automated LMS timestamps comparing submission timestamp against deadline timestamp.
  - Validated as a ratio: $\frac{\text{Submitted on time}}{\text{Total assigned}}$. Outliers (grace periods, medical exemptions) must be flagged and handled with neutral imputation.
* **Suitability:** **Model-Suitable**.
  - Early-term submission consistency is an established behavioral proxy for study discipline.
* **Privacy & Fairness:** High utility. Low risk if objective submission rates are used; penalty rules must accommodate sanctioned accommodations (e.g., disability extensions).
* **Evaluation Protocol:** SHAP contribution analysis to verify positive monotonicity (higher timely completion consistently lowers predicted risk).

---

### Dimension 3: Project & Practical Laboratory Assessment Milestones
* **Intended Use:** Capture applied, hands-on competence and collaborative capability, particularly in STEM and technical curricula.
* **Current Status in Schema:** Does not exist in the active ML pipeline; partially planned in `academic_records`.
* **Collection & Validation:**
  - Milestone rubrics (e.g., sprint deliverables, lab check-offs) scored by teaching assistants or faculty.
  - Validated on a structured rubric scale (1 to 5 or percentage).
* **Suitability:** **Model-Suitable (with temporal quarantine)**.
  - Must only include milestone deliverables completed *prior to mid-term*. Final project grades must be excluded to prevent direct target leakage.
* **Privacy & Fairness:** Moderate risk. Group projects can obscure individual contribution; peer ratings should be excluded to avoid interpersonal popularity bias.
* **Evaluation Protocol:** Measure incremental recall on borderline students who pass theory exams but fail practical components.

---

### Dimension 4: Longitudinal Attendance & Performance Trend Trajectories
* **Intended Use:** Distinguish students whose performance is improving from students experiencing a steep downward spiral.
* **Current Status in Schema:** Current model uses a static snapshot of `attendance_rate`. Longitudinal slope does not exist in the feature matrix.
* **Collection & Validation:**
  - Computed as linear slope of rolling 3-week attendance and quiz averages: $\beta = \frac{\Delta \text{score}}{\Delta t}$.
  - Validated for minimum observation count ($n \ge 3$ consecutive checkpoints).
* **Suitability:** **Model-Suitable**.
  - Trend velocity provides early warning before cumulative term averages drop below critical thresholds.
* **Privacy & Fairness:** Low fairness risk. Grounds prediction in demonstrated momentum rather than fixed static baselines.
* **Evaluation Protocol:** Compare ROC-AUC of static model vs dynamic trajectory model on holdout test set.

---

### Dimension 5: Structured Classroom Participation & Discussion Logs
* **Intended Use:** Evaluate in-class verbal engagement and discussion board activity.
* **Current Status in Schema:** Represented as optional fields `quiz_participation` and `lms_activity` in relational table `behavior_records`, but excluded from ML training.
* **Collection & Validation:**
  - Clickstream forum post counts or faculty formative participation tallies.
* **Suitability:** **Pedagogical Support Planning Only (EXCLUDED from ML Model)**.
  - High risk of subjective instructor grading bias. Introverted students, neurodivergent students, and non-native language speakers frequently participate less verbally despite high concept comprehension. Using this in automated risk scoring could unjustly inflate risk scores for marginalized groups.
* **Privacy & Fairness:** High fairness concern.
* **Evaluation Protocol:** Qualitative review by academic counselors during intervention meetings rather than algorithmic scoring.

---

### Dimension 6: Student-Reported Interests, Goals & Preferred Learning Modalities
* **Intended Use:** Personalize pedagogical intervention recommendations (e.g., pairing a struggling student who loves gaming with gamified concept practice, or recommending peer study groups to students seeking collaboration).
* **Current Status in Schema:** Does not exist.
* **Collection & Validation:**
  - Voluntary student onboarding survey conducted at beginning of academic year.
  - Self-reported multi-select choices.
* **Suitability:** **Pedagogical Support Planning Only (STRICTLY EXCLUDED from ML Model)**.
  - Non-predictive of underlying academic ability; high risk of spurious correlations (e.g., associating specific hobbies with failure).
* **Privacy & Fairness:** Critical privacy boundary. Student personal interests must remain confidential and used solely to humanize advising conversations.
* **Evaluation Protocol:** Educator feedback surveys measuring student intervention compliance and satisfaction.

---

## 3. Strict Pre-Requisites for Pipeline Modification

Under no circumstances should new fields be injected into the active prediction pipeline without satisfying the following 6-stage protocol:

```text
[1. Requirement Analysis] -> [2. Schema Migration & Validation Rules] -> [3. Retraining with Strict Folds] 
       -> [4. Leakage & SHAP Audit] -> [5. Regression Test Suite] -> [6. Ethical & Fairness Verification]
```

1. **Schema & Imputation Update:** Add feature definition, types, and bounds in `src/schema.py` and `config/settings.py`.
2. **Leakage Prevention Verification:** Execute `tests/test_leakage.py` to ensure the new field is absent from future observation windows.
3. **Imbalance-Aware Cross-Validation:** Apply SMOTE strictly inside training folds during hyperparameter tuning.
4. **SHAP Monotonicity Check:** Confirm that TreeSHAP and KernelSHAP attributions align with pedagogical logic.
5. **Holdout Evaluation:** Verify that test-set Macro F1 and High-Risk Recall outperform the current Random Forest benchmark (CV Macro F1 $\ge 0.8787$).
6. **Zero Invented Data Guarantee:** All training data must originate from verified student populations or strictly audited synthetic benchmark cohorts.
