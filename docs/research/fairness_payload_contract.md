# Fairness Payload Contract

This document defines the JSON payload that the ML layer (Person 3) must produce for every fairness audit. It is the single input to the AI reporting module (`backend/app/ai_reports/generator.py`). Keeping this contract stable is what lets report generation, BigQuery persistence, and the frontend evolve independently.

## Why this exists

The report generator never runs metrics itself. It consumes a fixed, validated payload and turns it into a structured, human-readable fairness report. If the payload is inconsistent across runs, the report generator, the validator, and the BigQuery schema all break at the same time. One contract, written once, avoids that.

## Top-level shape

Every audit run produces a single JSON object with the fields below. Fields marked optional may be omitted or set to `null`, but if a field is present it must conform to the type shown.

```json
{
  "audit_id": "aud_2026_04_17_001",
  "created_at": "2026-04-17T10:32:00Z",
  "project_id": "proj_acme_lending",
  "user_id": "user_abc",
  "dataset": {
    "name": "ACSIncome",
    "source": "folktables",
    "n_rows": 42000,
    "n_features": 11,
    "task_type": "tabular_classification",
    "target_column": "income_gt_50k",
    "positive_label": 1,
    "notes": "State filter: CA. Year: 2023."
  },
  "model": {
    "name": "logistic_regression_v1",
    "family": "linear",
    "framework": "scikit-learn",
    "hyperparameters": {"C": 1.0, "penalty": "l2"},
    "version": "1.0.0"
  },
  "protected_attributes": [
    {"name": "SEX", "type": "binary", "groups": ["Male", "Female"], "reference_group": "Male"},
    {"name": "RAC1P", "type": "categorical", "groups": ["White", "Black", "Asian", "Other"], "reference_group": "White"}
  ],
  "overall_performance": {
    "accuracy": 0.82,
    "precision": 0.78,
    "recall": 0.71,
    "f1": 0.745,
    "auc_roc": 0.87
  },
  "metrics_before_mitigation": {
    "per_attribute": [
      {
        "attribute": "SEX",
        "per_group": [
          {
            "group": "Male",
            "positive_prediction_rate": 0.48,
            "true_positive_rate": 0.81,
            "false_positive_rate": 0.19,
            "accuracy": 0.84,
            "support": 22000
          },
          {
            "group": "Female",
            "positive_prediction_rate": 0.27,
            "true_positive_rate": 0.62,
            "false_positive_rate": 0.14,
            "accuracy": 0.80,
            "support": 20000
          }
        ],
        "disparities": {
          "demographic_parity_difference": 0.21,
          "equal_opportunity_difference": 0.19,
          "equalized_odds_difference": 0.19,
          "disparate_impact_ratio": 0.56
        }
      }
    ],
    "intersectional": [
      {
        "attributes": ["SEX", "RAC1P"],
        "per_group": [
          {"group": "Female_Black", "positive_prediction_rate": 0.18, "support": 1800},
          {"group": "Male_White", "positive_prediction_rate": 0.52, "support": 12000}
        ],
        "worst_disparity": 0.34
      }
    ]
  },
  "metrics_after_mitigation": {
    "mitigation_method": "reweighing",
    "per_attribute": [
      {
        "attribute": "SEX",
        "per_group": [
          {"group": "Male", "positive_prediction_rate": 0.44, "true_positive_rate": 0.78, "false_positive_rate": 0.18, "accuracy": 0.82, "support": 22000},
          {"group": "Female", "positive_prediction_rate": 0.39, "true_positive_rate": 0.73, "false_positive_rate": 0.17, "accuracy": 0.81, "support": 20000}
        ],
        "disparities": {
          "demographic_parity_difference": 0.05,
          "equal_opportunity_difference": 0.05,
          "equalized_odds_difference": 0.06,
          "disparate_impact_ratio": 0.89
        }
      }
    ],
    "utility_cost": {
      "accuracy_delta": -0.015,
      "f1_delta": -0.01
    }
  },
  "counterfactuals": {
    "attribute_flipped": "SEX",
    "n_samples_tested": 500,
    "n_predictions_changed": 74,
    "proportion_changed": 0.148,
    "examples": [
      {
        "record_id": "row_1024",
        "features_summary": "age=34, education=BA, years_experience=8",
        "original_group": "Female",
        "flipped_group": "Male",
        "original_prediction": 0,
        "flipped_prediction": 1
      }
    ]
  },
  "nlp_benchmarks": {
    "bharatbbq": {"overall_score": 0.71, "per_language": {"hi": 0.68, "ta": 0.74, "en": 0.80}},
    "crows_pairs": {"stereotype_score": 0.58},
    "bbq": {"ambig_bias": 0.12, "disambig_bias": 0.03}
  },
  "data_quality_flags": [
    {"flag": "subgroup_underrepresentation", "attribute": "RAC1P", "group": "Asian", "severity": "medium"},
    {"flag": "positive_label_imbalance", "attribute": "SEX", "severity": "high"}
  ],
  "notes": "Baseline run against 2023 ACSIncome California sample; reweighing applied via Fairlearn."
}
```

## Field conventions

**Identity block** — `audit_id`, `created_at`, `project_id`, `user_id`. The `audit_id` must be globally unique. BigQuery is partitioned on `created_at`, so ISO-8601 UTC timestamps are mandatory.

**Dataset block** — captures what was audited. `task_type` is one of `tabular_classification`, `tabular_regression`, `text_classification`, or `multimodal`. If the task is NLP-only (a pure benchmark run), `target_column` and `positive_label` may be null.

**Model block** — captures what produced the predictions. `framework` is free-text but should be lowercase (`scikit-learn`, `xgboost`, `pytorch`, `gemini`).

**Protected attributes** — a list, not a single field, because real audits run on several at once. Each entry names a reference group, which the fairness metrics are computed against.

**Metrics** — split into `metrics_before_mitigation` and `metrics_after_mitigation`. If no mitigation was run, `metrics_after_mitigation` is null. Both sections share the same internal shape so the report generator can diff them without special-casing.

**Disparity metrics** — standardized names aligned with Fairlearn and the Vertex AI fairness docs: `demographic_parity_difference`, `equal_opportunity_difference`, `equalized_odds_difference`, `disparate_impact_ratio`. No renaming, no aliasing.

**NLP benchmarks** — optional, populated only for models that also produce text. The BharatBBQ per-language block is what lets us cite Indian-language fairness in the pitch.

**Data quality flags** — structured, not free-form. Each flag has a `flag` name from a fixed vocabulary (`subgroup_underrepresentation`, `positive_label_imbalance`, `missingness_by_group`, `proxy_correlation`), an `attribute`, an optional `group`, and a severity of `low`, `medium`, or `high`.

## What the ML layer must NOT do

- Do not write narrative strings. Keep all fields numeric or structural. Narrative is Gemini's job.
- Do not drop fields silently. If a metric could not be computed, set it to `null` rather than omitting the key.
- Do not combine before and after mitigation into one table. They must remain separate objects.
- Do not use different key names across datasets. The same metric keys apply to ACSIncome, Adult, South German Credit, and every NLP benchmark.

## What the AI reporting layer can be counted on to do

- Validate this payload strictly before calling Gemini.
- Return a clear error if required fields are missing.
- Never invent metrics. If a metric is null, it is acknowledged as unmeasured, not fabricated.
- Persist the full payload into BigQuery audit history, so the team can requery or rerun any audit later.

## Change policy

This contract is versioned. If a field needs to change, bump the document header version and update `backend/app/ai_reports/schemas.py` and the BigQuery schema in the same PR. No silent renames.

Current contract version: **1.0.0**
