from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    domain: str | None = Field(default=None, max_length=80)
    description: str | None = Field(default=None, max_length=500)


class ProjectResponse(BaseModel):
    project_id: str
    user_id: str
    name: str
    domain: str | None = None
    description: str | None = None
    created_at: datetime
    status: str = "created"
