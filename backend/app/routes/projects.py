from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas.common import ApiResponse, UserContext, success_response, utc_now
from app.schemas.projects import ProjectCreateRequest, ProjectResponse
from app.services.firestore_service import save_document
from app.utils.ids import prefixed_id

router = APIRouter(prefix="/api/v1", tags=["projects"])


@router.post("/projects", response_model=ApiResponse[ProjectResponse])
async def create_project(
    payload: ProjectCreateRequest,
    user: UserContext = Depends(get_current_user),
) -> ApiResponse[ProjectResponse]:
    project = ProjectResponse(
        project_id=prefixed_id("project"),
        user_id=user.user_id,
        name=payload.name,
        domain=payload.domain,
        description=payload.description,
        created_at=utc_now(),
    )
    save_document("projects", project.project_id, project.model_dump())
    return success_response(project)
