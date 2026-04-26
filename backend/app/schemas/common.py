from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class ApiError(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    error: ApiError | None = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: datetime


class UserContext(BaseModel):
    user_id: str
    auth_mode: str = "development"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def success_response(data: T) -> ApiResponse[T]:
    return ApiResponse[T](success=True, data=data, error=None)
