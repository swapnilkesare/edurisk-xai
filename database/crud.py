"""
Database CRUD Operations and Transaction Helpers for EduRisk XAI
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from database.models import (
    Student, AcademicRecord, BehaviorRecord, Prediction,
    SHAPExplanation, Intervention, InterventionRule, ModelRun, DatasetImport
)
from config.settings import DEFAULT_INTERVENTION_RULES

def seed_default_rules_if_empty(db: Session):
    """Populates default pedagogical intervention rules if table is empty."""
    count = db.query(InterventionRule).count()
    if count == 0:
        for rule_data in DEFAULT_INTERVENTION_RULES:
            rule = InterventionRule(
                feature=rule_data["feature"],
                threshold=rule_data["threshold"],
                direction=rule_data.get("direction", "below"),
                severity=rule_data.get("severity", "MEDIUM"),
                action=rule_data["action"],
                rationale=rule_data["rationale"],
                is_active=True
            )
            db.add(rule)
        db.commit()


def get_all_rules(db: Session, active_only: bool = True) -> List[InterventionRule]:
    query = db.query(InterventionRule)
    if active_only:
        query = query.filter(InterventionRule.is_active == True)
    return query.all()


def get_or_create_student(
    db: Session,
    student_identifier: str,
    name: Optional[str] = None
) -> Student:
    student = db.query(Student).filter(Student.student_identifier == student_identifier).first()
    if not student:
        student = Student(
            student_identifier=student_identifier,
            name=name or f"Student {student_identifier}",
            created_at=datetime.utcnow()
        )
        db.add(student)
        db.commit()
        db.refresh(student)
    return student


def save_prediction_and_xai(
    db: Session,
    student_identifier: Optional[str],
    model_version: str,
    model_name: str,
    predicted_class: int,
    risk_tier: str,
    probability: float,
    input_data: Dict[str, Any],
    shap_explanation: Optional[Dict[str, Any]] = None,
    interventions: Optional[List[Dict[str, Any]]] = None,
) -> Prediction:
    """Saves a complete inference audit record: Prediction -> SHAP -> Interventions."""
    student = None
    if student_identifier:
        student = get_or_create_student(db, student_identifier)

    prediction = Prediction(
        student_id=student.id if student else None,
        student_identifier=student_identifier,
        model_version=model_version,
        model_name=model_name,
        predicted_class=predicted_class,
        risk_tier=risk_tier,
        probability=probability,
        input_data=input_data,
        prediction_timestamp=datetime.utcnow()
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    # Save SHAP explanations
    if shap_explanation and shap_explanation.get("status") == "SUCCESS":
        for idx, contrib in enumerate(shap_explanation.get("contributions", [])):
            direction = "RISK_INCREASING" if contrib["is_risk_increasing"] else "PROTECTIVE"
            val = contrib.get("raw_value")
            shap_rec = SHAPExplanation(
                prediction_id=prediction.id,
                feature_name=contrib["feature"],
                feature_value=float(val) if isinstance(val, (int, float)) else None,
                shap_value=contrib["shap_value"],
                direction=direction,
                rank=idx + 1
            )
            db.add(shap_rec)

    # Save interventions
    if interventions:
        for item in interventions:
            interv = Intervention(
                student_id=student.id if student else None,
                prediction_id=prediction.id,
                risk_factor=item["feature"],
                intervention=item["action"],
                priority=item["priority"],
                status="Pending",
                rationale=item["rationale"],
                created_at=datetime.utcnow()
            )
            db.add(interv)

    db.commit()
    db.refresh(prediction)
    return prediction


def update_intervention_status(db: Session, intervention_id: int, new_status: str) -> bool:
    """Updates educator tracking status for a recommended intervention."""
    interv = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if interv:
        interv.status = new_status
        interv.updated_at = datetime.utcnow()
        db.commit()
        return True
    return False


def get_recent_predictions(db: Session, limit: int = 50) -> List[Prediction]:
    return db.query(Prediction).order_by(Prediction.prediction_timestamp.desc()).limit(limit).all()


def get_all_interventions(db: Session, limit: int = 100) -> List[Intervention]:
    return db.query(Intervention).order_by(Intervention.created_at.desc()).limit(limit).all()


def log_model_run(db: Session, run_data: Dict[str, Any]) -> ModelRun:
    """Saves a model training run record for reproducibility tracking."""
    run = ModelRun(
        experiment_id=run_data["experiment_id"],
        model_version=run_data["model_version"],
        model_name=run_data["model_name"],
        dataset_name=run_data["dataset_name"],
        dataset_hash=run_data["dataset_hash"],
        is_synthetic=run_data.get("is_synthetic", False),
        feature_list=run_data["feature_list"],
        hyperparameters=run_data.get("hyperparameters", {}),
        cv_metrics=run_data.get("cv_metrics", {}),
        test_metrics=run_data.get("test_metrics", {}),
        training_duration=run_data.get("training_duration", 0.0),
        inference_latency_ms=run_data.get("inference_latency_ms", 0.0),
        is_selected=run_data.get("is_selected", False),
        selection_rationale=run_data.get("selection_rationale", "")
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def get_student_history(db: Session, student_identifier: str) -> List[Prediction]:
    """Retrieves longitudinal prediction history for a specific student."""
    return db.query(Prediction).filter(
        Prediction.student_identifier == student_identifier
    ).order_by(Prediction.prediction_timestamp.asc()).all()
