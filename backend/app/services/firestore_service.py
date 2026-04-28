from __future__ import annotations

from copy import deepcopy
from typing import Any

from google.cloud.firestore_v1.base_query import FieldFilter

from app.services.firebase_app import get_firebase_app


COLLECTIONS = {
    "users",
    "projects",
    "uploads",
    "audits",
    "reports",
    "benchmarks",
    "mitigation_runs",
    "approvals",
}

_STORE: dict[str, dict[str, dict[str, Any]]] = {
    collection: {} for collection in COLLECTIONS
}


def save_document(collection: str, document_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Persist a document to Firestore when configured, else local memory."""
    _ensure_collection(collection)
    client = _firestore_client()
    if client is not None:
        client.collection(collection).document(document_id).set(deepcopy(payload))
        return deepcopy(payload)

    _STORE[collection][document_id] = deepcopy(payload)
    return deepcopy(_STORE[collection][document_id])


def get_document(collection: str, document_id: str) -> dict[str, Any] | None:
    _ensure_collection(collection)
    client = _firestore_client()
    if client is not None:
        snapshot = client.collection(collection).document(document_id).get()
        return snapshot.to_dict() if snapshot.exists else None

    item = _STORE[collection].get(document_id)
    return deepcopy(item) if item is not None else None


def list_documents(collection: str, **filters: str) -> list[dict[str, Any]]:
    _ensure_collection(collection)
    client = _firestore_client()
    if client is not None:
        query: Any = client.collection(collection)
        for key, value in filters.items():
            query = query.where(filter=FieldFilter(key, "==", value))
        return [snapshot.to_dict() for snapshot in query.stream()]

    items = list(_STORE[collection].values())
    for key, value in filters.items():
        items = [item for item in items if item.get(key) == value]
    return deepcopy(items)


def _ensure_collection(collection: str) -> None:
    if collection not in COLLECTIONS:
        raise ValueError(f"Unsupported Firestore collection: {collection}")


def _firestore_client() -> Any | None:
    app = get_firebase_app()
    if app is None:
        return None
    from firebase_admin import firestore

    return firestore.client(app=app)
