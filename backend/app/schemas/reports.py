from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class GenerateReportRequest(BaseModel):
    project_id: str
    audit_id: str
    mode: str = Field(default="executive", pattern="^(executive|technical)$")


class ReportResponse(BaseModel):
    report_id: str
    project_id: str
    audit_id: str
    user_id: str
    status: str
    mode: str
    created_at: datetime
    report: dict[str, Any]
