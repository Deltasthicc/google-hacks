# Demo Script

Walkthrough script for whoever is on camera. Timing targets are guidelines. If you run long, cut the policy-document block first; the fairness pipeline plus Gemini report carry the submission.

Target length: **4:00** to **5:30**. Hard cap if judges impose one: **6:00**.

Operator setup (commands, terminals, CSV paths) lives in **`demo_operator_handoff.md`** in this folder. Read that once before rehearsal.

---

## 0:00 — 0:25 · Hook and problem frame

*On screen:* NyayaLens title or landing hero; cursor steady.

**Anchor line:**

> "Automated systems decide loans, hiring shortlists, benefits, triage queues, thousands of times a day. Each decision looks small; the aggregate harm is not. If the model carries statistical bias against a protected group, that bias ships at scale. NyayaLens exists so teams measure that bias before deployment, explain it to non-engineers, and keep an audit trail."

**Extra yap (pick any):**

> "Most teams stop at offline notebooks. Compliance asks for evidence; notebooks do not survive audits. NyayaLens treats fairness like release engineering: repeatable runs, structured outputs, monitoring downstream."

Pause half a beat before clicking anything.

---

## 0:25 — 1:05 · Audience and product promise

*On screen:* Landing or dashboard with primary action visible.

**Anchor line:**

> "Three personas share one tool. An ML engineer validates disparity metrics before merge. A compliance officer reads plain-language findings without touching sklearn. An external researcher inspects documented audits instead of trusting vendor slides. Same backend; three reading depths."

**Extra yap:**

> "Fairness here is not vibes. Numbers come from Fairlearn on held-out data. Gemini narrates those numbers; it does not invent metrics. That separation matters when regulators ask what was measured."

Gesture toward navigation calmly; avoid racing through menus.

---

## 1:05 — 2:15 · Dataset and audit run

*On screen:* Project workspace; upload flow.

### Path A · Bundled synthetic CSV (recommended for reliability)

Use **`lending_mini_demo.csv`** from `ml/datasets/demo/` if OpenML or uploads stall.

**Anchor line:**

> "I am using a small synthetic lending-style table we ship in the repo so the demo is reproducible. Target column is approval; protected attribute is gender. I start the audit and let the pipeline train a baseline model, score the test split, measure group gaps, then apply Fairlearn mitigation."

**Extra yap:**

> "Synthetic does not mean fake math. Training, testing, disparity, mitigation, all run for real on this file. We label it synthetic in slides so nobody confuses it with production PII."

### Path B · South German Credit or Adult (if already loaded)

**Anchor line:**

> "On a fuller benchmark dataset you would map the credit or income target and flag sensitive fields the same way. I hit Run and wait for completion so every number you will see came from this run."

*Transition:* Audit status moves to completed; open results or dashboard card.

**Anchor line:**

> "Overall accuracy tells a partial story. What matters for fairness is whether positive decisions spread differently across groups. Here you see per-group rates and gaps, not just a headline AUC."

**Counterfactual card (if visible on UI):**

> "Counterfactuals test sensitivity: when we flip proxy or protected signal in a controlled way, how often does the model change its mind? A high flip rate is a warning that the boundary leans on attributes it should not."

If the UI hides exact flip numbers, speak them only if they are on screen (submission rule: no invented stats).

---

## 2:15 — 2:50 · Mitigation tradeoff

*On screen:* Before/after or mitigation toggle if present.

**Anchor line:**

> "Mitigation is not magic. Fairlearn ThresholdOptimizer searches fairer thresholds subject to constraints; you often pay a little accuracy for a lot of gap reduction. The product surfaces that tradeoff instead of hiding it behind a single green checkmark."

**Extra yap:**

> "Responsible teams disagree on acceptable tradeoffs; the product makes the tradeoff explicit so policy, not vibes, decides what ships."

---

## 2:50 — 4:00 · Gemini report (executive then technical)

*On screen:* Report view; Executive first.

**Anchor line:**

> "This is where Google Gemini plugs in. The model never recomputes fairness metrics. It reads a strict JSON audit payload produced by our pipeline and writes a governance-style report: verdict, severity, impacted groups, recommendations. That keeps narrative aligned with measurement."

**Extra yap:**

> "We validate model output against the payload. If Gemini names a group that was not in the data or cites a metric we did not compute, validation fails or repairs. Hallucinated harm is worse than no report."

*Scroll slowly* through one finding block.

**Technical tab:**

> "The same underlying JSON renders in technical mode for engineers: metric names, deltas, thresholds. One audit artifact, two audiences."

If `GEMINI_API_KEY` was not set during recording, say honestly:

> "In this take the backend used our offline narrative template because no API key was bound; with a key you get full Gemini prose on the same numbers."

---

## 4:00 — 4:40 · Policy block (optional; cut first if tight)

*On screen:* Policy upload; optional PDF.

**Anchor line:**

> "Some orgs anchor decisions in written policy. You can upload a PDF; a faster Gemini model extracts fairness-relevant clauses, and the report can include a policy alignment section. The model still cannot override measured disparities."

Skip entirely if PDF or extraction is not wired in this build.

---

## 4:40 — 5:15 · Persistence and monitoring

*On screen:* BigQuery or Looker Studio if deployed; otherwise Firestore history or export list.

**Anchor line:**

> "Audits worth running are audits worth remembering. Completed runs can land in BigQuery for trend analysis; Looker Studio shows how risk and gap patterns evolve across projects. That is the shift from notebook to system."

If cloud is not live:

> "This environment is local; in production the same pipeline streams to BigQuery for the dashboard judges can open from the submission links."

---

## 5:15 — 5:45 · Grounding and close

*On screen:* Closing card: team, repo link, SDG icons if applicable.

**Anchor line:**

> "We ground counterfactual-style analysis in published research on bias detection. We connect to Google Cloud: Flutter and Firebase on the client, Cloud Run for the API, Gemini for trustworthy narrative, BigQuery for history. Primary SDG alignment: reduced inequalities. Thank you."

**Extra yap (one sentence max):**

> "If you remember one thing: metrics are deterministic, language is grounded, tradeoffs are visible. That is NyayaLens."

---

## Recording checklist

- [ ] Screen recorded at 1080p minimum
- [ ] System audio muted; voiceover only on the track
- [ ] Cursor visible and steady; avoid rapid click spam
- [ ] Every number on screen traces to a real run in this session
- [ ] Browser has no personal tabs, no embarrassing bookmarks bar clutter
- [ ] Unlisted upload; link filed in submission and `docs/submission/project_links.md`
- [ ] Rehearsed once end-to-end with `demo_operator_handoff.md` commands

## If the live MVP breaks during recording

Fall back to a pre-recorded screen capture of the same flow, voiced over live. Keep the narrative honest about which take is live vs backup.
