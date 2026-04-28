# GCP Services To Enable

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com \
  bigquery.googleapis.com \
  logging.googleapis.com \
  aiplatform.googleapis.com
```

Create the image repository:

```bash
gcloud artifacts repositories create nyayalens \
  --repository-format=docker \
  --location=asia-south1
```

The backend can run with Firebase Admin application-default credentials on
Cloud Run. Local development can still use the in-memory fallback by leaving
Firebase credentials unset and `FIREBASE_STRICT=false`.
