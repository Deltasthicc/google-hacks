from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DataAuditRequest(BaseModel):
    project_id: str
    upload_id: str
    target_column: str
    sensitive_columns: list[str] = Field(default_factory=list)


class ModelAuditRequest(DataAuditRequest):
    prediction_column: str


class CounterfactualRequest(BaseModel):
    project_id: str
    upload_id: str | None = None
    audit_id: str | None = None
    sensitive_columns: list[str] = Field(default_factory=list)
    sample_limit: int = Field(default=100, ge=1, le=1000)


class BenchmarkSuiteRequest(BaseModel):
    project_id: str
    suite_name: str = "default"
    benchmarks: list[str] = Field(default_factory=lambda: ["bharatbbq", "bbq"])


class AuditResponse(BaseModel):
    audit_id: str
    project_id: str
    user_id: str
    audit_type: str
    status: str
    created_at: datetime
    inputs: dict[str, Any]
    results: dict[str, Any]


class AuditHistoryResponse(BaseModel):
    project_id: str
    audits: list[AuditResponse]


class BenchmarkResponse(BaseModel):
    benchmark_id: str
    project_id: str
    user_id: str
    status: str
    created_at: datetime
    benchmarks: list[str]
    results: dict[str, Any]
