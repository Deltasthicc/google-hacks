"""
Map ML pipeline outputs into the NyayaLens FairnessAuditPayload JSON shape.

Validated downstream with ``FairnessAuditPayload.model_validate`` in the backend.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd
from fairlearn.metrics import (
    demographic_parity_difference,
    equalized_odds_difference,
    equal_opportunity_difference,
)


def _iso_created_at(created_at: datetime) -> str:
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return created_at.isoformat().replace("+00:00", "Z")


def _disparate_impact_ratio(y_pred: np.ndarray, sensitive: np.ndarray) -> float:
    """Ratio min(selection_rate) / max(selection_rate) across groups."""
    df = pd.DataFrame({"p": y_pred.astype(float), "s": sensitive.astype(str)})
    rates = df.groupby("s", observed=True)["p"].mean()
    if rates.empty:
        return 1.0
    mx = float(rates.max())
    mn = float(rates.min())
    if mx <= 0:
        return 1.0
    return float(mn / mx)


def _per_attribute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive: np.ndarray,
    attribute_name: str,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for group in sorted(pd.Series(sensitive).astype(str).unique()):
        mask = sensitive.astype(str) == group
        yt = y_true[mask].astype(int)
        yp = y_pred[mask].astype(int)
        tp = int(((yt == 1) & (yp == 1)).sum())
        fp = int(((yt == 0) & (yp == 1)).sum())
        pos_n = int((yt == 1).sum())
        neg_n = int((yt == 0).sum())
        tpr = float(tp / pos_n) if pos_n else 0.0
        fpr = float(fp / neg_n) if neg_n else 0.0
        ppr = float(np.mean(yp)) if len(yp) else 0.0
        acc = float(np.mean(yt == yp)) if len(yt) else 0.0
        rows.append(
            {
                "group": group,
                "positive_prediction_rate": round(ppr, 6),
                "true_positive_rate": round(tpr, 6),
                "false_positive_rate": round(fpr, 6),
                "accuracy": round(acc, 6),
                "support": int(mask.sum()),
            }
        )

    dp = float(
        demographic_parity_difference(
            y_true, y_pred, sensitive_features=sensitive
        )
    )
    eod = float(
        equalized_odds_difference(y_true, y_pred, sensitive_features=sensitive)
    )
    eopp = float(
        equal_opportunity_difference(y_true, y_pred, sensitive_features=sensitive)
    )
    di = float(_disparate_impact_ratio(y_pred, sensitive))

    return {
        "attribute": attribute_name,
        "per_group": rows,
        "disparities": {
            "demographic_parity_difference": dp,
            "equal_opportunity_difference": eopp,
            "equalized_odds_difference": eod,
            "disparate_impact_ratio": di,
        },
    }


def build_fairness_audit_payload_dict(
    *,
    audit_id: str,
    created_at: datetime,
    project_id: str | None,
    user_id: str | None,
    pipeline_result: dict[str, Any],
    dataset_meta: dict[str, Any],
    counterfactual_result: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Build a dict matching ``FairnessAuditPayload`` from a successful pipeline_result.

    Expects pipeline_result to include mitigation keys plus ``_contract_arrays``.
    """
    arrays = pipeline_result.get("_contract_arrays") or {}
    y_true = np.asarray(arrays.get("y_true"), dtype=int)
    y_before = np.asarray(arrays.get("y_pred_before"), dtype=int)
    y_after = np.asarray(arrays.get("y_pred_after"), dtype=int)
    sensitive = np.asarray(arrays.get("sensitive"))
    attribute_name = str(arrays.get("attribute_name") or "sensitive_attribute")

    before_bias = pipeline_result["before"]["bias_detection"]
    after_bias = pipeline_result["after"]["bias_detection"]

    metrics_before = {
        "per_attribute": [
            _per_attribute_metrics(y_true, y_before, sensitive, attribute_name)
        ],
        "intersectional": None,
    }
    mitigation_method = pipeline_result.get(
        "mitigation_method",
        "Fairlearn ThresholdOptimizer (equalized_odds)",
    )
    bm = pipeline_result["before"]["model_metrics"]
    am = pipeline_result["after"]["model_metrics"]
    metrics_after = {
        "mitigation_method": mitigation_method,
        "per_attribute": [
            _per_attribute_metrics(y_true, y_after, sensitive, attribute_name)
        ],
        "intersectional": None,
        "utility_cost": {
            "accuracy_delta": float(am["accuracy"] - bm["accuracy"]),
            "f1_delta": float(am["f1"] - bm["f1"]),
        },
    }

    cf_block = None
    if counterfactual_result and counterfactual_result.get("status") == "success":
        flip_ct = int(counterfactual_result.get("flip_count", 0))
        flip_rt = float(counterfactual_result.get("flip_rate", 0.0))
        n_tested = len(y_true)
        cf_block = {
            "attribute_flipped": attribute_name,
            "n_samples_tested": n_tested,
            "n_predictions_changed": flip_ct,
            "proportion_changed": flip_rt,
            "examples": [],
        }

    dataset_name = dataset_meta.get("name", "tabular_classification_audit")
    n_rows = int(dataset_meta.get("n_rows", len(y_true)))
    notes_parts = [
        f"NyayaLens ML audit on {dataset_name}; mitigation={mitigation_method}.",
        (
            "Recall gap before="
            f"{before_bias['metrics']['differences'].get('recall_difference')}; "
            "after="
            f"{after_bias['metrics']['differences'].get('recall_difference')}."
        ),
    ]

    groups_sorted = sorted({str(g) for g in sensitive})

    payload: dict[str, Any] = {
        "audit_id": audit_id,
        "created_at": _iso_created_at(created_at),
        "project_id": project_id,
        "user_id": user_id,
        "dataset": {
            "name": dataset_name,
            "source": dataset_meta.get("source", "pipeline"),
            "n_rows": n_rows,
            "n_features": dataset_meta.get("n_features"),
            "task_type": "tabular_classification",
            "target_column": dataset_meta.get("target_column"),
            "positive_label": 1,
            "notes": "; ".join(notes_parts),
        },
        "model": {
            "name": dataset_meta.get("model_name", "logistic_regression_baseline"),
            "family": "linear",
            "framework": "scikit-learn",
            "hyperparameters": {"solver": "lbfgs"},
            "version": "1.0.0",
        },
        "protected_attributes": [
            {
                "name": attribute_name,
                "type": "categorical",
                "groups": groups_sorted,
                "reference_group": groups_sorted[0],
            }
        ],
        "overall_performance": {
            "accuracy": pipeline_result["before"]["model_metrics"]["accuracy"],
            "precision": pipeline_result["before"]["model_metrics"]["precision"],
            "recall": pipeline_result["before"]["model_metrics"]["recall"],
            "f1": pipeline_result["before"]["model_metrics"]["f1"],
            "auc_roc": None,
        },
        "metrics_before_mitigation": metrics_before,
        "metrics_after_mitigation": metrics_after,
        "counterfactuals": cf_block,
        "nlp_benchmarks": None,
        "data_quality_flags": [],
        "policy_document": None,
        "notes": "; ".join(notes_parts),
    }

    return payload
