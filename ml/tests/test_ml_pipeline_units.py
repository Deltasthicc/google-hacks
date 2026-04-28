from __future__ import annotations

from pathlib import Path

import pandas as pd

from ml.src.benchmark_runner import run_pipeline
from ml.src.counterfactuals import run_counterfactual_check
from ml.src.evaluate import detect_bias
from ml.src.preprocessing import preprocess
from ml.src.train import evaluate_model


class ConstantModel:
    def predict(self, features):
        return [1 for _ in range(len(features))]


def test_preprocess_rejects_missing_target_column():
    df = pd.DataFrame({"feature": [1, 2], "sex": ["F", "M"]})

    result = preprocess(df, target_col="income", sensitive_cols=["sex"])

    assert result["status"] == "error"
    assert "Column 'income' not found" in result["message"]


def test_evaluate_model_returns_json_safe_metrics():
    metrics = evaluate_model([0, 1, 1, 1], pd.Series([0, 1, 0, 1]))

    assert set(metrics) == {"accuracy", "precision", "recall", "f1"}
    assert all(isinstance(value, float) for value in metrics.values())
    assert metrics["accuracy"] == 0.75


def test_detect_bias_reports_group_metrics():
    result = detect_bias(
        predictions=[0, 1, 1, 1],
        income_labels_test=pd.Series([0, 1, 0, 1]),
        sensitive_test=pd.Series(["F", "F", "M", "M"]),
        attribute_name="sex",
    )

    assert result["status"] == "success"
    assert set(result["metrics"]["by_group"]) == {"F", "M"}
    assert "recall_difference" in result["metrics"]["differences"]


def test_counterfactual_check_returns_low_severity_for_constant_model():
    features = pd.DataFrame(
        {
            "relationship_Husband": [1, -1, 1, -1],
            "relationship_Wife": [-1, 1, -1, 1],
            "age": [0.1, -0.2, 0.3, -0.4],
        }
    )

    result = run_counterfactual_check(
        ConstantModel(),
        features,
        pd.Series(["M", "F", "M", "F"]),
    )

    assert result["status"] == "success"
    assert result["flip_rate"] == 0.0
    assert result["severity"] == "LOW"
    assert result["proxy_columns_used"] == ["relationship_Husband", "relationship_Wife"]


def test_demo_lending_mini_yaml_pipeline_runs_offline():
    """Bundled CSV demo needs no OpenML download (stable CI)."""
    repo_root = Path(__file__).resolve().parents[2]
    cfg = repo_root / "ml" / "configs" / "demo_lending_mini.yaml"
    result = run_pipeline(config_path=str(cfg))

    assert result["status"] == "success"
    assert result["dataset"] == "Demo Lending Mini"


def test_demo_hiring_mini_yaml_pipeline_runs_offline():
    repo_root = Path(__file__).resolve().parents[2]
    cfg = repo_root / "ml" / "configs" / "demo_hiring_mini.yaml"
    result = run_pipeline(config_path=str(cfg))

    assert result["status"] == "success"
    assert result["dataset"] == "Demo Hiring Mini"
