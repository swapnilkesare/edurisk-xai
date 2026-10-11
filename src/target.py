"""
Target Definition and Risk-Tier Mapping for EduRisk XAI
"""
from typing import Dict, Any, List, Union
import numpy as np
import pandas as pd

from config.settings import TARGET_COLUMN, HIGH_RISK_THRESHOLD, MODERATE_RISK_THRESHOLD

# Risk Tier String Constants
RISK_LOW = "LOW"
RISK_MODERATE = "MODERATE"
RISK_HIGH = "HIGH"

def construct_risk_target_from_grades(
    grades: pd.Series,
    threshold: float = 10.0
) -> pd.Series:
    """
    Constructs a binary risk target label from final grades.
    In European / Portuguese scale (0-20), grade < 10 indicates academic failure (at-risk).

    Args:
        grades: Series of final numeric marks (0-20)
        threshold: Failing boundary mark (default 10.0)

    Returns:
        Binary target Series (1 = At-Risk, 0 = On-Track)
    """
    return (grades < threshold).astype(int)


def map_probability_to_risk_tier(
    prob: float,
    high_threshold: float = HIGH_RISK_THRESHOLD,
    moderate_threshold: float = MODERATE_RISK_THRESHOLD
) -> str:
    """
    Maps continuous predicted risk probability to an operational risk tier.

    Tier boundaries:
        prob >= high_threshold           -> HIGH
        moderate_threshold <= prob < high -> MODERATE
        prob < moderate_threshold        -> LOW
    """
    if np.isnan(prob):
        return "UNKNOWN"
    if prob >= high_threshold:
        return RISK_HIGH
    elif prob >= moderate_threshold:
        return RISK_MODERATE
    else:
        return RISK_LOW


def map_probabilities_batch(
    probs: Union[np.ndarray, List[float]],
    high_threshold: float = HIGH_RISK_THRESHOLD,
    moderate_threshold: float = MODERATE_RISK_THRESHOLD
) -> List[str]:
    """
    Vectorized/batch mapping of predicted probabilities to risk tiers.
    """
    return [
        map_probability_to_risk_tier(p, high_threshold, moderate_threshold)
        for p in probs
    ]


def validate_target_safety(
    df: pd.DataFrame,
    feature_columns: List[str],
    target_column: str = TARGET_COLUMN
) -> bool:
    """
    Verifies that the target column does not leak into the candidate feature columns.
    """
    if target_column in feature_columns:
        raise ValueError(f"Target leakage detected! '{target_column}' is included in feature columns.")
    # Also verify that final grade variables (G3) are not in feature set
    forbidden_leak_indicators = ["G3", "g3", "final_grade", "target", "at_risk"]
    for col in feature_columns:
        if col.lower() in forbidden_leak_indicators:
            raise ValueError(f"Potential target leakage variable '{col}' found in feature columns!")
    return True
