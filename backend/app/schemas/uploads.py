from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class UploadMetadata(BaseModel):
    project_id: str
    upload_type: str = Field(..., pattern="^(dataset|policy_doc)$")
    filename: str
    content_type: str | None = None
    size_bytes: int


class UploadResponse(BaseModel):
    upload_id: str
    project_id: str
    user_id: str
    upload_type: str
    filename: str
    content_type: str | None = None
    size_bytes: int
    created_at: datetime
    status: str = "uploaded"
