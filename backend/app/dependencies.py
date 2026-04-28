from __future__ import annotations

from fastapi import Header

from app.schemas.common import UserContext
from app.services.firebase_auth import verify_firebase_token


async def get_current_user(
    authorization: str | None = Header(default=None),
) -> UserContext:
    return await verify_firebase_token(authorization)
