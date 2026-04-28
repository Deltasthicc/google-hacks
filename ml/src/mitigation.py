"""
Bias mitigation module for FairLens AI / NyayaLens.

Uses Fairlearn ThresholdOptimizer (post-processing) to produce fair
predictions that satisfy an equalized_odds constraint.
"""

import numpy as np

# ThresholdOptimizer wraps an already-trained classifier and finds
# group-specific decision thresholds that satisfy a fairness constraint.
from fairlearn.postprocessing import ThresholdOptimizer

try:
    from ml.src.train import evaluate_model
    from ml.src.evaluate import detect_bias
except ModuleNotFoundError:
    from src.train import evaluate_model
    from src.evaluate import detect_bias


def apply_mitigation(
    baseline_model,
    features_train, income_labels_train, sensitive_train,
    features_test, income_labels_test, sensitive_test,
    attribute_name="sex",
):
    """
    Apply ThresholdOptimizer mitigation and compute before/after comparison.

    ThresholdOptimizer is a post-processing method: it takes an already-trained
    classifier and finds per-group decision thresholds that satisfy the
    equalized_odds constraint while maximising balanced accuracy.

    Args:
        baseline_model:       Fitted sklearn estimator (e.g., LogisticRegression).
        features_train:       Training features (pandas DataFrame).
        income_labels_train:  Training labels (pandas Series, 0/1).
        sensitive_train:      Sensitive attribute for train set (pandas Series).
        features_test:        Test features (pandas DataFrame).
        income_labels_test:   Test labels (pandas Series, 0/1).
        sensitive_test:       Sensitive attribute for test set (pandas Series).
        attribute_name:       Name of the sensitive attribute (default: 'sex').

    Returns:
        result_dict: Dict with keys:
            - status: 'success'
            - before: bias detection results on original model
            - after:  bias detection results on mitigated predictions
            - improvement: accuracy change, recall gap change, summary text
    """
    # --- Before: evaluate baseline model ---
    baseline_predictions = baseline_model.predict(features_test)
    before_metrics = evaluate_model(baseline_predictions, income_labels_test)
    before_bias = detect_bias(
        baseline_predictions, income_labels_test, sensitive_test, attribute_name
    )

    # --- Apply ThresholdOptimizer ---
    # constraints="equalized_odds" requires equal TPR AND FPR across groups.
    # objective="balanced_accuracy_score" handles class imbalance better.
    # predict_method="predict_proba" lets the optimizer sweep thresholds smoothly.
    mitigated_predictor = ThresholdOptimizer(
        estimator=baseline_model,
        constraints="equalized_odds",
        objective="balanced_accuracy_score",
        predict_method="predict_proba",
    )

    mitigated_predictor.fit(
        features_train,
        income_labels_train,
        sensitive_features=sensitive_train,
    )

    mitigated_predictions = mitigated_predictor.predict(
        features_test,
        sensitive_features=sensitive_test,
    )

    # --- After: evaluate mitigated predictions ---
    after_metrics = evaluate_model(mitigated_predictions, income_labels_test)
    after_bias = detect_bias(
        mitigated_predictions, income_labels_test, sensitive_test, attribute_name
    )

    # --- Compute improvement summary ---
    accuracy_change    = float(after_metrics["accuracy"] - before_metrics["accuracy"])
    before_recall_diff = float(before_bias["metrics"]["differences"]["recall_difference"])
    after_recall_diff  = float(after_bias["metrics"]["differences"]["recall_difference"])
    recall_diff_change = float(after_recall_diff - before_recall_diff)

    improvement_summary = (
        f"Recall gap changed from {before_recall_diff:.2f} to {after_recall_diff:.2f} "
        f"(change: {recall_diff_change:+.2f}). "
        f"Accuracy change: {accuracy_change:+.4f}."
    )

    if recall_diff_change < 0:
        improvement_summary += " Mitigation recommended."
    else:
        improvement_summary += " Mitigation did not improve fairness."

    result_dict = {
        "status": "success",
        "mitigation_method": "Fairlearn ThresholdOptimizer (equalized_odds)",
        "before": {
            "model_metrics": before_metrics,
            "bias_detection": before_bias,
        },
        "after": {
            "model_metrics": after_metrics,
            "bias_detection": after_bias,
        },
        "improvement": {
            "accuracy_change":          float(round(accuracy_change, 4)),
            "recall_difference_change": float(round(recall_diff_change, 4)),
            "summary": improvement_summary,
        },
    }

    return result_dict
