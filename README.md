# NyayaLens

A fairness audit workspace for automated decision systems. Detects bias, explains it in plain language, checks it against an organisation's own policy documents, and stores the history so fairness becomes a practice, not a one-off check.

Built for the [Google Solution Challenge 2026 India — Build with AI](https://promptwars.in/solutionchallenge2026.html).

> **One-line pitch:** NyayaLens checks automated decision systems for unfair bias, explains the findings in language a policy officer can understand, and keeps a record so organisations can track fairness the same way they track security.

## The problem in one paragraph

Automated decision systems now control access to credit, jobs, welfare, healthcare, and education. When a model inherits historical bias from its training data, the people who were already disadvantaged continue to be disadvantaged, at machine speed and without a human in the loop to notice. Libraries like AIF360 and Fairlearn can compute fairness metrics accurately, but computing metrics is not the same as running an audit. An audit needs a workflow, an explanation that non-engineers can read, a check against the organisation's own policies, and a record so that fairness can be tracked over time. NyayaLens provides all four.

## What makes this different

- **Deterministic metrics, narrated AI report.** Fairness metrics are computed by deterministic libraries (Fairlearn, AIF360, scikit-learn). Gemini is used only to explain what the numbers already say. A validator strips any AI-generated claim that references a group not in the payload or a metric that was not actually measured.
- **Policy-aware governance check.** Upload a policy PDF and NyayaLens extracts the fairness rules it imposes, then adds a Policy Alignment block to the report showing where the model does and does not meet those rules.
- **Indian-context evaluation.** Language bias is checked not just in English but in Hindi, Marathi, Bengali, Tamil, Telugu, Odia, and Assamese via BharatBBQ.
- **Persistent audit history.** Every audit becomes a row in BigQuery. A Looker Studio dashboard turns the history into a trend, a failure breakdown, an impacted-groups view, and a mitigation-impact chart.

## Grounding

The counterfactual analysis module implements the bias-detection framework from:

> Iqbal, R., & Ismail, S. (2025). *Unbiased AI for a Sovereign Digital Future: A Bias Detection Framework.* Procedia Computer Science, 254, 118–126. [doi:10.1016/j.procs.2025.02.070](https://doi.org/10.1016/j.procs.2025.02.070)

We extend their counterfactual hypothesis-testing approach with the standard disparity metrics from the Fairlearn user guide and Google Vertex AI fairness documentation, and wrap the whole pipeline in an accessible product surface.

## Tech stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | Flutter web on Firebase Hosting | One codebase for web and mobile, fast path to a live MVP. |
| Auth | Firebase Authentication | Google and email sign-in out of the box. |
| Project data | Cloud Firestore | Flexible document store for projects, audits, and user state. |
| File uploads | Cloud Storage for Firebase | Tight integration with Auth rules. |
| Backend | FastAPI on Cloud Run | Serverless, containerised, good fit for Python fairness libraries. |
| AI reports | Gemini 2.5 Pro via `google-genai` | Structured output, multimodal input, fast iteration. |
| Policy parsing | Gemini 2.5 Flash document understanding | Fast PDF ingestion, structured rule extraction. |
| Fairness metrics | Fairlearn, AIF360, scikit-learn | Canonical, well-documented, open-source. |
| Audit history | BigQuery | Partitioned by day, clustered by risk level, cheap to query. |
| Monitoring | Looker Studio | Judge-friendly dashboards, no custom charting code required. |
| Security | Firebase App Check | Protects the Gemini calls and backend endpoints. |

## Repository layout

```
nyayalens/
├── backend/                  FastAPI service on Cloud Run
│   └── app/
│       ├── ai_reports/       ← Person 4's core module
│       │   ├── schemas.py    Pydantic models for input and output
│       │   ├── prompts.py    System prompt, exec/technical modes
│       │   ├── validator.py  Hallucination-catching rules
│       │   ├── generator.py  Gemini integration
│       │   ├── exporters.py  JSON, Markdown, HTML rendering
│       │   ├── bigquery_client.py  Audit history persistence
│       │   └── samples/      Reference payloads (lending, hiring)
│       ├── routes/           FastAPI routes
│       ├── services/         Firebase and Firestore wrappers
│       └── tests/            Pytest suite
├── frontend/
│   └── flutter_app/          Flutter web MVP
├── ml/
│   ├── src/                  Fairness metrics, mitigation, counterfactuals
│   ├── notebooks/            Dataset exploration and evaluation
│   └── configs/              One YAML per dataset
├── analytics/
│   ├── bigquery/
│   │   ├── schemas/          Field-descriptive JSON schemas
│   │   └── sql/              DDL and dashboard queries
│   └── looker/               Dashboard planning docs
├── infra/
│   ├── firebase/             Auth rules, Firestore indexes, storage rules
│   ├── gcp/                  Cloud Run, BigQuery, IAM notes
│   └── github/               CI, PR templates
└── docs/
    ├── submission/           Solution Challenge deliverables
    ├── pitch/                Deck outline, demo script, talking points
    ├── research/             Dataset notes, fairness metric reference,
    │                         fairness payload contract
    └── product/              Feature scope, accessibility, UX notes
```

## Local setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY="your-key-from-ai-studio"
export GOOGLE_CLOUD_PROJECT="your-gcp-project"
uvicorn app.main:app --reload --port 8080
```

### Frontend

```bash
cd frontend/flutter_app
flutter pub get
flutter run -d chrome
```

### Verify the AI reports module

```bash
cd backend
python -c "
import json
from app.ai_reports import FairnessAuditPayload, generate_report, ReportMode, to_markdown
from pathlib import Path

payload = FairnessAuditPayload.model_validate(
    json.loads(Path('app/ai_reports/samples/lending_sample.json').read_text())
)
result = generate_report(payload, mode=ReportMode.EXECUTIVE)
print(to_markdown(result.report))
"
```

## Try the live MVP

> **Live URL:** see `docs/submission/project_links.md` once the demo deployment is assigned.

The demo projects preloaded into the MVP are South German Credit (lending) and Adult (hiring). Both run end-to-end with pre-mitigation metrics, reweighing applied, and a policy document PDF attached.

## Team

Four students, one week, one MVP. See `docs/submission/project_links.md` for team members and role breakdowns.

## License

MIT. See `LICENSE`.

## Acknowledgements

Iqbal & Ismail (2025) for the bias-detection framework that grounds our counterfactual module. The Fairlearn and AIF360 teams for the libraries that do the metric computation. The BharatBBQ team for the Indian-language bias benchmark. And the Google Gen AI team for making the SDK easy enough to build a real product around in one week.

## Contributing

See `CONTRIBUTING.md`. Pull requests welcome after submission day.

## Feedback

If you are a judge, reviewer, or user and want to tell us what worked or what did not: file an issue on GitHub, or write to the team contact listed in `docs/submission/project_links.md`.
