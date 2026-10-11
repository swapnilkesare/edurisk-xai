"""
Unit Tests for Preprocessing Pipeline and Feature Alignment
"""
import pytest
import pandas as pd
import numpy as np

from src.preprocessing import build_preprocessing_pipeline, get_feature_names_out

def test_preprocessing_imputation_and_scaling():
    df_raw = pd.DataFrame({
        "attendance_rate": [80.0, np.nan, 95.0, 60.0],
        "internal_test_score": [50.0, 70.0, np.nan, 40.0],
        "sex": ["F", "M", np.nan, "F"],
    })
    numeric_features = ["attendance_rate", "internal_test_score"]
    categorical_features = ["sex"]

    preprocessor = build_preprocessing_pipeline(
        numeric_features=numeric_features,
        categorical_features=categorical_features
    )

    X_trans = preprocessor.fit_transform(df_raw)
    assert not np.isnan(X_trans).any(), "Transformed output must not contain NaNs"
    assert X_trans.shape[0] == 4

    feature_names = get_feature_names_out(preprocessor, numeric_features, categorical_features)
    assert "attendance_rate" in feature_names
    assert "internal_test_score" in feature_names
    assert len(feature_names) == X_trans.shape[1]

def test_preprocessing_numeric_only():
    df_num = pd.DataFrame({
        "attendance_rate": [80.0, 90.0, 70.0],
        "study_hours": [3.0, 5.0, 2.0]
    })
    numeric_features = ["attendance_rate", "study_hours"]
    preprocessor = build_preprocessing_pipeline(numeric_features=numeric_features)
    X_trans = preprocessor.fit_transform(df_num)
    assert X_trans.shape == (3, 2)
    names = get_feature_names_out(preprocessor, numeric_features)
    assert names == ["attendance_rate", "study_hours"]
