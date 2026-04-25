"""
Tests for the ai_reports module.

These tests cover the parts of the pipeline that do not require a live
Gemini key:

- Schema parsing of both sample payloads.
- Validator catches hallucinated groups, metrics, and mitigation claims.
- Validator consistency checks fire when risk level mismatches findings.
- Exporters produce non-empty Markdown and HTML for executive and
  technical modes.
- bigquery_client.build_audit_history_row flattens a payload plus report
  into the BigQuery row schema without error.

The live generate_report call is covered by a separate integration test
that is skipped unless GEMINI_API_KEY is set.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.ai_reports import (
    FairnessAuditPayload,
    FairnessReport,
    ReportMode,
    RiskLevel,
    Severity,
    bundle_exports,
    soft_repair,
    to_html,
    to_json,
    to_markdown,
    validate_report,
)
from app.ai_reports.bigquery_client import build_audit_history_row
from app.ai_reports.schemas import (
    FindingItem,
    ImpactedGroup,
    MitigationSummary,
    Recommendation,
)

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "ai_reports" / "samples"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def lending_payload() -> FairnessAuditPayload:
    data = json.loads((SAMPLES_DIR / "lending_sample.json").read_text())
    return FairnessAuditPayload.model_validate(data)


@pytest.fixture
def hiring_payload() -> FairnessAuditPayload:
    data = json.loads((SAMPLES_DIR / "hiring_sample.json").read_text())
    return FairnessAuditPayload.model_validate(data)


def _make_good_report(payload: FairnessAuditPayload, mode: ReportMode) -> FairnessReport:
    """Build a hand-rolled, internally consistent report for the given payload."""
    attr = payload.protected_attributes[0]
    group = attr.groups[0]
    return FairnessReport(
        audit_id=payload.audit_id,
        generated_at=datetime.now(timezone.utc),
        mode=mode,
        plain_english_verdict=(
            "The model shows a meaningful disparity in approval rates across "
            "the protected attribute and warrants review before deployment."
        ),
        risk_level=RiskLevel.HIGH,
        headline_findings=[
            FindingItem(
                title="Approval rate gap",
                severity=Severity.HIGH,
                metric_name="demographic_parity_difference",
                metric_value=0.19,
                threshold_used=0.10,
                explanation=(
                    "The gap in positive-prediction rates between groups "
                    "exceeds the conventional 10 percentage-point threshold."
                ),
            )
        ],
        impacted_groups=[
            ImpactedGroup(
                attribute=attr.name,
                group=group,
                harm_type="under_approval",
                evidence="Lower approval rate observed for this group.",
            )
        ],
        mitigation_summary=(
            MitigationSummary(
                method="reweighing",
                fairness_improvement="Gap reduced to within threshold.",
                utility_cost="Minor accuracy loss.",
            )
            if payload.metrics_after_mitigation is not None
            else None
        ),
        recommendations=[
            Recommendation(
                priority="immediate",
                action="Apply reweighing mitigation before deployment",
                rationale="Closes the observed disparity at a small utility cost",
                owner_hint="ml_team",
            )
        ],
        caveats=["This audit uses a benchmark dataset and may not reflect production data."],
    )


# ---------------------------------------------------------------------------
# Schema parsing
# ---------------------------------------------------------------------------


def test_lending_sample_parses(lending_payload: FairnessAuditPayload):
    assert lending_payload.audit_id == "aud_demo_lending_2026_04_17_001"
    assert lending_payload.dataset.name == "SouthGermanCredit"
    assert [a.name for a in lending_payload.protected_attributes] == ["gender"]
    assert lending_payload.metrics_after_mitigation is not None
    assert lending_payload.counterfactuals is not None


def test_hiring_sample_parses(hiring_payload: FairnessAuditPayload):
    assert hiring_payload.audit_id == "aud_demo_hiring_2026_04_17_002"
    assert hiring_payload.dataset.name == "Adult"
    assert {a.name for a in hiring_payload.protected_attributes} == {"sex", "race"}


def test_schema_rejects_unknown_fields():
    data = json.loads((SAMPLES_DIR / "lending_sample.json").read_text())
    data["unexpected_field"] = "should fail"
    with pytest.raises(Exception):
        FairnessAuditPayload.model_validate(data)


def test_schema_rejects_empty_protected_attributes():
    data = json.loads((SAMPLES_DIR / "lending_sample.json").read_text())
    data["protected_attributes"] = []
    with pytest.raises(Exception):
        FairnessAuditPayload.model_validate(data)


def test_schema_rejects_unknown_data_quality_flag():
    data = json.loads((SAMPLES_DIR / "lending_sample.json").read_text())
    data["data_quality_flags"] = [
        {"flag": "made_up_flag", "attribute": "gender", "severity": "medium"}
    ]
    with pytest.raises(Exception):
        FairnessAuditPayload.model_validate(data)


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------


def test_validator_accepts_a_good_report(lending_payload: FairnessAuditPayload):
    report = _make_good_report(lending_payload, ReportMode.EXECUTIVE)
    result = validate_report(report, lending_payload)
    assert result.is_valid, f"Expected valid, got errors: {result.errors}"


def test_validator_rejects_unknown_group(lending_payload: FairnessAuditPayload):
    report = _make_good_report(lending_payload, ReportMode.EXECUTIVE)
    report.impacted_groups[0].group = "Nonbinary"  # not in the payload
    result = validate_report(report, lending_payload)
    assert not result.is_valid
    assert any("unknown group" in e for e in result.errors)


def test_validator_rejects_unknown_metric(lending_payload: FairnessAuditPayload):
    report = _make_good_report(lending_payload, ReportMode.EXECUTIVE)
    report.headline_findings[0].metric_name = "made_up_metric"
    result = validate_report(report, lending_payload)
    assert not result.is_valid
    assert any("not present in the input" in e for e in result.errors)


def test_validator_rejects_mitigation_claim_without_evidence(
    lending_payload: FairnessAuditPayload,
):
    no_mitigation = lending_payload.model_copy(update={"metrics_after_mitigation": None})
    report = _make_good_report(lending_payload, ReportMode.EXECUTIVE)
    # Mitigation was populated by the helper, so this claim is now unfounded
    result = validate_report(report, no_mitigation)
    assert not result.is_valid
    assert any("mitigation_summary" in e for e in result.errors)


def test_validator_rejects_audit_id_mismatch(lending_payload: FairnessAuditPayload):
    report = _make_good_report(lending_payload, ReportMode.EXECUTIVE)
    report = report.model_copy(update={"audit_id": "wrong_id"})
    result = validate_report(report, lending_payload)
    assert not result.is_valid
    assert any("audit_id" in e for e in result.errors)


def test_validator_warns_when_risk_level_mismatches_severity(
    lending_payload: FairnessAuditPayload,
):
    report = _make_good_report(lending_payload, ReportMode.EXECUTIVE)
    report = report.model_copy(update={"risk_level": RiskLevel.MINIMAL})
    result = validate_report(report, lending_payload)
    assert any("risk_level" in w for w in result.warnings)


def test_soft_repair_strips_offending_groups(lending_payload: FairnessAuditPayload):
    report = _make_good_report(lending_payload, ReportMode.EXECUTIVE)
    report.impacted_groups.append(
        ImpactedGroup(
            attribute="gender",
            group="Nonbinary",
            harm_type="under_approval",
            evidence="Fabricated evidence.",
        )
    )
    repaired = soft_repair(report, lending_payload)
    group_names = {ig.group for ig in repaired.impacted_groups}
    assert "Nonbinary" not in group_names
    assert len(repaired.impacted_groups) >= 1


# ---------------------------------------------------------------------------
# Exporters
# ---------------------------------------------------------------------------


def test_markdown_executive_contains_verdict(lending_payload: FairnessAuditPayload):
    report = _make_good_report(lending_payload, ReportMode.EXECUTIVE)
    md = to_markdown(report)
    assert "Fairness Report (Executive)" in md
    assert "Verdict" in md
    assert report.plain_english_verdict in md


def test_markdown_technical_uses_metric_table(lending_payload: FairnessAuditPayload):
    report = _make_good_report(lending_payload, ReportMode.TECHNICAL)
    md = to_markdown(report)
    assert "Fairness Report (Technical)" in md
    assert "| # | Finding |" in md
    assert "demographic_parity_difference" in md


def test_html_export_is_self_contained(lending_payload: FairnessAuditPayload):
    report = _make_good_report(lending_payload, ReportMode.EXECUTIVE)
    html = to_html(report)
    assert html.startswith("<!doctype html>")
    assert "</html>" in html
    assert "<style>" in html
    assert report.plain_english_verdict in html


def test_json_export_round_trips(lending_payload: FairnessAuditPayload):
    report = _make_good_report(lending_payload, ReportMode.EXECUTIVE)
    data = json.loads(to_json(report))
    assert data["audit_id"] == report.audit_id
    assert data["mode"] == "executive"
    assert len(data["headline_findings"]) == 1


def test_bundle_exports_has_all_three_formats(lending_payload: FairnessAuditPayload):
    report = _make_good_report(lending_payload, ReportMode.EXECUTIVE)
    bundle = bundle_exports(report)
    assert set(bundle.keys()) == {"json", "markdown", "html"}
    for fmt, content in bundle.items():
        assert len(content) > 100, f"{fmt} export is suspiciously short"


# ---------------------------------------------------------------------------
# BigQuery row flattening
# ---------------------------------------------------------------------------


def test_build_audit_history_row_lending(lending_payload: FairnessAuditPayload):
    report = _make_good_report(lending_payload, ReportMode.EXECUTIVE)
    row = build_audit_history_row(lending_payload, report)
    assert row.audit_id == lending_payload.audit_id
    assert row.dataset_name == "SouthGermanCredit"
    assert row.risk_level == RiskLevel.HIGH
    assert row.mitigation_method == "reweighing"
    assert "per_attribute" in row.metrics_before
    assert row.metrics_after is not None


def test_build_audit_history_row_no_mitigation(lending_payload: FairnessAuditPayload):
    no_mitigation = lending_payload.model_copy(update={"metrics_after_mitigation": None})
    report = _make_good_report(lending_payload, ReportMode.EXECUTIVE)
    report = report.model_copy(update={"mitigation_summary": None})
    row = build_audit_history_row(no_mitigation, report)
    assert row.mitigation_method is None
    assert row.metrics_after is None


# ---------------------------------------------------------------------------
# Live integration test (skipped without an API key)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")),
    reason="Requires a live Gemini API key",
)
def test_live_generation(lending_payload: FairnessAuditPayload):
    """End-to-end smoke test against a live Gemini endpoint."""
    from app.ai_reports import generate_report

    result = generate_report(lending_payload, mode=ReportMode.EXECUTIVE)
    assert result.report.audit_id == lending_payload.audit_id
    assert result.report.mode == ReportMode.EXECUTIVE
    assert len(result.report.headline_findings) >= 1
    assert len(result.report.recommendations) >= 1
