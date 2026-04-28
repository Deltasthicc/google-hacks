# Analytics Layer

Persistence and reporting layer for NyayaLens fairness audits. Turns a one-time notebook output into a long-term governance surface.

## What lives here

```
analytics/
  bigquery/
    schemas/         JSON schemas matching the Pydantic models in
                     backend/app/ai_reports/schemas.py
    sql/             Table-creation DDL and dashboard queries
  looker/            Dashboard planning docs (notes, charts, filters)
  exports/           Local sample exported reports, ignored except .gitkeep
```

## Responsibilities

1. **Audit history persistence.** Every audit run produces one row in `fairness.audit_history`, containing the full pre-mitigation metrics, post-mitigation metrics if any, and the generated fairness report JSON. The FastAPI backend writes this row via `backend/app/ai_reports/bigquery_client.py::insert_audit`.

2. **Dashboard queries.** Four pre-built SQL files drive the Looker Studio dashboard. Each query is parameterised on the project and dataset so the same files work across demo, staging, and production projects.

3. **Export tracking.** `fairness.report_exports` records every JSON / Markdown / HTML / PDF export, with byte size and Cloud Storage URI. Supports usage analytics.

## Bringing a fresh BigQuery project online

```bash
# 1. Create the dataset
bq --location=US mk --dataset \
  --description "NyayaLens fairness audit storage" \
  ${PROJECT}:fairness

# 2. Create the tables (substitute ${project} and ${dataset})
bq query --use_legacy_sql=false \
  --parameter="project:STRING:${PROJECT}" \
  --parameter="dataset:STRING:fairness" \
  < analytics/bigquery/sql/create_audit_history_table.sql

bq query --use_legacy_sql=false \
  --parameter="project:STRING:${PROJECT}" \
  --parameter="dataset:STRING:fairness" \
  < analytics/bigquery/sql/create_report_exports_table.sql

# 3. Verify
bq show ${PROJECT}:fairness.audit_history
```

## Schema change policy

The audit history schema is versioned by the `report_version` column. Adding a field is non-breaking. Removing or renaming a field requires:

1. Bumping the `report_version` default in `backend/app/ai_reports/schemas.py`.
2. Updating the BigQuery schema JSON and DDL in the same pull request.
3. Documenting the migration path in this file.

No silent renames.
