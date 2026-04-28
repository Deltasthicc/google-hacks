from __future__ import annotations

from typing import Any

from app.schemas.common import utc_now
from app.services.firestore_service import save_document
from app.utils.ids import prefixed_id


def create_audit(
    *,
    user_id: str,
    project_id: str,
    audit_type: str,
    inputs: dict[str, Any],
    results: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a placeholder audit record.

    TODO(Person 3): call run_data_audit, run_model_audit, counterfactual, and
    benchmark functions here. Person 3 should receive plain data/columns only,
    not Firebase or Storage objects.
    """
    audit_id = prefixed_id("audit")
    document = {
        "audit_id": audit_id,
        "project_id": project_id,
        "user_id": user_id,
        "audit_type": audit_type,
        "status": "queued",
        "created_at": utc_now(),
        "inputs": inputs,
        "results": results or _placeholder_results(audit_type),
    }
    return save_document("audits", audit_id, document)


def create_benchmark_run(
    *,
    user_id: str,
    project_id: str,
    benchmarks: list[str],
) -> dict[str, Any]:
    benchmark_id = prefixed_id("benchmark")
    document = {
        "benchmark_id": benchmark_id,
        "project_id": project_id,
        "user_id": user_id,
        "status": "queued",
        "created_at": utc_now(),
        "benchmarks": benchmarks,
        "results": {
            "message": "Benchmark suite placeholder. Person 3/4 benchmark runners plug in here."
        },
    }
    return save_document("benchmarks", benchmark_id, document)


def _placeholder_results(audit_type: str) -> dict[str, Any]:
    return {
        "message": f"{audit_type} placeholder accepted. Fairness computation is not wired yet.",
        "metrics": {},
        "next_step": "Wire this service to ml/src functions when Person 3 exposes them.",
    }
