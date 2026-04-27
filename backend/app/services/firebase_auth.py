from __future__ import annotations

from fastapi import status
from firebase_admin import auth

from app.schemas.common import UserContext
from app.config import get_settings
from app.services.firebase_app import get_firebase_app
from app.utils.errors import ApiException


async def verify_firebase_token(authorization: str | None) -> UserContext:
    """Return the authenticated user.

    With FIREBASE_STRICT=true this verifies real Firebase Auth ID tokens. When
    strict mode is off, local stub auth stays enabled so Person 2 can test real
    Firestore/Storage before Person 1 wires frontend sign-in tokens.
    """
    token = _extract_bearer_token(authorization)
    if get_settings().firebase_strict:
        if not token:
            raise ApiException(
                "AUTH_REQUIRED",
                "Firebase ID token is required.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            app = get_firebase_app()
            decoded_token = auth.verify_id_token(token, app=app)
        except Exception as exc:
            raise ApiException(
                "INVALID_FIREBASE_TOKEN",
                "Firebase ID token could not be verified.",
                status_code=status.HTTP_401_UNAUTHORIZED,
                details={"reason": exc.__class__.__name__},
            ) from exc
        return UserContext(user_id=decoded_token["uid"], auth_mode="firebase")

    if token:
        return UserContext(user_id=token[:64], auth_mode="bearer_stub")
    return UserContext(user_id="local_demo_user", auth_mode="development")


def _extract_bearer_token(authorization: str | None) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        return token or None
    return None
