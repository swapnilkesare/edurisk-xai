from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline as SklearnPipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

def get_preprocessor():
    """
    Returns a scikit-learn ColumnTransformer for preprocessing the core features.
    It uses imputation and standard scaling for numeric features.
    """
    numeric_features = [
        'attendance_rate', 
        'study_hours', 
        'internal_test_score', 
        'assignment_submission_frequency'
    ]
    
    numeric_transformer = SklearnPipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features)
        ],
        remainder='drop'
    )
    
    return preprocessor
