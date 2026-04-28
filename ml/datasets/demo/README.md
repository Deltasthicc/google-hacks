# Demo datasets (synthetic CSV)

These files exist so NyayaLens demos work **without internet** (no OpenML fetch) and show **clear fairness gaps** plus mitigation.

## Files

| File | Rows | Target | Sensitive attribute | Role |
|------|-----:|--------|---------------------|------|
| `lending_mini_demo.csv` | 220 | `approved` | `gender` | Lending-style approval |
| `hiring_mini_demo.csv` | 180 | `hired` | `sex` | Hiring-style decision |

Data are generated with fixed seeds so git checkouts reproduce the same metrics. They are **not** real lending or HR records; label them as synthetic in decks and videos.

## YAML configs

| Config | CSV |
|--------|-----|
| `ml/configs/demo_lending_mini.yaml` | `datasets/demo/lending_mini_demo.csv` |
| `ml/configs/demo_hiring_mini.yaml` | `datasets/demo/hiring_mini_demo.csv` |

## Run the pipeline locally

From the repository root:

```bash
python -c "
from datetime import datetime, timezone
from ml.src.benchmark_runner import run_pipeline
r = run_pipeline(
    config_path='ml/configs/demo_lending_mini.yaml',
    audit_id='aud_demo', project_id='proj_demo', user_id='user_demo',
    created_at=datetime.now(timezone.utc),
)
print(r['status'], list(r.keys()))
"
```

Or save JSON:

```bash
python -c "
from datetime import datetime, timezone
from ml.src.benchmark_runner import run_pipeline, save_report
from pathlib import Path
r = run_pipeline(config_path='ml/configs/demo_lending_mini.yaml',
    audit_id='aud_demo', project_id='p', user_id='u',
    created_at=datetime.now(timezone.utc))
Path('ml/outputs/reports').mkdir(parents=True, exist_ok=True)
save_report(r, 'ml/outputs/reports/demo_lending_report.json')
print('wrote ml/outputs/reports/demo_lending_report.json')
"
```

## Use from the FastAPI audit API

Pass `config_name` in the audit request body (supported by `audit_service`): `demo_lending_mini.yaml` or `demo_hiring_mini.yaml`. Optionally upload your own CSV via Storage and set `upload_id`; if download fails or you omit upload, the selected YAML still drives the run.

## Flutter upload demo

Copy `lending_mini_demo.csv` into the UI upload flow with:

- Target column: `approved`
- Sensitive columns: `gender`

Use `hiring_mini_demo.csv` with target `hired` and sensitive `sex`.
