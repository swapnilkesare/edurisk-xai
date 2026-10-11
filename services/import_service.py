"""
Data Import and Ingestion Service for EduRisk XAI
"""
from typing import Dict, Any, Tuple, Optional
from pathlib import Path

import io
import pandas as pd

from config.settings import PROCESSED_DATA_DIR, TARGET_COLUMN, CORE_FEATURES
from src.schema import validate_dataframe_schema, get_dataset_metadata
from src.data_loader import compute_dataframe_fingerprint, DatasetProvenance
from src.target import validate_target_safety
from database.database import SessionLocal
from database.models import DatasetImport

class ImportService:
    """
    Validates uploaded CSV datasets, verifies schema and feature integrity,
    checks for target leakage, and registers dataset provenance.
    """
    def validate_and_ingest_csv(
        self,
        file_buffer: io.BytesIO,
        filename: str
    ) -> Tuple[bool, Optional[pd.DataFrame], Optional[DatasetProvenance], Dict[str, Any]]:
        """
        Processes an uploaded CSV file.

        Returns:
            (success, DataFrame, DatasetProvenance, report_dict)
        """
        try:
            df = pd.read_csv(file_buffer)
        except Exception as e:
            return False, None, None, {"error": f"Failed to parse CSV file: {str(e)}"}

        is_valid, errors, warnings = validate_dataframe_schema(
            df,
            required_features=CORE_FEATURES,
            check_target=True
        )

        if not is_valid:
            return False, df, None, {
                "errors": errors,
                "warnings": warnings,
                "row_count": len(df),
                "columns": list(df.columns)
            }

        # Validate target leakage safety
        feature_cols = [c for c in df.columns if c != TARGET_COLUMN]
        try:
            validate_target_safety(df, feature_cols, TARGET_COLUMN)
        except ValueError as leak_err:
            return False, df, None, {
                "errors": [str(leak_err)],
                "warnings": warnings
            }

        fingerprint = compute_dataframe_fingerprint(df)
        meta = get_dataset_metadata(df)

        provenance = DatasetProvenance(
            source_type="USER_UPLOADED",
            name=f"Uploaded: {filename}",
            path=None,
            row_count=len(df),
            feature_count=len(feature_cols),
            fingerprint=fingerprint,
            is_synthetic=False,
            description="User-uploaded institutional or benchmark educational dataset.",
            target_distribution=meta.get("target_distribution", {})
        )

        # Persist processed copy
        clean_filename = f"uploaded_{fingerprint[:8]}.csv"
        save_path = PROCESSED_DATA_DIR / clean_filename
        df.to_csv(save_path, index=False)
        provenance.path = str(save_path)

        # Log into SQLite DB
        try:
            db = SessionLocal()
            rec = DatasetImport(
                filename=filename,
                source_type="USER_UPLOADED",
                row_count=len(df),
                feature_count=len(feature_cols),
                fingerprint=fingerprint,
                is_synthetic=False,
                status="VALIDATED"
            )
            db.add(rec)
            db.commit()
            db.close()
        except Exception as e:
            print(f"[Database Warning] Failed to log dataset import: {e}")

        report = {
            "status": "VALIDATED",
            "errors": [],
            "warnings": warnings,
            "metadata": meta,
            "saved_path": str(save_path),
            "fingerprint": fingerprint
        }

        return True, df, provenance, report
