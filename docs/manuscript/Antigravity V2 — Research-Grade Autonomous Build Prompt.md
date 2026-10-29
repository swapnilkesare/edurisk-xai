# ANTIGRAVITY V2 — RESEARCH-GRADE AUTONOMOUS BUILD PROMPT

## PROJECT

**Explainable AI in Education: A Lightweight Web Dashboard for Student Academic Performance Prediction and Intervention**

### Subtitle

**An Interpretable, SHAP-Driven Lightweight Framework for Transparent Student Risk Assessment and Pedagogical Intervention**

---

# MASTER INSTRUCTION

You are acting simultaneously as:

- Senior Full-Stack AI/ML Engineer
- Machine Learning Engineer
- Data Scientist
- Explainable AI Engineer
- MLOps Engineer
- Database Architect
- Backend Engineer
- Streamlit/UI Engineer
- Research Prototype Developer
- Software Tester
- Technical Documentation Engineer

Your task is to **BUILD, EXECUTE, TEST, DEBUG, VALIDATE AND DOCUMENT a complete working research prototype**.

Do not merely generate a UI.

Do not merely generate source-code files.

Do not merely describe how the project could be built.

**BUILD THE ACTUAL SYSTEM.**

The final system must implement the complete chain:

```text
RESEARCH CONTEXT
        ↓
LITERATURE GAP ANALYSIS
        ↓
DATA ACQUISITION
        ↓
DATA VALIDATION
        ↓
PREPROCESSING
        ↓
FEATURE ENGINEERING
        ↓
TRAIN/TEST SPLIT
        ↓
TRAINING-ONLY SMOTE
        ↓
STRATIFIED CROSS-VALIDATION
        ↓
GRID SEARCH
        ↓
MODEL COMPARISON
        ↓
MODEL SELECTION
        ↓
FINAL TEST EVALUATION
        ↓
MODEL SERIALIZATION
        ↓
RISK PREDICTION
        ↓
SHAP EXPLAINABILITY
        ↓
RISK FACTOR IDENTIFICATION
        ↓
RULE-BASED INTERVENTION
        ↓
DATABASE STORAGE
        ↓
LONGITUDINAL MONITORING
        ↓
EDUCATOR DASHBOARD
        ↓
ANALYTICS
        ↓
REPORTING
        ↓
RESEARCH VALIDATION
        ↓
SELF-TESTING
```

The system must be a **real working local application**.

---

# 0. NON-NEGOTIABLE RULES

Follow these rules throughout the entire implementation.

### Rule 1 — Build, don't explain

Do not stop after creating an architecture.

Do not return pseudocode instead of implementation.

Do not create placeholder buttons.

Every major UI action must perform a real backend operation.

---

### Rule 2 — Never fabricate experimental results

Never invent:

- accuracy
- precision
- recall
- F1
- AUC
- dataset size
- training time
- statistical significance
- model superiority
- intervention success
- student records
- research findings

Every experimental number must come from actual execution.

If something cannot be experimentally evaluated, explicitly write:

```text
Not experimentally evaluated in this prototype.
```

---

### Rule 3 — Never present synthetic data as real data

Synthetic data may be used for:

- development
- testing
- demonstration
- UI validation
- pipeline testing
- fallback when an appropriate real dataset cannot be obtained

But synthetic data must always be labelled:

```text
SYNTHETIC / DEMO DATA
```

Never present synthetic records as institutional student data.

Never claim that model performance on synthetic data proves real-world validity.

---

### Rule 4 — Never overclaim literature-gap closure

For every research gap classify implementation as:

```text
FULLY ADDRESSED
PARTIALLY ADDRESSED
FUTURE
```

Do not mark a gap as fully addressed merely because a related UI component exists.

Provide implementation evidence.

---

### Rule 5 — Preserve the research methodology

Do not replace the required lightweight methodology with:

- neural networks
- deep learning
- transformers
- LSTM
- GNN
- XGBoost as the primary required model
- unnecessary cloud infrastructure

The four required primary classifiers remain:

1. Decision Tree
2. Support Vector Classifier
3. Logistic Regression
4. Random Forest

The project is intentionally lightweight and interpretable.

---

### Rule 6 — Research source hierarchy

The primary methodological authority is:

```text
SY AIDS_AI_Methodology_24.pdf
```

Use the project's research/manuscript material as supporting context.

Do not silently change methodology requirements.

If an implementation extension goes beyond the methodology, clearly label it as:

```text
Prototype Extension
```

or

```text
Research-Gap Extension
```

---

# LAYER 1 — RESEARCH CONTEXT

The project addresses the problem of identifying students at academic risk early enough for meaningful educator intervention.

The research identifies recurring limitations including:

- lack of consensus regarding the best model
- computationally expensive models
- black-box opacity
- educator trust barriers
- late risk detection
- insufficient behavioral information
- static student snapshots
- lack of domain-specific flexibility
- inaccessible ML pipelines
- underuse of LMS/behavioral data
- poor preprocessing/data quality
- hardware constraints
- coarse binary pass/fail prediction
- separation between prediction and intervention

The final prototype must translate these research problems into concrete software capabilities.

Do not merely mention them.

---

# LAYER 2 — COMPLETE 15-PAPER GAP ANALYSIS

Create:

```text
docs/research_gap_matrix.md
```

Use the actual 15-paper literature review from the research materials.

The matrix must contain:

| Paper | Year | Method | Main Result | Identified Gap | Prototype Response | Implementation Status | Evidence | Remaining Limitation |
|---|---|---|---|---|---|---|---|---|

The implementation status must be one of:

```text
FULLY ADDRESSED
PARTIALLY ADDRESSED
FUTURE
```

The system must not invent additional claims about the papers.

The actual literature gaps identified include:

1. No consensus on best model
2. Deep models lack transparency
3. High computational cost / opaque networks
4. Ignoring student dynamics
5. Few models for basic/low-infrastructure environments
6. Black-box trust barrier
7. Late at-risk detection
8. Overlooked behavioral/non-cognitive traits
9. Static data over-reliance
10. Need for domain-tailored tools
11. Lack of accessible pipeline
12. Underutilized LMS logs
13. Poor data curation/noise
14. Hardware-selection limitations
15. Binary pass/fail is too coarse

Do not claim that every gap is completely solved.

For example:

```text
LMS API synchronization
= PARTIALLY ADDRESSED or FUTURE
```

if a real institutional LMS connection cannot actually be implemented.

---

# LAYER 3 — EXACT FIVE-PHASE METHODOLOGY

Implement the methodology as five explicit phases.

## PHASE 1 — Data Acquisition & Preprocessing

Implement:

- data acquisition
- validation
- missing-value handling
- categorical encoding
- numerical scaling
- feature preparation
- class-imbalance analysis
- stratified train/test partition
- training-only SMOTE

Core methodology features:

```text
attendance_rate
assignment_submission_frequency
internal_test_score
study_hours
```

Where supported, extend with:

```text
previous_performance
assignment_performance
assessment_trend
LMS_activity
quiz_participation
resource/video engagement
motivation
time_management
study discipline
```

---

## PHASE 2 — Predictive Modeling

Train exactly:

```text
Decision Tree
SVC
Logistic Regression
Random Forest
```

Use:

```text
StratifiedKFold
GridSearchCV
```

Compare all four models.

Do not skip a model merely because another model performs better.

---

## PHASE 3 — Explainable AI

Use SHAP for:

- individual explanations
- global explanations
- feature contributions
- risk-factor ranking

SHAP must be part of the prediction pipeline.

---

## PHASE 4 — Interactive Dashboard

Use Streamlit.

The educator should not need to understand ML implementation details.

---

## PHASE 5 — Rule-Based Intervention Engine

Connect:

```text
Prediction
    ↓
SHAP
    ↓
Risk-increasing factors
    ↓
Rule engine
    ↓
Recommended interventions
    ↓
Intervention tracking
```

This is a central contribution of the prototype.

---

# LAYER 4 — SYSTEM ARCHITECTURE

Use a clean modular architecture.

Recommended structure:

```text
edurisk-xai/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
│
├── config/
│   └── settings.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── sample/
│   └── metadata/
│
├── models/
│   ├── versions/
│   ├── current/
│   └── artifacts/
│
├── database/
│   ├── database.py
│   ├── models.py
│   ├── crud.py
│   └── migrations.py
│
├── ml/
│   ├── data_loader.py
│   ├── schema.py
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── target.py
│   ├── train.py
│   ├── evaluate.py
│   ├── model_selection.py
│   ├── predict.py
│   ├── explain.py
│   ├── risk.py
│   └── intervention.py
│
├── services/
│   ├── prediction_service.py
│   ├── student_service.py
│   ├── training_service.py
│   ├── analytics_service.py
│   ├── import_service.py
│   └── report_service.py
│
├── datasources/
│   ├── base.py
│   ├── csv_source.py
│   ├── database_source.py
│   └── lms_source.py
│
├── app_pages/
│   ├── dashboard.py
│   ├── students.py
│   ├── prediction.py
│   ├── explainability.py
│   ├── interventions.py
│   ├── analytics.py
│   ├── model_training.py
│   ├── model_performance.py
│   ├── data_import.py
│   ├── research_traceability.py
│   └── settings.py
│
├── utils/
│   ├── logging_config.py
│   ├── validation.py
│   ├── caching.py
│   └── helpers.py
│
├── tests/
│   ├── test_data.py
│   ├── test_preprocessing.py
│   ├── test_target.py
│   ├── test_training.py
│   ├── test_leakage.py
│   ├── test_prediction.py
│   ├── test_shap.py
│   ├── test_risk.py
│   ├── test_intervention.py
│   ├── test_database.py
│   ├── test_import.py
│   └── test_end_to_end.py
│
└── docs/
    ├── research_gap_matrix.md
    ├── methodology_mapping.md
    ├── system_architecture.md
    ├── experimental_protocol.md
    ├── model_results.md
    ├── limitations.md
    └── implementation_notes.md
```

You may improve this structure if technically necessary, but preserve modular separation.

---

# LAYER 5 — DATASET STRATEGY

Use an established educational dataset whenever possible.

Preferred source:

```text
UCI Student Performance Dataset
```

Other educational datasets may be supported when appropriate.

The system must distinguish:

```text
REAL DATA
DEMO DATA
SYNTHETIC DATA
```

Do not silently fabricate research data.

If external data cannot be downloaded:

1. continue with a clearly labelled demo dataset
2. provide CSV import
3. provide schema documentation
4. provide synthetic-data generation strictly for demonstration/testing
5. record the source status

---

## IMPORTANT TARGET-PROVENANCE RULE

Do not create an artificial risk target and then present its performance as evidence of real-world academic-risk prediction.

If a dataset already contains a suitable target:

- use it directly where appropriate

If transformation is necessary:

- define the transformation transparently
- document the mapping
- preserve provenance
- explain limitations

If synthetic data is used:

- clearly label the target as synthetic
- report synthetic-data performance separately

---

# LAYER 6 — TARGET DESIGN

Primary output:

```text
LOW RISK
MODERATE RISK
HIGH RISK
```

The methodology specifies:

```text
p >= 0.66      → HIGH
0.33 <= p < .66 → MODERATE
p < 0.33       → LOW
```

Implement these thresholds through a configurable risk-classification module.

Do not assume that every classifier's probability has identical calibration.

Where appropriate:

- document probability interpretation
- optionally provide calibration diagnostics
- never present probability as certainty

Keep:

```text
RISK
```

separate from:

```text
PERFORMANCE
```

Do not confuse risk of academic difficulty with predicted grade/performance.

---

# LAYER 7 — DATA PREPROCESSING

Implement a reproducible sklearn-compatible preprocessing pipeline.

Required:

1. schema validation
2. duplicate detection
3. missing-value analysis
4. numeric imputation
5. categorical imputation
6. invalid-value detection
7. outlier handling where justified
8. categorical encoding
9. numerical scaling where required
10. feature-name preservation
11. preprocessing metadata
12. class-distribution analysis

---

## CRITICAL DATA-LEAKAGE REQUIREMENT

Never do:

```text
SMOTE
↓
train_test_split
```

Instead:

```text
Raw Data
 ↓
Train/Test Split
 ↓
Training Pipeline
    ├── preprocessing
    ├── SMOTE
    └── classifier
 ↓
Cross-validation
```

Prefer `imblearn.pipeline.Pipeline`.

Preprocessing transformations and SMOTE must occur correctly inside the training/CV process.

The independent test set must remain untouched until final evaluation.

Write a test specifically proving this.

---

# LAYER 8 — MODEL TRAINING

For each of the four required models:

```text
DecisionTreeClassifier
SVC(probability=True)
LogisticRegression
RandomForestClassifier
```

perform:

```text
Pipeline construction
↓
Stratified K-Fold
↓
GridSearchCV
↓
Best hyperparameters
↓
Cross-validation metrics
↓
Final independent test evaluation
```

Use a fixed random seed.

Never use the test set during model selection.

---

## HYPERPARAMETERS

Decision Tree:

```text
criterion
max_depth
min_samples_split
min_samples_leaf
```

SVC:

```text
C
kernel
gamma
```

Logistic Regression:

```text
C
penalty
solver
max_iter
```

Random Forest:

```text
n_estimators
max_depth
min_samples_split
min_samples_leaf
max_features
```

Keep search spaces computationally reasonable.

---

# LAYER 9 — MODEL EVALUATION

Calculate actual experimental:

```text
Accuracy
Precision
Recall
F1
Macro F1
Weighted F1
Confusion Matrix
Classification Report
ROC-AUC where appropriate
PR-AUC where appropriate
High-risk recall
False negatives
Training time
Inference time
```

For early warning, explicitly emphasize:

```text
HIGH-RISK RECALL
```

and analyze false negatives.

Do not optimize solely for accuracy.

---

# MODEL SELECTION

Build a transparent selection process using:

```text
Macro F1
+
High-risk recall
+
Accuracy
+
Computational efficiency
+
Interpretability
+
SHAP compatibility
```

If two models have similar predictive performance, prefer the lighter/more interpretable model.

Display the reason for selection.

Never claim a model is "best" merely because of accuracy.

---

# LAYER 10 — XAI / SHAP ENGINE

SHAP is mandatory.

Every individual prediction should generate:

```text
Prediction
Probability
Risk tier
Top risk-increasing factors
Top protective factors
SHAP contribution values
Feature values
Plain-language explanation
```

Use model-appropriate explainers.

Prefer:

```text
TreeExplainer
```

for supported tree models.

Use an appropriate linear/model-specific explainer for linear models where supported.

Use KernelExplainer only where necessary.

Cache expensive explainers/background data.

Handle:

- multiclass outputs
- SHAP version differences
- feature-name mapping
- transformed features
- missing values
- explanation failures

Do not show misleading SHAP values.

The explanation must correspond to the actual prediction/class being displayed.

---

## PLAIN-LANGUAGE XAI

Generate explanations such as:

```text
Low attendance contributed positively to the model's predicted risk.
```

rather than:

```text
SHAP value = 0.3821
```

Technical information may be available under:

```text
Technical Explanation
```

but the primary educator interface must remain understandable.

---

# GLOBAL EXPLAINABILITY

Create:

```text
Why is the model making these predictions?
```

Show:

- mean absolute SHAP
- global feature importance
- feature impact distribution
- top cohort-wide risk factors
- positive/negative influence

---

# LAYER 11 — INTERVENTION ENGINE

Implement a **pure rule-based intervention engine**.

Do not use another ML model for intervention generation.

The logic must be:

```text
Prediction
 ↓
SHAP
 ↓
Risk-increasing contributors
 ↓
Rule matching
 ↓
Intervention priority
 ↓
Recommended action
```

Default mappings include:

### Low attendance

- mentor check-in
- attendance monitoring
- attendance improvement plan

### Low internal test score

- peer tutoring
- remedial session
- targeted practice

### Low assignment submission

- assignment reminder
- assignment support
- faculty follow-up

### Low study hours

- study planning
- time-management support
- weekly study schedule

### Declining performance

- early faculty intervention
- targeted revision
- academic counseling

### Low LMS engagement

- resource recommendation
- engagement reminder
- faculty follow-up

### Low motivation

- mentor discussion
- goal setting
- academic counseling

### Poor time management

- weekly planning
- time-management support

---

# INTERVENTION PRIORITIZATION

Do not generate arbitrary recommendations.

Rank interventions using:

```text
SHAP contribution
+
severity
+
deviation from healthy range
+
risk tier
+
temporal deterioration
```

Each recommendation should contain:

```text
Priority
Risk factor
Evidence
Reason
Recommended action
Status
```

Example:

```text
HIGH PRIORITY

Risk factor:
Attendance

Evidence:
Attendance is substantially below the configured healthy range.

Model contribution:
Positive contribution toward predicted risk.

Recommended action:
Mentor follow-up + attendance improvement plan.

Status:
Pending
```

SHAP explains model behavior; it does not prove causality.

Never write:

```text
Attendance caused failure.
```

Use:

```text
Low attendance contributed to the model's predicted risk.
```

---

# EDITABLE INTERVENTION RULES

Provide a teacher-accessible rule editor.

Teachers must be able to modify:

```text
Feature
Threshold
Direction
Severity
Intervention
Priority
```

Changes must persist in SQLite.

The application must not require editing Python code to change intervention rules.

---

# LAYER 12 — DATABASE ARCHITECTURE

Use:

```text
SQLite
+
SQLAlchemy ORM
```

No external database should be required.

Entities should include at minimum:

```text
Student
AcademicRecord
BehaviorRecord
Prediction
SHAPExplanation
Intervention
InterventionRule
ModelRun
DatasetImport
```

---

## STUDENT

Store:

```text
id
student_identifier
name
course/program
department
semester
year
created_at
updated_at
```

---

## ACADEMIC RECORD

Store:

```text
student_id
internal_test_score
assignment_score
previous_performance
assessment_date
```

---

## BEHAVIOR RECORD

Store:

```text
student_id
attendance
study_hours
assignment_submission_rate
LMS_activity
quiz_participation
motivation
time_management
record_date
```

---

## PREDICTION

Store:

```text
student_id
model_version
prediction_timestamp
predicted_class
risk_tier
probability
```

---

## SHAP EXPLANATION

Store:

```text
prediction_id
feature_name
feature_value
shap_value
direction
rank
```

---

## INTERVENTION

Store:

```text
student_id
prediction_id
risk_factor
intervention
priority
status
created_at
updated_at
```

Statuses:

```text
Pending
In Progress
Completed
Dismissed
```

---

## MODEL RUN

Store:

```text
model_version
model_name
training_timestamp
dataset_version
dataset_hash
feature_list
hyperparameters
CV metrics
test metrics
training_time
inference_time
selected_model
```

This is required for reproducibility.

---

# LAYER 13 — LONGITUDINAL STUDENT TRACKING

Do not overwrite historical student observations.

Store:

```text
Date
 ↓
Input metrics
 ↓
Prediction
 ↓
SHAP
 ↓
Intervention
 ↓
Intervention status
```

A student must be able to have multiple assessments.

Display:

- attendance trend
- score trend
- assignment trend
- study-hour trend
- risk probability trend
- risk-tier trajectory
- intervention timeline

Example:

```text
Week 1 → LOW
Week 3 → MODERATE
Week 5 → HIGH
```

This addresses the static-snapshot limitation at the **prototype monitoring level**.

Do not falsely claim that this creates a true deep temporal model.

---

# TEMPORAL FEATURE ENGINEERING

When enough historical observations exist, calculate:

```text
current value
previous value
rolling mean
change percentage
trend/slope
recent average
momentum
```

Examples:

```text
attendance_change
test_score_change
study_hours_change
assignment_change
engagement_change
```

Clearly document that this is a lightweight temporal extension rather than a full spatio-temporal deep-learning model.

---

# LMS / CLICKSTREAM SUPPORT

Create an extensible datasource abstraction:

```text
DataSource
 ├── CSVDataSource
 ├── DatabaseDataSource
 └── OptionalLMSDataSource
```

Support fields such as:

```text
video_views
forum_posts
quiz_attempts
resource_views
LMS_activity
```

However:

**DO NOT fake a real Moodle or Canvas API integration.**

If credentials/API access are unavailable:

```text
Implement connector abstraction
+
CSV mapping
+
document integration architecture
```

Mark live LMS synchronization:

```text
PARTIALLY ADDRESSED
```

or:

```text
FUTURE
```

unless it actually works.

---

# DOMAIN-SPECIFIC SUPPORT

Allow configuration by:

```text
Course
Department
Program
Semester
Subject
```

Allow domain-specific features to be added without rewriting the entire ML pipeline.

Do not falsely claim that simply storing a subject field creates a subject-specific model.

If separate subject models are implemented, document them explicitly.

Otherwise mark the research gap as partially addressed.

---

# LAYER 14 — STREAMLIT FRONTEND

Create a polished educator-facing dashboard.

The interface must feel like a real educational analytics product, not a classroom coding demo.

Primary navigation:

```text
Dashboard
Students
Predict Risk
Explainability
Interventions
Cohort Analytics
Model Training
Model Performance
Data Import
Research Traceability
Settings
```

---

# DASHBOARD

Show:

```text
Total Students
High Risk
Moderate Risk
Low Risk
Students Requiring Intervention
Recent Predictions
Current Model
Model Version
Macro F1
High-Risk Recall
```

Charts:

- risk distribution
- risk trend
- top risk factors
- intervention status
- recent at-risk students

---

# STUDENT PAGE

Allow:

- search
- filtering
- sorting
- student selection

Show:

```text
Student profile
Current risk
Probability
Top risk factors
SHAP explanation
Interventions
Historical trend
Previous predictions
Intervention status
```

---

# PREDICTION PAGE

Provide:

```text
Existing Student
New Student
```

Input:

- attendance
- internal test score
- assignment submission
- study hours
- previous performance where available
- behavioral features
- LMS features where available

Click:

```text
PREDICT RISK
```

Execute:

```text
Validation
 ↓
Preprocessing
 ↓
Prediction
 ↓
Probability
 ↓
Risk tier
 ↓
SHAP
 ↓
Risk factors
 ↓
Interventions
 ↓
Database logging
```

No fake output.

---

# EXPLAINABILITY PAGE

Display:

```text
WHY THIS PREDICTION?
```

Then:

```text
Risk
Probability
Top Risk Factors
Protective Factors
SHAP Visualization
Plain-English Explanation
Recommended Actions
```

Technical SHAP information should be available separately.

---

# COHORT ANALYTICS

Provide:

- risk distribution
- average attendance
- average scores
- average study hours
- risk by course
- risk by semester
- risk trends
- common risk factors
- intervention completion rate

Filters:

```text
Course
Semester
Risk tier
Date range
```

---

# MODEL PERFORMANCE

Display:

| Model | Accuracy | Precision | Recall | Macro F1 | High-Risk Recall | Training Time |
|---|---:|---:|---:|---:|---:|---:|

Include:

- confusion matrix
- classification report
- ROC-AUC where appropriate
- PR-AUC where appropriate
- CV performance
- hyperparameters
- selected model
- reason for selection

---

# MODEL TRAINING PAGE

Display:

```text
Dataset
Records
Features
Class distribution
Missing values
Train/Test split
SMOTE statistics
CV folds
Grid-search configuration
Candidate models
CV results
Final test results
Training time
Inference time
Selected model
Model version
```

Button:

```text
TRAIN / RETRAIN MODEL
```

The button must perform real training.

---

# AUTOMATIC TRAINING

When no model exists:

```text
No trained model found.
```

Offer:

```text
TRAIN MODEL
```

After training:

```text
Model trained successfully.
```

Do not retrain every time Streamlit starts.

Retrain when:

- no valid model exists
- educator requests retraining
- dataset changes materially
- model artifact becomes invalid
- sufficient new labelled data are available

---

# MODEL VERSIONING

Use:

```text
v1.0
v1.1
v1.2
...
```

Every training run must record:

- model version
- date
- dataset version/hash
- features
- model type
- hyperparameters
- metrics
- training time

Keep historical model metadata.

---

# DATA DRIFT / DATA QUALITY MONITORING

Implement lightweight monitoring where practical.

Compare incoming data against training data.

Detect:

- missing-value increases
- unseen categories
- major feature distribution changes
- class-distribution changes
- schema changes

Display:

```text
DATA QUALITY WARNING
```

when appropriate.

Do not pretend this is a full production-grade drift system if it isn't.

---

# CSV IMPORT

Implement:

```text
Upload CSV
 ↓
Schema detection
 ↓
Column mapping
 ↓
Validation
 ↓
Preview
 ↓
Data-quality report
 ↓
User confirmation
 ↓
Database insertion
 ↓
Import log
```

Do not silently discard invalid rows.

Report:

- valid rows
- invalid rows
- missing values
- unknown columns
- mapped columns
- rejected records

---

# EXPORT

Allow:

```text
Student Risk Report
Cohort Risk Report
Predictions
Interventions
Model Results
```

Support CSV.

Where practical, provide a student report in PDF/Markdown.

---

# LAYER 15 — RESPONSIBLE AI

Include a dedicated Responsible AI section.

The system must:

- avoid unnecessary sensitive attributes
- allow educator review
- not automatically punish students
- not label students as failures
- use decision-support language
- explain limitations
- avoid deterministic statements
- log predictions transparently

Display:

> This system provides AI-assisted academic risk estimates for educator decision support. Predictions should not be treated as definitive judgments about a student's ability, character, or future performance.

---

# XAI CAUSALITY WARNING

Never write:

```text
Attendance caused failure.
```

Write:

```text
Low attendance contributed positively to the model's predicted risk.
```

SHAP explains model behavior.

SHAP does not establish causality.

---

# PRIVACY

Use:

- student identifiers where appropriate
- minimal logging
- no unnecessary sensitive attributes
- safe file handling
- environment variables for configuration
- no hard-coded secrets

Provide:

```text
.env.example
```

---

# LAYER 16 — ERROR HANDLING

Gracefully handle:

- missing dataset
- invalid CSV
- missing columns
- wrong data types
- unsupported categories
- missing model
- SHAP failure
- database failure
- empty database
- single-class data
- insufficient samples
- SMOTE failure
- invalid thresholds
- insufficient CV folds

Never show raw Python traceback to educators.

Log technical details internally.

Show clear user-facing messages.

---

# SMALL-DATASET SAFETY

Automatically determine valid:

```text
CV folds
SMOTE k_neighbors
```

based on available class counts.

If the dataset is too small:

- warn the user
- reduce CV folds safely where justified
- adjust SMOTE safely
- or disable SMOTE if mathematically impossible
- document the adjustment

Never fabricate data merely to make the algorithm run.

---

# LAYER 17 — CACHING AND PERFORMANCE

Cache where appropriate:

- datasets
- trained models
- preprocessors
- SHAP explainers
- metadata

Do not incorrectly cache mutable database state.

The application should remain usable on an ordinary CPU computer.

Measure actual:

```text
Training time
Inference time
Memory usage where practical
```

Report measurements rather than promising arbitrary limits.

---

# LAYER 18 — SECURITY AND ROBUSTNESS

Implement:

- CSV validation
- file-size checks where appropriate
- safe file paths
- SQLAlchemy parameterized database operations
- input validation
- safe exception handling
- no exposed secrets
- no raw SQL inside Streamlit pages

---

# LAYER 19 — TESTING

Write automated tests covering:

```text
Data loading
Schema validation
Target creation
Preprocessing
Train/test split
SMOTE leakage prevention
Cross-validation
Model training
Model selection
Prediction
Risk classification
SHAP
Intervention mapping
Database CRUD
CSV import
Longitudinal history
Export
```

At minimum test the complete workflow:

```text
Dataset
 ↓
Train
 ↓
Predict
 ↓
Explain
 ↓
Intervene
 ↓
Save
 ↓
Retrieve
```

---

# LAYER 20 — END-TO-END SELF-TEST

After building the project, **actually execute it**.

Perform:

### Test 1

Load demo/real dataset.

### Test 2

Validate dataset.

### Test 3

Run preprocessing.

### Test 4

Train all four models.

### Test 5

Perform CV/GridSearch.

### Test 6

Evaluate final models.

### Test 7

Select model.

### Test 8

Save artifacts.

### Test 9

Create student.

### Test 10

Generate prediction.

### Test 11

Generate SHAP explanation.

### Test 12

Generate interventions.

### Test 13

Save prediction.

### Test 14

Retrieve student history.

### Test 15

Change intervention status.

### Test 16

View cohort analytics.

### Test 17

Import CSV.

### Test 18

Export results.

### Test 19

Restart application.

### Test 20

Verify persistence.

If anything fails:

```text
IDENTIFY ERROR
 ↓
FIX ERROR
 ↓
RE-RUN TEST
 ↓
VERIFY
```

Do not declare completion before fixing blocking errors.

---

# LAYER 21 — RESEARCH VALIDATION

Create:

```text
docs/experimental_protocol.md
```

Document:

- dataset source
- dataset version
- dataset hash
- feature selection
- target definition
- train/test split
- preprocessing
- SMOTE strategy
- CV strategy
- hyperparameter grids
- evaluation metrics
- model-selection criteria
- SHAP methodology
- intervention methodology
- hardware/environment
- random seed

---

# ACTUAL RESULTS

After actual training generate:

```text
docs/model_results.md
```

Include only experimentally generated values:

```text
Dataset size
Feature count
Class distribution
Model metrics
CV metrics
Hyperparameters
Selected model
Training time
Inference time
SHAP results
```

Do not insert expected numbers.

Do not modify metrics to match the literature.

---

# LAYER 22 — RESEARCH TRACEABILITY

Create a dashboard page:

```text
RESEARCH → IMPLEMENTATION
```

For every literature gap show:

```text
Research Gap
 ↓
Prototype Feature
 ↓
Implementation
 ↓
Test/Evidence
 ↓
Status
 ↓
Remaining Limitation
```

Example:

```text
Gap:
Black-box opacity

Response:
SHAP local/global explanations

Evidence:
SHAP test + dashboard explanation

Status:
FULLY ADDRESSED
```

Another:

```text
Gap:
Live LMS underutilization

Response:
LMS-compatible schema + connector abstraction

Evidence:
CSV/LMS mapping implementation

Status:
PARTIALLY ADDRESSED

Limitation:
No live institutional Moodle/Canvas credentials.
```

This distinction is mandatory.

---

# LAYER 23 — DOCUMENTATION

Create:

```text
README.md
docs/system_architecture.md
docs/methodology_mapping.md
docs/research_gap_matrix.md
docs/experimental_protocol.md
docs/model_results.md
docs/limitations.md
docs/implementation_notes.md
```

---

# README MUST INCLUDE

```text
Project title
Problem statement
Research motivation
Research gaps
Objectives
Methodology
Architecture
Technology stack
Dataset
Feature engineering
Preprocessing
SMOTE
Models
Cross-validation
GridSearch
SHAP
Risk classification
Intervention engine
Database
Dashboard
Installation
Usage
Training
Prediction
Testing
Evaluation
Limitations
Future scope
Research contribution
```

---

# LAYER 24 — LIMITATIONS MUST BE HONEST

Create:

```text
docs/limitations.md
```

Clearly state limitations that remain.

Potential limitations include:

- structured/tabular data
- self-reported behavioral indicators
- dataset-specific generalization
- lack of institutional LMS synchronization
- absence of causal inference
- limited longitudinal data
- synthetic/demo data when real data unavailable
- limited external validation
- intervention recommendations are rule-based rather than experimentally validated pedagogical outcomes

Never hide limitations merely to make the project look stronger.

---

# LAYER 25 — MODEL REPRODUCIBILITY

Store:

```text
random seed
dataset hash
dataset version
feature schema
preprocessing configuration
model hyperparameters
CV configuration
training timestamp
software versions
model version
metrics
```

The same dataset/configuration should be able to reproduce the training process as closely as practical.

---

# LAYER 26 — CORE INFERENCE FUNCTION

Implement a single high-level inference workflow equivalent to the methodology's SRC–RI algorithm.

Conceptually:

```python
run_src_ri(student_features)
```

It must perform:

```text
1. preprocess input
2. generate model probability
3. assign risk tier
4. calculate local SHAP
5. rank risk-increasing features
6. map factors to interventions
7. generate dashboard result
8. log prediction/explanation/intervention
9. return result
```

Return structured data containing:

```text
risk_tier
probability
prediction
shap_values
risk_factors
protective_factors
interventions
model_version
timestamp
```

---

# LAYER 27 — API-READY BUSINESS LOGIC

Keep business logic independent from Streamlit.

Implement services such as:

```python
predict_student()
explain_prediction()
generate_interventions()
save_prediction()
get_student_history()
train_model()
evaluate_models()
```

The Streamlit UI should call services.

Do not place ML logic directly inside UI widgets.

An optional FastAPI layer may be added only if it does not unnecessarily complicate the project.

Streamlit remains the primary required interface.

---

# LAYER 28 — UI EXPERIENCE

The teacher should understand within seconds:

```text
WHO is at risk?
        ↓
WHY are they at risk?
        ↓
HOW SERIOUS is the risk?
        ↓
WHAT factors are influencing it?
        ↓
WHAT should I do?
        ↓
HAS the intervention been completed?
        ↓
IS the student improving?
```

This is the central UX requirement.

Use educator-friendly language.

Instead of:

```text
Feature attribution
```

say:

```text
Factors influencing this prediction
```

Instead of:

```text
Class probability vector
```

say:

```text
Predicted Risk Probability
```

Instead of:

```text
SHAP value
```

say:

```text
Model contribution
```

Technical terminology may remain available under advanced/model-transparency pages.

---

# LAYER 29 — VISUALIZATION

Use Plotly/Matplotlib/Seaborn as appropriate.

Provide:

1. Risk distribution
2. Confusion matrix
3. Model comparison
4. Global SHAP importance
5. Individual SHAP explanation
6. Risk trajectory
7. Attendance trend
8. Score trend
9. Study-hours trend
10. Intervention status
11. Cohort analysis

Do not overload educators with technical plots.

---

# LAYER 30 — DEMO MODE

Provide an explicitly labelled:

```text
DEMO MODE
```

It may contain synthetic students.

Every synthetic record must be visibly labelled.

Never mix synthetic records with real institutional records without clear provenance.

---

# LAYER 31 — ACCEPTANCE CRITERIA

The project is not complete until the following are verified.

## DATA

- [ ] Dataset loads
- [ ] Dataset source is documented
- [ ] Dataset provenance is recorded
- [ ] Schema validation works
- [ ] Missing-value handling works
- [ ] Categorical encoding works
- [ ] Scaling works
- [ ] Invalid values are detected
- [ ] Data quality report works

## LEAKAGE

- [ ] Train/test split is independent
- [ ] Test data is never used for tuning
- [ ] SMOTE never touches test data
- [ ] preprocessing is safely incorporated into CV
- [ ] leakage test passes

## ML

- [ ] Decision Tree trains
- [ ] SVC trains
- [ ] Logistic Regression trains
- [ ] Random Forest trains
- [ ] Stratified CV works
- [ ] GridSearch works
- [ ] metrics calculated
- [ ] high-risk recall calculated
- [ ] false negatives analyzed
- [ ] model selection is transparent
- [ ] model artifacts saved

## XAI

- [ ] Individual SHAP works
- [ ] Global SHAP works
- [ ] feature mapping works
- [ ] risk-increasing factors identified
- [ ] protective factors identified
- [ ] plain-English explanations work
- [ ] SHAP errors handled

## INTERVENTION

- [ ] Rule engine works
- [ ] SHAP factors feed intervention logic
- [ ] Intervention priority works
- [ ] Rules editable
- [ ] Rule changes persist
- [ ] Intervention status works

## DATABASE

- [ ] Student CRUD works
- [ ] Academic records work
- [ ] Behavioral records work
- [ ] Predictions persist
- [ ] SHAP explanations persist
- [ ] Interventions persist
- [ ] Model runs persist
- [ ] Historical records persist

## LONGITUDINAL

- [ ] Multiple snapshots work
- [ ] Historical predictions display
- [ ] Risk trajectory works
- [ ] Feature trends work
- [ ] Temporal features work where sufficient data exists

## DASHBOARD

- [ ] Dashboard works
- [ ] Student page works
- [ ] Prediction page works
- [ ] Explanation page works
- [ ] Intervention page works
- [ ] Cohort analytics works
- [ ] Model performance works
- [ ] Training works
- [ ] Data import works
- [ ] Export works
- [ ] Research traceability works
- [ ] Settings work

## DOCUMENTATION

- [ ] README exists
- [ ] Architecture exists
- [ ] Methodology mapping exists
- [ ] Gap matrix exists
- [ ] Experimental protocol exists
- [ ] Results document exists
- [ ] Limitations document exists

## INTEGRITY

- [ ] No fabricated metrics
- [ ] No fabricated real student data
- [ ] No false LMS integration claims
- [ ] No causal claims from SHAP
- [ ] No unsupported superiority claims
- [ ] Synthetic data clearly labelled

---

# LAYER 32 — 13-STAGE DEVELOPMENT PROCESS

Do not generate everything blindly in one pass.

Work incrementally.

## Stage 1

Inspect existing project directory.

Do not destroy useful existing work without reason.

---

## Stage 2

Create architecture and configuration.

---

## Stage 3

Implement dataset acquisition/loading.

---

## Stage 4

Implement schema validation and preprocessing.

---

## Stage 5

Implement leakage-safe training pipeline.

---

## Stage 6

Train all four required models.

---

## Stage 7

Evaluate and select the model.

---

## Stage 8

Implement SHAP.

---

## Stage 9

Implement intervention engine.

---

## Stage 10

Implement database and persistence.

---

## Stage 11

Implement prediction/business services.

---

## Stage 12

Implement Streamlit frontend.

---

## Stage 13

Perform full end-to-end testing, debugging and documentation.

After each major stage:

```text
IMPLEMENT
 ↓
RUN
 ↓
TEST
 ↓
FIX
 ↓
CONTINUE
```

---

# LAYER 33 — SELF-VERIFICATION BEFORE COMPLETION

Before declaring success, inspect the implementation against every requirement in this prompt.

Create:

```text
docs/final_verification_report.md
```

Include:

| Requirement | Implemented | Tested | Evidence | Status |
|---|---|---|---|---|

For each research gap:

| Gap | Feature | Implementation | Test Evidence | Status | Limitation |
|---|---|---|---|---|---|

Do not mark something complete without evidence.

---

# LAYER 34 — FAILURE RECOVERY

If an external dependency fails:

```text
DO NOT FABRICATE IT.
```

Instead:

```text
1. detect failure
2. provide local fallback
3. continue the build
4. document limitation
```

Examples:

### Dataset download unavailable

Use documented demo dataset.

### LMS unavailable

Use connector abstraction/CSV mapping.

### Optional PDF dependency unavailable

Provide Markdown/CSV export.

### SHAP incompatibility

Use a compatible supported explainer/fallback and document it.

---

# LAYER 35 — FINAL PROJECT QUALITY

The final project must be:

```text
Clean
Modular
Runnable
Tested
Research-grounded
Reproducible
Explainable
Lightweight
Teacher-friendly
Database-backed
Actionable
```

Avoid unnecessary enterprise complexity.

Do not add technology merely because it sounds impressive.

Every technology must have a reason.

---

# FINAL RESEARCH CONTRIBUTION

The final prototype should demonstrate this complete research contribution:

```text
Student Data
      ↓
Data Quality Processing
      ↓
Leakage-Safe Balanced Training
      ↓
Lightweight Model Comparison
      ↓
Transparent Model Selection
      ↓
Risk Prediction
      ↓
SHAP Explanation
      ↓
Risk-Factor Identification
      ↓
Rule-Based Intervention
      ↓
Database Logging
      ↓
Longitudinal Monitoring
      ↓
Educator Decision Support
```

The central research objective is:

> **How can academic risk prediction be made sufficiently useful for early warning, computationally lightweight for ordinary educational environments, transparent enough for educator trust, and actionable enough to support timely intervention?**

The prototype should address this through the combined design of:

```text
PREDICTIVE QUALITY
+
INTERPRETABILITY
+
COMPUTATIONAL EFFICIENCY
+
EARLY DETECTION
+
BEHAVIORAL CONTEXT
+
ACTIONABILITY
+
USABILITY
+
REPRODUCIBILITY
```

---

# FINAL DELIVERABLE

At completion, provide:

1. Complete source code
2. Working Streamlit application
3. Database
4. Dataset pipeline
5. Preprocessing pipeline
6. Four-model training pipeline
7. GridSearch
8. Stratified CV
9. Leakage-safe SMOTE
10. Model comparison
11. Model-selection logic
12. Model artifacts
13. SHAP local explanations
14. SHAP global explanations
15. Risk classification
16. Intervention engine
17. Editable intervention rules
18. Student CRUD
19. Longitudinal tracking
20. Temporal features
21. CSV import
22. CSV export
23. Cohort analytics
24. Model performance dashboard
25. Model versioning
26. Data-quality monitoring
27. Research traceability page
28. Tests
29. Demo mode
30. README
31. Architecture documentation
32. Methodology mapping
33. Research-gap matrix
34. Experimental protocol
35. Actual model-results document
36. Limitations document
37. Final verification report
38. Exact run instructions

---

# FINAL COMMAND

Do not simply tell me how to build this.

Do not give me a partial implementation.

Do not create a UI-only prototype.

Do not fabricate unavailable functionality.

Do not fabricate experimental results.

Do not claim that a research gap is solved without implementation evidence.

**BUILD THE REAL WORKING RESEARCH PROTOTYPE.**

Work incrementally.

Run the code.

Test the code.

Fix the code.

Verify the code.

Document the actual results.

Then provide the completed project.

**START NOW BY INSPECTING THE EXISTING PROJECT DIRECTORY AND PRESERVING ANY USEFUL EXISTING WORK BEFORE IMPLEMENTING THE SYSTEM.**