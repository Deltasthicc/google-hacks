# Backend Service

FastAPI service for NyayaLens file ingestion, audit orchestration, report generation, and future Cloud Run deployment.

## Local Run

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

Then open:

```text
http://localhost:8080/health
http://localhost:8080/docs
```

## Current Scope

- Uses the shared success/error response envelope.
- Exposes the blueprint endpoints under `/api/v1`.
- Uses prefixed UUID public IDs such as `project_<uuid>` and `audit_<uuid>`.
- Stores records in an in-memory Firestore stub for local development.
- Reads uploaded file bytes but does not persist them to paid cloud storage yet.
- Treats `Authorization: Bearer <token>` as a local stub user id until Firebase Admin verification is wired.

## Cloud TODOs

- Replace `services/firebase_auth.py` with real Firebase Auth token verification.
- Replace `services/firestore_service.py` with Cloud Firestore.
- Replace `services/storage_service.py` with Firebase Storage or Cloud Storage.
- Connect `services/audit_service.py` to Person 3's fairness functions.
- Connect `services/export_service.py` to Person 4's AI report generator.
