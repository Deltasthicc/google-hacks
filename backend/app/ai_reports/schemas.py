"""
Pydantic schemas for AI-generated fairness reports.

This module defines two families of models:

1. Input models: the payload the ML layer (Person 3) produces. These mirror
   the contract in docs/research/fairness_payload_contract.md.
2. Output models: the structured report Gemini produces, after validation.

Both are strict. Unknown fields are rejected on inputs. Numeric fields are
checked for sane ranges. Anything that does not parse cleanly fails loudly,
which is the behavior we want: a fairness report silently dropping a field
is worse than no report at all.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# Enums and constrained vocabularies
# ---------------------------------------------------------------------------


class TaskType(str, Enum):
    TABULAR_CLASSIFICATION = "tabular_classification"
    TABULAR_REGRESSION = "tabular_regression"
    TEXT_CLASSIFICATION = "text_classification"
    MULTIMODAL = "multimodal"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskLevel(str, Enum):
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


class ReportMode(str, Enum):
    """Two rendering styles driven by the same underlying report JSON."""

    EXECUTIVE = "executive"
    TECHNICAL = "technical"


DATA_QUALITY_FLAG_VOCAB = {
    "subgroup_underrepresentation",
    "positive_label_imbalance",
    "missingness_by_group",
    "proxy_correlation",
    "outcome_imbalance",
    "small_sample_group",
}


# ---------------------------------------------------------------------------
# Input payload models (from the ML layer)
# ---------------------------------------------------------------------------


class StrictModel(BaseModel):
    """Base class: reject unknown fields on inputs, strip whitespace from strings."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class DatasetInfo(StrictModel):
    name: str
    source: str | None = None
    n_rows: int | None = Field(default=None, ge=0)
    n_features: int | None = Field(default=None, ge=0)
    task_type: TaskType
    target_column: str | None = None
    positive_label: Any | None = None
    notes: str | None = None


class ModelInfo(StrictModel):
    name: str
    family: str | None = None
    framework: str | None = None
    hyperparameters: dict[str, Any] | None = None
    version: str | None = None


class ProtectedAttribute(StrictModel):
    name: str
    type: Literal["binary", "categorical", "continuous"]
    groups: list[str]
    reference_group: str | None = None

    @field_validator("groups")
    @classmethod
    def groups_non_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("protected attribute must declare at least one group")
        return v


class OverallPerformance(StrictModel):
    accuracy: float | None = Field(default=None, ge=0, le=1)
    precision: float | None = Field(default=None, ge=0, le=1)
    recall: float | None = Field(default=None, ge=0, le=1)
    f1: float | None = Field(default=None, ge=0, le=1)
    auc_roc: float | None = Field(default=None, ge=0, le=1)


class PerGroupMetric(StrictModel):
    group: str
    positive_prediction_rate: float | None = Field(default=None, ge=0, le=1)
    true_positive_rate: float | None = Field(default=None, ge=0, le=1)
    false_positive_rate: float | None = Field(default=None, ge=0, le=1)
    accuracy: float | None = Field(default=None, ge=0, le=1)
    support: int | None = Field(default=None, ge=0)


class DisparityMetrics(StrictModel):
    demographic_parity_difference: float | None = None
    equal_opportunity_difference: float | None = None
    equalized_odds_difference: float | None = None
    disparate_impact_ratio: float | None = Field(default=None, ge=0)


class PerAttributeMetrics(StrictModel):
    attribute: str
    per_group: list[PerGroupMetric]
    disparities: DisparityMetrics


class IntersectionalMetrics(StrictModel):
    attributes: list[str]
    per_group: list[PerGroupMetric]
    worst_disparity: float | None = None


class MetricsBlock(StrictModel):
    per_attribute: list[PerAttributeMetrics]
    intersectional: list[IntersectionalMetrics] | None = None


class MitigatedMetricsBlock(MetricsBlock):
    mitigation_method: str
    utility_cost: dict[str, float] | None = None


class CounterfactualExample(StrictModel):
    record_id: str
    features_summary: str
    original_group: str
    flipped_group: str
    original_prediction: Any
    flipped_prediction: Any


class CounterfactualBlock(StrictModel):
    attribute_flipped: str
    n_samples_tested: int = Field(ge=0)
    n_predictions_changed: int = Field(ge=0)
    proportion_changed: float = Field(ge=0, le=1)
    examples: list[CounterfactualExample] = Field(default_factory=list)


class NLPBenchmarks(BaseModel):
    """NLP benchmark shapes vary across benchmarks, so allow extra keys here."""

    model_config = ConfigDict(extra="allow")
    bharatbbq: dict[str, Any] | None = None
    crows_pairs: dict[str, Any] | None = None
    bbq: dict[str, Any] | None = None
    stereoset: dict[str, Any] | None = None


class DataQualityFlag(StrictModel):
    flag: str
    attribute: str | None = None
    group: str | None = None
    severity: Severity

    @field_validator("flag")
    @classmethod
    def flag_in_vocab(cls, v: str) -> str:
        if v not in DATA_QUALITY_FLAG_VOCAB:
            raise ValueError(
                f"unknown data quality flag '{v}'. "
                f"Allowed: {sorted(DATA_QUALITY_FLAG_VOCAB)}"
            )
        return v


class PolicyDocument(StrictModel):
    """Optional multimodal input: a governance or policy document."""

    filename: str
    mime_type: str = "application/pdf"
    extracted_rules: list[str] | None = None
    summary: str | None = None


class FairnessAuditPayload(StrictModel):
    """The top-level input produced by the ML layer."""

    audit_id: str
    created_at: datetime
    project_id: str | None = None
    user_id: str | None = None
    dataset: DatasetInfo
    model: ModelInfo
    protected_attributes: list[ProtectedAttribute]
    overall_performance: OverallPerformance | None = None
    metrics_before_mitigation: MetricsBlock
    metrics_after_mitigation: MitigatedMetricsBlock | None = None
    counterfactuals: CounterfactualBlock | None = None
    nlp_benchmarks: NLPBenchmarks | None = None
    data_quality_flags: list[DataQualityFlag] = Field(default_factory=list)
    policy_document: PolicyDocument | None = None
    notes: str | None = None

    @field_validator("protected_attributes")
    @classmethod
    def at_least_one_attr(cls, v: list[ProtectedAttribute]) -> list[ProtectedAttribute]:
        if not v:
            raise ValueError("at least one protected attribute is required")
        return v


# ---------------------------------------------------------------------------
# Output report models (what Gemini returns, after validation)
# ---------------------------------------------------------------------------


class ImpactedGroup(BaseModel):
    """A group shown to be harmed by the model's decisions."""

    model_config = ConfigDict(extra="ignore")
    attribute: str
    group: str
    harm_type: Literal[
        "under_approval",
        "over_denial",
        "quality_of_service",
        "stereotype_reinforcement",
        "representation",
    ]
    evidence: str  # short factual statement grounded in the metrics


class FindingItem(BaseModel):
    """A single substantive fairness finding, with evidence."""

    model_config = ConfigDict(extra="ignore")
    title: str
    severity: Severity
    metric_name: str | None = None
    metric_value: float | None = None
    threshold_used: float | None = None
    explanation: str


class MitigationSummary(BaseModel):
    model_config = ConfigDict(extra="ignore")
    method: str
    fairness_improvement: str
    utility_cost: str
    residual_concerns: str | None = None


class Recommendation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    priority: Literal["immediate", "short_term", "long_term"]
    action: str
    rationale: str
    owner_hint: Literal["data_team", "ml_team", "policy_team", "product_team"] | None = None


class PolicyAlignmentBlock(BaseModel):
    """Only populated when a policy document was supplied on input."""

    model_config = ConfigDict(extra="ignore")
    document_name: str
    rules_considered: list[str]
    alignment_verdict: Literal["aligned", "partial", "misaligned"]
    gaps: list[str] = Field(default_factory=list)


class FairnessReport(BaseModel):
    """Structured report. Rendered into Executive or Technical Markdown downstream."""

    model_config = ConfigDict(extra="ignore")
    audit_id: str
    generated_at: datetime
    report_version: str = "1.0.0"
    mode: ReportMode
    plain_english_verdict: str
    risk_level: RiskLevel
    headline_findings: list[FindingItem]
    impacted_groups: list[ImpactedGroup] = Field(default_factory=list)
    mitigation_summary: MitigationSummary | None = None
    counterfactual_insight: str | None = None
    recommendations: list[Recommendation]
    caveats: list[str] = Field(default_factory=list)
    policy_alignment: PolicyAlignmentBlock | None = None
    tradeoffs: str | None = None

    @field_validator("headline_findings")
    @classmethod
    def at_least_one_finding(cls, v: list[FindingItem]) -> list[FindingItem]:
        if not v:
            raise ValueError("report must include at least one headline finding")
        return v

    @field_validator("recommendations")
    @classmethod
    def at_least_one_rec(cls, v: list[Recommendation]) -> list[Recommendation]:
        if not v:
            raise ValueError("report must include at least one recommendation")
        return v


# ---------------------------------------------------------------------------
# Flattened view for BigQuery audit_history table
# ---------------------------------------------------------------------------


class AuditHistoryRow(BaseModel):
    model_config = ConfigDict(extra="ignore")
    audit_id: str
    created_at: datetime
    project_id: str | None = None
    user_id: str | None = None
    dataset_name: str
    model_name: str
    task_type: TaskType
    protected_attributes: list[str]
    risk_level: RiskLevel
    mitigation_method: str | None = None
    verdict: str
    metrics_before: dict[str, Any]
    metrics_after: dict[str, Any] | None = None
    report_json: dict[str, Any]
    report_version: str = "1.0.0"
