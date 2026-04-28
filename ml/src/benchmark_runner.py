"""
Benchmark runner for FairLens AI / NyayaLens.

Runs the full pipeline (load -> preprocess -> train -> evaluate -> detect bias
-> mitigate) on a given dataset config and saves structured JSON results
to ml/outputs/reports/.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

_ML_ROOT = Path(__file__).resolve().parent.parent

try:
    from ml.src.data_loader import load_adult_dataset, load_csv_dataset
    from ml.src.fairness_contract_export import build_fairness_audit_payload_dict
    from ml.src.preprocessing import preprocess
    from ml.src.train import train_model
    from ml.src.counterfactuals import run_counterfactual_check
    from ml.src.mitigation import apply_mitigation
except ModuleNotFoundError:
    from src.data_loader import load_adult_dataset, load_csv_dataset
    from src.fairness_contract_export import build_fairness_audit_payload_dict
    from src.preprocessing import preprocess
    from src.train import train_model
    from src.counterfactuals import run_counterfactual_check
    from src.mitigation import apply_mitigation


def run_pipeline(
    config_path: str | None = None,
    csv_path: str | None = None,
    df: Any = None,
    target_col: str = "class",
    sensitive_cols: list[str] | None = None,
    audit_id: str | None = None,
    project_id: str | None = None,
    user_id: str | None = None,
    created_at: datetime | None = None,
) -> dict[str, Any]:
    """
    Execute the full fairness audit pipeline and return a results dict.

    When no config, CSV, or DataFrame is given, defaults to ``ml/configs/adult.yaml``.

    If ``audit_id`` and ``created_at`` are set, attaches a validated
    ``fairness_audit_payload`` dict for the FastAPI reporting layer.
    """
    if sensitive_cols is None:
        sensitive_cols = ["sex"]

    if config_path is None and csv_path is None and df is None:
        config_path = str(_ML_ROOT / "configs" / "adult.yaml")

    if config_path is not None:
        with open(config_path, "r", encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)
        dataset_name = config.get("dataset_name", "Unknown")
        if config.get("target_column"):
            target_col = config["target_column"]
        if config.get("protected_attributes"):
            sensitive_cols = config["protected_attributes"]
    else:
        config = {}
        dataset_name = "Custom Dataset"

    if df is not None:
        raw_df = df
    elif csv_path is not None:
        loaded = load_csv_dataset(csv_path)
        if isinstance(loaded, dict):
            return loaded
        raw_df = loaded
    elif config.get("local_csv"):
        local_csv_path = _ML_ROOT / str(config["local_csv"])
        loaded = load_csv_dataset(str(local_csv_path))
        if isinstance(loaded, dict):
            return loaded
        raw_df = loaded
    elif config.get("openml_id"):
        try:
            from ml.src.data_loader import load_openml_dataset
        except ModuleNotFoundError:
            from src.data_loader import load_openml_dataset

        raw_df = load_openml_dataset(config["openml_id"])
    elif dataset_name == "Adult":
        raw_df = load_adult_dataset()
    else:
        return {
            "status": "error",
            "message": (
                f"No loader implemented for dataset '{dataset_name}'. "
                "Provide csv_path or use ml/configs/adult.yaml."
            ),
        }

    prep_result = preprocess(
        raw_df, target_col=target_col, sensitive_cols=sensitive_cols
    )
    if prep_result["status"] == "error":
        return prep_result

    features_train = prep_result["features_train"]
    features_test = prep_result["features_test"]
    labels_train = prep_result["income_labels_train"]
    labels_test = prep_result["income_labels_test"]
    sensitive_train = prep_result["sensitive_train"]
    sensitive_test = prep_result["sensitive_test"]

    model = train_model(features_train, labels_train)

    mitigation_result = apply_mitigation(
        model,
        features_train,
        labels_train,
        sensitive_train,
        features_test,
        labels_test,
        sensitive_test,
        attribute_name=sensitive_cols[0],
    )

    cf_result = run_counterfactual_check(model, features_test, sensitive_test)

    final_result: dict[str, Any] = {
        "status": "success",
        "dataset": dataset_name,
        "sensitive_columns": sensitive_cols,
        "target_column": target_col,
    }
    final_result.update(mitigation_result)
    final_result["counterfactual_check"] = cf_result

    dataset_meta = {
        "name": dataset_name,
        "source": "csv_upload" if csv_path is not None else "openml",
        "n_rows": int(len(raw_df)),
        "n_features": int(raw_df.shape[1]),
        "target_column": target_col,
        "model_name": config.get("model_name", "logistic_regression_baseline"),
    }

    if audit_id is not None and created_at is not None:
        dt = created_at
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        final_result["fairness_audit_payload"] = build_fairness_audit_payload_dict(
            audit_id=audit_id,
            created_at=dt,
            project_id=project_id,
            user_id=user_id,
            pipeline_result=final_result,
            dataset_meta=dataset_meta,
            counterfactual_result=cf_result,
        )

    return final_result


def save_report(result: dict[str, Any], output_path: str) -> None:
    """Save pipeline results to a JSON file."""
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)


if __name__ == "__main__":
    run_result = run_pipeline()
    save_report(run_result, "ml/outputs/reports/adult_audit.json")
    print(json.dumps(run_result, indent=2, default=str))
