"""
Model Evaluation and Metrics Calculation for EduRisk XAI
"""
from typing import Dict, Any, Optional
import time
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_auc_score,
    average_precision_score,
)

def evaluate_predictions(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray] = None,
    training_duration: float = 0.0,
    inference_latency_ms: float = 0.0,
    model_size_kb: float = 0.0,
) -> Dict[str, Any]:
    """
    Computes rigorous evaluation metrics from ground truth and predictions.
    Emphasizes high-risk recall and false negatives as required by the research methodology.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))

    cm = confusion_matrix(y_true, y_pred).tolist()
    if len(cm) == 2 and len(cm[0]) == 2:
        tn, fp = cm[0][0], cm[0][1]
        fn, tp = cm[1][0], cm[1][1]
    else:
        tn, fp, fn, tp = 0, 0, 0, 0

    high_risk_total = tp + fn
    high_risk_recall = float(tp / high_risk_total) if high_risk_total > 0 else 0.0
    false_negative_rate = float(fn / high_risk_total) if high_risk_total > 0 else 0.0

    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)

    # ROC-AUC and PR-AUC
    roc_auc = None
    pr_auc = None
    if y_prob is not None:
        try:
            # Handle 1D probabilities or 2D class probabilities
            probs_for_calc = y_prob[:, 1] if (hasattr(y_prob, "ndim") and y_prob.ndim == 2) else y_prob
            if len(np.unique(y_true)) > 1:
                roc_auc = float(roc_auc_score(y_true, probs_for_calc))
                pr_auc = float(average_precision_score(y_true, probs_for_calc))
        except Exception:
            pass

    return {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "high_risk_recall": round(high_risk_recall, 4),
        "false_negatives": int(fn),
        "false_negative_rate": round(false_negative_rate, 4),
        "confusion_matrix": cm,
        "classification_report": report,
        "roc_auc": round(roc_auc, 4) if roc_auc is not None else None,
        "pr_auc": round(pr_auc, 4) if pr_auc is not None else None,
        "training_duration_seconds": round(training_duration, 4),
        "inference_latency_ms": round(inference_latency_ms, 4),
        "model_size_kb": round(model_size_kb, 2),
    }


def measure_inference_latency(pipeline: Any, X_sample: Any, n_iterations: int = 50) -> float:
    """
    Measures mean inference latency per sample in milliseconds.
    """
    try:
        # Take single row
        single_row = X_sample.iloc[[0]] if hasattr(X_sample, "iloc") else X_sample[[0]]
        start = time.perf_counter()
        for _ in range(n_iterations):
            _ = pipeline.predict_proba(single_row)
        elapsed = time.perf_counter() - start
        return (elapsed / n_iterations) * 1000.0
    except Exception:
        return 0.0
