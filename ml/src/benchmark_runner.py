"""
Benchmark runner for FairLens AI / NyayaLens.

Runs the full pipeline (load -> preprocess -> train -> evaluate -> detect bias
-> mitigate) on a given dataset config and saves structured JSON results
to ml/outputs/reports/.
"""

import json
import os
import yaml

try:
    from ml.src.data_loader import load_adult_dataset, load_csv_dataset
    from ml.src.preprocessing import preprocess
    from ml.src.train import train_model, evaluate_model
    from ml.src.evaluate import detect_bias
    from ml.src.mitigation import apply_mitigation
except ModuleNotFoundError:
    from src.data_loader import load_adult_dataset, load_csv_dataset
    from src.preprocessing import preprocess
    from src.train import train_model, evaluate_model
    from src.evaluate import detect_bias
    from src.mitigation import apply_mitigation


def run_pipeline(config_path=None, csv_path=None, df=None, target_col="class",
                 sensitive_cols=None):
    """
    Execute the full fairness audit pipeline and return a results dict.

    Can be driven by a YAML config file, a CSV path, or a direct DataFrame.

    Args:
        config_path:     Path to a YAML config in ml/configs/ (optional).
        csv_path:        Direct path to a CSV file (optional).
        df:              Direct pandas DataFrame (optional).
        target_col:      Name of the target column.
        sensitive_cols:  List of sensitive attribute column names.

    Returns:
        result: Dict with full before/after bias audit results,
                or a dict with status='error'.
    """
    if sensitive_cols is None:
        sensitive_cols = ["sex"]

    # --- Load config if provided ---
    if config_path is not None:
        with open(config_path, "r") as config_file:
            config = yaml.safe_load(config_file)
        dataset_name = config.get("dataset_name", "Unknown")
        if config.get("target_column"):
            target_col = config["target_column"]
        if config.get("protected_attributes"):
            sensitive_cols = config["protected_attributes"]
    else:
        config = {}
        dataset_name = "Custom Dataset"

    # --- Load data ---
    if df is not None:
        raw_df = df
    elif csv_path is not None:
        raw_df = load_csv_dataset(csv_path)
    elif config.get("openml_id"):
        from ml.src.data_loader import load_openml_dataset
        raw_df = load_openml_dataset(config["openml_id"])
    elif dataset_name == "Adult":
        raw_df = load_adult_dataset()
    else:
        return {"status": "error", "message": "No data source or openml_id provided."}
    # --- Preprocess ---
    prep_result = preprocess(raw_df, target_col=target_col,
                             sensitive_cols=sensitive_cols)
    if prep_result["status"] == "error":
        return prep_result

    features_train = prep_result["features_train"]
    features_test = prep_result["features_test"]
    labels_train = prep_result["income_labels_train"]
    labels_test = prep_result["income_labels_test"]
    sensitive_train = prep_result["sensitive_train"]
    sensitive_test = prep_result["sensitive_test"]

    # --- Train baseline ---
    model = train_model(features_train, labels_train)

    # --- Full mitigation pipeline (includes before/after) ---
    mitigation_result = apply_mitigation(
        model,
        features_train, labels_train, sensitive_train,
        features_test, labels_test, sensitive_test,
        attribute_name=sensitive_cols[0],
    )

    # --- Wrap final output ---
    final_result = {
        "status": "success",
        "dataset": dataset_name,
        "sensitive_columns": sensitive_cols,
        "target_column": target_col,
    }
    final_result.update(mitigation_result)

    return final_result


def save_report(result, output_path):
    """
    Save pipeline results to a JSON file.

    Args:
        result:      Dict from run_pipeline().
        output_path: File path for the JSON output.
    """
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    result = run_pipeline()
    save_report(result, "ml/outputs/reports/adult_audit.json")
    print(json.dumps(result, indent=2))
