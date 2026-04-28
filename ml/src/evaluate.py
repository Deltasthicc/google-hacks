"""
Bias detection module for FairLens AI / NyayaLens.

Uses Fairlearn MetricFrame to compute per-group fairness metrics
and flag disparities across sensitive attribute groups.
"""

from sklearn.metrics import accuracy_score, recall_score

# Fairlearn MetricFrame computes any sklearn metric broken down by
# each unique value of a sensitive feature (e.g., Male vs Female).
from fairlearn.metrics import MetricFrame


def detect_bias(predictions, income_labels_test, sensitive_test, attribute_name="sex"):
    """
    Measure how model predictions differ across groups in a sensitive attribute.

    Uses Fairlearn's MetricFrame to compute accuracy and recall separately
    for each group, then calculates the max gap between groups. Flags
    disparities as HIGH (>10%), MEDIUM (5-10%), or LOW (<5%).

    Args:
        predictions:         numpy array of predicted labels (0 or 1).
        income_labels_test:  pandas Series of true labels (0 or 1).
        sensitive_test:      pandas Series of sensitive attribute values
                             for the test set (e.g., 'Male'/'Female').
        attribute_name:      String name of the sensitive attribute,
                             used in finding descriptions. Defaults to 'sex'.

    Returns:
        bias_results: Dict with keys:
            - status: 'success'
            - metrics: { by_group: {...}, differences: {...} }
            - findings: list of severity-tagged findings
    """
    # MetricFrame: computes each metric per-group automatically
    fairness_frame = MetricFrame(
        metrics={
            "accuracy": accuracy_score,
            "recall":   recall_score,
        },
        y_true=income_labels_test,
        y_pred=predictions,
        sensitive_features=sensitive_test,
    )

    per_group_table = fairness_frame.by_group
    metric_differences = fairness_frame.difference()

    # Build per-group dict (JSON-safe floats)
    by_group_dict = {}
    for group_name in per_group_table.index:
        by_group_dict[str(group_name)] = {
            "accuracy": float(per_group_table.loc[group_name, "accuracy"]),
            "recall":   float(per_group_table.loc[group_name, "recall"]),
        }

    accuracy_difference = float(metric_differences["accuracy"])
    recall_difference   = float(metric_differences["recall"])

    # Classify severity for each metric gap
    findings_list = []
    for metric_name, difference_value in [("accuracy_difference", accuracy_difference),
                                           ("recall_difference",   recall_difference)]:
        if difference_value > 0.10:
            severity_level = "HIGH"
        elif difference_value >= 0.05:
            severity_level = "MEDIUM"
        else:
            severity_level = "LOW"

        if severity_level in ("HIGH", "MEDIUM"):
            finding_description = (
                f"{metric_name.replace('_', ' ').title()} is "
                f"{difference_value * 100:.0f} percentage points. "
                f"Severity: {severity_level}."
            )
            findings_list.append({
                "severity":    severity_level,
                "attribute":   attribute_name,
                "description": finding_description,
                "metric":      metric_name,
                "value":       float(round(difference_value, 4)),
            })

    bias_results = {
        "status": "success",
        "metrics": {
            "by_group": by_group_dict,
            "differences": {
                "accuracy_difference": float(round(accuracy_difference, 4)),
                "recall_difference":   float(round(recall_difference, 4)),
            },
        },
        "findings": findings_list,
    }

    return bias_results
