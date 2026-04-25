# Architecture

How NyayaLens is built, how the pieces talk, and why the design choices look the way they do.

## High-level diagram

```
┌──────────────────────────┐
│   Flutter web (PWA)      │
│   Firebase Hosting       │
└──────────────┬───────────┘
               │ HTTPS (App Check verified)
               ▼
┌──────────────────────────┐         ┌───────────────────────┐
│  FastAPI on Cloud Run    │────────▶│  Gemini API           │
│  Python 3.11+            │  reports │  (google-genai SDK)  │
│                          │         │  2.5 Pro, 2.5 Flash   │
│  ┌──────────────────┐    │         └───────────────────────┘
│  │ ai_reports/      │    │
│  │  schemas         │    │         ┌───────────────────────┐
│  │  prompts         │    │────────▶│  Firestore            │
│  │  validator       │    │  state  │  projects, audits     │
│  │  generator       │    │         └───────────────────────┘
│  │  exporters       │    │
│  │  bigquery_client │    │         ┌───────────────────────┐
│  └──────────────────┘    │────────▶│  Cloud Storage        │
│                          │  files  │  uploads, exports     │
│  ┌──────────────────┐    │         └───────────────────────┘
│  │ ml/              │    │
│  │  metrics         │    │         ┌───────────────────────┐
│  │  mitigation      │    │────────▶│  BigQuery             │
│  │  counterfactuals │    │  audits │  fairness.audit_      │
│  └──────────────────┘    │         │  history              │
└──────────────────────────┘         └──────────┬────────────┘
                                                │
                                                ▼
                                     ┌───────────────────────┐
                                     │  Looker Studio        │
                                     │  Monitoring dashboard │
                                     └───────────────────────┘
```

## Request flow, end-to-end

A typical audit run traces the following path.

### 1. User signs in

Flutter web calls Firebase Authentication. The returned ID token is attached to every subsequent API call as a Bearer header. Firestore and Storage rules check the token for ownership before any read or write.

### 2. User uploads a dataset and optionally a policy document

The frontend uploads the CSV to Cloud Storage under a path keyed by user ID and project ID. A Cloud Function triggered by the upload writes a corresponding document to Firestore. If a policy PDF is also uploaded, the same flow applies.

### 3. User triggers an audit

Flutter calls `POST /audits` on the Cloud Run service. The backend validates the request, loads the uploaded CSV, and hands off to the ML layer.

### 4. ML layer computes the fairness payload

`ml/src/evaluate.py` trains or loads a baseline model, computes per-group and disparity metrics via Fairlearn, runs a counterfactual check via the Iqbal & Ismail hypothesis-testing procedure, and optionally applies a mitigation method and recomputes metrics. The result is a dict matching the `FairnessAuditPayload` schema.

### 5. AI reporting layer generates the report

`backend/app/ai_reports/generator.py::generate_report` validates the incoming payload with Pydantic, constructs the Gemini prompt, and calls the model with `response_schema=FairnessReport` for structured output. The returned report is parsed into the `FairnessReport` Pydantic model. The validator then checks every claim against the original payload. If validation fails, one retry with a stricter prompt is attempted. If the second attempt also fails, the soft-repair fallback strips the offending fields and marks the result as unverified.

### 6. Optional: policy document enrichment

If a policy PDF was uploaded, `extract_policy_rules_from_path` calls Gemini 2.5 Flash with document understanding enabled, extracts structured rules, and attaches them to the payload before report generation. The report then includes a `policy_alignment` block.

### 7. Persistence

The backend calls `bigquery_client.insert_audit` to write one row to `fairness.audit_history`. The row contains the full pre-mitigation metrics, post-mitigation metrics if any, the generated report JSON, and metadata like dataset name, model name, and risk level.

### 8. Frontend renders

Flutter receives the structured report JSON and renders it using widgets that mirror the report sections: verdict card, findings list, impacted groups, mitigation summary, recommendations. The user can toggle between Executive and Technical views without a new API call, since both views share the same underlying JSON.

### 9. Dashboard reflects

The Looker Studio dashboard queries `fairness.audit_history` directly via the four dashboard SQL files in `analytics/bigquery/sql/`. New audits show up within seconds of insertion.

## Key design decisions and why

### Deterministic metrics, narrated report

Fairness metrics are computed by deterministic, well-tested libraries (Fairlearn, scikit-learn). Gemini never sees the raw model or raw data. It only sees a validated JSON of numbers and is allowed to narrate them. This is the single most important trust boundary in the architecture. It means that even if Gemini produces a fluent but wrong explanation, the validator catches it.

### Strict Pydantic schemas on both input and output

The `FairnessAuditPayload` schema rejects unknown fields on input, so a malformed upstream payload fails loudly rather than silently dropping data. The `FairnessReport` schema is the response schema Gemini writes to, which means structural failures are impossible: you cannot get a report missing a field. Faithfulness failures (real fields with fabricated values) are caught by the `validate_report` function in `validator.py`.

### Lazy-imported Google SDKs

The `google-genai` and `google-cloud-bigquery` imports happen inside the functions that need them, not at module top level. This means Person 3's ML notebooks, unit tests, and any environment without those SDKs can still import the `ai_reports` package. Treat this as a small thing that will save real integration pain.

### BigQuery over a custom database

BigQuery fits the access pattern perfectly: write-once per audit, read many for dashboards, and most dashboard queries hit only the last 30 or 90 days. Partitioning on `created_at` and clustering on `risk_level` and `dataset_name` means dashboard scan cost is proportional to the time window, not the table size. A custom relational DB would require its own operational story. BigQuery does not.

### Two report modes, one JSON

Executive and Technical reports share the same `FairnessReport` JSON. The difference is entirely at the rendering layer (`to_markdown`, `to_html`). This means the validator runs once, the BigQuery row is identical regardless of which mode was rendered, and adding a third mode later (for example, a translated Hindi report) is a renderer change, not a schema change.

### Gemini 2.5 Pro for reports, Flash for document parsing

Pro is worth the latency cost for the main report because the reasoning matters. Flash is faster and cheap enough to ingest a 50-page policy document in a few seconds, which is the right tradeoff for that step.

### Firebase App Check

The Gemini calls happen server-side, not from the Flutter client, which removes the most common abuse vector. App Check is still enabled on the Firebase project as a second line of defense against abuse of the backend endpoints.

## Data contracts

Two contracts matter most:

1. **Fairness payload contract.** Documented in `docs/research/fairness_payload_contract.md`. This is the JSON that flows from the ML layer into the AI reports layer. Any change here requires a version bump and coordinated changes in `backend/app/ai_reports/schemas.py` and `analytics/bigquery/schemas/audit_history.json`.

2. **Fairness report schema.** Defined in `backend/app/ai_reports/schemas.py::FairnessReport`. Any change here requires a bump to `report_version` and a migration plan for older BigQuery rows.

## Deployment

### Cloud Run

The backend is containerised via `backend/Dockerfile`. Deploy with:

```bash
gcloud run deploy nyayalens-backend \
  --source=backend \
  --region=us-central1 \
  --allow-unauthenticated=false \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT}" \
  --set-secrets="GEMINI_API_KEY=gemini-api-key:latest"
```

### Firebase Hosting

```bash
cd frontend/flutter_app
flutter build web --release
firebase deploy --only hosting
```

### BigQuery

See `analytics/README.md` for the exact `bq` commands to create the dataset and tables.

## Observability

- **Cloud Logging.** All FastAPI logs and structured generator logs flow here. Every Gemini call logs the audit ID, mode, attempt count, model used, and whether the validator passed.
- **Error Reporting.** Attached to Cloud Run, surfaces unhandled exceptions automatically.
- **Cloud Monitoring.** Cloud Run request counts, latency, and error rates. A simple alert fires if 5xx rate exceeds 5% over a 10-minute window.
- **BigQuery INFORMATION_SCHEMA.** Used for query-cost sanity checks. Any dashboard query that scans more than 1 GB in a single run is a signal to revisit the partition filter.

## Security posture

- No secrets in the repository. `.env.example` only.
- Firebase Auth required for every user-facing endpoint.
- Firestore rules restrict reads and writes to the owning user.
- Storage rules restrict uploads and downloads to the owning user.
- App Check enabled on the Firebase project.
- The Gemini API key lives in Secret Manager, read by Cloud Run at start.
- Sensitive Data Protection is not integrated in Phase 1 but is documented in the roadmap.

## What this architecture is not

It is not a multi-tenant SaaS. One GCP project per organisation is the Phase 1 assumption.

It is not a real-time streaming system. Audits are batch requests, not streams.

It is not a model-training platform. We audit models that have already been trained or whose predictions have already been produced. Training is out of scope for Phase 1.
