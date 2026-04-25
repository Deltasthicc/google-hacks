# Deck Outline

Twelve-slide submission deck. Every slide has one job. No slide carries more than one idea. Slide titles are meant to be shown literally; speaker-note bullets tell the presenter what to say.

## Slide 1 — Title

**Title:** NyayaLens

**Subtitle:** A fairness lens for automated decision systems

**Footer:** Solution Challenge 2026 India — Build with AI · Team [name]

Speaker note: pause half a beat, then lead with the one-line pitch.

## Slide 2 — The problem

**Title:** Automated decisions at machine speed, with human-scale consequences

**Visual:** Two side-by-side cards, one labelled "Approved at 71%" with a male silhouette, one labelled "Approved at 52%" with a female silhouette. Same underlying data. Subtitle in small type: "Same credit profile. Different outcomes."

Speaker notes:
- Automated decision systems now control access to credit, jobs, welfare, healthcare, and education.
- When a model inherits historical bias, the people who were already disadvantaged continue to be disadvantaged, now at machine speed and scale.
- This is not hypothetical. Real credit-scoring, hiring, and healthcare-triage systems have been shown to exhibit exactly this pattern.

## Slide 3 — Who is affected

**Title:** Bias in Indian automated decisions lands on specific people

**Visual:** A short list of real-world harm categories, each paired with a one-line example. Gender in credit, region in hiring shortlists, language in chatbot responses, caste-correlated postcodes in underwriting proxies.

Speaker notes:
- Our users are not only data scientists. They include compliance officers at NBFCs, policy officers at public institutions, and civil-society researchers.
- Existing fairness tooling is for engineers. We are building for the people who need to explain what the model is doing to a regulator, to a board, and to the public.

## Slide 4 — Existing tools fall short

**Title:** The fairness toolkit gap

**Visual:** A three-column comparison table. Columns: AIF360, Fairlearn, NyayaLens. Rows: computes metrics, explains results in plain language, reads organisational policy, stores audit history, Indian-language benchmarks.

Speaker notes:
- AIF360 and Fairlearn are excellent libraries. We use them.
- But they are libraries, not products. They do not explain, they do not remember, and they do not speak to the organisation's own policies.
- NyayaLens sits on top.

## Slide 5 — The solution

**Title:** NyayaLens: fairness, explained, remembered

**Visual:** The six-module diagram. Dataset Audit → Model Audit → Counterfactual Sandbox → Policy Review → Mitigation Studio → Continuous Monitoring. Each module is a tile with a one-word label and a small icon.

Speaker notes:
- Six modules. The first three are the audit. The fourth brings the organisation's own policies into the conversation. The fifth closes the loop with mitigation. The sixth keeps everything persistent.
- Under the hood, standard fairness metrics from Fairlearn and Vertex AI, wrapped in an explanation layer that Gemini produces and our validator checks.

## Slide 6 — Architecture

**Title:** Google-native, end to end

**Visual:** Architecture diagram. Flutter web (Firebase Hosting) → FastAPI on Cloud Run → Gemini API for reports, Gemini document understanding for policy PDFs, Firestore + Cloud Storage for project data, BigQuery for audit history, Looker Studio for monitoring.

Speaker notes:
- One codebase for the frontend, one service for the backend, one foundation model family for the AI.
- Lazy-loaded dependencies mean the code runs in teammates' notebooks and on Cloud Run without divergent setups.

## Slide 7 — Before mitigation

**Title:** What we found on the lending demo

**Visual:** Bar chart. Demographic parity difference of 0.19 between Male and Female applicants. Equal opportunity difference of 0.18. Disparate impact ratio of 0.73.

Speaker notes:
- South German Credit dataset. Logistic regression baseline. Same features, same model. Approval rate gap of nineteen percentage points.
- This is not a pathological dataset. It is the corrected, modern replacement for the canonical German Credit benchmark.

## Slide 8 — After mitigation

**Title:** What reweighing does to the gap

**Visual:** Same bar chart, now with "after" bars alongside the "before" bars. DP diff drops from 0.19 to 0.05. DI ratio rises from 0.73 to 0.92. Accuracy loss: two points.

Speaker notes:
- Reweighing via Fairlearn. Two lines of code in the ML layer. The disparity closes to within conventional thresholds.
- Accuracy drops by two percentage points. That is the tradeoff. Our report says so, out loud.

## Slide 9 — The AI report

**Title:** Not a chart. A verdict.

**Visual:** Screenshot of the executive report: risk level card, plain-English verdict paragraph, findings list with severities, impacted groups, mitigation summary, recommendations.

Speaker notes:
- Gemini writes the narrative. We never let Gemini write the numbers.
- The validator rejects any claim that names a group not in the payload, or a metric that is null in the input. Hallucination is caught before the user sees it.
- Two modes. Executive for a compliance officer. Technical for an ML engineer. Same underlying JSON.

## Slide 10 — Audit history and monitoring

**Title:** One-off audits don't fix anything. Ongoing audits do.

**Visual:** Screenshot of the Looker dashboard. Risk trend area chart on top, metric failures and impacted groups in the middle, mitigation impact at the bottom.

Speaker notes:
- Every audit is one row in BigQuery. Partitioned by day, clustered by risk level and dataset.
- Four dashboard queries turn the history into four answers: what's our posture, where are we failing, who is affected, and does mitigation actually help.
- This is what turns the product from a notebook into a system.

## Slide 11 — Grounded in research, aimed at India

**Title:** Built on published work, tuned for Indian users

**Visual:** Two-panel callout. Left panel: the Iqbal & Ismail 2025 paper reference with a one-sentence summary. Right panel: the BharatBBQ languages list (Hindi, Marathi, Bengali, Tamil, Telugu, Odia, Assamese, English).

Speaker notes:
- Our counterfactual analysis is a direct implementation of the bias-detection framework from Iqbal and Ismail's 2025 Procedia paper.
- Our language fairness benchmarks include BharatBBQ, which evaluates bias across eight Indian languages, not just English.
- SDG alignment: primarily SDG 10 Reduced Inequalities, secondarily SDG 16 and SDG 5.

## Slide 12 — What's next and who we are

**Title:** Roadmap and team

**Visual:** Left: a four-item roadmap bullet list (Vertex AI scheduled re-audits, multi-tenant org accounts, custom fairness classifier packs, Slack alerting). Right: team names with one-word role labels. Bottom: repo link and demo video link.

Speaker notes:
- We are not claiming to have solved fairness. We are claiming to have built the workspace where fairness becomes tractable.
- Four of us, one week, one MVP. Thank you.

## Design constraints for the deck

- Dark blue primary (#0b57d0) matching the product UI.
- Plain typeface (Inter, Roboto, or system sans). No decorative fonts.
- Maximum six lines of text on any slide except the architecture and demo-script slides.
- Every screenshot must come from the live MVP, not from a mock.
- Every number must come from an actual audit run, not a fabricated example.
