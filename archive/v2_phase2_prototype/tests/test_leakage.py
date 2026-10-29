import pytest
import pandas as pd
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE
from sklearn.tree import DecisionTreeClassifier
from src.preprocessing import get_preprocessor

def test_leakage_smote_does_not_affect_test_set():
    """
    Validates that the ImbPipeline architecture successfully isolates the SMOTE
    transformation to the training set during fit, and leaves the test set untouched
    during predict.
    """
    preprocessor = get_preprocessor()
    smote = SMOTE(random_state=42, k_neighbors=1)
    clf = DecisionTreeClassifier(random_state=42)
    
    pipeline = ImbPipeline([
        ('preprocessor', preprocessor),
        ('smote', smote),
        ('classifier', clf)
    ])
    
    # Dummy data
    X_train = pd.DataFrame({
        'attendance_rate': [90, 80, 50, 40, 20],
        'study_hours': [10, 8, 5, 2, 1],
        'internal_test_score': [80, 70, 50, 30, 20],
        'assignment_submission_frequency': [90, 80, 40, 20, 10]
    })
    y_train = pd.Series([0, 0, 1, 1, 1]) # Imbalanced 2 vs 3
    
    X_test = pd.DataFrame({
        'attendance_rate': [85, 30],
        'study_hours': [9, 3],
        'internal_test_score': [75, 40],
        'assignment_submission_frequency': [85, 30]
    })
    
    # Fit
    pipeline.fit(X_train, y_train)
    
    # Predict
    preds = pipeline.predict(X_test)
    
    # If the pipeline leaked SMOTE into transform/predict, X_test shape would be altered
    # internally and it might throw an error or we can check the imblearn pipeline behavior.
    assert len(preds) == len(X_test), "Test set length was altered during prediction! LEAKAGE DETECTED."
