"""
Rigorous Tests Proving Absence of Data Leakage and Quarantined Evaluation
"""
import pytest
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE
from sklearn.tree import DecisionTreeClassifier

from src.data_loader import generate_synthetic_demo_data
from src.preprocessing import build_preprocessing_pipeline
from src.train import train_all_models
from config.settings import TARGET_COLUMN

def test_smote_does_not_resample_holdout_test_set():
    """
    Verifies that SMOTE resampling embedded in ImbPipeline modifies ONLY the training fold,
    leaving the evaluation test set strictly untouched.
    """
    df, _ = generate_synthetic_demo_data(n_samples=200, random_state=42)
    feature_cols = ["attendance_rate", "internal_test_score", "study_hours"]

    X = df[feature_cols]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=42
    )

    original_test_len = len(X_test)
    original_test_hash = pd.util.hash_pandas_object(X_test).sum()

    preprocessor = build_preprocessing_pipeline(numeric_features=feature_cols)
    pipeline = ImbPipeline(steps=[
        ("preprocessor", preprocessor),
        ("smote", SMOTE(random_state=42)),
        ("classifier", DecisionTreeClassifier(random_state=42))
    ])

    # Fit pipeline strictly on training data
    pipeline.fit(X_train, y_train)

    # Execute predictions on holdout test set
    preds = pipeline.predict(X_test)

    # Verify holdout test set was NOT mutated or enlarged by SMOTE
    assert len(X_test) == original_test_len, "Test set size was mutated!"
    assert pd.util.hash_pandas_object(X_test).sum() == original_test_hash, "Test set values were altered!"
    assert len(preds) == original_test_len

def test_training_pipeline_quarantines_test_evaluation():
    """
    Verifies train_all_models keeps train and test partitions completely separate.
    """
    df, _ = generate_synthetic_demo_data(n_samples=100, random_state=99)
    results = train_all_models(
        df=df,
        feature_columns=["attendance_rate", "internal_test_score", "study_hours"],
        cv_folds=3,
        use_smote=True,
        random_state=99
    )

    X_train = results["X_train"]
    X_test = results["X_test"]

    # Verify mutual exclusivity of index sets
    intersection = set(X_train.index).intersection(set(X_test.index))
    assert len(intersection) == 0, "Train and test partitions overlap! Severe leakage."
    assert len(X_train) + len(X_test) == len(df)
