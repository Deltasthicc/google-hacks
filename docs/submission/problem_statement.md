# Problem Statement

Automated decision systems now shape access to credit, jobs, welfare, healthcare, and education. When a model inherits historical bias from its training data, the people who were already disadvantaged continue to be disadvantaged, at machine speed and without a human in the loop to notice.

The tooling to detect this exists. Libraries like AIF360, Fairlearn, and Themis-ML can compute fairness metrics accurately. What does not exist, especially for Indian teams working with Indian-language models and Indian regulatory expectations, is an accessible product that:

1. Computes fairness metrics without asking the user to write a notebook.
2. Explains the results in language that a compliance officer can read and act on.
3. Checks those results against the organisation's own written policies.
4. Remembers what it has done so fairness becomes a practice, not a one-off check.
5. Supports the languages and contexts that matter to users outside of the English-speaking Global North.

NyayaLens is a fairness audit workspace that does all five. It is aimed at product teams, compliance officers, and civil-society researchers who need to inspect automated decision systems for hidden unfairness before those systems affect real people.

The design is grounded in the general bias-detection framework proposed by Iqbal and Ismail (Procedia Computer Science, 2025), extended with the standard disparity metrics documented in Fairlearn and Google Vertex AI, and wrapped in an accessible Google-native product stack.
