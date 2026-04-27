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
- Uses Firebase Admin for Auth, Firestore, and Storage when credentials are configured.
- Falls back to in-memory/local stub mode when Firebase credentials are absent.
- Keeps private Storage paths out of public upload responses.

## Firebase Environment

For real Firebase mode, set these values in your local shell or uncommitted `.env`:

```text
APP_ENV=development
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_STORAGE_BUCKET=your-firebase-bucket-name
FIREBASE_SERVICE_ACCOUNT_JSON_PATH=C:\path\to\service-account.json
```

`FIREBASE_STRICT=true` forces Firebase mode and fails requests when tokens or credentials are invalid. Leave it `false` while teammates are testing locally without Firebase.

## Cloud TODOs

- Tighten Firebase Auth fallback before production/demo deploy.
- Add signed download/export endpoints if frontend needs file access.
- Connect `services/audit_service.py` to Person 3's fairness functions.
- Connect `services/export_service.py` to Person 4's AI report generator.
