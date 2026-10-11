# Reproducibility Guide — EduRisk XAI

## 1. System Requirements
- Operating System: Windows 10/11, macOS, or Linux
- Python Version: Python 3.10 to 3.13 (Tested on Python 3.13.14 on Windows)
- Hardware: Standard commodity CPU (No GPU required)
- RAM: Minimum 4 GB RAM

---

## 2. Environment Setup & Dependency Installation
Navigate into the project directory and install dependencies:

```bash
cd "edurisk-xai"
pip install -r requirements.txt
```

---

## 3. Automated Test Suite Execution
Execute the full unit and end-to-end test suite:

```bash
python -m pytest tests -v
```

Expected result: **25 passed in ~60 seconds**.

---

## 4. Formal Multi-Model Training Run
To execute the formal multi-model training pipeline on the benchmark dataset:

```bash
python train_experiment.py
```

This command will:
1. Load `data/raw/student_data.csv`.
2. Partition 80% train and 20% quarantined holdout test sets (`random_state=42`).
3. Execute 5-fold Stratified K-Fold cross-validation and hyperparameter grid searches with in-fold SMOTE.
4. Select the best model based on CV Macro F1.
5. Evaluate on the untouched holdout test set.
6. Serialize model artifacts to `models/artifacts/best_model.pkl` and `models/artifacts/model_metadata.json`.
7. Generate publication-ready figures in `results/figures/`.
8. Save structured experiment JSON and CSV payloads in `results/experiments/`.

---

## 5. Launching the Interactive Streamlit Dashboard
To launch the educator dashboard:

```bash
streamlit run app.py
```

Access the interface in your browser at `http://localhost:8501`.
Navigate between the 9 modules via the sidebar menu.
