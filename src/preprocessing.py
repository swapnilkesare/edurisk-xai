"""
Data Preprocessing Pipeline Construction and Feature Alignment
"""
from typing import List, Tuple, Optional
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

def build_preprocessing_pipeline(
    numeric_features: List[str],
    categorical_features: Optional[List[str]] = None
) -> ColumnTransformer:
    """
    Creates an sklearn ColumnTransformer that safely handles missing values,
    scales numerical features, and one-hot encodes categorical variables.
    """
    categorical_features = categorical_features or []

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    transformers = [("num", numeric_transformer, numeric_features)]

    if categorical_features:
        categorical_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ])
        transformers.append(("cat", categorical_transformer, categorical_features))

    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder="drop",
        verbose_feature_names_out=False
    )
    return preprocessor


def get_feature_names_out(
    preprocessor: ColumnTransformer,
    numeric_features: List[str],
    categorical_features: Optional[List[str]] = None
) -> List[str]:
    """
    Extracts explicit output feature names after ColumnTransformer fitting.
    Guarantees 1-to-1 alignment with SHAP explanation matrices.
    """
    try:
        return list(preprocessor.get_feature_names_out())
    except Exception:
        # Fallback manual reconstruction if get_feature_names_out fails
        feature_names = list(numeric_features)
        if categorical_features and "cat" in preprocessor.named_transformers_:
            cat_pipe = preprocessor.named_transformers_["cat"]
            if hasattr(cat_pipe, "named_steps") and "onehot" in cat_pipe.named_steps:
                onehot = cat_pipe.named_steps["onehot"]
                if hasattr(onehot, "get_feature_names_out"):
                    feature_names.extend(list(onehot.get_feature_names_out(categorical_features)))
        return feature_names
