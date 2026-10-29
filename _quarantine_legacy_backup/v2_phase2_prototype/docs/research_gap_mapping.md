------------------------------------------------------------
GAP 1
------------------------------------------------------------

Literature Gap:
No consensus on best model

Evidence in manuscript:
Row 01

Prototype response:
Four lightweight classifiers are empirically compared.

Implementation:
`src/train.py` (Trains Decision Tree, SVC, Logistic Regression, Random Forest and evaluates via Stratified K-Fold CV) + `app.py` UI rendering the results.

Demonstration:
Model Comparison page

Evidence:
Actual experiment results generated dynamically in `results/model_comparison.json`.

Status:
FULLY DEMONSTRATED BY PHASE-2 PROTOTYPE

Remaining limitation:
Evaluation is based on the selected dataset and prototype-scale experiment.

------------------------------------------------------------
GAP 2
------------------------------------------------------------

Literature Gap:
Deep models lack transparency

Prototype response:
Lightweight classifiers + SHAP

Implementation:
`src/explain.py` extracts local `TreeExplainer` or `LinearExplainer` values from the pipeline.

Demonstration:
SHAP explanation on the "Predict Student Risk" -> "WHY?" section.

Status:
FULLY DEMONSTRATED BY PHASE-2 PROTOTYPE

Remaining limitation:
SHAP explains model behavior, not causal relationships.

------------------------------------------------------------
GAP 3
------------------------------------------------------------

Literature Gap:
High compute / opaque network

Prototype response:
CPU-based lightweight models with measured runtime.

Implementation:
runtime measurement integrated into `src/train.py` computing train time, inference time per sample, and disk payload size.

Demonstration:
Model performance / runtime panel on the "Model Comparison" page.

Status:
DEMONSTRATED

Remaining limitation:
Runtime depends on hardware and dataset size.

------------------------------------------------------------
GAP 4
------------------------------------------------------------

Literature Gap:
Black-box trust barrier

Prototype response:
Teacher-readable explanations showing feature contributions.

Implementation:
SHAP explanation layer (`src/explain.py`) feeding into natural language rendering and actionable mappings (`src/intervention.py`).

Demonstration:
"Why was this student flagged?" and "Recommended Support" sections.

Status:
FULLY DEMONSTRATED BY PHASE-2 PROTOTYPE

Remaining limitation:
Human trust/usability has not yet been evaluated through a formal user study.
