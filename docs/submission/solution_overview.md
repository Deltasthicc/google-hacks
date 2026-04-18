# NyayaLens: Solution Overview

## What we are building

NyayaLens is a fairness audit workspace for automated decision systems. Before an organisation deploys a hiring, lending, admissions, or triage model, NyayaLens inspects the data, model predictions, counterfactual behaviour, and the organisation's own policy documents for signs of unfairness. It explains what it found in plain language, recommends a concrete next step, and stores every audit so teams can track fairness over time rather than checking it once and forgetting.

The name comes from the Sanskrit *nyaya* (justice) and *lens*. The product is a lens for looking carefully at systems that make decisions about people.

## Why this problem matters

The Indian digital ecosystem is rapidly adopting automated decision systems in the very areas where historical inequities are most concentrated: credit scoring at NBFCs, entrance-exam evaluation, welfare disbursal, hiring screens, and insurance underwriting. When a model inherits historical bias from training data, the people who were already disadvantaged continue to be disadvantaged, now at machine speed and scale, and without a human reviewer in the loop who can notice it.

Bias is rarely obvious from a single accuracy number. An 85% accurate model can still approve men 30 percentage points more often than women with identical profiles. A model can pass an aggregate audit and still systematically underserve applicants from specific linguistic or socioeconomic groups. These failures are detectable, but detection requires disciplined metric work, intersectional slicing, and clear communication to non-technical stakeholders. Most teams do not have that workflow today.

## Who this is for

- Product and data-science teams at NBFCs, fintechs, and insurance companies in India who want to run a fairness check before shipping a model.
- Compliance and policy officers who need an accessible artifact to show regulators, auditors, and customers.
- Academic and civil-society researchers who want a repeatable methodology to audit third-party models.
- Small organisations that cannot afford a full in-house responsible-AI team but still want to do the right thing.

## How it works

A user signs in, creates a project, uploads a dataset and optionally a policy document, selects the target column and protected attributes, and runs an audit. The product computes pre-mitigation fairness metrics across each protected attribute and every intersection it can form, runs a counterfactual check to see how often predictions flip when a sensitive attribute is toggled, and optionally applies a mitigation method and recomputes. Gemini then turns those numbers into a structured fairness report with a plain-English verdict, a risk level, specific findings grounded in the actual metrics, a list of impacted groups, a mitigation summary, and concrete recommendations. If the user uploaded a policy PDF, Gemini also extracts the fairness rules that document imposes and flags gaps between what the policy promises and what the model actually does.

Every audit is written to BigQuery. A Looker Studio dashboard turns the history into four views: a trend line of risk posture over time, a breakdown of which metrics fail most often, the groups that get flagged repeatedly across audits, and whether mitigation actually closes the gap.

## What makes NyayaLens different

There are existing fairness toolkits, most notably AIF360, Fairlearn, and Themis-ML. They are all strong libraries for computing disparity metrics. What they are not is a product.

NyayaLens combines three things that no single existing toolkit offers together:

1. **A responsible explanation layer.** The fairness metrics are computed deterministically, never by the language model, and the language model is only allowed to explain results that are actually present in the payload. The validator strips any claim that references a group or metric that was not measured. This is a trust boundary most bias-explanation tools do not draw.

2. **A policy-aware governance check.** An uploaded PDF of an organisation's hiring guidelines, underwriting policy, or model card is parsed by Gemini into a structured list of fairness rules, which are then compared against the actual audit findings. This turns the fairness report from a standalone artifact into something that speaks directly to the organisation's own written commitments.

3. **An Indian-context evaluation path.** Language benchmarks like CrowS-Pairs and BBQ are English-only. We include BharatBBQ, which was purpose-built to evaluate bias in Hindi, Marathi, Bengali, Tamil, Telugu, Odia, and Assamese, alongside English. This makes the product meaningful for the majority of users the Solution Challenge India track cares about, not just English-speaking ones.

The combination of deterministic fairness math, structured and validated AI narrative, governance-document awareness, and multilingual benchmarks is what turns a fairness notebook into an actual fairness audit system.

## Grounding in prior work

Our methodology builds on the bias-detection framework proposed by Iqbal and Ismail in *Unbiased AI for a Sovereign Digital Future: A Bias Detection Framework* (Procedia Computer Science 254, 2025). Their paper sets out a general, domain-agnostic approach to detecting whether a potentially biased attribute influences model predictions, via hypothesis testing on paired counterfactual outcomes. We take that framework, implement it as the counterfactual analysis module, extend it with standard disparity metrics from the Fairlearn and Vertex AI fairness documentation, and wrap the entire pipeline in an accessible product surface with an AI-generated, policy-aware report layer.

## Scope for Phase 1 submission

- Tabular audits on four benchmark datasets: Adult, ACSIncome, South German Credit, and COMPAS.
- NLP benchmark audits via BharatBBQ (primary) and BBQ / CrowS-Pairs as English comparisons.
- Policy document ingestion for PDFs up to 50 pages.
- Gemini-generated executive and technical fairness reports, validated before being returned.
- Persistent audit history in BigQuery, and a Looker Studio monitoring dashboard.
- A live Flutter web MVP that walks a user through upload, audit, and report review.

Out of scope for Phase 1, documented in the roadmap: Vertex AI Model Monitoring integration for scheduled re-audits, multi-tenant organisation accounts, custom-trained fairness classifiers, and cross-audit alerting.

## Alignment with the UN Sustainable Development Goals

- **SDG 10 (Reduced Inequalities):** primary alignment. NyayaLens is a tool for detecting and reducing inequalities baked into automated decision systems.
- **SDG 16 (Peace, Justice, and Strong Institutions):** secondary alignment. Institutions that can explain the fairness of their automated decisions are more accountable, more transparent, and more trustworthy.
- **SDG 5 (Gender Equality):** demonstrated alignment via our lending and hiring demo packs, both of which surface gender-based disparities and then show mitigation.

## One-line pitch

NyayaLens checks automated decision systems for unfair bias, explains the findings in language a policy officer can understand, and keeps a record so organisations can track fairness the same way they track security.
