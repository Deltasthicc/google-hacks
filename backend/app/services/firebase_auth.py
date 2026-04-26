from __future__ import annotations

from app.schemas.common import UserContext


async def verify_firebase_token(authorization: str | None) -> UserContext:
    """Return the authenticated user.

    TODO(Person 2): initialize firebase_admin and verify real Firebase Auth
    ID tokens. For the local MVP skeleton, a Bearer token is treated as a
    stable demo uid and missing auth falls back to local_demo_user.
    """
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        if token:
            return UserContext(user_id=token[:64], auth_mode="bearer_stub")
    return UserContext(user_id="local_demo_user", auth_mode="development")
