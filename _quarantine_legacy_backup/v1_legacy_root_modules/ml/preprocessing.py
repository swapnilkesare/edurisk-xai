import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from config.settings import CORE_FEATURES

def get_preprocessor(df: pd.DataFrame) -> ColumnTransformer:
    """
    Creates a scikit-learn ColumnTransformer for preprocessing the dataset.
    Automatically identifies numerical and categorical columns.
    """
    # Exclude target and metadata columns
    exclude_cols = ['target_at_risk', 'is_synthetic_demo_data']
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    # Identify numerical and categorical columns
    numeric_features = df[feature_cols].select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
    categorical_features = df[feature_cols].select_dtypes(include=['object', 'category', 'bool']).columns.tolist()

    # Preprocessing for numerical data: Impute missing with median, then scale
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    # Preprocessing for categorical data: Impute missing with mode, then one-hot encode
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    # Combine preprocessing steps
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='passthrough'
    )

    return preprocessor

def get_feature_names(preprocessor, numeric_features, categorical_features):
    """Utility to get feature names after preprocessing, useful for SHAP."""
    # This assumes the preprocessor has been fitted
    try:
        cat_features_out = preprocessor.named_transformers_['cat'].named_steps['onehot'].get_feature_names_out(categorical_features)
        return list(numeric_features) + list(cat_features_out)
    except Exception:
        # Fallback if un-fitted or something fails
        return list(numeric_features) + list(categorical_features)
