"""
Counterfactual analysis module for FairLens AI / NyayaLens.

Tests whether flipping gender-proxy features changes model predictions.
A high flip rate indicates the model relies on proxy features for the
sensitive attribute, even though it was removed from the feature set.
"""

import numpy as np
import pandas as pd


def run_counterfactual_check(model, features_test, sensitive_test):
    """
    Run a counterfactual sensitivity check on the test set.

    Creates a counterfactual version of the test set by flipping
    relationship proxy columns (Husband <-> Wife) and measures how
    many predictions change.

    Args:
        model:           Fitted sklearn model with .predict() method.
        features_test:   Test features (pandas DataFrame, scaled).
        sensitive_test:  Sensitive attribute values for test set (pandas Series).

    Returns:
        result: Dict with keys:
            - status: 'success'
            - flip_count: number of predictions that changed
            - flip_rate: proportion of predictions that changed
            - flip_rate_by_group: dict of flip rate per sensitive group
            - severity: 'HIGH' (>10%), 'MEDIUM' (5-10%), 'LOW' (<5%)
    """
    original_predictions = model.predict(features_test)

    # Find relationship proxy columns (these correlate with gender)
    relationship_cols = [c for c in features_test.columns
                         if "relationship" in c.lower()]

    counterfactual_test = features_test.copy()

    # Try to find and swap Wife <-> Husband columns
    wife_cols = [c for c in relationship_cols if "wife" in c.lower()]
    husband_cols = [c for c in relationship_cols if "husband" in c.lower()]

    if wife_cols and husband_cols:
        wife_col = wife_cols[0]
        husband_col = husband_cols[0]
        original_wife = counterfactual_test[wife_col].copy()
        counterfactual_test[wife_col] = counterfactual_test[husband_col]
        counterfactual_test[husband_col] = original_wife
    else:
        # Fallback: negate all relationship columns
        for col in relationship_cols:
            counterfactual_test[col] = -counterfactual_test[col]

    counterfactual_predictions = model.predict(counterfactual_test)

    # Measure flip rate
    prediction_flipped = original_predictions != counterfactual_predictions
    flip_count = int(prediction_flipped.sum())
    flip_rate = float(flip_count / len(prediction_flipped))

    # Flip rate by group
    flip_df = pd.DataFrame({
        "group": sensitive_test.values,
        "flipped": prediction_flipped,
    })
    flip_rate_by_group = {}
    for group_name, group_data in flip_df.groupby("group"):
        flip_rate_by_group[str(group_name)] = float(group_data["flipped"].mean())

    # Severity
    if flip_rate > 0.10:
        severity = "HIGH"
    elif flip_rate > 0.05:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    result = {
        "status": "success",
        "flip_count": flip_count,
        "flip_rate": float(round(flip_rate, 4)),
        "flip_rate_by_group": flip_rate_by_group,
        "severity": severity,
        "proxy_columns_used": relationship_cols,
    }

    return result
