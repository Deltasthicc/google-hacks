"""
ai_reports: NyayaLens AI-powered fairness reporting.

Public API:
    - FairnessAuditPayload: input from the ML layer
    - FairnessReport:       validated output
    - generate_report:      Gemini call, with validation and retry
    - extract_policy_rules: optional multimodal policy-doc step
    - to_json / to_markdown / to_html / bundle_exports: renderers
    - validate_report:      standalone validator
"""

from .exporters import bundle_exports, to_html, to_json, to_markdown
from .generator import (
    GenerationResult,
    extract_policy_rules,
    extract_policy_rules_from_path,
    generate_report,
)
from .schemas import (
    AuditHistoryRow,
    FairnessAuditPayload,
    FairnessReport,
    PolicyDocument,
    ReportMode,
    RiskLevel,
    Severity,
    TaskType,
)
from .validator import ValidationResult, soft_repair, validate_report

__all__ = [
    "AuditHistoryRow",
    "FairnessAuditPayload",
    "FairnessReport",
    "GenerationResult",
    "PolicyDocument",
    "ReportMode",
    "RiskLevel",
    "Severity",
    "TaskType",
    "ValidationResult",
    "bundle_exports",
    "extract_policy_rules",
    "extract_policy_rules_from_path",
    "generate_report",
    "soft_repair",
    "to_html",
    "to_json",
    "to_markdown",
    "validate_report",
]
