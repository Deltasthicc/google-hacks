# NyayaLens API Contracts

Base URL for local development: `http://localhost:8080`

All user-facing API responses use this envelope:

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

Errors use:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {}
  }
}
```

## Auth

Send Firebase Auth tokens as:

```http
Authorization: Bearer <firebase_id_token>
```

Current implementation is a local stub. Real Firebase Admin verification will replace it without changing route contracts.

## IDs

- `project_id = project_<uuid>`
- `upload_id = upload_<uuid>`
- `audit_id = audit_<uuid>`
- `report_id = report_<uuid>`
- `benchmark_id = benchmark_<uuid>`
- `mitigation_run_id = mitigation_<uuid>`
- `approval_id = approval_<uuid>`

## Endpoints

### `GET /health`

Returns service status outside the response envelope for infrastructure health checks.

### `POST /api/v1/projects`

Request:

```json
{
  "name": "Lending fairness demo",
  "domain": "lending",
  "description": "Optional notes"
}
```

Response `data`: project object with `project_id`, `user_id`, timestamps, and `status`.

### `POST /api/v1/upload-dataset`

Multipart form:

- `project_id`
- `file`

Response `data`: upload metadata. Private `storage_path` is stored server-side only.

### `POST /api/v1/upload-policy-doc`

Multipart form:

- `project_id`
- `file`

Response `data`: upload metadata. Private `storage_path` is stored server-side only.

### `POST /api/v1/run-data-audit`

Request:

```json
{
  "project_id": "project_...",
  "upload_id": "upload_...",
  "target_column": "approved",
  "sensitive_columns": ["gender", "region"]
}
```

Current response is a queued placeholder audit. Person 3 will wire deterministic data-bias metrics here.

### `POST /api/v1/run-model-audit`

Request:

```json
{
  "project_id": "project_...",
  "upload_id": "upload_...",
  "target_column": "approved",
  "prediction_column": "prediction",
  "sensitive_columns": ["gender", "region"]
}
```

Current response is a queued placeholder audit. Person 3 will wire model-bias metrics here.

### `POST /api/v1/run-counterfactuals`

Request:

```json
{
  "project_id": "project_...",
  "upload_id": "upload_...",
  "audit_id": "audit_...",
  "sensitive_columns": ["gender"],
  "sample_limit": 100
}
```

`upload_id` and `audit_id` are optional so this can run either from raw uploads or an existing audit.

### `POST /api/v1/run-benchmark-suite`

Request:

```json
{
  "project_id": "project_...",
  "suite_name": "default",
  "benchmarks": ["bharatbbq", "bbq", "crows_pairs"]
}
```

Response `data`: `benchmark_id`, status, selected benchmarks, and placeholder results.

### `POST /api/v1/generate-report`

Request:

```json
{
  "project_id": "project_...",
  "audit_id": "audit_...",
  "mode": "executive"
}
```

`mode` can be `executive` or `technical`. Current response is a placeholder report until Person 3's payload is ready for Person 4's `ai_reports.generate_report`.

### `GET /api/v1/audit/{audit_id}`

Returns one audit owned by the authenticated user.

### `GET /api/v1/project/{project_id}/history`

Returns audit history for a project owned by the authenticated user.

## Firestore Collections

Expected collections:

- `users`
- `projects`
- `uploads`
- `audits`
- `reports`
- `benchmarks`
- `mitigation_runs`
- `approvals`

The current local service mirrors these collection names in memory so the Cloud Firestore implementation can replace it later.
