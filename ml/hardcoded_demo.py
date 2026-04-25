"""
FairLens AI — Phase 1: Hardcoded Standalone Demo
=================================================
This script runs the entire bias detection and mitigation pipeline
end-to-end using the UCI Adult dataset. No dependencies on other
team members' code. Hardcoded dataset path and sensitive column.

Mitigation: Fairlearn ThresholdOptimizer (equalized_odds constraint)
replaces AIF360 Reweighing for better recall gap reduction.

Run with:  python ml/hardcoded_demo.py
"""

import json
import os

import numpy as np
import pandas as pd
from sklearn.datasets import fetch_openml
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Fairlearn: MetricFrame for per-group bias measurement,
# ThresholdOptimizer for post-processing fairness mitigation.
from fairlearn.metrics import MetricFrame
from fairlearn.postprocessing import ThresholdOptimizer


# ─────────────────────────────────────────────────────────────────────
# STEP 1: Load the UCI Adult dataset
# ─────────────────────────────────────────────────────────────────────

def load_adult_dataset():
    """
    Download the UCI Adult (Census Income) dataset from OpenML.

    Returns:
        raw_dataframe: pandas DataFrame with all columns including target.
    """
    print("=" * 60)
    print("STEP 1: Loading UCI Adult dataset from OpenML...")
    print("=" * 60)

    adult_bunch = fetch_openml("adult", version=2, as_frame=True)
    raw_dataframe = adult_bunch.frame

    print(f"  Loaded {raw_dataframe.shape[0]} rows, {raw_dataframe.shape[1]} columns")
    print(f"  Columns: {list(raw_dataframe.columns)}")
    print()

    return raw_dataframe


# ─────────────────────────────────────────────────────────────────────
# STEP 2: Preprocess the data
# ─────────────────────────────────────────────────────────────────────

def preprocess_data(raw_dataframe):
    """
    Clean, encode, and split the Adult dataset for training.

    Steps:
        - Drop rows with '?' or NaN
        - Encode target: '>50K' -> 1, '<=50K' -> 0
        - Separate the sensitive column ('sex')
        - Drop 'sex', 'race', 'fnlwgt' from features
        - One-hot encode remaining categorical columns
        - Split into train/test (80/20)
        - StandardScale numerical features

    Args:
        raw_dataframe: pandas DataFrame from load_adult_dataset().

    Returns:
        features_train, features_test,
        income_labels_train, income_labels_test,
        gender_sensitive_train, gender_sensitive_test
    """
    print("=" * 60)
    print("STEP 2: Preprocessing data...")
    print("=" * 60)

    cleaned_dataframe = raw_dataframe.copy()

    for column_name in cleaned_dataframe.columns:
        if cleaned_dataframe[column_name].dtype == object:
            has_question_mark = cleaned_dataframe[column_name] == "?"
            cleaned_dataframe = cleaned_dataframe[~has_question_mark]

    cleaned_dataframe = cleaned_dataframe.dropna()
    print(f"  After dropping missing values: {cleaned_dataframe.shape[0]} rows remain")

    target_column_name = "class"
    income_labels = cleaned_dataframe[target_column_name].apply(
        lambda value: 1 if ">50K" in str(value) else 0
    )
    print(f"  Target distribution: {income_labels.value_counts().to_dict()}")

    gender_sensitive_column = cleaned_dataframe["sex"].copy()
    print(f"  Sensitive column 'sex' distribution: {gender_sensitive_column.value_counts().to_dict()}")

    columns_to_drop = ["sex", "race", "fnlwgt", target_column_name]
    feature_dataframe = cleaned_dataframe.drop(columns=columns_to_drop)

    feature_dataframe = pd.get_dummies(feature_dataframe, drop_first=True)
    print(f"  Feature matrix shape after encoding: {feature_dataframe.shape}")

    features_train, features_test, income_labels_train, income_labels_test = train_test_split(
        feature_dataframe,
        income_labels,
        test_size=0.2,
        random_state=42
    )

    feature_scaler = StandardScaler()
    scaled_train_array = feature_scaler.fit_transform(features_train)
    scaled_test_array = feature_scaler.transform(features_test)

    features_train = pd.DataFrame(
        scaled_train_array,
        columns=features_train.columns,
        index=features_train.index,
    )
    features_test = pd.DataFrame(
        scaled_test_array,
        columns=features_test.columns,
        index=features_test.index,
    )

    gender_sensitive_train = gender_sensitive_column.loc[features_train.index]
    gender_sensitive_test = gender_sensitive_column.loc[features_test.index]

    print(f"  X_train shape: {features_train.shape}")
    print(f"  X_test shape:  {features_test.shape}")
    print()

    return (
        features_train, features_test,
        income_labels_train, income_labels_test,
        gender_sensitive_train, gender_sensitive_test
    )


# ─────────────────────────────────────────────────────────────────────
# STEP 3: Train a Logistic Regression model
# ─────────────────────────────────────────────────────────────────────

def train_logistic_regression(features_train, income_labels_train):
    """
    Train a Logistic Regression classifier on the training data.

    Args:
        features_train:       Training features (pandas DataFrame).
        income_labels_train:  Training target labels, 0 or 1 (pandas Series).

    Returns:
        trained_model: Fitted LogisticRegression model object.
    """
    trained_model = LogisticRegression(max_iter=5000, random_state=42)
    trained_model.fit(features_train, income_labels_train)
    return trained_model


def evaluate_model(predictions, income_labels_test):
    """
    Compute accuracy, precision, recall, and F1 for a set of predictions.

    Args:
        predictions:         Array of predicted labels (0 or 1).
        income_labels_test:  True test labels, 0 or 1 (pandas Series).

    Returns:
        metrics_dict: Dictionary with keys 'accuracy', 'precision', 'recall', 'f1'.
    """
    metrics_dict = {
        "accuracy":  float(accuracy_score(income_labels_test, predictions)),
        "precision": float(precision_score(income_labels_test, predictions)),
        "recall":    float(recall_score(income_labels_test, predictions)),
        "f1":        float(f1_score(income_labels_test, predictions)),
    }
    return metrics_dict


# ─────────────────────────────────────────────────────────────────────
# STEP 4: Compute bias metrics using Fairlearn
# ─────────────────────────────────────────────────────────────────────

def compute_bias_metrics(income_labels_test, approval_predictions, gender_sensitive_test):
    """
    Measure how model performance differs across gender groups using Fairlearn.

    Args:
        income_labels_test:     True labels (pandas Series).
        approval_predictions:   Model predictions (numpy array).
        gender_sensitive_test:  Sensitive attribute values for test set (pandas Series).

    Returns:
        bias_results: Dictionary containing per-group metrics, differences,
                      and severity findings.
    """
    fairness_metrics_frame = MetricFrame(
        metrics={
            "accuracy": accuracy_score,
            "recall":   recall_score,
        },
        y_true=income_labels_test,
        y_pred=approval_predictions,
        sensitive_features=gender_sensitive_test,
    )

    per_group_table = fairness_metrics_frame.by_group
    print("  Per-group metrics:")
    print(per_group_table.to_string())
    print()

    metric_differences = fairness_metrics_frame.difference()
    print("  Metric differences (max gap between groups):")
    print(f"    Accuracy difference:  {metric_differences['accuracy']:.4f}")
    print(f"    Recall difference:    {metric_differences['recall']:.4f}")

    by_group_dict = {}
    for group_name in per_group_table.index:
        by_group_dict[str(group_name)] = {
            "accuracy": float(per_group_table.loc[group_name, "accuracy"]),
            "recall":   float(per_group_table.loc[group_name, "recall"]),
        }

    accuracy_difference = float(metric_differences["accuracy"])
    recall_difference   = float(metric_differences["recall"])

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
                "attribute":   "sex",
                "description": finding_description,
                "metric":      metric_name,
                "value":       float(round(difference_value, 4)),
            })

    any_high_risk = any(f["severity"] == "HIGH" for f in findings_list)
    if any_high_risk:
        print("  [WARNING] HIGH RISK: Significant bias detected!")
    print()

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


# ─────────────────────────────────────────────────────────────────────
# STEP 5: Apply mitigation using Fairlearn ThresholdOptimizer
# ─────────────────────────────────────────────────────────────────────

def apply_threshold_optimizer_mitigation(
    baseline_model,
    features_train, income_labels_train, gender_sensitive_train,
    features_test, gender_sensitive_test
):
    """
    Use Fairlearn's ThresholdOptimizer to produce fair predictions.

    ThresholdOptimizer is a post-processing method: it takes an already-trained
    classifier and finds group-specific decision thresholds that satisfy a
    fairness constraint (equalized_odds) while maximising balanced accuracy.

    Why this works better than Reweighing on Adult:
        Reweighing adjusts training sample weights, but Logistic Regression
        on a heavily imbalanced feature space often absorbs those weights
        without changing decision boundaries enough. ThresholdOptimizer acts
        *after* training and directly controls per-group thresholds, giving
        it a more direct lever on the recall gap.

    Args:
        baseline_model:           Fitted LogisticRegression (sklearn estimator).
        features_train:           Training features (pandas DataFrame).
        income_labels_train:      Training target labels (pandas Series).
        gender_sensitive_train:   Sensitive column for training set (pandas Series).
        features_test:            Test features (pandas DataFrame).
        gender_sensitive_test:    Sensitive column for test set (pandas Series).

    Returns:
        mitigated_predictions: numpy array of fair predictions on the test set.
        mitigated_predictor:   Fitted ThresholdOptimizer object (for inspection).
    """
    # ThresholdOptimizer wraps any sklearn-compatible classifier.
    # constraints="equalized_odds" requires equal TPR AND FPR across groups.
    # objective="balanced_accuracy_score" maximises balanced accuracy
    #   (average of recall per class), which handles class imbalance better
    #   than plain accuracy.
    # predict_method="predict_proba" uses probability scores internally so
    #   the optimizer can sweep thresholds smoothly.
    mitigated_predictor = ThresholdOptimizer(
        estimator=baseline_model,
        constraints="equalized_odds",
        objective="balanced_accuracy_score",
        predict_method="predict_proba",
    )

    # .fit() learns the per-group thresholds from training data
    mitigated_predictor.fit(
        features_train,
        income_labels_train,
        sensitive_features=gender_sensitive_train,
    )

    # .predict() applies the learned thresholds to produce fair predictions
    mitigated_predictions = mitigated_predictor.predict(
        features_test,
        sensitive_features=gender_sensitive_test,
    )

    print("  ThresholdOptimizer mitigation complete.")
    print(f"  Unique prediction values: {np.unique(mitigated_predictions)}")
    print()

    return mitigated_predictions, mitigated_predictor


# ─────────────────────────────────────────────────────────────────────
# STEP 6 & 7: Print comparison table and save results
# ─────────────────────────────────────────────────────────────────────

def print_comparison_table(before_metrics, after_metrics, before_bias, after_bias):
    """
    Print a side-by-side before/after comparison of model performance and fairness.
    """
    print("=" * 60)
    print("COMPARISON: Before vs After Mitigation")
    print("=" * 60)

    before_by_group = before_bias["metrics"]["by_group"]
    after_by_group  = after_bias["metrics"]["by_group"]
    group_names     = list(before_by_group.keys())

    header = f"{'Metric':<25} {'Before':>10} {'After':>10}"
    print(header)
    print("-" * 47)

    print(f"{'Accuracy':<25} {before_metrics['accuracy']:>10.4f} {after_metrics['accuracy']:>10.4f}")
    print(f"{'Precision':<25} {before_metrics['precision']:>10.4f} {after_metrics['precision']:>10.4f}")
    print(f"{'Recall':<25} {before_metrics['recall']:>10.4f} {after_metrics['recall']:>10.4f}")
    print(f"{'F1':<25} {before_metrics['f1']:>10.4f} {after_metrics['f1']:>10.4f}")
    print()

    for group_name in group_names:
        before_recall = before_by_group[group_name]["recall"]
        after_recall  = after_by_group[group_name]["recall"]
        label = f"Recall ({group_name})"
        print(f"{label:<25} {before_recall:>10.4f} {after_recall:>10.4f}")

    before_recall_diff = before_bias["metrics"]["differences"]["recall_difference"]
    after_recall_diff  = after_bias["metrics"]["differences"]["recall_difference"]
    print(f"{'Recall Difference':<25} {before_recall_diff:>10.4f} {after_recall_diff:>10.4f}")
    print()


def save_results_to_json(
    before_metrics, after_metrics, before_bias, after_bias, output_path
):
    """
    Save the full before/after results to a JSON file.
    """
    accuracy_change    = float(after_metrics["accuracy"] - before_metrics["accuracy"])
    before_recall_diff = float(before_bias["metrics"]["differences"]["recall_difference"])
    after_recall_diff  = float(after_bias["metrics"]["differences"]["recall_difference"])
    recall_diff_change = float(after_recall_diff - before_recall_diff)

    improvement_summary = (
        f"Recall gap reduced from {before_recall_diff:.2f} to {after_recall_diff:.2f} "
        f"(change: {recall_diff_change:+.2f}). "
        f"Accuracy change: {accuracy_change:+.4f}."
    )

    if recall_diff_change < 0:
        improvement_summary += " Mitigation recommended."
    else:
        improvement_summary += " Mitigation did not improve fairness."

    final_output = {
        "status": "success",
        "dataset": "UCI Adult (Census Income)",
        "sensitive_column": "sex",
        "target_column": "income (class)",
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

    output_directory = os.path.dirname(output_path)
    if output_directory and not os.path.exists(output_directory):
        os.makedirs(output_directory, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(final_output, json_file, indent=2)

    print(f"Results saved to: {output_path}")
    return final_output


# ─────────────────────────────────────────────────────────────────────
# MAIN — Run the full pipeline
# ─────────────────────────────────────────────────────────────────────

def main():
    """
    Execute the complete FairLens AI bias detection and mitigation pipeline.

    Sequence:
        1. Load dataset
        2. Preprocess
        3. Train baseline model & evaluate
        4. Detect bias in baseline model
        5. Apply ThresholdOptimizer mitigation
        6. Detect bias in mitigated predictions
        7. Print comparison & save results
    """

    # ── STEP 1: Load ─────────────────────────────────────────────────
    raw_dataframe = load_adult_dataset()

    # ── STEP 2: Preprocess ───────────────────────────────────────────
    (
        features_train, features_test,
        income_labels_train, income_labels_test,
        gender_sensitive_train, gender_sensitive_test,
    ) = preprocess_data(raw_dataframe)

    # ── STEP 3: Train baseline model ─────────────────────────────────
    print("=" * 60)
    print("STEP 3: Training baseline Logistic Regression...")
    print("=" * 60)

    baseline_model = train_logistic_regression(features_train, income_labels_train)
    baseline_predictions = baseline_model.predict(features_test)
    baseline_metrics = evaluate_model(baseline_predictions, income_labels_test)

    print(f"  Accuracy:  {baseline_metrics['accuracy']:.4f}")
    print(f"  Precision: {baseline_metrics['precision']:.4f}")
    print(f"  Recall:    {baseline_metrics['recall']:.4f}")
    print(f"  F1:        {baseline_metrics['f1']:.4f}")
    print()

    # ── STEP 4: Detect bias in baseline ──────────────────────────────
    print("=" * 60)
    print("STEP 4: Detecting bias in baseline model (Fairlearn)...")
    print("=" * 60)

    baseline_bias_results = compute_bias_metrics(
        income_labels_test, baseline_predictions, gender_sensitive_test
    )

    # ── STEP 5: Apply ThresholdOptimizer mitigation ──────────────────
    print("=" * 60)
    print("STEP 5: Applying Fairlearn ThresholdOptimizer mitigation...")
    print("=" * 60)

    mitigated_predictions, _ = apply_threshold_optimizer_mitigation(
        baseline_model,
        features_train, income_labels_train, gender_sensitive_train,
        features_test, gender_sensitive_test,
    )

    mitigated_metrics = evaluate_model(mitigated_predictions, income_labels_test)

    print(f"  Mitigated Accuracy:  {mitigated_metrics['accuracy']:.4f}")
    print(f"  Mitigated Precision: {mitigated_metrics['precision']:.4f}")
    print(f"  Mitigated Recall:    {mitigated_metrics['recall']:.4f}")
    print(f"  Mitigated F1:        {mitigated_metrics['f1']:.4f}")
    print()

    # ── STEP 6: Detect bias in mitigated model ───────────────────────
    print("=" * 60)
    print("STEP 6: Detecting bias in mitigated model...")
    print("=" * 60)

    mitigated_bias_results = compute_bias_metrics(
        income_labels_test, mitigated_predictions, gender_sensitive_test
    )

    # ── STEP 7: Compare and save ─────────────────────────────────────
    print_comparison_table(
        baseline_metrics, mitigated_metrics,
        baseline_bias_results, mitigated_bias_results,
    )

    output_file_path = os.path.join("ml", "demo_output.json")
    final_results = save_results_to_json(
        baseline_metrics, mitigated_metrics,
        baseline_bias_results, mitigated_bias_results,
        output_file_path,
    )

    print()
    print("=" * 60)
    print("[OK] Phase 1 complete! Pipeline ran successfully.")
    print("=" * 60)
    print()
    print("Full JSON output:")
    print(json.dumps(final_results, indent=2))


if __name__ == "__main__":
    main()