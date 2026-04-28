# User Flow

1. Sign in
2. Create / open project
3. Upload dataset or select benchmark
4. Run audit
5. Review dashboard
6. Open AI report
7. Export results

## MVP Flow

The current web app starts in Workspace setup. A user creates a project, uploads
a dataset and optional policy document, configures target/prediction/sensitive
columns, then queues data, model, counterfactual, or benchmark audits. Reports
are generated from the latest audit and shown in executive or technical mode.

## Production Flow

Firebase Auth supplies ID tokens to the backend. Uploaded files are stored in
Firebase Storage, audit metadata is stored in Firestore, generated report rows
can be persisted to BigQuery, and the dashboard reads the project audit history.
