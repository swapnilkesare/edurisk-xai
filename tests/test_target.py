"""
Unit Tests for Target Construction and Risk-Tier Mapping
"""
import pytest
import pandas as pd
import numpy as np

from src.target import (
    construct_risk_target_from_grades,
    map_probability_to_risk_tier,
    map_probabilities_batch,
    validate_target_safety,
    RISK_LOW, RISK_MODERATE, RISK_HIGH
)

def test_target_construction_from_grades():
    grades = pd.Series([8.5, 9.9, 10.0, 14.5, 18.0])
    target = construct_risk_target_from_grades(grades, threshold=10.0)
    # Grades < 10 are at risk (1), >= 10 are on track (0)
    assert list(target) == [1, 1, 0, 0, 0]

def test_probability_risk_tier_boundary_conditions():
    assert map_probability_to_risk_tier(0.66) == RISK_HIGH
    assert map_probability_to_risk_tier(0.85) == RISK_HIGH
    assert map_probability_to_risk_tier(0.6599) == RISK_MODERATE
    assert map_probability_to_risk_tier(0.33) == RISK_MODERATE
    assert map_probability_to_risk_tier(0.3299) == RISK_LOW
    assert map_probability_to_risk_tier(0.05) == RISK_LOW

def test_batch_risk_mapping():
    probs = [0.10, 0.45, 0.75]
    tiers = map_probabilities_batch(probs)
    assert tiers == [RISK_LOW, RISK_MODERATE, RISK_HIGH]

def test_target_leakage_detection():
    df = pd.DataFrame({"attendance": [80], "target_at_risk": [0]})
    # Should raise error if target is in feature set
    with pytest.raises(ValueError, match="Target leakage detected"):
        validate_target_safety(df, feature_columns=["attendance", "target_at_risk"])

    # Should raise error if G3 (final grade) is in features
    with pytest.raises(ValueError, match="Potential target leakage variable"):
        validate_target_safety(df, feature_columns=["attendance", "G3"])
