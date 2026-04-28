# BigQuery Setup

# BigQuery Setup

Create the audit dataset:

```bash
bq --location=asia-south1 mk --dataset "${GOOGLE_CLOUD_PROJECT}:fairness"
```

Create the audit history and export tables from the repository schemas:

```bash
bq mk --table \
  "${GOOGLE_CLOUD_PROJECT}:fairness.audit_history" \
  analytics/bigquery/schemas/audit_history.json

bq mk --table \
  "${GOOGLE_CLOUD_PROJECT}:fairness.report_exports" \
  analytics/bigquery/schemas/report_exports.json
```

The dashboard SQL under `analytics/bigquery/sql/` expects:

- `NYAYA_BQ_DATASET=fairness`
- `NYAYA_BQ_AUDIT_TABLE=audit_history`

Grant the Cloud Run service account BigQuery Data Editor on the dataset and
BigQuery Job User on the project.
