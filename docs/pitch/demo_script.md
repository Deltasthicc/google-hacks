# Demo Script

A four-minute walkthrough. Every timing target is a guideline, not a hard cut. If you run long, cut the policy-document section first, because the core story survives without it.

Target length: 4:00. Hard cap: 5:00.

---

## 0:00 — 0:20 · Open with the stake

*On screen:* NyayaLens title card.

> "When an automated system decides who gets a loan, who gets shortlisted for a job, or who gets triaged first in a hospital, it makes that decision thousands of times a day. If that system is biased, the harm scales with it. NyayaLens is a fairness audit workspace that catches that bias before the system ships."

## 0:20 — 0:50 · Who it is for, in one breath

*On screen:* Landing page of the MVP with the "Create an audit" button highlighted.

> "NyayaLens is built for three kinds of user. The data scientist who wants to run a fairness check before deploying a model. The compliance officer who has to explain what that model does to a regulator. And the civil-society researcher auditing someone else's system from the outside. All three get the same product. They just read it at different depths."

## 0:50 — 1:30 · The audit walkthrough, lending demo

*On screen:* Upload page. Select the pre-loaded South German Credit sample.

> "Here's a real audit on the South German Credit dataset. I've mapped the target column to `credit_approved` and flagged `gender` as the protected attribute. I hit Run."

*Transition to the results page.*

> "The model is 78% accurate overall. But look at the approval rates. Men approved 71% of the time. Women approved 52% of the time. A demographic-parity gap of nineteen percentage points."

*Point at the counterfactual card.*

> "This counterfactual card shows what happens when we flip the gender attribute on 200 applicants. In 16% of cases, the prediction changes. Same features. Same model. Different outcome."

## 1:30 — 2:00 · Mitigation

*On screen:* Toggle on "Apply reweighing mitigation" and re-run.

> "One click applies reweighing, which is a standard pre-processing mitigation from Fairlearn. The gap closes from 19% to 5%. Disparate impact ratio rises to 0.92, well inside conventional thresholds. Accuracy costs us two percentage points. The product tells you that tradeoff explicitly."

## 2:00 — 2:45 · The AI report

*On screen:* Switch to the Executive report tab.

> "This is the part most fairness tools do not do. Gemini takes the structured audit output and writes a report a compliance officer can actually read. Plain-English verdict. Risk level. Findings with severity. Who is affected. What to do next."

*Scroll down, pause on the "Who is affected" card.*

> "Every claim in this report is grounded in a number that was actually computed. Our validator rejects any output that names a group not in the payload or a metric that was not measured. Hallucination is caught before the user sees it."

*Switch to the Technical tab.*

> "Same JSON. Different rendering. An ML engineer gets the full metric table, thresholds, and algorithmic recommendations."

## 2:45 — 3:15 · Policy-aware governance (optional, cut if running long)

*On screen:* Policy upload screen. Drop a sample underwriting policy PDF.

> "Let me add a policy document. This is a fictional underwriting guideline from a lending organisation. Gemini reads it, extracts the fairness rules it imposes, and the report gets a Policy Alignment block. In this case the policy says approval rates cannot differ by more than 10% across genders. Our unmitigated model violates that rule. The report says so."

## 3:15 — 3:45 · Audit history and monitoring

*On screen:* Switch to the Looker Studio dashboard (pre-filtered to the demo project).

> "Every audit is stored in BigQuery. This dashboard shows the risk trend over the last 30 days, which disparity metrics fail most often, which groups get flagged repeatedly across audits, and whether mitigation actually closes the gap. This is the difference between a fairness notebook and a fairness system. The product remembers."

## 3:45 — 4:00 · Grounding and close

*On screen:* Closing title card with team names, repo link, SDG badges (10, 16, 5).

> "The counterfactual framework we use is built on Iqbal and Ismail's 2025 paper on bias detection in sovereign digital systems. The benchmarks include BharatBBQ, which evaluates bias across eight Indian languages. SDG 10, reduced inequalities, primary. Built with Flutter, Firebase, Cloud Run, Gemini, and BigQuery. Thank you."

---

## Recording checklist

- [ ] Screen recorded at 1080p minimum
- [ ] System audio muted; only voiceover on the track
- [ ] Cursor visible and steady; no dart-and-click
- [ ] Every number on screen is real, not a mock
- [ ] Browser has no personal tabs, no bookmarks visible
- [ ] Unlisted upload, link added to `docs/submission/project_links.md`

## If the live MVP breaks during the recording

Fall back to a pre-recorded screen capture of the audit run, played back in real time, voiced over live. The fact that this exists as a plan saves the submission.
