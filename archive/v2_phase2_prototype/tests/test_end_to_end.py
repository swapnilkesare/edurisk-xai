import os
import sys
from pathlib import Path

# Setup path so we can import src
sys.path.append(str(Path(__file__).parent.parent))

from src.data_loader import DataLoader
from src.train import ModelTrainer
from src.predict import Predictor
from src.explain import Explainer
from src.intervention import InterventionEngine

def run_tests():
    print("Running Phase 2 Prototype End-to-End Test...")
    
    print("Test 1: Data Loading & Preprocessing mapping...")
    loader = DataLoader()
    df = loader.load_data()
    assert not df.empty, "Dataset empty."
    assert 'target_at_risk' in df.columns, "Target missing."
    assert 'is_synthetic_demo_data' in df.columns, "Metadata missing."
    print("-> PASS: Data Loaded.")
    
    print("Test 2: Model Training Pipeline (SMOTE, 4-Models, GridSearch)...")
    trainer = ModelTrainer(df)
    res = trainer.run_training_pipeline()
    assert res['selected_model'] is not None, "No model selected."
    assert len(res['results']) == 4, "Not all 4 models were evaluated."
    print(f"-> PASS: Models trained. Selected: {res['selected_model']}")
    
    print("Test 3: Prediction and Risk Calculation...")
    predictor = Predictor()
    sample_student = {
        'attendance_rate': 40,
        'study_hours': 3,
        'internal_test_score': 35,
        'assignment_submission_frequency': 40
    }
    pred_res = predictor.predict(sample_student)
    assert 'probability' in pred_res
    assert pred_res['risk_tier'] in ['HIGH', 'MODERATE', 'LOW']
    print(f"-> PASS: Prediction successful. Risk: {pred_res['risk_tier']}")
    
    print("Test 4: SHAP Explanations...")
    explainer = Explainer()
    shap_res = explainer.explain(pred_res['input_df'])
    assert len(shap_res['contributions']) == 4
    print("-> PASS: SHAP executed.")
    
    print("Test 5: Intervention Mapping...")
    engine = InterventionEngine()
    actions = engine.generate_recommendations(shap_res['contributions'])
    assert type(actions) == list
    print("-> PASS: Intervention generated.")
    
    print("ALL TESTS PASSED.")

if __name__ == "__main__":
    run_tests()
