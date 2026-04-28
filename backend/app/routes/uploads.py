from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.dependencies import get_current_user
from app.schemas.common import ApiResponse, UserContext, success_response, utc_now
from app.schemas.uploads import UploadResponse
from app.services.firestore_service import save_document
from app.services.storage_service import upload_file
from app.utils.ids import prefixed_id

router = APIRouter(prefix="/api/v1", tags=["uploads"])


@router.post("/upload-dataset", response_model=ApiResponse[UploadResponse])
async def upload_dataset(
    project_id: str = Form(...),
    file: UploadFile = File(...),
    user: UserContext = Depends(get_current_user),
) -> ApiResponse[UploadResponse]:
    return await _create_upload(
        project_id=project_id,
        file=file,
        upload_type="dataset",
        user=user,
    )


@router.post("/upload-policy-doc", response_model=ApiResponse[UploadResponse])
async def upload_policy_doc(
    project_id: str = Form(...),
    file: UploadFile = File(...),
    user: UserContext = Depends(get_current_user),
) -> ApiResponse[UploadResponse]:
    return await _create_upload(
        project_id=project_id,
        file=file,
        upload_type="policy_doc",
        user=user,
    )


async def _create_upload(
    *,
    project_id: str,
    file: UploadFile,
    upload_type: str,
    user: UserContext,
) -> ApiResponse[UploadResponse]:
    upload_id = prefixed_id("upload")
    metadata = await upload_file(
        file.file,
        user_id=user.user_id,
        project_id=project_id,
        upload_id=upload_id,
        filename=file.filename or "upload.bin",
        content_type=file.content_type,
    )
    upload = UploadResponse(
        upload_id=upload_id,
        project_id=project_id,
        user_id=user.user_id,
        upload_type=upload_type,
        filename=file.filename or "upload.bin",
        content_type=file.content_type,
        size_bytes=int(metadata["size_bytes"]),
        created_at=utc_now(),
    )
    document = upload.model_dump()
    document["storage_path"] = metadata["storage_path"]
    save_document("uploads", upload_id, document)
    return success_response(upload)
