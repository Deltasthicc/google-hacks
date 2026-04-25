"""
Gemini integration for fairness report generation.

Uses the google-genai SDK (the unified SDK, not the deprecated
google-generativeai). Configures structured output against the
FairnessReport Pydantic schema so Gemini returns JSON that we can parse
directly.

Environment
-----------
The SDK reads the API key from GEMINI_API_KEY or GOOGLE_API_KEY. Or, for
Vertex AI deployments, GOOGLE_GENAI_USE_VERTEXAI=true plus the project
and location variables. Cloud Run in this project sets the first.

Retry policy
------------
One retry on validation failure, with stricter instructions appended. If
the second attempt still fails validation, we soft-repair and flag the
report as unverified.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from google import genai  # noqa: F401

from .prompts import (
    POLICY_EXTRACTION_RESPONSE_SCHEMA,
    POLICY_EXTRACTION_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    build_policy_extraction_prompt,
    build_report_prompt,
    dump_payload_for_logging,
)
from .schemas import (
    FairnessAuditPayload,
    FairnessReport,
    PolicyDocument,
    ReportMode,
)
from .validator import ValidationResult, soft_repair, validate_report

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_REPORT_MODEL = os.getenv("NYAYA_REPORT_MODEL", "gemini-2.5-pro")
DEFAULT_FAST_MODEL = os.getenv("NYAYA_FAST_MODEL", "gemini-2.5-flash")

# Gemini returns structured output when we pass response_schema. We derive
# the schema from the Pydantic FairnessReport model.
_REPORT_RESPONSE_SCHEMA = FairnessReport


# ---------------------------------------------------------------------------
# Result containers
# ---------------------------------------------------------------------------


@dataclass
class GenerationResult:
    report: FairnessReport
    validation: ValidationResult
    raw_response: str
    attempts: int
    model_used: str


# ---------------------------------------------------------------------------
# Client factory
# ---------------------------------------------------------------------------


def _make_client() -> "genai.Client":
    """
    Construct a Gen AI client. Supports both the Gemini Developer API path
    and Vertex AI, switched via environment variables.

    Imports the SDK lazily so the rest of the package (schemas, validator,
    exporters) is usable in environments without google-genai installed,
    e.g. unit tests and Person 3's notebooks.
    """
    from google import genai  # lazy import

    if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true":
        return genai.Client(
            vertexai=True,
            project=os.environ["GOOGLE_CLOUD_PROJECT"],
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )
    # Developer API path. SDK auto-reads GEMINI_API_KEY or GOOGLE_API_KEY.
    return genai.Client()


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def generate_report(
    payload: FairnessAuditPayload,
    mode: ReportMode = ReportMode.EXECUTIVE,
    client: "genai.Client | None" = None,
    model: str | None = None,
    max_retries: int = 1,
) -> GenerationResult:
    """
    Generate a validated fairness report from a fairness audit payload.

    The function returns a GenerationResult even if validation fails. The
    caller decides whether to serve the report, regenerate, or log and
    escalate based on validation.is_valid.
    """
    from google.genai import types as genai_types  # lazy import

    client = client or _make_client()
    model_name = model or DEFAULT_REPORT_MODEL

    logger.info(
        "generate_report start: %s",
        dump_payload_for_logging(payload),
    )

    user_prompt = build_report_prompt(payload, mode)
    config = genai_types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        response_mime_type="application/json",
        response_schema=_REPORT_RESPONSE_SCHEMA,
        temperature=0.3,  # Low temperature; faithfulness matters more than flair.
    )

    last_raw = ""
    last_report: FairnessReport | None = None
    last_validation: ValidationResult | None = None

    for attempt in range(1, max_retries + 2):
        response = client.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config=config,
        )
        last_raw = response.text or ""
        try:
            # google-genai populates response.parsed when response_schema
            # is a Pydantic model. We prefer that, falling back to JSON
            # parsing if parsed is unavailable.
            report = _coerce_to_report(response, payload, mode)
        except Exception as e:
            logger.warning(
                "attempt %d: could not parse response (%s). Retrying.",
                attempt,
                e,
            )
            user_prompt = _stricter_retry_prompt(user_prompt, str(e))
            continue

        validation = validate_report(report, payload)
        last_report = report
        last_validation = validation

        if validation.is_valid:
            logger.info(
                "generate_report success on attempt %d; %d warnings",
                attempt,
                len(validation.warnings),
            )
            return GenerationResult(
                report=report,
                validation=validation,
                raw_response=last_raw,
                attempts=attempt,
                model_used=model_name,
            )

        logger.warning(
            "attempt %d failed validation: %s",
            attempt,
            "; ".join(validation.errors),
        )
        user_prompt = _stricter_retry_prompt(
            user_prompt,
            "Validation failures: " + "; ".join(validation.errors),
        )

    # Out of retries. Soft-repair the last report and return with is_valid=False.
    assert last_report is not None and last_validation is not None
    repaired = soft_repair(last_report, payload)
    logger.error(
        "generate_report exhausted retries; returning soft-repaired report"
    )
    return GenerationResult(
        report=repaired,
        validation=last_validation,
        raw_response=last_raw,
        attempts=max_retries + 1,
        model_used=model_name,
    )


# ---------------------------------------------------------------------------
# Policy document extraction (optional multimodal step)
# ---------------------------------------------------------------------------


def extract_policy_rules(
    pdf_bytes: bytes,
    filename: str,
    client: "genai.Client | None" = None,
    model: str | None = None,
) -> PolicyDocument:
    """
    Extract fairness-relevant rules from an uploaded policy PDF.

    The output PolicyDocument can be attached to a FairnessAuditPayload
    before calling generate_report, which then populates policy_alignment.
    """
    from google.genai import types as genai_types  # lazy import

    client = client or _make_client()
    model_name = model or DEFAULT_FAST_MODEL  # flash is plenty for this task

    pdf_part = genai_types.Part.from_bytes(
        data=pdf_bytes, mime_type="application/pdf"
    )
    config = genai_types.GenerateContentConfig(
        system_instruction=POLICY_EXTRACTION_SYSTEM_PROMPT,
        response_mime_type="application/json",
        response_schema=POLICY_EXTRACTION_RESPONSE_SCHEMA,
        temperature=0.2,
    )

    response = client.models.generate_content(
        model=model_name,
        contents=[pdf_part, build_policy_extraction_prompt()],
        config=config,
    )
    raw = response.text or "{}"
    data = json.loads(raw)

    return PolicyDocument(
        filename=filename,
        mime_type="application/pdf",
        summary=data.get("summary"),
        extracted_rules=data.get("extracted_rules") or [],
    )


def extract_policy_rules_from_path(
    path: str | Path,
    client: "genai.Client | None" = None,
    model: str | None = None,
) -> PolicyDocument:
    """Convenience wrapper for reading a PDF off disk."""
    p = Path(path)
    return extract_policy_rules(
        pdf_bytes=p.read_bytes(),
        filename=p.name,
        client=client,
        model=model,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _coerce_to_report(
    response: Any,
    payload: FairnessAuditPayload,
    mode: ReportMode,
) -> FairnessReport:
    """
    Convert a Gemini response into a FairnessReport Pydantic model.

    Prefers response.parsed (populated when a Pydantic schema is passed),
    falls back to parsing response.text as JSON.
    """
    parsed = getattr(response, "parsed", None)
    if isinstance(parsed, FairnessReport):
        report = parsed
    else:
        raw = response.text or ""
        data = json.loads(raw)
        # Stamp audit_id, generated_at, and mode server-side so the model
        # cannot rewrite them. This prevents a whole class of subtle bugs.
        data["audit_id"] = payload.audit_id
        data["mode"] = mode.value
        data.setdefault("generated_at", datetime.now(timezone.utc).isoformat())
        report = FairnessReport.model_validate(data)

    # Always overwrite audit_id, mode, generated_at with authoritative values.
    return report.model_copy(
        update={
            "audit_id": payload.audit_id,
            "mode": mode,
            "generated_at": datetime.now(timezone.utc),
        }
    )


def _stricter_retry_prompt(original: str, problem: str) -> str:
    return (
        original
        + "\n\n"
        + f"PREVIOUS ATTEMPT FAILED. Reason: {problem}\n"
        + "Regenerate the report. Do not repeat the same mistake. "
        + "Only reference attributes, groups, and metrics that appear in "
        + "the payload above. Return JSON only."
    )
