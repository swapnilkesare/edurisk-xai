"""
Database CRUD Operations and Transaction Helpers for EduRisk XAI
"""
from typing import List, Dict, Any, Optional, Tuple, Union
import re
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
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


def normalize_prn(raw_prn: str) -> str:
    """
    Normalizes Permanent Roll Number (PRN):
    - Trims leading and trailing whitespace
    - Converts to uppercase
    - Preserves meaningful internal separators and leading zeros
    """
    if not raw_prn:
        return ""
    # Strip whitespace, collapse multi-spaces, and uppercase
    cleaned = raw_prn.strip()
    return cleaned.upper()


def validate_prn(prn: str) -> Tuple[bool, str]:
    """
    Validates PRN format according to institutional policy:
    - Must be between 2 and 48 characters
    - Alphanumeric with permitted institutional hyphens, slashes, or underscores
    - Cannot be purely blank or contain invalid control characters
    """
    normalized = normalize_prn(prn)
    if not normalized:
        return False, "PRN cannot be empty."
    if len(normalized) < 2:
        return False, "PRN must be at least 2 characters long."
    if len(normalized) > 48:
        return False, "PRN cannot exceed 48 characters."
    if not re.match(r"^[A-Z0-9_\-\/\.]+$", normalized):
        return False, "PRN may only contain letters, numbers, hyphens, slashes, and periods."
    return True, ""


def get_student_by_prn(
    db: Session,
    prn_or_id: str,
    organization_id: Optional[int] = None
) -> Optional[Student]:
    """
    Finds a student by normalized PRN or legacy identifier.
    Respects institutional organization scoping if organization_id is provided.
    """
    norm = normalize_prn(prn_or_id)
    if not norm:
        return None

    query = db.query(Student).filter(
        or_(
            Student.prn == norm,
            Student.student_identifier == norm,
            Student.student_identifier == prn_or_id.strip()
        )
    )
    if organization_id is not None:
        query = query.filter(
            or_(
                Student.organization_id == organization_id,
                Student.organization_id == None
            )
        )
    return query.first()


def register_student_prn(
    db: Session,
    prn: str,
    name: str,
    course: str = "Computer Science & AI",
    department: str = "Engineering",
    semester: int = 3,
    year: int = 2,
    batch_year: str = "2024–2028",
    division: str = "A",
    email: Optional[str] = None,
    organization_id: Optional[int] = None,
    created_by_user_id: Optional[int] = None,
) -> Tuple[Optional[Student], bool, str]:
    """
    Persistent, One-Time Student Registration workflow using PRN as unique identifier.
    Guarantees:
    - PRN is validated and normalized
    - Uniqueness enforced within organization scope
    - Atomic database commit with rollback on conflict
    Returns (student, is_newly_registered, message).
    """
    norm_prn = normalize_prn(prn)
    is_valid, err_msg = validate_prn(norm_prn)
    if not is_valid:
        return None, False, err_msg

    if not name or not name.strip():
        return None, False, "Student full name is required."

    clean_name = name.strip()

    # Check for existing student within scope
    existing = get_student_by_prn(db, norm_prn, organization_id=organization_id)
    if existing:
        return existing, False, f"Student with PRN '{norm_prn}' is already registered in this organization."

    try:
        new_student = Student(
            prn=norm_prn,
            student_identifier=norm_prn,  # Synchronized for legacy reference compatibility
            name=clean_name,
            course=course.strip() if course else "Computer Science & AI",
            department=department.strip() if department else "Engineering",
            semester=int(semester),
            year=int(year),
            batch_year=batch_year.strip() if batch_year else "2024–2028",
            division=division.strip() if division else "A",
            email=email.strip().lower() if email else None,
            enrollment_status="Active",
            academic_history=[],
            organization_id=organization_id,
            created_by_user_id=created_by_user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return new_student, True, f"Successfully registered student {clean_name} (PRN: {norm_prn})."
    except Exception as e:
        db.rollback()
        return None, False, f"Database transaction failed during registration: {str(e)}"


def update_student_academic_placement(
    db: Session,
    student_id: int,
    new_semester: Optional[int] = None,
    new_course: Optional[str] = None,
    new_department: Optional[str] = None,
    new_division: Optional[str] = None,
    note: Optional[str] = None
) -> Optional[Student]:
    """
    Updates academic placement (semester, course, section) without duplicating the student record.
    Appends the transition snapshot to the student's auditable academic_history log.
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return None

    history_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "previous_semester": student.semester,
        "previous_course": student.course,
        "previous_division": student.division,
        "note": note or "Academic progression update"
    }

    history = list(student.academic_history or [])
    history.append(history_entry)
    student.academic_history = history

    if new_semester is not None:
        student.semester = int(new_semester)
    if new_course is not None:
        student.course = new_course.strip()
    if new_department is not None:
        student.department = new_department.strip()
    if new_division is not None:
        student.division = new_division.strip()

    student.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(student)
    return student


def get_or_create_student(
    db: Session,
    student_identifier: str,
    name: Optional[str] = None,
    organization_id: Optional[int] = None,
    created_by_user_id: Optional[int] = None,
) -> Student:
    """
    Backward-compatible student retrieval/creation helper with PRN synchronization.
    """
    norm = normalize_prn(student_identifier)
    student = get_student_by_prn(db, norm, organization_id=organization_id)
    if not student:
        student = Student(
            prn=norm,
            student_identifier=student_identifier,
            name=name or f"Student {norm}",
            organization_id=organization_id,
            created_by_user_id=created_by_user_id,
            created_at=datetime.utcnow()
        )
        db.add(student)
        db.commit()
        db.refresh(student)
    elif organization_id and not student.organization_id:
        student.organization_id = organization_id
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
    organization_id: Optional[int] = None,
    created_by_user_id: Optional[int] = None,
) -> Prediction:
    """Saves a complete inference audit record: Prediction -> SHAP -> Interventions."""
    student = None
    if student_identifier:
        student = get_or_create_student(
            db, 
            student_identifier,
            organization_id=organization_id,
            created_by_user_id=created_by_user_id
        )

    prediction = Prediction(
        student_id=student.id if student else None,
        student_identifier=student_identifier,
        organization_id=organization_id or (student.organization_id if student else None),
        created_by_user_id=created_by_user_id,
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


def get_student_history(db: Session, student_ref: Union[int, str]) -> List[Prediction]:
    """Retrieves longitudinal prediction history for a specific student by ID or PRN."""
    if isinstance(student_ref, int):
        return db.query(Prediction).filter(
            or_(Prediction.student_id == student_ref, Prediction.student_identifier == str(student_ref))
        ).order_by(Prediction.prediction_timestamp.asc()).all()
    else:
        norm = normalize_prn(str(student_ref))
        return db.query(Prediction).filter(
            or_(Prediction.student_identifier == norm, Prediction.student_identifier == str(student_ref))
        ).order_by(Prediction.prediction_timestamp.asc()).all()

