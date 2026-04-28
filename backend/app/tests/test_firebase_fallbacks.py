from __future__ import annotations

from io import BytesIO
from types import SimpleNamespace

import pytest

from app.services import firebase_auth, firestore_service, storage_service


@pytest.mark.asyncio
async def test_non_strict_auth_uses_local_development_user(monkeypatch):
    monkeypatch.setattr(
        firebase_auth,
        "get_settings",
        lambda: SimpleNamespace(firebase_strict=False),
    )

    user = await firebase_auth.verify_firebase_token(None)

    assert user.user_id == "local_demo_user"
    assert user.auth_mode == "development"


@pytest.mark.asyncio
async def test_non_strict_auth_accepts_bearer_stub(monkeypatch):
    monkeypatch.setattr(
        firebase_auth,
        "get_settings",
        lambda: SimpleNamespace(firebase_strict=False),
    )

    user = await firebase_auth.verify_firebase_token("Bearer local-token")

    assert user.user_id == "local-token"
    assert user.auth_mode == "bearer_stub"


@pytest.mark.asyncio
async def test_strict_auth_requires_firebase_token(monkeypatch):
    monkeypatch.setattr(
        firebase_auth,
        "get_settings",
        lambda: SimpleNamespace(firebase_strict=True),
    )

    with pytest.raises(firebase_auth.ApiException) as exc_info:
        await firebase_auth.verify_firebase_token(None)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail["code"] == "AUTH_REQUIRED"


@pytest.mark.asyncio
async def test_strict_auth_returns_verified_firebase_user(monkeypatch):
    app = object()
    monkeypatch.setattr(
        firebase_auth,
        "get_settings",
        lambda: SimpleNamespace(firebase_strict=True),
    )
    monkeypatch.setattr(firebase_auth, "get_firebase_app", lambda: app)
    monkeypatch.setattr(
        firebase_auth.auth,
        "verify_id_token",
        lambda token, app=None: {"uid": f"firebase-{token}", "app": app},
    )

    user = await firebase_auth.verify_firebase_token("Bearer abc123")

    assert user.user_id == "firebase-abc123"
    assert user.auth_mode == "firebase"


def test_storage_path_sanitizes_uploaded_filename():
    path = storage_service.build_storage_path(
        "user_1",
        "project_1",
        "upload_1",
        "../nested\\demo.csv",
    )

    assert path == "users/user_1/projects/project_1/uploads/upload_1/.._nested_demo.csv"


@pytest.mark.asyncio
async def test_local_upload_returns_private_metadata(monkeypatch):
    monkeypatch.setattr(storage_service, "get_firebase_app", lambda: None)

    metadata = await storage_service.upload_file(
        BytesIO(b"target,gender\n1,F\n"),
        user_id="user_1",
        project_id="project_1",
        upload_id="upload_1",
        filename="demo.csv",
        content_type="text/csv",
    )

    assert metadata == {
        "storage_path": "users/user_1/projects/project_1/uploads/upload_1/demo.csv",
        "size_bytes": 18,
    }


def test_firestore_local_fallback_copies_saved_documents(monkeypatch):
    monkeypatch.setattr(firestore_service, "get_firebase_app", lambda: None)
    payload = {"project_id": "project_test", "nested": {"value": 1}}

    saved = firestore_service.save_document("projects", "project_test", payload)
    payload["nested"]["value"] = 2
    saved["nested"]["value"] = 3

    loaded = firestore_service.get_document("projects", "project_test")

    assert loaded == {"project_id": "project_test", "nested": {"value": 1}}


def test_firestore_rejects_unknown_collections():
    with pytest.raises(ValueError, match="Unsupported Firestore collection"):
        firestore_service.save_document("unknown", "doc_1", {})
