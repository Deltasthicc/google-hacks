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
    firebase_service_account_json_path: str | None = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_JSON_PATH"
    )
    upload_bucket_name: str | None = os.getenv("UPLOAD_BUCKET_NAME")
    export_bucket_name: str | None = os.getenv("EXPORT_BUCKET_NAME")
    firebase_strict: bool = os.getenv("FIREBASE_STRICT", "false").lower() == "true"

    @property
    def firebase_bucket(self) -> str | None:
        return (
            self.firebase_storage_bucket
            or self.upload_bucket_name
            or self.export_bucket_name
        )

    @property
    def should_use_firebase(self) -> bool:
        if self.firebase_strict:
            return True
        return bool(
            self.firebase_service_account_json_path
            or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            or self.app_env.lower() in {"staging", "production"}
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
