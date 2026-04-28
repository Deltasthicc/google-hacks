"""
BigQuery client for NyayaLens audit history.

Two responsibilities:

1. Persist a completed audit (payload + generated report) as a row in the
   audit_history table. This is what turns the product from a notebook
   into a system.
2. Run the three dashboard queries that the Looker dashboard reads from.

Everything here is thin: the real schema and SQL live in
analytics/bigquery/. This module is the callable glue the FastAPI layer
imports.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from google.cloud import bigquery  # noqa: F401

from .schemas import AuditHistoryRow, FairnessAuditPayload, FairnessReport

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
DEFAULT_DATASET = os.getenv("NYAYA_BQ_DATASET", "fairness")
DEFAULT_TABLE = os.getenv("NYAYA_BQ_AUDIT_TABLE", "audit_history")

_SQL_ROOT = Path(__file__).resolve().parents[3] / "analytics" / "bigquery" / "sql"


# ---------------------------------------------------------------------------
# Flattening helpers
# ---------------------------------------------------------------------------


def build_audit_history_row(
    payload: FairnessAuditPayload,
    report: FairnessReport,
) -> AuditHistoryRow:
    """Flatten a payload + report into the BigQuery row schema."""
    metrics_after = (
        payload.metrics_after_mitigation.model_dump()
        if payload.metrics_after_mitigation is not None
        else None
    )
    mitigation_method = (
        payload.metrics_after_mitigation.mitigation_method
        if payload.metrics_after_mitigation is not None
        else None
    )

    return AuditHistoryRow(
        audit_id=payload.audit_id,
        created_at=payload.created_at,
        project_id=payload.project_id,
        user_id=payload.user_id,
        dataset_name=payload.dataset.name,
        model_name=payload.model.name,
        task_type=payload.dataset.task_type,
        protected_attributes=[a.name for a in payload.protected_attributes],
        risk_level=report.risk_level,
        mitigation_method=mitigation_method,
        verdict=report.plain_english_verdict,
        metrics_before=payload.metrics_before_mitigation.model_dump(),
        metrics_after=metrics_after,
        report_json=report.model_dump(mode="json"),
        report_version=report.report_version,
    )


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def insert_audit(
    payload: FairnessAuditPayload,
    report: FairnessReport,
    *,
    client: "bigquery.Client | None" = None,
    project: str | None = None,
    dataset: str = DEFAULT_DATASET,
    table: str = DEFAULT_TABLE,
) -> None:
    """Insert one audit row into BigQuery via streaming insert."""
    from google.cloud import bigquery  # lazy import

    project = project or DEFAULT_PROJECT
    if project is None:
        raise RuntimeError(
            "No GCP project configured. Set GOOGLE_CLOUD_PROJECT."
        )

    client = client or bigquery.Client(project=project)
    table_ref = f"{project}.{dataset}.{table}"

    row = build_audit_history_row(payload, report)
    # BigQuery streaming wants simple JSON-friendly dicts.
    row_dict: dict[str, Any] = row.model_dump(mode="json")

    errors = client.insert_rows_json(table_ref, [row_dict])
    if errors:
        logger.error("BigQuery insert failed: %s", errors)
        raise RuntimeError(f"BigQuery insert failed: {errors}")

    logger.info(
        "Inserted audit %s into %s",
        payload.audit_id,
        table_ref,
    )


# ---------------------------------------------------------------------------
# Dashboard queries
# ---------------------------------------------------------------------------


def _load_sql(filename: str) -> str:
    path = _SQL_ROOT / filename
    return path.read_text(encoding="utf-8")


def _render_sql(filename: str, project: str, dataset: str) -> str:
    """Substitute ${project} and ${dataset} placeholders. BigQuery does not
    parse this syntax natively, so we do it client-side before sending."""
    if not project:
        raise RuntimeError("No GCP project configured. Set GOOGLE_CLOUD_PROJECT.")
    return (
        _load_sql(filename)
        .replace("${project}", project)
        .replace("${dataset}", dataset)
    )


def run_risk_summary(
    *,
    client: "bigquery.Client | None" = None,
    project: str | None = None,
    dataset: str = DEFAULT_DATASET,
) -> list[dict[str, Any]]:
    """Audit counts by risk level over the last 90 days."""
    return _run_query(
        "dashboard_risk_summary.sql", client=client, project=project, dataset=dataset
    )


def run_metric_failures(
    *,
    client: "bigquery.Client | None" = None,
    project: str | None = None,
    dataset: str = DEFAULT_DATASET,
) -> list[dict[str, Any]]:
    """Most common failing fairness metric across audits."""
    return _run_query(
        "dashboard_metric_failures.sql", client=client, project=project, dataset=dataset
    )


def run_mitigation_impact(
    *,
    client: "bigquery.Client | None" = None,
    project: str | None = None,
    dataset: str = DEFAULT_DATASET,
) -> list[dict[str, Any]]:
    """Before/after disparity deltas grouped by mitigation method."""
    return _run_query(
        "dashboard_mitigation_impact.sql", client=client, project=project, dataset=dataset
    )


def _run_query(
    filename: str,
    *,
    client: "bigquery.Client | None" = None,
    project: str | None = None,
    dataset: str = DEFAULT_DATASET,
) -> list[dict[str, Any]]:
    from google.cloud import bigquery  # lazy import

    project = project or DEFAULT_PROJECT
    client = client or bigquery.Client(project=project)
    sql = _render_sql(filename, project, dataset)
    job = client.query(sql)
    return [dict(row) for row in job.result()]
