from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

from app.ai_reports import (
    FairnessAuditPayload,
    FairnessReport,
    GenerationResult,
    ReportMode,
    RiskLevel,
    Severity,
    generate_report,
)
from app.ai_reports.schemas import FindingItem, ImpactedGroup, Recommendation
from app.utils.errors import ApiException

logger = logging.getLogger(__name__)


def _fallback_report(payload: FairnessAuditPayload, mode: ReportMode) -> FairnessReport:
    """Structured report when Gemini is unavailable or raises."""
    attr = payload.protected_attributes[0]
    disp = payload.metrics_before_mitigation.per_attribute[0].disparities
    dp = disp.demographic_parity_difference

    headline_metric_value = float(dp) if dp is not None else 0.05

    return FairnessReport(
        audit_id=payload.audit_id,
        generated_at=datetime.now(timezone.utc),
        mode=mode,
        plain_english_verdict=(
            "Fairness metrics were computed deterministically from your audit payload. "
            "Configure GEMINI_API_KEY or Vertex AI for full Gemini narratives."
        ),
        risk_level=RiskLevel.MODERATE,
        headline_findings=[
            FindingItem(
                title="Measured disparity (offline narrative)",
                severity=Severity.MEDIUM,
                metric_name="demographic_parity_difference",
                metric_value=headline_metric_value,
                threshold_used=0.10,
                explanation=(
                    "Values above come from Fairlearn on the held-out split; "
                    "see metrics_before_mitigation in the payload for details."
                ),
            )
        ],
        impacted_groups=[
            ImpactedGroup(
                attribute=attr.name,
                group=attr.groups[0],
                harm_type="under_approval",
                evidence="Compare per-group rates in the audit metrics tables.",
            )
        ],
        recommendations=[
            Recommendation(
                priority="short_term",
                action="Enable Gemini for AI-generated remediation text and risk scoring.",
                rationale="Offline mode lists metrics only.",
                owner_hint="ml_team",
            )
        ],
        caveats=[
            "Generated without Gemini API access; numeric results are still from Fairlearn.",
        ],
    )


def create_report(
    *,
    user_id: str,
    project_id: str,
    audit_id: str,
    mode: str,
    audit: dict[str, Any] | None,
) -> dict[str, Any]:
    """Generate a fairness report from a persisted audit and store it in Firestore."""
    from app.utils.ids import prefixed_id
    from app.services.firestore_service import save_document

    if not audit:
        raise ApiException(
            "AUDIT_REQUIRED",
            "Audit document is required.",
            status_code=400,
        )

    raw_payload = audit.get("fairness_audit_payload")
    if raw_payload is None:
        raise ApiException(
            "NO_FAIRNESS_PAYLOAD",
            "Run a data or model audit first so fairness metrics are available.",
            status_code=400,
        )

    payload = FairnessAuditPayload.model_validate(raw_payload)
    mode_enum = ReportMode.EXECUTIVE if mode == "executive" else ReportMode.TECHNICAL

    gen: GenerationResult | None = None
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        try:
            gen = generate_report(payload, mode_enum)
            report_model = gen.report
        except Exception:
            logger.exception("Gemini generate_report failed; using fallback narrative.")
            report_model = _fallback_report(payload, mode_enum)
    else:
        logger.warning("No Gemini API key set; returning deterministic fallback report.")
        report_model = _fallback_report(payload, mode_enum)

    if os.getenv("GOOGLE_CLOUD_PROJECT"):
        try:
            from app.ai_reports.bigquery_client import insert_audit

            insert_audit(payload, report_model)
        except Exception:
            logger.warning("BigQuery insert_audit skipped.", exc_info=True)

    report_status = "generated_fallback"
    if gen is not None:
        if gen.validation.is_valid:
            report_status = "generated"
        else:
            report_status = "generated_with_warnings"

    report_id = prefixed_id("report")
    document = {
        "report_id": report_id,
        "project_id": project_id,
        "audit_id": audit_id,
        "user_id": user_id,
        "status": report_status,
        "mode": mode,
        "created_at": datetime.now(timezone.utc),
        "report": report_model.model_dump(mode="json"),
        "generation_warnings": (
            gen.validation.warnings if gen else ["offline_fallback"]
        ),
    }
    return save_document("reports", report_id, document)
