from __future__ import annotations

from typing import BinaryIO


def build_storage_path(user_id: str, project_id: str, upload_id: str, filename: str) -> str:
    safe_name = filename.replace("\\", "_").replace("/", "_")
    return f"users/{user_id}/projects/{project_id}/uploads/{upload_id}/{safe_name}"


async def upload_file_stub(
    file: BinaryIO,
    *,
    user_id: str,
    project_id: str,
    upload_id: str,
    filename: str,
) -> dict[str, str | int]:
    """Pretend to upload a file and return private storage metadata.

    TODO(Person 2): replace this with Firebase Storage or Cloud Storage upload
    code. Keep storage_path private; routes should not expose raw bucket paths
    unless a debug flag is intentionally added.
    """
    content = file.read()
    return {
        "storage_path": build_storage_path(user_id, project_id, upload_id, filename),
        "size_bytes": len(content),
    }
