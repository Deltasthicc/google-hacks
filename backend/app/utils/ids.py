from __future__ import annotations

from uuid import uuid4


VALID_PREFIXES = {
    "project",
    "upload",
    "audit",
    "report",
    "benchmark",
    "mitigation",
    "approval",
}


def prefixed_id(prefix: str) -> str:
    if prefix not in VALID_PREFIXES:
        raise ValueError(f"Unsupported id prefix: {prefix}")
    return f"{prefix}_{uuid4().hex}"
