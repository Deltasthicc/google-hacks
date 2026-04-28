# NyayaLens Flutter Frontend

Flutter web workspace for the NyayaLens audit flow.

## Screens

- Workspace: create/open a project and check backend health.
- Dashboard: inspect the active project, uploaded files, queued audits, and reports.
- Upload: select dataset/policy files, upload to the FastAPI backend, and run audit jobs.
- Reports: generate executive/technical reports from the latest audit.
- Settings: configure API base URL and bearer token.

## Local run

```bash
flutter pub get
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8080
```

The backend supports local fallback auth when `FIREBASE_STRICT=false`, so the default
demo bearer token is enough for local testing. In strict Firebase mode, replace it in
Settings with a real Firebase ID token.

## Deploy

```bash
flutter build web --release --dart-define=API_BASE_URL=https://your-api.example.com
firebase deploy --only hosting
```
