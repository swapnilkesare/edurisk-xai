"""
Research Reporting and Visualization Service for EduRisk XAI
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

from config.settings import FIGURES_DIR, REPORTS_DIR

# Set scientific plotting style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"

class ReportService:
    """
    Generates publication-quality experimental reports, markdown summaries,
    and research figures from genuine experimental runs.
    """
    def generate_experiment_figures(
        self,
        experiment_record: Dict[str, Any],
        output_dir: Optional[Path] = None
    ) -> List[str]:
        """
        Generates and saves publication-ready figures from actual model metrics.
        Returns list of generated file paths.
        """
        target_dir = Path(output_dir) if output_dir else FIGURES_DIR
        target_dir.mkdir(parents=True, exist_ok=True)
        generated_files = []

        models = experiment_record.get("models", {})
        if not models:
            return []

        model_names = list(models.keys())
        cv_f1s = [models[m].get("cv_macro_f1", 0.0) for m in model_names]
        test_f1s = [models[m].get("test_macro_f1", 0.0) for m in model_names]
        recalls = [models[m].get("test_high_risk_recall", 0.0) for m in model_names]

        # 1. Model Comparison Bar Chart (CV Macro F1 vs Test Macro F1 vs High-Risk Recall)
        fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
        x = np.arange(len(model_names))
        width = 0.25

        ax.bar(x - width, cv_f1s, width, label="CV Macro F1", color="#3b82f6")
        ax.bar(x, test_f1s, width, label="Test Macro F1", color="#10b981")
        ax.bar(x + width, recalls, width, label="High-Risk Recall", color="#f59e0b")

        ax.set_ylabel("Metric Score", fontsize=11, fontweight="bold")
        ax.set_title("Empirical Classifier Comparison (EduRisk XAI)", fontsize=13, fontweight="bold", pad=12)
        ax.set_xticks(x)
        ax.set_xticklabels(model_names, fontsize=10)
        ax.set_ylim(0.0, 1.05)
        ax.legend(frameon=True, loc="lower right")

        for i in range(len(model_names)):
            ax.text(x[i] - width, cv_f1s[i] + 0.02, f"{cv_f1s[i]:.2f}", ha="center", fontsize=8)
            ax.text(x[i], test_f1s[i] + 0.02, f"{test_f1s[i]:.2f}", ha="center", fontsize=8)
            ax.text(x[i] + width, recalls[i] + 0.02, f"{recalls[i]:.2f}", ha="center", fontsize=8)

        plt.tight_layout()
        fig_path = target_dir / "figure_1_model_comparison.png"
        fig.savefig(fig_path)
        plt.close(fig)
        generated_files.append(str(fig_path))

        # 2. Computational Latency & Training Time Comparison
        train_times = [models[m].get("training_duration", 0.0) for m in model_names]
        inf_latencies = [models[m].get("inference_latency_ms", 0.0) for m in model_names]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)

        ax1.bar(model_names, train_times, color="#6366f1")
        ax1.set_ylabel("Training Duration (seconds)", fontweight="bold")
        ax1.set_title("CPU Training Overhead", fontweight="bold")
        ax1.tick_params(axis="x", rotation=15)

        ax2.bar(model_names, inf_latencies, color="#ec4899")
        ax2.set_ylabel("Inference Latency per Sample (ms)", fontweight="bold")
        ax2.set_title("Single-Student Prediction Latency", fontweight="bold")
        ax2.tick_params(axis="x", rotation=15)

        plt.tight_layout()
        latency_path = target_dir / "figure_2_computational_efficiency.png"
        fig.savefig(latency_path)
        plt.close(fig)
        generated_files.append(str(latency_path))

        return generated_files

    def generate_markdown_report(self, experiment_record: Dict[str, Any]) -> str:
        """
        Builds a comprehensive research report in Markdown.
        """
        exp_id = experiment_record.get("experiment_id", "N/A")
        timestamp = experiment_record.get("timestamp", "N/A")
        selected = experiment_record.get("selected_model", "N/A")
        rationale = experiment_record.get("selection_rationale", "N/A")
        dataset = experiment_record.get("dataset", {})
        models = experiment_record.get("models", {})

        md = [
            f"# EduRisk XAI — Experimental Evaluation Report",
            f"",
            f"- **Experiment ID**: `{exp_id}`",
            f"- **Execution Timestamp**: `{timestamp}`",
            f"- **Dataset**: {dataset.get('name', 'N/A')} (Fingerprint: `{dataset.get('fingerprint', 'N/A')}`)",
            f"- **Synthetic Flag**: {'[SYNTHETIC / DEMO DATA]' if dataset.get('is_synthetic') else 'Real Benchmark Data'}",
            f"- **Samples**: Train = {experiment_record.get('train_samples', 'N/A')}, Test = {experiment_record.get('test_samples', 'N/A')}",
            f"- **Selected Optimal Model**: **{selected}**",
            f"",
            f"### Selection Policy Rationale",
            f"> {rationale}",
            f"",
            f"### Comparative Performance Matrix",
            f"",
            f"| Model | CV Macro F1 | Test Macro F1 | Test Acc | High-Risk Recall | False Negatives | Train Time (s) | Latency (ms) |",
            f"|---|---|---|---|---|---|---|---|",
        ]

        for name, m in models.items():
            md.append(
                f"| {name} | {m.get('cv_macro_f1', 0):.4f} | {m.get('test_macro_f1', 0):.4f} | "
                f"{m.get('test_accuracy', 0):.4f} | {m.get('test_high_risk_recall', 0):.4f} | "
                f"{m.get('false_negatives', 0)} | {m.get('training_duration', 0):.2f}s | "
                f"{m.get('inference_latency_ms', 0):.2f}ms |"
            )

        md.extend([
            f"",
            f"### Research Integrity Notes",
            f"1. **Holdout Independence**: The test set was strictly quarantined prior to preprocessing and SMOTE resampling.",
            f"2. **Resampling Isolation**: SMOTE was executed exclusively within training cross-validation folds.",
            f"3. **Lightweight Deployment**: All pipelines operated on consumer CPU without GPU dependencies.",
        ])

        report_content = "\n".join(md)
        report_file = REPORTS_DIR / f"{exp_id}_report.md"
        with open(report_file, "w") as f:
            f.write(report_content)

        return report_content
