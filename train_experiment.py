"""
Executable CLI Script to Run Training Experiment on Real Dataset
"""
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import json
from services.training_service import TrainingService
from services.report_service import ReportService
from src.data_loader import load_dataset

def main():
    print("=" * 60)
    print("EduRisk XAI — Formal Multi-Model Training Experiment")
    print("=" * 60)

    # 1. Load Real Public Dataset
    df, provenance = load_dataset(fallback_to_synthetic=False)
    print(f"Loaded dataset: {provenance.name}")
    print(f"Records: {len(df)}, Features: {provenance.feature_count}, Fingerprint: {provenance.fingerprint}")

    # 2. Run Training Pipeline
    train_svc = TrainingService()
    experiment_record = train_svc.run_full_training(
        df=df,
        provenance=provenance,
        use_smote=True
    )

    print("\n" + "=" * 60)
    print(f"Experiment ID: {experiment_record['experiment_id']}")
    print(f"Selected Model: {experiment_record['selected_model']}")
    print(f"Selection Rationale: {experiment_record['selection_rationale']}")
    print("=" * 60)

    print("\nModel Evaluation Summary on Holdout Test Set:")
    for name, data in experiment_record["models"].items():
        print(f"\n--- {name} ---")
        print(f"  CV Macro F1:        {data['cv_macro_f1']:.4f} (+/- {data['cv_macro_f1_std']:.4f})")
        print(f"  Test Macro F1:      {data['test_macro_f1']:.4f}")
        print(f"  Test Accuracy:      {data['test_accuracy']:.4f}")
        print(f"  High-Risk Recall:   {data['test_high_risk_recall']:.4f}")
        print(f"  False Negatives:    {data['false_negatives']}")
        print(f"  ROC-AUC:            {data['test_roc_auc']}")
        print(f"  Training Duration:  {data['training_duration']:.2f}s")
        print(f"  Inference Latency:  {data['inference_latency_ms']:.2f}ms")
        print(f"  Serialized Size:    {data['model_size_kb']:.2f} KB")

    # 3. Generate Publication Figures and Markdown Report
    report_svc = ReportService()
    figures = report_svc.generate_experiment_figures(experiment_record)
    print(f"\nGenerated {len(figures)} publication-quality figures:")
    for fig_path in figures:
        print(f"  - {fig_path}")

    report_md = report_svc.generate_markdown_report(experiment_record)
    print("\nGenerated Markdown Experiment Report.")

if __name__ == "__main__":
    main()
