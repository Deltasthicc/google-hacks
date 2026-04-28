# IAM Roles

# IAM Roles

## Cloud Run Runtime Service Account

Grant the backend runtime service account:

- `roles/datastore.user`
- `roles/storage.objectAdmin` on the Firebase Storage bucket
- `roles/bigquery.dataEditor` on the `fairness` dataset
- `roles/bigquery.jobUser` on the project
- Gemini/Vertex permissions required by the selected Gen AI endpoint

## Cloud Build Service Account

Grant the Cloud Build service account:

- `roles/artifactregistry.writer`
- `roles/run.admin`
- `roles/iam.serviceAccountUser` for the Cloud Run runtime service account

## Firebase Hosting Deployer

Grant the deployer account:

- `roles/firebasehosting.admin`
- `roles/serviceusage.serviceUsageViewer`

## Frontend Users

End users authenticate through Firebase Auth. The current frontend can also use
the backend's local bearer-token fallback while `FIREBASE_STRICT=false`.
