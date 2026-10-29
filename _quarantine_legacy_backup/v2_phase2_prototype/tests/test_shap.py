import pytest
import pandas as pd
import os
from src.data_loader import DataLoader
from src.train import ModelTrainer
from src.explain import Explainer

def test_shap_explanation_structure():
    """
    Validates that the SHAP explainer correctly maps 4 features to 4 contributions
    and returns valid numerical results.
    """
    # 1. Quickly train a very small DT to get an artifact
    loader = DataLoader()
    df = loader._generate_demo_data(n=20)
    trainer = ModelTrainer(df)
    
    # Restrict to just DT for speed
    dt = trainer.models['Decision Tree']
    trainer.models = {'Decision Tree': dt}
    trainer.run_training_pipeline()
    
    # 2. Extract Explainer
    assert os.path.exists('models/artifacts/best_model.pkl')
    explainer = Explainer('models/artifacts/best_model.pkl')
    
    # 3. Test on 1 sample
    sample = pd.DataFrame({
        'attendance_rate': [50],
        'study_hours': [2],
        'internal_test_score': [40],
        'assignment_submission_frequency': [30]
    })
    
    res = explainer.explain(sample)
    
    assert 'expected_value' in res
    assert 'contributions' in res
    assert len(res['contributions']) == 4
    
    # Check that feature names made it through
    features_present = [c['feature'] for c in res['contributions']]
    assert 'attendance_rate' in features_present
    
    # Check no NaNs
    for c in res['contributions']:
        assert not pd.isna(c['value'])
