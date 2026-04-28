from __future__ import annotations

from typing import BinaryIO

from app.services.firebase_app import get_firebase_app


def build_storage_path(user_id: str, project_id: str, upload_id: str, filename: str) -> str:
    safe_name = filename.replace("\\", "_").replace("/", "_")
    return f"users/{user_id}/projects/{project_id}/uploads/{upload_id}/{safe_name}"


async def upload_file(
    file: BinaryIO,
    *,
    user_id: str,
    project_id: str,
    upload_id: str,
    filename: str,
    content_type: str | None = None,
) -> dict[str, str | int]:
    """Upload a file to Firebase Storage when configured, else local metadata.

    The returned storage_path remains private backend metadata. Routes should
    expose download URLs only through explicit export/download endpoints.
    """
    content = file.read()
    storage_path = build_storage_path(user_id, project_id, upload_id, filename)
    app = get_firebase_app()
    if app is not None:
        from firebase_admin import storage

        bucket = storage.bucket(app=app)
        blob = bucket.blob(storage_path)
        blob.upload_from_string(content, content_type=content_type)

    return {
        "storage_path": storage_path,
        "size_bytes": len(content),
    }


def download_storage_object(storage_path: str, destination_path: str) -> None:
    """Download a Storage object to a local path. Requires Firebase Storage."""
    app = get_firebase_app()
    if app is None:
        raise RuntimeError("Firebase Storage is not configured.")

    from firebase_admin import storage

    bucket = storage.bucket(app=app)
    blob = bucket.blob(storage_path)
    blob.download_to_filename(destination_path)


upload_file_stub = upload_file
