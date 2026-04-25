"""
Validator for AI-generated fairness reports.

Gemini produces structured JSON, but structure alone is not enough. The
validator catches three classes of failure:

1. Shape failures: missing required fields, wrong enum values. These are
   handled by Pydantic parsing in schemas.FairnessReport. This module does
   NOT re-do shape checks.
2. Faithfulness failures: the report mentions a group that was not in the
   input, or claims mitigation when none was run, or names a metric that
   is null in the payload. These are the important checks. We catch them
   here and either reject the report or strip the offending fields.
3. Consistency failures: risk_level does not match the severity of the
   findings, or the verdict contradicts the findings, or mitigation is
   claimed when metrics_after_mitigation is null.

Validator output is a ValidationResult. If is_valid is False, the caller
should regenerate (one retry) rather than blindly serve the report.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .schemas import (
    FairnessAuditPayload,
    FairnessReport,
    RiskLevel,
    Severity,
)


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def fail(self, msg: str) -> None:
        self.is_valid = False
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


# ---------------------------------------------------------------------------
# Faithfulness checks
# ---------------------------------------------------------------------------


def _allowed_attributes(payload: FairnessAuditPayload) -> set[str]:
    return {a.name for a in payload.protected_attributes}


def _allowed_groups(payload: FairnessAuditPayload) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for attr in payload.protected_attributes:
        for group in attr.groups:
            pairs.add((attr.name, group))
    # Also include any groups seen in per_group blocks (in case of
    # intersections or finer-grained group labels from the ML layer).
    for block in payload.metrics_before_mitigation.per_attribute:
        for g in block.per_group:
            pairs.add((block.attribute, g.group))
    return pairs


def _metrics_present(payload: FairnessAuditPayload) -> set[str]:
    """Which disparity metric names are actually non-null in the input."""
    present: set[str] = set()
    for block in payload.metrics_before_mitigation.per_attribute:
        d = block.disparities.model_dump()
        for name, value in d.items():
            if value is not None:
                present.add(name)
    return present


# ---------------------------------------------------------------------------
# Consistency checks
# ---------------------------------------------------------------------------


_SEVERITY_TO_RISK_FLOOR = {
    Severity.LOW: {RiskLevel.MINIMAL, RiskLevel.LOW, RiskLevel.MODERATE},
    Severity.MEDIUM: {RiskLevel.LOW, RiskLevel.MODERATE, RiskLevel.HIGH},
    Severity.HIGH: {RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.SEVERE},
}


def _risk_consistent_with_findings(report: FairnessReport) -> bool:
    """Risk level should sit within a band matching the worst finding severity."""
    if not report.headline_findings:
        return False
    worst = max(
        report.headline_findings,
        key=lambda f: {"low": 0, "medium": 1, "high": 2}[f.severity.value],
    ).severity
    return report.risk_level in _SEVERITY_TO_RISK_FLOOR[worst]


# ---------------------------------------------------------------------------
# Top-level validate() entrypoint
# ---------------------------------------------------------------------------


def validate_report(
    report: FairnessReport,
    payload: FairnessAuditPayload,
) -> ValidationResult:
    """Run all checks. Returns a ValidationResult with errors and warnings."""
    result = ValidationResult(is_valid=True)

    # 1. audit_id must match
    if report.audit_id != payload.audit_id:
        result.fail(
            f"report.audit_id '{report.audit_id}' does not match "
            f"payload.audit_id '{payload.audit_id}'"
        )

    allowed_attrs = _allowed_attributes(payload)
    allowed_pairs = _allowed_groups(payload)
    present_metrics = _metrics_present(payload)

    # 2. impacted_groups must reference real attributes and groups
    for ig in report.impacted_groups:
        if ig.attribute not in allowed_attrs:
            result.fail(
                f"impacted_groups references unknown attribute '{ig.attribute}'"
            )
        elif (ig.attribute, ig.group) not in allowed_pairs:
            result.fail(
                f"impacted_groups references unknown group "
                f"'{ig.group}' under attribute '{ig.attribute}'"
            )

    # 3. findings that name a metric must name one that exists in the input
    for f in report.headline_findings:
        if f.metric_name is not None and f.metric_name not in present_metrics:
            result.fail(
                f"finding '{f.title}' names metric '{f.metric_name}' "
                f"which is not present in the input payload"
            )

    # 4. mitigation claim consistency
    has_mitigation_input = payload.metrics_after_mitigation is not None
    claims_mitigation = report.mitigation_summary is not None
    if claims_mitigation and not has_mitigation_input:
        result.fail(
            "report includes mitigation_summary but no metrics_after_mitigation "
            "were provided in the payload"
        )
    if has_mitigation_input and not claims_mitigation:
        result.warn(
            "mitigated metrics were provided but the report did not populate "
            "mitigation_summary"
        )

    # 5. counterfactual claim consistency
    has_cf_input = payload.counterfactuals is not None
    claims_cf = report.counterfactual_insight is not None
    if claims_cf and not has_cf_input:
        result.fail(
            "report includes counterfactual_insight but no counterfactuals "
            "were provided"
        )

    # 6. policy alignment consistency
    has_policy_input = payload.policy_document is not None
    claims_policy = report.policy_alignment is not None
    if claims_policy and not has_policy_input:
        result.fail(
            "report includes policy_alignment but no policy_document was "
            "provided"
        )

    # 7. risk level consistency with findings
    if not _risk_consistent_with_findings(report):
        result.warn(
            f"risk_level '{report.risk_level.value}' does not match the worst "
            f"finding severity; consider regenerating"
        )

    # 8. verdict sanity
    if len(report.plain_english_verdict.strip()) < 20:
        result.fail("plain_english_verdict is too short to be meaningful")

    # 9. recommendations sanity
    for rec in report.recommendations:
        if len(rec.action.strip()) < 10 or len(rec.rationale.strip()) < 10:
            result.fail(
                f"recommendation '{rec.action[:30]}...' has an action or "
                f"rationale that is too short to be useful"
            )

    return result


# ---------------------------------------------------------------------------
# Soft repair: strip offending fields instead of failing hard
# ---------------------------------------------------------------------------


def soft_repair(
    report: FairnessReport,
    payload: FairnessAuditPayload,
) -> FairnessReport:
    """
    Strip any impacted_groups or findings that fail faithfulness checks,
    without failing the whole report. Use this for non-critical fields
    where the best action is to drop the offending item.
    """
    allowed_pairs = _allowed_groups(payload)
    present_metrics = _metrics_present(payload)

    kept_groups = [
        ig for ig in report.impacted_groups if (ig.attribute, ig.group) in allowed_pairs
    ]
    kept_findings = [
        f
        for f in report.headline_findings
        if f.metric_name is None or f.metric_name in present_metrics
    ]

    if not kept_findings:
        # Keep the original findings if stripping would leave us empty.
        # The caller should mark the report as suspect.
        kept_findings = report.headline_findings

    return report.model_copy(
        update={
            "impacted_groups": kept_groups,
            "headline_findings": kept_findings,
        }
    )
