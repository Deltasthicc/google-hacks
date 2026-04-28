from __future__ import annotations

import logging

import firebase_admin
from firebase_admin import credentials

from app.config import get_settings

logger = logging.getLogger("nyayalens.firebase")


def is_firebase_configured() -> bool:
    return get_settings().should_use_firebase


def get_firebase_app() -> firebase_admin.App | None:
    """Initialize and return the Firebase Admin app when configured.

    Local development deliberately falls back to in-memory services unless a
    service account path, GOOGLE_APPLICATION_CREDENTIALS, production env, or
    FIREBASE_STRICT=true is present.
    """
    settings = get_settings()
    if not settings.should_use_firebase:
        return None

    if firebase_admin._apps:
        return firebase_admin.get_app()

    options: dict[str, str] = {}
    if settings.firebase_project_id:
        options["projectId"] = settings.firebase_project_id
    if settings.firebase_bucket:
        options["storageBucket"] = settings.firebase_bucket

    if settings.firebase_service_account_json_path:
        cred = credentials.Certificate(settings.firebase_service_account_json_path)
        logger.info("Initializing Firebase Admin with service account file")
        return firebase_admin.initialize_app(cred, options)

    logger.info("Initializing Firebase Admin with application default credentials")
    return firebase_admin.initialize_app(options=options)
