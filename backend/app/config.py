from __future__ import annotations

import os
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "NyayaLens Audit API"
    app_version: str = "0.1.0"
    app_env: str = os.getenv("APP_ENV", "development")
    port: int = int(os.getenv("PORT", "8080"))
    google_cloud_project: str | None = os.getenv("GOOGLE_CLOUD_PROJECT")
    firebase_project_id: str | None = os.getenv("FIREBASE_PROJECT_ID")
    firebase_storage_bucket: str | None = os.getenv("FIREBASE_STORAGE_BUCKET")
    upload_bucket_name: str | None = os.getenv("UPLOAD_BUCKET_NAME")
    export_bucket_name: str | None = os.getenv("EXPORT_BUCKET_NAME")


@lru_cache
def get_settings() -> Settings:
    return Settings()
