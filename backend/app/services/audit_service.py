from __future__ import annotations

import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from app.schemas.common import utc_now
from app.services.firestore_service import get_document, save_document
from app.utils.ids import prefixed_id

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[3]


def _ensure_repo_root_on_path() -> None:
    root = str(_REPO_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def _scrub_ml_heavy_fields(blob: dict[str, Any]) -> None:
    blob.pop("_contract_arrays", None)


def _run_benchmark_for_inputs(
    *,
    audit_id: str,
    project_id: str,
    user_id: str,
    created_at,
    inputs: dict[str, Any],
) -> dict[str, Any]:
    """Run ml/src pipeline; return structured result or error description."""
    _ensure_repo_root_on_path()
    from ml.src.benchmark_runner import run_pipeline

    try:
        from app.services.storage_service import download_storage_object
    except ImportError:
        download_storage_object = None

    csv_path: str | None = None
    temp_path: str | None = None
    upload_id = inputs.get("upload_id")
    if upload_id and download_storage_object is not None:
        upload = get_document("uploads", upload_id)
        if upload and upload.get("storage_path"):
            temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".csv").name
            try:
                download_storage_object(str(upload["storage_path"]), temp_path)
                csv_path = temp_path
            except Exception as exc:
                logger.warning(
                    "Upload %s could not be downloaded (%s); using default Adult config.",
                    upload_id,
                    exc,
                )
                if os.path.isfile(temp_path):
                    try:
                        os.unlink(temp_path)
                    except OSError:
                        pass
                temp_path = None
                csv_path = None

    sensitive = inputs.get("sensitive_columns") or ["sex"]
    if not sensitive:
        sensitive = ["sex"]
    target_col = inputs.get("target_column") or "class"
    config_name = inputs.get("config_name")
    config_path: str | None = None
    if config_name:
        candidate = _REPO_ROOT / "ml" / "configs" / config_name
        if candidate.is_file():
            config_path = str(candidate)

    try:
        ml_out = run_pipeline(
            config_path=config_path,
            csv_path=csv_path,
            target_col=target_col,
            sensitive_cols=list(sensitive),
            audit_id=audit_id,
            project_id=project_id,
            user_id=user_id,
            created_at=created_at,
        )
    finally:
        if temp_path and os.path.isfile(temp_path):
            try:
                os.unlink(temp_path)
            except OSError:
                pass

    if ml_out.get("status") != "success":
        return {
            "status": "failed",
            "error": ml_out.get("message", "Pipeline error"),
            "raw": ml_out,
        }

    fairness_payload = ml_out.pop("fairness_audit_payload", None)
    _scrub_ml_heavy_fields(ml_out)

    return {
        "status": "completed",
        "ml": ml_out,
        "fairness_audit_payload": fairness_payload,
    }


def create_audit(
    *,
    user_id: str,
    project_id: str,
    audit_type: str,
    inputs: dict[str, Any],
    results: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create an audit record; run the ML fairness pipeline where applicable."""
    audit_id = prefixed_id("audit")
    created_at = utc_now()
    fairness_audit_payload = None

    if audit_type in ("data_audit", "model_audit", "counterfactuals"):
        run_out = _run_benchmark_for_inputs(
            audit_id=audit_id,
            project_id=project_id,
            user_id=user_id,
            created_at=created_at,
            inputs=inputs,
        )
        if run_out["status"] == "failed":
            document = {
                "audit_id": audit_id,
                "project_id": project_id,
                "user_id": user_id,
                "audit_type": audit_type,
                "status": "failed",
                "created_at": created_at,
                "inputs": inputs,
                "results": {
                    "message": run_out.get("error", "Pipeline failed."),
                    "details": run_out.get("raw"),
                },
            }
            return save_document("audits", audit_id, document)

        fairness_audit_payload = run_out.get("fairness_audit_payload")
        merged_results = run_out["ml"]
    else:
        merged_results = results or _placeholder_results(audit_type)

    document = {
        "audit_id": audit_id,
        "project_id": project_id,
        "user_id": user_id,
        "audit_type": audit_type,
        "status": "completed",
        "created_at": created_at,
        "inputs": inputs,
        "results": merged_results,
    }
    if fairness_audit_payload is not None:
        document["fairness_audit_payload"] = fairness_audit_payload

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
            "message": (
                "NLP benchmark suite is not wired to the tabular pipeline in this build. "
                f"Requested: {benchmarks}"
            ),
        },
    }
    return save_document("benchmarks", benchmark_id, document)


def _placeholder_results(audit_type: str) -> dict[str, Any]:
    return {
        "message": f"{audit_type} uses the standard pipeline when ML is available.",
        "metrics": {},
    }
