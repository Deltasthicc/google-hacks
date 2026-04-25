-- Create the fairness.report_exports table for NyayaLens.
--
-- Tracks every export (JSON / Markdown / HTML / PDF) of a fairness report.
-- Useful for the dashboard "audits exported in the last N days" view and
-- for usage analytics.

CREATE TABLE IF NOT EXISTS `${project}.${dataset}.report_exports` (
  export_id    STRING     NOT NULL  OPTIONS(description="Unique export identifier."),
  audit_id     STRING     NOT NULL  OPTIONS(description="The audit this export belongs to. Foreign key to audit_history."),
  format       STRING     NOT NULL  OPTIONS(description="One of json, markdown, html, pdf."),
  user_id      STRING               OPTIONS(description="Firebase UID that requested the export."),
  created_at   TIMESTAMP  NOT NULL  OPTIONS(description="When the export was produced."),
  byte_size    INT64                OPTIONS(description="Size of the exported artifact in bytes."),
  storage_uri  STRING               OPTIONS(description="Cloud Storage URI if the export was persisted.")
)
PARTITION BY DATE(created_at)
CLUSTER BY format, audit_id
OPTIONS(
  description="NyayaLens report export log.",
  labels=[("product","nyayalens"), ("layer","analytics")]
);
