# Environment Matrix

## Local

| Variable | Value |
|---|---|
| `APP_ENV` | `development` |
| `PORT` | `8080` |
| `FIREBASE_STRICT` | `false` |
| `GOOGLE_CLOUD_PROJECT` | optional |
| `FIREBASE_PROJECT_ID` | optional |
| `FIREBASE_STORAGE_BUCKET` | optional |
| `NYAYA_BQ_DATASET` | `fairness` |
| `NYAYA_BQ_AUDIT_TABLE` | `audit_history` |

## Staging

| Variable | Value |
|---|---|
| `APP_ENV` | `staging` |
| `FIREBASE_STRICT` | `true` |
| `GOOGLE_CLOUD_PROJECT` | staging GCP project |
| `FIREBASE_PROJECT_ID` | staging Firebase project |
| `FIREBASE_STORAGE_BUCKET` | staging Storage bucket |
| `NYAYA_BQ_DATASET` | `fairness` |
| `NYAYA_BQ_AUDIT_TABLE` | `audit_history` |

## Production / Demo

| Variable | Value |
|---|---|
| `APP_ENV` | `production` |
| `FIREBASE_STRICT` | `true` |
| `GOOGLE_CLOUD_PROJECT` | demo GCP project |
| `FIREBASE_PROJECT_ID` | demo Firebase project |
| `FIREBASE_STORAGE_BUCKET` | demo Storage bucket |
| `NYAYA_BQ_DATASET` | `fairness` |
| `NYAYA_BQ_AUDIT_TABLE` | `audit_history` |
