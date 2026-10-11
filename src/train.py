"""
Data-Leakage Safe Model Training Pipeline for EduRisk XAI
"""
from typing import Dict, Any, List, Tuple, Optional
import time
import os
import io
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, GridSearchCV, train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE

from config.settings import (
    RANDOM_STATE, TEST_SIZE, CV_FOLDS, PARAM_GRIDS,
    CORE_FEATURES, TARGET_COLUMN
)
from src.preprocessing import build_preprocessing_pipeline, get_feature_names_out
from src.evaluate import evaluate_predictions, measure_inference_latency

CANDIDATE_ESTIMATORS = {
    "Decision Tree": DecisionTreeClassifier(random_state=RANDOM_STATE),
    "Support Vector Classifier": SVC(probability=True, random_state=RANDOM_STATE),
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
    "Random Forest": RandomForestClassifier(random_state=RANDOM_STATE),
}

def train_all_models(
    df: pd.DataFrame,
    feature_columns: Optional[List[str]] = None,
    target_column: str = TARGET_COLUMN,
    use_smote: bool = True,
    cv_folds: int = CV_FOLDS,
    random_state: int = RANDOM_STATE,
) -> Dict[str, Any]:
    """
    Executes leak-safe training across all 4 candidate models.

    Key research integrity guarantees:
    1. Independent test split (20%) is created FIRST and quarantined.
    2. Imputation, Scaling, and SMOTE are embedded in ImbPipeline.
    3. Resampling is applied strictly to training folds during CV.
    4. Model selection is based exclusively on Cross-Validation Macro F1.
    5. Final test metrics are evaluated once on the quarantined holdout test set.
    """
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' missing from DataFrame.")

    # Determine numeric and categorical features
    if feature_columns is None:
        feature_columns = [c for c in df.columns if c != target_column]

    numeric_features = [
        c for c in feature_columns
        if pd.api.types.is_numeric_dtype(df[c])
    ]
    categorical_features = [
        c for c in feature_columns
        if c not in numeric_features
    ]

    X = df[feature_columns].copy()
    y = df[target_column].copy().astype(int)

    # 1. Stratified Train / Test split BEFORE any transformation or resampling
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        stratify=y,
        random_state=random_state
    )

    minority_count = int(min(y_train.value_counts()))
    est_fold_minority = int(minority_count * (cv_folds - 1) / cv_folds)

    # SMOTE requires at least 2 minority samples in training fold
    can_use_smote = use_smote and (est_fold_minority >= 2)
    k_neighbors = max(1, min(3, est_fold_minority - 1)) if can_use_smote else 1

    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)


    results: Dict[str, Any] = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "feature_columns": feature_columns,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "class_distribution_train": y_train.value_counts().to_dict(),
        "class_distribution_test": y_test.value_counts().to_dict(),
        "models": {},
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test,
    }

    for model_name, base_estimator in CANDIDATE_ESTIMATORS.items():
        print(f"[Training] Initiating pipeline for: {model_name}...")
        start_train_time = time.perf_counter()

        preprocessor = build_preprocessing_pipeline(
            numeric_features=numeric_features,
            categorical_features=categorical_features
        )

        steps = [("preprocessor", preprocessor)]

        # Embed SMOTE inside pipeline only if enabled and feasible
        if can_use_smote:
            steps.append(("smote", SMOTE(random_state=random_state, k_neighbors=k_neighbors)))


        steps.append(("classifier", base_estimator))

        pipeline = ImbPipeline(steps=steps)
        grid_params = PARAM_GRIDS.get(model_name, {})

        grid_search = GridSearchCV(
            estimator=pipeline,
            param_grid=grid_params,
            cv=cv,
            scoring="f1_macro",
            n_jobs=1,
            refit=True,
            return_train_score=False
        )

        try:
            grid_search.fit(X_train, y_train)
            train_duration = time.perf_counter() - start_train_time

            best_pipeline = grid_search.best_estimator_
            cv_best_score = float(grid_search.best_score_)
            cv_std_score = float(grid_search.cv_results_["std_test_score"][grid_search.best_index_])

            # Latency and model size
            latency_ms = measure_inference_latency(best_pipeline, X_test)
            buffer = io.BytesIO()
            joblib.dump(best_pipeline, buffer)
            model_size_kb = len(buffer.getvalue()) / 1024.0

            # Evaluate on independent quarantined test set
            y_pred = best_pipeline.predict(X_test)
            y_prob = best_pipeline.predict_proba(X_test)

            test_metrics = evaluate_predictions(
                y_true=y_test.values,
                y_pred=y_pred,
                y_prob=y_prob,
                training_duration=train_duration,
                inference_latency_ms=latency_ms,
                model_size_kb=model_size_kb,
            )

            # Extract transformed feature names
            fitted_prep = best_pipeline.named_steps["preprocessor"]
            feature_names_out = get_feature_names_out(
                fitted_prep, numeric_features, categorical_features
            )

            results["models"][model_name] = {
                "status": "SUCCESS",
                "pipeline": best_pipeline,
                "best_params": grid_search.best_params_,
                "cv_macro_f1_mean": round(cv_best_score, 4),
                "cv_macro_f1_std": round(cv_std_score, 4),
                "test_metrics": test_metrics,
                "feature_names_out": feature_names_out,
                "training_duration": round(train_duration, 4),
                "inference_latency_ms": round(latency_ms, 4),
                "model_size_kb": round(model_size_kb, 2),
            }
            print(f"[Training] Completed {model_name}: CV Macro F1={cv_best_score:.4f}, Test Macro F1={test_metrics['macro_f1']:.4f}")

        except Exception as e:
            print(f"[Training Error] Failed to train {model_name}: {e}")
            results["models"][model_name] = {
                "status": "FAILED",
                "error": str(e),
                "pipeline": None,
                "best_params": {},
                "cv_macro_f1_mean": 0.0,
                "cv_macro_f1_std": 0.0,
                "test_metrics": {},
                "feature_names_out": [],
                "training_duration": 0.0,
                "inference_latency_ms": 0.0,
                "model_size_kb": 0.0,
            }

    return results
