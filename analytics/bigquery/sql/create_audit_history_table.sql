-- Create the fairness.audit_history table for NyayaLens.
--
-- Partitioning:
--   By DAY on created_at. Keeps scan cost low for dashboard queries that
--   look at the last 7/30/90 days. Required partition filter is NOT set,
--   because long-term trend queries legitimately scan the whole table.
--
-- Clustering:
--   By risk_level and dataset_name. Those are the two fields every dashboard
--   query filters or groups on.
--
-- Substitute ${project} and ${dataset} via your BigQuery client or the
-- bq CLI (`--parameter` or simple sed).

CREATE TABLE IF NOT EXISTS `${project}.${dataset}.audit_history` (
  audit_id              STRING      NOT NULL   OPTIONS(description="Globally unique audit identifier."),
  created_at            TIMESTAMP   NOT NULL   OPTIONS(description="When the audit ran. Partition key."),
  project_id            STRING                 OPTIONS(description="Optional project this audit belongs to."),
  user_id               STRING                 OPTIONS(description="Firebase UID of the user who triggered the audit."),
  dataset_name          STRING      NOT NULL   OPTIONS(description="Human-readable dataset name."),
  model_name            STRING      NOT NULL   OPTIONS(description="Human-readable model identifier."),
  task_type             STRING      NOT NULL   OPTIONS(description="One of tabular_classification, tabular_regression, text_classification, multimodal."),
  protected_attributes  ARRAY<STRING> NOT NULL OPTIONS(description="Protected attributes covered by this audit."),
  risk_level            STRING      NOT NULL   OPTIONS(description="Risk level from the AI report: minimal, low, moderate, high, severe."),
  mitigation_method     STRING                 OPTIONS(description="Mitigation method applied, if any."),
  verdict               STRING      NOT NULL   OPTIONS(description="Plain-English verdict from the AI report."),
  metrics_before        JSON        NOT NULL   OPTIONS(description="Full pre-mitigation metrics payload."),
  metrics_after         JSON                   OPTIONS(description="Full post-mitigation metrics payload, null if not run."),
  report_json           JSON        NOT NULL   OPTIONS(description="Full FairnessReport JSON."),
  report_version        STRING      NOT NULL   OPTIONS(description="Schema version of the report JSON.")
)
PARTITION BY DATE(created_at)
CLUSTER BY risk_level, dataset_name
OPTIONS(
  description="NyayaLens fairness audit history. One row per audit run.",
  labels=[("product","nyayalens"), ("layer","analytics")]
);
