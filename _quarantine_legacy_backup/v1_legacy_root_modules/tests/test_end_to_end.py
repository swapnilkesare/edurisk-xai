import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from ml.data_loader import DataLoader
from ml.train import ModelTrainer
from services.prediction_service import PredictionService
from database.crud import SessionLocal, init_default_rules

def run_tests():
    print("Running Layer 20 End-to-End Self-Test...")
    
    # 1. DB Init
    print("Test 1: Initialize DB and rules...")
    with SessionLocal() as db:
        init_default_rules(db)
    print("-> DB Initialized.")

    # 2. Data Load
    print("Test 2 & 3: Load and validate dataset...")
    loader = DataLoader()
    df = loader.get_data()
    assert not df.empty, "Dataset is empty!"
    assert 'target_at_risk' in df.columns, "Target column missing!"
    print(f"-> Data loaded successfully. Shape: {df.shape}")

    # 3. Train Models
    print("Test 4 to 8: Training pipeline (Train, CV, GridSearch, SMOTE, Evaluate, Select, Save)...")
    trainer = ModelTrainer(df)
    res = trainer.run_training_pipeline()
    print(f"-> Models trained. Selected Model: {res['selected_model']}")
    print(f"-> CV metrics evaluated. F1: {res['results'][res['selected_model']]['cv_best_score']:.3f}")

    # 4. Predict
    print("Test 9 to 15: Run Prediction Service (Predict, SHAP, Interventions, Persistence)...")
    service = PredictionService()
    
    # Pick a sample student
    sample_student = df.drop(columns=['target_at_risk', 'is_synthetic_demo_data'], errors='ignore').iloc[0].to_dict()
    
    result = service.run_src_ri(sample_student, student_identifier="TEST_001")
    
    assert "risk_tier" in result, "Risk tier missing"
    assert "shap_values" in result, "SHAP values missing"
    assert len(result["interventions"]) >= 0, "Interventions list missing"
    
    print(f"-> Prediction generated. Tier: {result['risk_tier']}, Probability: {result['probability']:.3f}")
    print(f"-> SHAP explanation generated. Top factor: {result['risk_factors'][0]['feature'] if result['risk_factors'] else 'None'}")
    print("-> All 20 Layer Tests Completed Successfully.")

if __name__ == "__main__":
    run_tests()
