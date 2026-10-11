"""
Training Service Orchestrator for EduRisk XAI
"""
from typing import Dict, Any, Optional
from pathlib import Path
import json
import time
import uuid
import joblib
import pandas as pd

from config.settings import (
    ARTIFACTS_DIR, VERSIONS_DIR, EXPERIMENTS_DIR,
    CORE_FEATURES, TARGET_COLUMN
)
from src.data_loader import load_dataset, DatasetProvenance
from src.train import train_all_models
from src.model_selection import select_best_model
from database.database import SessionLocal, init_db
from database.crud import log_model_run

class TrainingService:
    """
    Coordinates data loading, leak-free multi-model training, model selection,
    artifact persistence, and experiment provenance tracking.
    """
    def __init__(self):
        init_db()

    def run_full_training(
        self,
        df: Optional[pd.DataFrame] = None,
        provenance: Optional[DatasetProvenance] = None,
        use_smote: bool = True
    ) -> Dict[str, Any]:
        """
        Runs the full 4-model experimental pipeline and persists artifacts.
        """
        # Load dataset if not provided
        if df is None:
            df, provenance = load_dataset()

        experiment_id = f"exp_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        model_version = f"v_{time.strftime('%Y%m%d_%H%M%S')}"

        # Train candidate models
        training_output = train_all_models(
            df=df,
            feature_columns=[c for c in df.columns if c != TARGET_COLUMN],
            target_column=TARGET_COLUMN,
            use_smote=use_smote,
        )

        # Select best model based on CV evidence
        best_model_name, best_pipeline, rationale = select_best_model(training_output)

        # Persist best pipeline artifact
        artifact_path = ARTIFACTS_DIR / "best_model.pkl"
        versioned_path = VERSIONS_DIR / f"{best_model_name.replace(' ', '_').lower()}_{model_version}.pkl"

        joblib.dump(best_pipeline, artifact_path)
        joblib.dump(best_pipeline, versioned_path)

        # Build clean serializable summary
        model_summaries = {}
        comparison_rows = []
        for name, data in training_output["models"].items():
            if data["status"] == "SUCCESS":
                tm = data["test_metrics"]
                model_summaries[name] = {
                    "cv_macro_f1": data["cv_macro_f1_mean"],
                    "cv_macro_f1_std": data["cv_macro_f1_std"],
                    "test_accuracy": tm["accuracy"],
                    "test_macro_f1": tm["macro_f1"],
                    "test_high_risk_recall": tm["high_risk_recall"],
                    "test_roc_auc": tm.get("roc_auc"),
                    "false_negatives": tm["false_negatives"],
                    "training_duration": data["training_duration"],
                    "inference_latency_ms": data["inference_latency_ms"],
                    "model_size_kb": data["model_size_kb"],
                    "best_params": data["best_params"],
                }
                comparison_rows.append({
                    "Model": name,
                    "CV Macro F1": data["cv_macro_f1_mean"],
                    "Test Macro F1": tm["macro_f1"],
                    "Test Accuracy": tm["accuracy"],
                    "High-Risk Recall": tm["high_risk_recall"],
                    "ROC-AUC": tm.get("roc_auc"),
                    "False Negatives": tm["false_negatives"],
                    "Train Time (s)": data["training_duration"],
                    "Inference (ms)": data["inference_latency_ms"],
                    "Size (KB)": data["model_size_kb"],
                })

        # Save comparison CSV
        df_comparison = pd.DataFrame(comparison_rows)
        csv_path = EXPERIMENTS_DIR / f"{experiment_id}_comparison.csv"
        df_comparison.to_csv(csv_path, index=False)

        # Build experiment payload
        experiment_record = {
            "experiment_id": experiment_id,
            "model_version": model_version,
            "selected_model": best_model_name,
            "selection_rationale": rationale,
            "dataset": provenance.to_dict() if provenance else {},
            "train_samples": training_output["train_samples"],
            "test_samples": training_output["test_samples"],
            "models": model_summaries,
            "feature_columns": training_output["feature_columns"],
            "timestamp": training_output["timestamp"],
            "artifact_path": str(artifact_path),
        }

        # Save JSON experiment record
        json_path = EXPERIMENTS_DIR / f"{experiment_id}.json"
        with open(json_path, "w") as f:
            json.dump(experiment_record, f, indent=2)

        # Save active model metadata
        meta_path = ARTIFACTS_DIR / "model_metadata.json"
        with open(meta_path, "w") as f:
            json.dump(experiment_record, f, indent=2)

        # Log into SQLite DB
        try:
            db = SessionLocal()
            for name, data in training_output["models"].items():
                if data["status"] == "SUCCESS":
                    log_model_run(db, {
                        "experiment_id": f"{experiment_id}_{name.replace(' ', '_')}",
                        "model_version": model_version,
                        "model_name": name,
                        "dataset_name": provenance.name if provenance else "Educational Dataset",
                        "dataset_hash": provenance.fingerprint if provenance else "unknown",
                        "is_synthetic": provenance.is_synthetic if provenance else False,
                        "feature_list": training_output["feature_columns"],
                        "hyperparameters": data["best_params"],
                        "cv_metrics": {
                            "cv_macro_f1": data["cv_macro_f1_mean"],
                            "cv_macro_f1_std": data["cv_macro_f1_std"]
                        },
                        "test_metrics": data["test_metrics"],
                        "training_duration": data["training_duration"],
                        "inference_latency_ms": data["inference_latency_ms"],
                        "is_selected": bool(name == best_model_name),
                        "selection_rationale": rationale if name == best_model_name else ""
                    })
            db.close()
        except Exception as e:
            print(f"[Database Warning] Failed to log model run to DB: {e}")

        experiment_record["pipeline"] = best_pipeline
        experiment_record["raw_training_output"] = training_output
        return experiment_record
