# NyayaLens — Branch-by-Branch Audit Report

## 0. Background

There is **no central work-division document** in this repo. The closest things are:
- `infra/github/branch_strategy.md` — names the four feature branches with no detail.
- `PERSON4_HANDOFF.md` (root) — a self-handoff Person 4 wrote, listing what they built and what they handed off to teammates.
- `docs/submission/project_links.md` — names Person 4 (Rohit Sudhakar) and lists all other roles as "TBD".

Authorship from `git log` confirms the split:

| Person | Branch | Author | Scope |
|---|---|---|---|
| 1 | `feature/person1-ui` | (no commits authored) | Flutter web frontend (`frontend/flutter_app/`) |
| 2 | `feature/person2-backend` | Yashvardhan Singh Chauhan | FastAPI on Cloud Run (`backend/app/`) |
| 3 | `feature/person3-ml` | Abhiraj Agarwal | ML / fairness pipeline (`ml/`) |
| 4 | `feature/person4-reports` (merged to `master`) | Shashwat Rajan / "Deltasthicc" | `backend/app/ai_reports/`, `analytics/`, submission docs |

Methodology: I created git worktrees at `/tmp/nyaya-audit/{p1,p2,p3,p4}` so each branch could be tested in isolation. I ran the actual test suites and validated payloads against the cross-team contract (Person 4's `FairnessAuditPayload` Pydantic schema).

---

## 1. PERSON 1 — Flutter UI 🚨 CRITICAL

### What they built
**Effectively nothing.** The branch sits on commit `e6f31cd chore: initialize hackathon project scaffold` — the *initial* repo commit. Person 1 has not made a single commit of their own.

### What's there (all from the scaffold)
- `pubspec.yaml`: minimum Flutter SDK only — no `firebase_core`, `firebase_auth`, `cloud_firestore`, `firebase_storage`, no HTTP client, no router, no state-management library.
- `lib/main.dart` — 2 lines: `// Placeholder entry point` + `// TODO`.
- `lib/app.dart` — 2 lines: `// Placeholder root widget` + `// TODO`.
- `lib/models/fairness_report.dart` — 2 lines: `// Placeholder fairness report model` + `// TODO: Match backend report schema`.
- `lib/features/{upload,reports,settings,dashboard,onboarding}/...` — a folder skeleton; every Dart file is **0 bytes** or a 2-line TODO placeholder.
- `lib/core/services/{api,auth,storage}_service.dart` — empty.

### What works
- Nothing renderable. There is no app to run.

### What's broken/missing
| Severity | Item | Evidence |
|---|---|---|
| 🔴 Critical | No work done. Branch never moved past scaffold. | `git log` shows zero Person-1 commits. |
| 🔴 Critical | Cannot run `flutter pub get` to a usable state — no real deps declared. | `pubspec.yaml` has only `flutter` SDK. |
| 🔴 Critical | No Firebase Auth, Firestore, or Storage wiring. | No firebase deps, no init code in `main.dart`. |
| 🔴 Critical | No backend integration — `api_service.dart` is empty. | Empty file. |
| 🔴 Critical | `fairness_report.dart` model not defined — won't deserialize Person 4's `FairnessReport`. | 2-line stub. |
| 🟠 High | Flutter is not even installed on this machine, so even if code existed it couldn't be tested locally. | `which flutter` → not found. |

### Fix plan (Person 1)
This is essentially **start from zero**:
1. **Update `pubspec.yaml`**: add `firebase_core`, `firebase_auth`, `cloud_firestore`, `firebase_storage`, `http` (or `dio`), `provider` or `riverpod`, `go_router`.
2. **Wire `main.dart` + `app.dart`**: Firebase init, MaterialApp with router.
3. **Implement `api_service.dart`**: typed methods for `POST /api/v1/projects`, `POST /api/v1/upload-dataset`, `POST /api/v1/upload-policy-doc`, `POST /api/v1/run-data-audit`, `POST /api/v1/run-model-audit`, `POST /api/v1/generate-report`, `GET /api/v1/audit/{id}`, `GET /api/v1/project/{id}/history`. Attach Firebase ID token as `Authorization: Bearer …`.
4. **Implement `fairness_report.dart`**: mirror `backend/app/ai_reports/schemas.py::FairnessReport` (`audit_id`, `risk_level`, `plain_english_verdict`, `headline_findings[]`, `impacted_groups[]`, `mitigation_summary?`, `recommendations[]`, `caveats[]`, `policy_alignment?`).
5. **Build pages**: onboarding/sign-in → dashboard → upload → reports list → report view (with executive/technical toggle since both modes share JSON).
6. Install Flutter locally before continuing.

---

## 2. PERSON 2 — FastAPI Backend ✅ STRONG (with gaps)

### What they built
- **15 routes** across 5 routers, all wired in `main.py` with consistent `ApiResponse[T]` envelope and `ApiError` for failures.
  - `GET /health`
  - `POST /api/v1/projects`
  - `POST /api/v1/upload-dataset`, `POST /api/v1/upload-policy-doc`
  - `POST /api/v1/run-data-audit`, `POST /api/v1/run-model-audit`, `POST /api/v1/run-counterfactuals`, `POST /api/v1/run-benchmark-suite`
  - `GET /api/v1/audit/{audit_id}`, `GET /api/v1/project/{project_id}/history`
  - `POST /api/v1/generate-report`
- **Real Firebase Auth** with `FIREBASE_STRICT` toggle so dev mode falls back to a stub user (`firebase_auth.py:12`).
- **Real Firebase Storage upload** that writes bytes to a real bucket when configured, in-memory otherwise (`storage_service.py:13`).
- **Firestore wrapper** with the same real-or-in-memory pattern (`firestore_service.py:27`).
- Working **Dockerfile**, sane `.env.example`, request-id-style prefixed UUIDs (`utils/ids.py`), proper exception handlers in `main.py:38-85`.
- **`requirements.txt`** is well thought out: it deliberately excludes Fairlearn/AIF360 from the runtime image (those go to `requirements-ml.txt`).

### What works (verified)
- `python -c "from app.main import app"` — clean import.
- `pytest -v` → **25 passed, 1 skipped** (the 1 skip is the live-Gemini integration test, which is correct behaviour without an API key).
- All routes registered correctly.
- Test coverage spans health, auth envelope, upload flow, report parsing, validator, exporters, BigQuery row builder, and SQL placeholder substitution.

### What's broken / missing

| Severity | Item | Evidence |
|---|---|---|
| 🔴 Critical | **`audit_service.create_audit` is a placeholder** — does NOT call Person 3's ML code; just stores `_placeholder_results`. | `services/audit_service.py:18-23, 59-64` — explicit `TODO(Person 3)`. |
| 🔴 Critical | **`reports.py::generate_report` calls `export_service.create_report`, not Person 4's `ai_reports.generate_report`.** Returns hardcoded fake findings. | `routes/reports.py:23-30` → `services/export_service.py:18-22` — explicit `TODO(Person 4)`. |
| 🟠 High | **3 empty Python files** (`routes/auth.py`, `routes/exports.py`, `schemas/auth.py`) — 0 bytes, included in repo. Not imported but pollute the tree. | `wc -l` confirms. |
| 🟠 High | **CORS set to `allow_origins=["*"]`** with `allow_credentials=True` — that combination is invalid per CORS spec and a security concern even if it "works" today. | `main.py:23-29`. |
| 🟡 Medium | `audits.py:32` passes `payload.model_dump()` (raw user input including `upload_id`) into Firestore as `inputs` — fine for now, but no size limit and could grow. | `services/audit_service.py:32`. |
| 🟡 Medium | `list_documents` accepts `**filters: str` but actually filters on equality with any value type — type hint is misleading. | `firestore_service.py:50`. |
| 🟢 Low | `upload_file_stub = upload_file` alias at end of `storage_service.py` — appears unused, leftover from an earlier stub-vs-real toggle. | `storage_service.py:43`. |

### Fix plan (Person 2)

1. **Wire ML integration in `audit_service.create_audit`** — replace the placeholder block with a call into Person 3's `ml.src.benchmark_runner.run_pipeline(...)` (or `evaluate.py`) once Person 3's output matches the contract. This is blocked on Person 3's contract fix below.
2. **Wire AI reports in `export_service.create_report`** — replace the entire body with:
   ```python
   from app.ai_reports import FairnessAuditPayload, generate_report, ReportMode, bundle_exports
   payload = FairnessAuditPayload.model_validate(audit["results"])
   result = generate_report(payload, mode=ReportMode(mode))
   bundle = bundle_exports(result.report)
   # store + return
   ```
3. **Delete the 3 empty files** (or implement them; they look forgotten).
4. **CORS**: replace `allow_origins=["*"]` with the actual frontend origin once Person 1 deploys. Keep credentials only with explicit origins.
5. **Add wiring tests** that mock `app.ai_reports.generate_report` and assert `routes/generate-report` calls it with the correct payload.

---

## 3. PERSON 3 — ML / Fairness Pipeline 🟠 HIGH (works, but contract-broken)

### What they built
- **Real, well-commented Fairlearn code** for the UCI Adult dataset:
  - `ml/src/data_loader.py` — fetch UCI Adult from OpenML, plus `load_csv_dataset(csv_path)` for user uploads.
  - `ml/src/preprocessing.py` — clean `?`/NaN, encode target, separate sensitive cols, one-hot, scale, train/test split.
  - `ml/src/train.py` — `LogisticRegression(max_iter=5000)`.
  - `ml/src/evaluate.py::detect_bias` — Fairlearn `MetricFrame` with accuracy/recall per group, severity classification (HIGH > 10%, MEDIUM ≥ 5%).
  - `ml/src/mitigation.py::apply_mitigation` — Fairlearn `ThresholdOptimizer` with `equalized_odds` constraint.
  - `ml/src/counterfactuals.py::run_counterfactual_check` — flips Husband↔Wife relationship one-hot columns, measures flip rate per group.
  - `ml/src/benchmark_runner.py::run_pipeline` — driven by YAML config or args, end-to-end.
  - `ml/hardcoded_demo.py` — standalone end-to-end script.
  - `ml/demo_output.json` — captured output of running the pipeline.
  - `test_all_modules.py` (root) — sequential smoke test.

### What works
- Code is readable and the algorithms are correct in isolation: Fairlearn `MetricFrame`, `ThresholdOptimizer.fit/predict`, sklearn pipeline, train/test split, scaling.

### What's broken / missing

| Severity | Item | Evidence |
|---|---|---|
| 🔴 **CRITICAL — HEADLINE** | **`demo_output.json` does not validate against `FairnessAuditPayload`.** | I ran the validation: `13 validation errors`. Missing required fields `audit_id`, `created_at`, `model`, `protected_attributes`, `metrics_before_mitigation`. `dataset` is a string ("UCI Adult …") but schema expects `DatasetInfo` object. Extra fields `status`, `sensitive_column`, `target_column`, `mitigation_method`, `before`, `after`, `improvement` violate `extra='forbid'`. |
| 🔴 Critical | `test_all_modules.py` **fails on first step** today. | `OpenMLError: Dataset adult with version 2 not found.` — OpenML changed and v2 is gone. v1 still works. |
| 🟠 High | **No code path produces a `FairnessAuditPayload`-shaped dict.** None of `evaluate.py`, `mitigation.py`, `benchmark_runner.py` emit `audit_id`, `created_at`, `dataset` (object), `model` (object), `protected_attributes` (object list), `metrics_before_mitigation.per_attribute[].per_group[]`, `metrics_before_mitigation.per_attribute[].disparities`, `counterfactuals.{n_samples_tested, n_predictions_changed, proportion_changed}`. | Compare `mitigation.py:100-117` output with `schemas.py:210-227`. |
| 🟠 High | **No counterfactual schema parity.** P3's `counterfactuals.run_counterfactual_check` returns `flip_count`, `flip_rate`, `flip_rate_by_group`, `severity`, `proxy_columns_used`. The schema's `CounterfactualBlock` wants `attribute_flipped`, `n_samples_tested`, `n_predictions_changed`, `proportion_changed`, `examples`. | `counterfactuals.py:81-89` vs `schemas.py:166-172`. |
| 🟠 High | **No metric-name parity.** Schema wants `demographic_parity_difference`, `equal_opportunity_difference`, `equalized_odds_difference`, `disparate_impact_ratio`. P3 only computes `accuracy_difference` and `recall_difference`. | `evaluate.py:38-46` vs `schemas.py:128-132`. |
| 🟠 High | `benchmark_runner.py:1-15` says "saves results to ml/outputs/reports/" but `run_pipeline()` returns the dict; only the `__main__` block calls `save_report`. The save path is hardcoded to "Adult". | `benchmark_runner.py:113-115`. |
| 🟡 Medium | The README claims **BharatBBQ + multi-Indian-language NLP bias evaluation**. None of that exists in P3's code — there is no NLP benchmark, no Hindi/Marathi/Tamil/etc. | Search for "bharat", "bbq", "hindi" in `ml/src/` returns nothing. |
| 🟡 Medium | The README claims P3 implements the **Iqbal & Ismail (2025) hypothesis-testing framework**. P3's counterfactual is an ad-hoc Husband↔Wife column swap specific to UCI Adult. Not what the paper describes. | `counterfactuals.py:46-55`. |
| 🟡 Medium | `ml/configs/adult.yaml` is referenced by `benchmark_runner.py:42` but I didn't see actual usage in `test_all_modules.py`. Risk of drift. | Static read. |
| 🟢 Low | Hardcoded `random_state=42`, `test_size=0.2`, `max_iter=5000` everywhere; should come from config. | Multiple files. |

### Fix plan (Person 3)
1. **(Blocking the whole product)** Add a thin adapter — call it `ml/src/contract_adapter.py::to_fairness_audit_payload(pipeline_result, *, audit_id, project_id, user_id, dataset_info, model_info)` — that produces a dict matching `FairnessAuditPayload`. Specifically:
   - Wrap dataset string into `DatasetInfo(name=..., source="UCI", task_type="tabular_classification", target_column=..., n_rows=..., n_features=...)`.
   - Wrap model into `ModelInfo(name="logistic_regression_v1", family="linear", framework="scikit-learn", hyperparameters={"C":1.0,"max_iter":5000}, version="1.0.0")`.
   - Wrap sensitive cols into `protected_attributes=[ProtectedAttribute(name="sex", type="binary", groups=["Male","Female"], reference_group="Male")]`.
   - Build `metrics_before_mitigation.per_attribute[0]` with a `per_group` list (one `PerGroupMetric` per group with `accuracy`, `true_positive_rate=recall`, `support`, etc.) and a `disparities` block.
   - Same for `metrics_after_mitigation`, plus `mitigation_method="ThresholdOptimizer (equalized_odds)"`.
   - Build `counterfactuals` with `attribute_flipped`, `n_samples_tested=len(features_test)`, `n_predictions_changed=flip_count`, `proportion_changed=flip_rate`.
2. **Compute the missing disparity metrics**. Fairlearn already exposes `demographic_parity_difference`, `equalized_odds_difference`. Use them.
3. **Fix `data_loader.py`** — `version=2` no longer exists on OpenML. Use `version=1` or pin the data id. This is breaking `test_all_modules.py` immediately.
4. **Decide**: either drop the BharatBBQ / multi-language claim from README, or actually wire up the dataset (Person 4's schema already has `nlp_benchmarks.bharatbbq`).
5. **Decide**: either implement Iqbal & Ismail's actual hypothesis-testing procedure, or soften the README claim to "an Iqbal-and-Ismail-inspired counterfactual sensitivity check".

---

## 4. PERSON 4 — AI Reports + Analytics ✅ STRONG (delivered)

### What they built
- **`backend/app/ai_reports/`** — schemas (`StrictModel` with `extra='forbid'`), prompts, validator with 9 distinct check classes including faithfulness (groups must exist in payload, metrics must be present, mitigation only claimed when `metrics_after_mitigation` exists), generator with Gemini structured output (`response_schema=FairnessReport`), retry-with-stricter-prompt loop, soft-repair fallback, exporters (JSON, executive Markdown, technical Markdown with metric table, self-contained HTML with inline CSS), bigquery_client with `build_audit_history_row`, `insert_audit`, three dashboard query runners.
- Two realistic sample payloads: `lending_sample.json` (SouthGermanCredit), `hiring_sample.json` (Adult).
- 8 BigQuery SQL files (DDL + 5 dashboards) under `analytics/bigquery/sql/`.
- Looker planning docs under `analytics/looker/`.
- Submission docs (`docs/submission/`, `docs/pitch/`, `docs/research/fairness_payload_contract.md`).

### What works (verified)
- `pytest app/tests/test_reports.py -v` → I ran it inside the P2 worktree (which carries Person 4's full module): **25 passed, 1 skipped** — exceeding the self-reported "19 pass / 1 skip" because Person 2 picked up Person 4 + the post-merge SQL-substitution fix, which added two new tests.
- Both `lending_sample.json` and `hiring_sample.json` validate against `FairnessAuditPayload`. ✅
- The validator correctly rejects unknown groups, unknown metrics, mitigation claims without evidence, audit_id mismatches; soft-repair correctly strips offending entries.
- Markdown exports include verdict, technical mode includes the `| # | Finding |` table; HTML is self-contained with inline CSS and starts with `<!doctype html>`.
- Recent fix `1a24e7c` (`${project}/${dataset}` substitution) is correct and tested by `test_render_sql_substitutes_placeholders` and `test_render_sql_requires_project`. No regression.

### What's broken / missing

| Severity | Item | Evidence |
|---|---|---|
| 🟡 Medium | `generator.py:_coerce_to_report` always overwrites `audit_id`, `mode`, `generated_at` — good for safety, but if Gemini returns nothing parseable on attempt 1, the `_stricter_retry_prompt` is built from `user_prompt` which in the catch branch hasn't been reassigned yet (`continue` skips validation). Minor: fine logic but worth a comment. | `generator.py:154-166`. |
| 🟡 Medium | `_make_client()` will raise on missing API key only at the actual `client.models.generate_content` call, not at construction — the failure mode for misconfiguration is a runtime error mid-request. | `generator.py:85-103`. |
| 🟡 Medium | `bigquery_client.py:39` computes `_SQL_ROOT = Path(__file__).resolve().parents[3] / "analytics" / "bigquery" / "sql"`. That assumes a fixed layout. If `app/ai_reports/` is ever vendored into a different repo it silently breaks. Consider an env var override. | `bigquery_client.py:39`. |
| 🟢 Low | `exporters.py` markdown uses emoji characters in `_RISK_EMOJI`. Fine in HTML, fine in modern terminals; some CI log viewers will mangle. Not actually broken. | `exporters.py:32-38`. |
| 🟢 Low | `validator.py:_metrics_present` only inspects `metrics_before_mitigation`; metrics that exist only in `metrics_after_mitigation` (rare but possible) wouldn't be considered "present". | `validator.py:70-78`. |
| 🟢 Low | `bigquery_client.insert_audit` uses streaming `insert_rows_json` — fine, but streaming has a buffer that delays Looker visibility by minutes. Worth knowing for the demo. | `bigquery_client.py:112`. |

### Fix plan (Person 4)
This module is the most complete. Items are polish, not blockers:
1. Add a unit test that mocks `client.models.generate_content` returning malformed JSON to prove the retry path works (currently you have to trust the loop logic).
2. Make `_SQL_ROOT` overridable via `NYAYA_SQL_ROOT` env var.
3. Tiny: doc-comment the `_stricter_retry_prompt` chain in `generator.py` so future maintainers see the intent.

---

## 5. Cross-person integration (the real story)

Even though P2 + P4 are individually solid, **the end-to-end product does not work**:

```
  Flutter UI (P1)         FastAPI (P2)              ai_reports (P4)         BigQuery
       │                       │                          │                     │
  ❌ NOT BUILT  ──── HTTP ────►│                          │                     │
                               │  audit_service           │                     │
                               │  ❌ placeholder          │                     │
                               │  (does not call ML)      │                     │
                               │                          │                     │
                               │  export_service          │                     │
                               │  ❌ placeholder          │                     │
                               │  (does not call          │                     │
                               │   ai_reports)            │                     │
                               │                          │                     │
ML pipeline (P3) ── output ──► ❌ shape mismatch ───────► FairnessAuditPayload  │
(works, but emits             (13 Pydantic errors)        ✅ would accept        │
 wrong shape)                                              correct payload      │
                                                           ✅ insert_audit ────►│
```

There are **two missing wires** keeping the pipeline from working end-to-end (one of which is itself a 2-line edit once the contract is fixed):
1. P3 must produce `FairnessAuditPayload`-shaped output.
2. P2 must replace the two `TODO(Person 3/4)` placeholders with real calls.
3. P1 must build a frontend.

---

## 6. Prioritised global fix plan

| # | Owner | Fix | Why |
|---|---|---|---|
| 1 | **P3** | Write `to_fairness_audit_payload(...)` adapter producing valid `FairnessAuditPayload`. | Blocks the whole pipeline. Without this, every wiring change downstream is dead weight. |
| 2 | **P3** | Fix OpenML version (`adult`, version=1). | `test_all_modules.py` is broken right now. |
| 3 | **P3** | Add `demographic_parity_difference` and `equalized_odds_difference` via Fairlearn. | Validator will reject metric_name references that aren't present. |
| 4 | **P2** | Replace `audit_service.create_audit` placeholder with a call into P3's adapter output. | Until then, `/run-data-audit` returns fake data. |
| 5 | **P2** | Replace `export_service.create_report` placeholder with `ai_reports.generate_report(payload, mode)`. | Until then, `/generate-report` returns a hardcoded "Placeholder report". |
| 6 | **P1** | Build the Flutter app (everything — `pubspec.yaml`, Firebase init, router, API client, report renderer). | Without this, there is no demo. |
| 7 | **P2** | Delete or implement the 3 empty files (`routes/auth.py`, `routes/exports.py`, `schemas/auth.py`). | Cleanup. |
| 8 | **P2** | Replace CORS `allow_origins=["*"]` with actual frontend origin. | Security + spec compliance. |
| 9 | **P3** | Honest the README: drop or scope down BharatBBQ multi-language and Iqbal & Ismail framework claims. | Currently the README oversells what is built. |
| 10 | **P4** | Add a malformed-response retry test; make `_SQL_ROOT` env-overridable. | Polish, not a blocker. |

---

## 7. TL;DR for the team

- **Person 4: solid, shipped, tests pass.** Only needs polish.
- **Person 2: solid scaffolding + auth + uploads + 25 tests pass, but the two business-logic services are stubs.** Two 5-line edits unblock the pipeline once Person 3 is fixed.
- **Person 3: real working ML, but emits the wrong JSON shape and the smoke test is broken on today's OpenML.** This is the single highest-leverage fix — without the contract adapter, nothing downstream can be tested with real data.
- **Person 1: has not started.** The Flutter app is empty placeholders on the scaffold commit. This is a from-scratch build, not a fix-up.

The product cannot demo end-to-end today. The fastest path to a working demo is, in order: P3 contract adapter → P2 wires both placeholders to real calls → P1 builds the minimal frontend (sign-in → upload → trigger → render report).
