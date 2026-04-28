# Cloud Run

Backend deployment target for the FastAPI service.

## Prerequisites

- Enable Cloud Run, Cloud Build, Artifact Registry, Firestore, Cloud Storage,
  BigQuery, and the Gemini API surface used by the backend.
- Create an Artifact Registry Docker repository named `nyayalens` or override
  `_REPOSITORY` in the Cloud Build command.
- Grant the Cloud Run service account access to Firestore, Storage, BigQuery,
  and any configured Gemini/Vertex resources.

## Deploy

From the repository root:

```bash
gcloud builds submit backend \
  --config backend/cloudbuild.yaml \
  --substitutions _REGION=asia-south1,_SERVICE=nyayalens-backend,_REPOSITORY=nyayalens,_FIREBASE_STORAGE_BUCKET=YOUR_BUCKET
```

For local development, keep `FIREBASE_STRICT=false`. For demo/production,
the Cloud Build config sets `FIREBASE_STRICT=true`.
