"""
Prompt templates for Gemini report generation.

Design notes
------------
We never ask Gemini to compute fairness metrics. Gemini is given a
pre-validated metrics JSON and asked to explain it, never to invent it.
The prompts enforce this by:

1. Stating what Gemini may and may not do, in the system prompt.
2. Passing the metrics payload verbatim, as JSON.
3. Declaring the exact JSON schema Gemini must return.

We support two modes, Executive and Technical. Both produce the same
FairnessReport schema on output, but the *style* guidance differs so the
plain_english_verdict, explanations, and recommendations read differently.

A third, optional prompt (extract_policy_rules) is used when a governance
document is uploaded alongside the audit.
"""

from __future__ import annotations

import json
from typing import Any

from .schemas import FairnessAuditPayload, ReportMode

# ---------------------------------------------------------------------------
# System prompt (shared across modes)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are NyayaLens, a structured fairness-report assistant. You receive a
validated JSON payload of fairness metrics from a machine learning audit and
produce a single structured JSON report.

Your job is narrow and important:

1. Explain what the metrics show, in plain language, without inventing numbers.
2. Identify which groups are most affected, grounded in the per-group numbers.
3. Summarize whether mitigation helped, if mitigation metrics are provided.
4. Recommend concrete next steps, labeled by priority and owner.
5. Call out tradeoffs, caveats, and anything the metrics cannot tell you.

Hard rules:

- Never invent metric values. If a metric is null in the input, treat it as
  unmeasured and say so explicitly. Do not estimate, approximate, or guess.
- Never invent groups. Only refer to groups listed under protected_attributes
  or present in per_group blocks.
- Never claim causation from correlational metrics. Use language like
  "the model's predictions differ across groups" rather than "the model
  discriminates because of X."
- Never fill fields with generic filler. If you have nothing substantive to
  say for a field, omit it or set it to null where the schema allows.
- The report must be internally consistent: the risk_level should match the
  severity of the headline findings and the verdict.
- Keep the plain_english_verdict to two or three short sentences. A non-
  technical reader should grasp the outcome from that field alone.

Output:

You must return a single JSON object that conforms exactly to the provided
response schema. No prose before or after the JSON. No markdown fences.
"""


# ---------------------------------------------------------------------------
# Mode-specific style guidance
# ---------------------------------------------------------------------------

_EXECUTIVE_STYLE = """\
Style for this report: EXECUTIVE.

- Write the verdict and explanations for a non-technical reader (a policy
  officer, compliance lead, or executive sponsor).
- Prefer plain-language names over metric jargon. Say "approval rate gap"
  instead of "demographic_parity_difference."
- Explanations for each finding should be one short paragraph.
- Recommendations should focus on business action, not on algorithms.
- Keep caveats concise. Two or three is enough.
"""

_TECHNICAL_STYLE = """\
Style for this report: TECHNICAL.

- Write for an ML engineer or data scientist.
- Use the canonical metric names in findings (demographic_parity_difference,
  equal_opportunity_difference, equalized_odds_difference,
  disparate_impact_ratio). Always pair metric_name with metric_value.
- Explanations can reference thresholds, sample sizes, and metric
  interactions. Call out when a metric is unreliable due to small support.
- Recommendations can include algorithmic mitigation methods (reweighing,
  threshold tuning, adversarial debiasing) where appropriate.
- Caveats should be specific and plural: sample size limits, proxy risk,
  non-stationarity of the data, and so on.
"""


# ---------------------------------------------------------------------------
# Report generation prompt builder
# ---------------------------------------------------------------------------


def build_report_prompt(
    payload: FairnessAuditPayload,
    mode: ReportMode,
) -> str:
    """
    Build the user-turn prompt for a fairness report.

    The system prompt is sent separately via the SDK's system_instruction
    parameter. This function builds the user message only.
    """
    style_block = (
        _EXECUTIVE_STYLE if mode == ReportMode.EXECUTIVE else _TECHNICAL_STYLE
    )

    payload_json = payload.model_dump_json(indent=2)

    # If a policy document was supplied, nudge Gemini to populate
    # policy_alignment. Otherwise explicitly tell it to omit that field.
    policy_hint = (
        "A policy document was supplied in the payload. Populate the "
        "policy_alignment block, grounding each gap in a specific rule from "
        "policy_document.extracted_rules."
        if payload.policy_document is not None
        else "No policy document was supplied. Set policy_alignment to null."
    )

    # Similarly hint for mitigation and counterfactuals.
    mitigation_hint = (
        "Mitigated metrics are present. Populate mitigation_summary, "
        "compare before and after, and acknowledge any utility_cost."
        if payload.metrics_after_mitigation is not None
        else "No mitigated metrics were supplied. Set mitigation_summary to null "
        "and flag in recommendations that mitigation should be run next."
    )

    counterfactual_hint = (
        "Counterfactual results are present. Summarize what they imply in "
        "counterfactual_insight. Be cautious: counterfactuals over protected "
        "attributes are a correlational signal, not proof of causation."
        if payload.counterfactuals is not None
        else "No counterfactual results were supplied. Set counterfactual_insight "
        "to null."
    )

    return f"""\
{style_block}

Audit payload (validated, do not modify):

```json
{payload_json}
```

Additional guidance for this specific audit:

- {mitigation_hint}
- {counterfactual_hint}
- {policy_hint}

Generate the fairness report JSON now.
"""


# ---------------------------------------------------------------------------
# Policy document prompt
# ---------------------------------------------------------------------------

POLICY_EXTRACTION_SYSTEM_PROMPT = """\
You read governance, policy, or model-card documents. You extract the
fairness-relevant rules the document imposes, with no embellishment.

Return a JSON object with two fields:

- summary: a two-sentence plain-language summary of the document's purpose.
- extracted_rules: a list of short, declarative rules that the model or
  dataset under audit would need to satisfy. Each rule is one sentence.
  Only rules that can be checked against a fairness audit are relevant.
  Skip organizational boilerplate, disclaimers, and brand language.

Do not invent rules not stated in the document. If the document does not
contain fairness-relevant rules, return extracted_rules as an empty list.
"""


POLICY_EXTRACTION_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "summary": {"type": "STRING"},
        "extracted_rules": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
        },
    },
    "required": ["summary", "extracted_rules"],
}


def build_policy_extraction_prompt() -> str:
    """User turn for the policy-extraction call. The PDF is attached as a part."""
    return (
        "Read the attached policy or model-card document. Extract fairness "
        "rules following the schema. Return JSON only."
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def dump_payload_for_logging(payload: FairnessAuditPayload) -> str:
    """Compact representation for logs. Never used as prompt input."""
    return json.dumps(
        {
            "audit_id": payload.audit_id,
            "dataset": payload.dataset.name,
            "model": payload.model.name,
            "protected_attributes": [p.name for p in payload.protected_attributes],
            "has_mitigation": payload.metrics_after_mitigation is not None,
            "has_counterfactuals": payload.counterfactuals is not None,
            "has_policy_doc": payload.policy_document is not None,
        }
    )
