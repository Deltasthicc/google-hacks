from __future__ import annotations

from fastapi import APIRouter

from app.config import get_settings
from app.schemas.common import HealthResponse, utc_now

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        timestamp=utc_now(),
    )
