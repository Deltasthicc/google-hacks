"""
Quick test script — runs each ml/src module in sequence to verify imports
and basic functionality for any dataset defined in ml/configs/.
"""

import json
import yaml
import os
import pandas as pd

# =============================================================
# CHANGE THIS LINE TO SWITCH DATASETS
# =============================================================
CONFIG_NAME = "acs_income.yaml"  # Try "acs_income.yaml" or "adult.yaml"
# =============================================================

# Load config
config_path = os.path.join("ml", "configs", CONFIG_NAME)
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

target_col = config.get("target_column")
sensitive_cols = config.get("protected_attributes")
dataset_name = config.get("dataset_name")

print(f"Running modular tests for dataset: {dataset_name}")
print(f"Target: {target_col}, Sensitive: {sensitive_cols}")

print("\n" + "=" * 60)
print("TEST 1: data_loader")
print("=" * 60)
from ml.src.data_loader import load_adult_dataset, load_openml_dataset
if config.get("openml_id"):
    raw_df = load_openml_dataset(config["openml_id"])
else:
    raw_df = load_adult_dataset()
print(f"  PASSED: loaded {raw_df.shape}")
print()

print("=" * 60)
print("TEST 2: preprocessing")
print("=" * 60)
from ml.src.preprocessing import preprocess
prep = preprocess(raw_df, target_col=target_col, sensitive_cols=sensitive_cols)
if prep['status'] == 'error':
    print(f"  FAILED: {prep['message']}")
    exit(1)
print(f"  Status: {prep['status']}")
print(f"  Train: {prep['features_train'].shape}")
print(f"  Test:  {prep['features_test'].shape}")
print(f"  PASSED")
print()

print("=" * 60)
print("TEST 3: train + evaluate")
print("=" * 60)
from ml.src.train import train_model, evaluate_model
model = train_model(prep["features_train"], prep["income_labels_train"])
predictions = model.predict(prep["features_test"])
metrics = evaluate_model(predictions, prep["income_labels_test"])
print(f"  Accuracy:  {metrics['accuracy']:.4f}")
print(f"  Precision: {metrics['precision']:.4f}")
print(f"  Recall:    {metrics['recall']:.4f}")
print(f"  F1:        {metrics['f1']:.4f}")
print(f"  PASSED")
print()

print("=" * 60)
print("TEST 4: evaluate (bias detection)")
print("=" * 60)
from ml.src.evaluate import detect_bias
bias = detect_bias(predictions, prep["income_labels_test"], prep["sensitive_test"])
print(f"  Status: {bias['status']}")
print(f"  By group: {json.dumps(bias['metrics']['by_group'], indent=4)}")
print(f"  Findings: {len(bias['findings'])} issue(s)")
for f in bias["findings"]:
    print(f"    [{f['severity']}] {f['description']}")
print(f"  PASSED")
print()

print("=" * 60)
print("TEST 5: mitigation")
print("=" * 60)
from ml.src.mitigation import apply_mitigation
mit = apply_mitigation(
    model,
    prep["features_train"], prep["income_labels_train"], prep["sensitive_train"],
    prep["features_test"], prep["income_labels_test"], prep["sensitive_test"],
)
print(f"  Status: {mit['status']}")
print(f"  Before recall diff: {mit['before']['bias_detection']['metrics']['differences']['recall_difference']:.4f}")
print(f"  After recall diff:  {mit['after']['bias_detection']['metrics']['differences']['recall_difference']:.4f}")
print(f"  Improvement: {mit['improvement']['summary']}")
print(f"  PASSED")
print()

print("=" * 60)
print("TEST 6: counterfactuals")
print("=" * 60)
from ml.src.counterfactuals import run_counterfactual_check
cf = run_counterfactual_check(model, prep["features_test"], prep["sensitive_test"])
print(f"  Status: {cf['status']}")
print(f"  Flip rate:  {cf['flip_rate']:.2%}")
print(f"  Severity:   {cf['severity']}")
print(f"  PASSED")
print()

print("=" * 60)
print(f"ALL 6 TESTS PASSED FOR {dataset_name.upper()}")
print("=" * 60)
