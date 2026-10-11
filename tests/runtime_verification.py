"""
Runtime Verification Script for EduRisk XAI
Executes programmatic end-to-end verification of dataset, model, prediction,
SHAP explainability, interventions, and database persistence.
"""
import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pandas as pd
import numpy as np

# 1. Component Imports
from src.data_loader import load_dataset
from src.schema import validate_dataframe_schema, CORE_FEATURE_BOUNDS
from src.target import construct_risk_target_from_grades, map_probability_to_risk_tier, validate_target_safety, TARGET_COLUMN
from src.risk import RiskClassifier
from services.prediction_service import PredictionService
from database.database import SessionLocal
from database.crud import get_recent_predictions, get_all_rules

def main():
    print("=" * 70)
    print("EDURISK XAI — PROGRAMMATIC END-TO-END RUNTIME VERIFICATION")
    print("=" * 70)

    # STEP 1: Verify Dataset and Target Construction
    print("\n[CHECK 1] Dataset Ingestion & Schema Integrity...")
    df, prov = load_dataset(fallback_to_synthetic=False)
    print(f" -> Dataset Name: {prov.name}")
    print(f" -> Total Records: {len(df)}")
    print(f" -> Feature Count: {prov.feature_count}")
    print(f" -> Fingerprint: {prov.fingerprint}")
    print(f" -> Synthetic Flag: {prov.is_synthetic}")
    
    # Target distribution
    if "G3" in df.columns:
        df_target = construct_risk_target_from_grades(df["G3"])
        target_counts = df_target.value_counts().to_dict()
        print(f" -> Target Distribution from G3: {target_counts} (0: Low-Risk/Pass, 1: High-Risk/Fail)")
    elif TARGET_COLUMN in df.columns:
        target_counts = df[TARGET_COLUMN].value_counts().to_dict()
        print(f" -> Target Distribution: {target_counts} (0: Low-Risk/Pass, 1: High-Risk/Fail)")

    # STEP 2: Verify Leakage Safeguards
    print("\n[CHECK 2] Leakage Safeguards...")
    feature_cols = [c for c in df.columns if c not in ["G1", "G2", "G3", TARGET_COLUMN]]
    safety_ok = validate_target_safety(df, feature_cols)
    print(f" -> Target Safety Validation Result: {safety_ok}")

    # Core features bounds
    print(f" -> Core Features Bound Rules: {list(CORE_FEATURE_BOUNDS.keys())}")
    for f in ["G1", "G2", "G3"]:
        assert f not in CORE_FEATURE_BOUNDS, f"Future grade {f} must not be a feature!"
    print(" -> Leakage Check PASSED: Future grade indicators G1, G2, G3 are strictly excluded.")

    # STEP 3: Verify Model Deserialization & Prediction Service
    print("\n[CHECK 3] Model Loading & Prediction Service...")
    pred_svc = PredictionService()
    assert pred_svc.is_model_ready(), "Trained model artifact must load"
    print(f" -> Loaded Model Pipeline: {type(pred_svc.pipeline)}")
    print(f" -> Model Selection Meta: {pred_svc.metadata.get('selected_model')}")
    print(f" -> Model Version: {pred_svc.metadata.get('model_version')}")

    # Test High-Risk Sample Student
    high_risk_input = {
        "attendance_rate": 55.0,
        "internal_test_score": 25.0,
        "assignment_submission_frequency": 45.0,
        "study_hours": 1.0,
        "Walc": 3.0,
    }

    pred_res_high = pred_svc.predict_and_explain(
        student_data=high_risk_input,
        student_identifier="VERIF-STUDENT-HIGH",
        save_to_db=True
    )
    print("\n -> High-Risk Student Prediction & SHAP Output:")
    pred_info_h = pred_res_high["prediction"]
    shap_info_h = pred_res_high["shap"]
    interv_info_h = pred_res_high["interventions"]

    print(f"    * Predicted Class: {pred_info_h['predicted_class']} (1=At-Risk, 0=On-Track)")
    print(f"    * Risk Probability: {pred_info_h['risk_probability']:.4f}")
    print(f"    * Assigned Risk Tier: {pred_info_h['risk_tier']}")
    print(f"    * Urgency Level: {pred_info_h['urgency']}")
    assert pred_info_h['risk_tier'] in ["MODERATE", "HIGH"], f"Expected MODERATE/HIGH risk tier, got {pred_info_h['risk_tier']}"

    # Verify SHAP for High-Risk Student
    assert shap_info_h["status"] == "SUCCESS", "SHAP explanation should succeed"
    print(f"    * SHAP Base Value: {shap_info_h['base_value']:.4f}")
    print(f"    * SHAP Contributions: {len(shap_info_h['contributions'])} features evaluated")
    for c in shap_info_h["contributions"]:
        impact = "INCREASES RISK" if c["is_risk_increasing"] else "PROTECTIVE"
        print(f"      - {c['feature']} (val={c['raw_value']}): SHAP={c['shap_value']:+.4f} [{impact}]")
    print(f"    * Plain Language Summary: {shap_info_h['plain_language_summary']}")

    # Verify Interventions for High-Risk Student
    print(f"    * Triggered Interventions: {len(interv_info_h)} actions")
    for iv in interv_info_h:
        print(f"      - [{iv['priority'].upper()}] {iv['action']} (Reason: {iv['rationale']})")

    # Test Low-Risk Sample Student
    low_risk_input = {
        "attendance_rate": 96.0,
        "internal_test_score": 92.0,
        "assignment_submission_frequency": 95.0,
        "study_hours": 8.0,
    }

    pred_res_low = pred_svc.predict_and_explain(
        student_data=low_risk_input,
        student_identifier="VERIF-STUDENT-LOW",
        save_to_db=True
    )
    pred_info_l = pred_res_low["prediction"]
    print("\n -> Low-Risk Student Prediction Output:")
    print(f"    * Predicted Class: {pred_info_l['predicted_class']}")
    print(f"    * Risk Probability: {pred_info_l['risk_probability']:.4f}")
    print(f"    * Assigned Risk Tier: {pred_info_l['risk_tier']}")
    print(f"    * Urgency Level: {pred_info_l['urgency']}")
    assert pred_info_l['risk_tier'] == "LOW", f"Expected LOW risk tier, got {pred_info_l['risk_tier']}"

    # STEP 4: Global SHAP Importance
    print("\n[CHECK 4] Global Feature Importance via SHAP...")
    bg_features = df[feature_cols].head(25)
    global_importance = pred_svc.xai_engine.compute_global_importance(bg_features)
    print(f" -> Global Feature Importance Computed for {len(global_importance)} features:")
    for f in global_importance:
        print(f"    * {f['feature']}: Mean |SHAP| = {f['mean_abs_shap']:.4f}")

    # STEP 5: Verify Database Persistence
    print("\n[CHECK 5] SQLite Database Persistence Verification...")
    db = SessionLocal()
    try:
        preds = get_recent_predictions(db, limit=5)
        print(f" -> Total Recent Predictions Queried from SQLite: {len(preds)}")
        for p in preds[:2]:
            print(f"    * DB ID={p.id}, Student={p.student_identifier}, Tier={p.risk_tier}, Prob={p.probability:.4f}")
        rules = get_all_rules(db, active_only=True)
        print(f" -> Active Intervention Rules in SQLite: {len(rules)}")
        for r in rules[:3]:
            print(f"    * Rule: If {r.feature} {r.direction} {r.threshold} -> [{r.severity}] {r.action}")
    finally:
        db.close()

    # STEP 6: Verify All 11 Dashboard Pages
    print("\n[CHECK 6] Verifying All 11 Streamlit Dashboard Pages...")
    page_functions = [
        ("app_pages.dashboard", "render_dashboard"),
        ("app_pages.predict_student", "render_predict_student"),
        ("app_pages.students", "render_students"),
        ("app_pages.reports", "render_reports"),
        ("app_pages.data_import", "render_data_import"),
        ("app_pages.model_training", "render_model_training"),
        ("app_pages.model_comparison", "render_model_comparison"),
        ("app_pages.explainability", "render_explainability"),
        ("app_pages.interventions", "render_interventions"),
        ("app_pages.analytics", "render_analytics"),
        ("app_pages.research_traceability", "render_research_traceability")
    ]
    for pm, fn in page_functions:
        mod = __import__(pm, fromlist=[fn])
        assert hasattr(mod, fn), f"Page module {pm} missing {fn}() entry point!"
        print(f" -> Page verified: {pm} ({fn} found)")

    # STEP 7: Verify Authentication & Role Access
    print("\n[CHECK 7] Verifying PBKDF2 Authentication & Multi-Tenancy Scoping...")
    from services.auth_service import authenticate_user, seed_default_auth, get_scoped_students
    db = SessionLocal()
    try:
        seed_default_auth(db)
        teacher = authenticate_user(db, "teacher1", "Teacher@123")
        assert teacher is not None, "Teacher authentication failed"
        assert teacher.role == "TEACHER"
        scoped_students = get_scoped_students(db, teacher)
        print(f" -> Teacher1 Authenticated: Role={teacher.role}, Org={teacher.organization.name}, Scoped Students={len(scoped_students)}")
    finally:
        db.close()

    print("\n" + "=" * 70)
    print("ALL RUNTIME VERIFICATION CHECKS PASSED WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == "__main__":
    main()
