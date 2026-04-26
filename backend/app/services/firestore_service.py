from __future__ import annotations

from copy import deepcopy
from typing import Any


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
    """Persist a document in the local in-memory store.

    TODO(Person 2): replace with google-cloud-firestore writes while preserving
    this module as the only Firestore boundary for routes/services.
    """
    _ensure_collection(collection)
    _STORE[collection][document_id] = deepcopy(payload)
    return deepcopy(_STORE[collection][document_id])


def get_document(collection: str, document_id: str) -> dict[str, Any] | None:
    _ensure_collection(collection)
    item = _STORE[collection].get(document_id)
    return deepcopy(item) if item is not None else None


def list_documents(collection: str, **filters: str) -> list[dict[str, Any]]:
    _ensure_collection(collection)
    items = list(_STORE[collection].values())
    for key, value in filters.items():
        items = [item for item in items if item.get(key) == value]
    return deepcopy(items)


def _ensure_collection(collection: str) -> None:
    if collection not in COLLECTIONS:
        raise ValueError(f"Unsupported Firestore collection: {collection}")
