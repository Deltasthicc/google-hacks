from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas.audits import (
    AuditHistoryResponse,
    AuditResponse,
    BenchmarkResponse,
    BenchmarkSuiteRequest,
    CounterfactualRequest,
    DataAuditRequest,
    ModelAuditRequest,
)
from app.schemas.common import ApiResponse, UserContext, success_response
from app.services.audit_service import create_audit, create_benchmark_run
from app.services.firestore_service import get_document, list_documents
from app.utils.errors import ApiException

router = APIRouter(prefix="/api/v1", tags=["audits"])


@router.post("/run-data-audit", response_model=ApiResponse[AuditResponse])
async def run_data_audit(
    payload: DataAuditRequest,
    user: UserContext = Depends(get_current_user),
) -> ApiResponse[AuditResponse]:
    audit = create_audit(
        user_id=user.user_id,
        project_id=payload.project_id,
        audit_type="data_audit",
        inputs=payload.model_dump(),
    )
    return success_response(AuditResponse.model_validate(audit))


@router.post("/run-model-audit", response_model=ApiResponse[AuditResponse])
async def run_model_audit(
    payload: ModelAuditRequest,
    user: UserContext = Depends(get_current_user),
) -> ApiResponse[AuditResponse]:
    audit = create_audit(
        user_id=user.user_id,
        project_id=payload.project_id,
        audit_type="model_audit",
        inputs=payload.model_dump(),
    )
    return success_response(AuditResponse.model_validate(audit))


@router.post("/run-counterfactuals", response_model=ApiResponse[AuditResponse])
async def run_counterfactuals(
    payload: CounterfactualRequest,
    user: UserContext = Depends(get_current_user),
) -> ApiResponse[AuditResponse]:
    audit = create_audit(
        user_id=user.user_id,
        project_id=payload.project_id,
        audit_type="counterfactuals",
        inputs=payload.model_dump(),
    )
    return success_response(AuditResponse.model_validate(audit))


@router.post("/run-benchmark-suite", response_model=ApiResponse[BenchmarkResponse])
async def run_benchmark_suite(
    payload: BenchmarkSuiteRequest,
    user: UserContext = Depends(get_current_user),
) -> ApiResponse[BenchmarkResponse]:
    benchmark = create_benchmark_run(
        user_id=user.user_id,
        project_id=payload.project_id,
        benchmarks=payload.benchmarks,
    )
    return success_response(BenchmarkResponse.model_validate(benchmark))


@router.get("/audit/{audit_id}", response_model=ApiResponse[AuditResponse])
async def get_audit(
    audit_id: str,
    user: UserContext = Depends(get_current_user),
) -> ApiResponse[AuditResponse]:
    audit = get_document("audits", audit_id)
    if audit is None or audit.get("user_id") != user.user_id:
        raise ApiException("AUDIT_NOT_FOUND", "Audit was not found.", status_code=404)
    return success_response(AuditResponse.model_validate(audit))


@router.get("/project/{project_id}/history", response_model=ApiResponse[AuditHistoryResponse])
async def get_project_history(
    project_id: str,
    user: UserContext = Depends(get_current_user),
) -> ApiResponse[AuditHistoryResponse]:
    audits = list_documents("audits", project_id=project_id, user_id=user.user_id)
    parsed = [AuditResponse.model_validate(audit) for audit in audits]
    return success_response(AuditHistoryResponse(project_id=project_id, audits=parsed))
