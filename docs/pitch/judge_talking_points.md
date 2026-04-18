# Judge Talking Points

Short, pre-rehearsed answers to the questions we expect from judges. Each one delivers a complete answer in under thirty seconds.

## "What does NyayaLens actually do?"

NyayaLens audits automated decision systems for unfair bias before they ship. A user uploads a dataset and optionally a policy document, picks the protected attributes, and the product computes fairness metrics, runs a counterfactual check, applies a mitigation method, and generates a plain-English report that a compliance officer can read and act on. Every audit is stored in BigQuery so teams can track fairness over time. The product is built end-to-end on Flutter, Firebase, Cloud Run, Gemini, and BigQuery.

## "How is this different from AIF360 or Fairlearn?"

AIF360 and Fairlearn are excellent libraries. We use both. What they are not is a product. They do not explain their results in language a non-engineer can read. They do not check the results against the organisation's own written policies. They do not remember what they did last week. NyayaLens sits on top of them to provide the explanation, the policy alignment, the audit history, and the Indian-language benchmark support that turn a fairness library into a fairness workspace.

## "Isn't it risky to have an AI write the fairness report?"

That is exactly the right question to ask, and the answer is in the architecture. The language model never computes a fairness metric. It receives a validated numeric payload and is only allowed to explain what that payload contains. Our validator strips any claim that references a group not present in the input, any metric name that was not actually measured, and any mitigation summary that does not match the mitigation that was actually run. The validator catches hallucinations deterministically, before the report reaches the user. The language model is a narrator. It is not allowed to be an analyst.

## "What makes this aligned with India specifically?"

Three things. First, our NLP benchmark suite includes BharatBBQ, which was built to evaluate bias in Hindi, Marathi, Bengali, Tamil, Telugu, Odia, Assamese, and English. Most fairness benchmarks are English only. Second, the policy-document feature is designed around the kinds of documents Indian organisations actually produce: RBI underwriting guidelines, UGC admission policies, EPFO eligibility rules. Third, our product framing speaks to Indian regulatory moments around automated decisioning in credit, welfare, and public services, not abstract Western examples.

## "Which SDG does this address?"

Primarily SDG 10, Reduced Inequalities. Secondarily SDG 16, Peace, Justice and Strong Institutions, because institutions that can explain their automated decisions are more accountable. And SDG 5, Gender Equality, because our demo pack explicitly surfaces gender-based disparities in lending and hiring and shows how mitigation closes them.

## "What Google technologies are you using and why?"

Flutter for the frontend: one codebase, web and mobile. Firebase for auth, Firestore, Storage, and Hosting because it is the fastest path to a live MVP. Cloud Run for our Python FastAPI backend because it is serverless and handles the heavy fairness-metric compute naturally. Gemini 2.5 Pro via the Google Gen AI SDK for report generation, Gemini 2.5 Flash for document parsing. BigQuery for audit history, partitioned by day and clustered by risk level. Looker Studio for the monitoring dashboard. Every piece earns its place by answering a specific product need.

## "Is this real or is this a mock?"

It is real. The live MVP is at [URL]. The GitHub repo is at [URL]. You can sign in with a Google account, upload the sample CSV in the repository, and run a full audit yourself. The numbers in our deck come from actual audit runs, not hand-filled examples.

## "What are you building next?"

Four roadmap items. Integration with Vertex AI Model Monitoring for scheduled re-audits. Multi-tenant organisation accounts with role-based access. Custom fairness classifier packs for specific domains like healthcare triage or insurance underwriting. And a Slack or email alerting channel that fires when severe audits exceed a threshold over a rolling window.

## "Who uses this tomorrow morning?"

A data-science lead at an NBFC who has to ship a credit model this quarter and needs a defensible fairness check. A compliance officer at a fintech who has to answer the board when someone asks "are our approvals fair across demographics." A civil-society researcher at an organisation like IDFC Institute or Centre for Internet and Society who wants to audit third-party models. Those three users are our Phase 1 target.

## "What is the single most defensible thing about the product?"

The validator. It is the line between a fairness tool and a fairness theatre. Our language model is structurally prevented from inventing findings, and every claim in the final report traces back to a specific computed number. That is the contract we make with the user, and the code enforces it automatically.

## "What is the paper you keep citing?"

Iqbal and Ismail, 2025, *Unbiased AI for a Sovereign Digital Future: A Bias Detection Framework*, published in Procedia Computer Science. They propose a general domain-agnostic method for detecting whether a potentially biased attribute influences model predictions, via hypothesis testing on paired counterfactual outcomes. Our counterfactual module implements their framework directly, and the product wraps that implementation in an accessible workflow.

## "If we could build only one more thing, what would it be?"

Continuous monitoring with alerting. The audit history is already there. What is missing is the push-notification leg: when a model's fairness posture degrades on a scheduled re-audit, a Slack message arrives in the compliance channel. That one feature would turn the product from a pre-deployment check into a post-deployment guardrail.
