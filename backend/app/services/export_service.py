from __future__ import annotations

from typing import Any

from app.schemas.common import utc_now
from app.services.firestore_service import save_document
from app.utils.ids import prefixed_id


def create_report(
    *,
    user_id: str,
    project_id: str,
    audit_id: str,
    mode: str,
    audit: dict[str, Any] | None,
) -> dict[str, Any]:
    """Create a placeholder report record.

    TODO(Person 4): replace the body with ai_reports.generate_report(payload,
    mode) once the audit payload from Person 3 matches the report contract.
    """
    report_id = prefixed_id("report")
    document = {
        "report_id": report_id,
        "project_id": project_id,
        "audit_id": audit_id,
        "user_id": user_id,
        "status": "generated_placeholder",
        "mode": mode,
        "created_at": utc_now(),
        "report": {
            "title": "NyayaLens Fairness Report",
            "summary": "Draft report generated from accepted audit metadata.",
            "audit_status": audit.get("status") if audit else "unknown",
            "findings": [],
            "recommendations": [
                "Connect Person 3 fairness payloads to Person 4 report generation."
            ],
        },
    }
    return save_document("reports", report_id, document)
