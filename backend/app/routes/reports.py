from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas.common import ApiResponse, UserContext, success_response
from app.schemas.reports import GenerateReportRequest, ReportResponse
from app.services.export_service import create_report
from app.services.firestore_service import get_document
from app.utils.errors import ApiException

router = APIRouter(prefix="/api/v1", tags=["reports"])


@router.post("/generate-report", response_model=ApiResponse[ReportResponse])
async def generate_report(
    payload: GenerateReportRequest,
    user: UserContext = Depends(get_current_user),
) -> ApiResponse[ReportResponse]:
    audit = get_document("audits", payload.audit_id)
    if audit is None or audit.get("user_id") != user.user_id:
        raise ApiException("AUDIT_NOT_FOUND", "Audit was not found.", status_code=404)
    report = create_report(
        user_id=user.user_id,
        project_id=payload.project_id,
        audit_id=payload.audit_id,
        mode=payload.mode,
        audit=audit,
    )
    return success_response(ReportResponse.model_validate(report))
