from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routes import audits, health, projects, reports, uploads
from app.schemas.common import ApiError, ApiResponse

settings = get_settings()
logger = logging.getLogger("nyayalens.audit_api")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FastAPI backend for NyayaLens fairness audit workflows.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(projects.router)
app.include_router(uploads.router)
app.include_router(audits.router)
app.include_router(reports.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.warning("validation_error path=%s errors=%s", request.url.path, exc.errors())
    body = ApiResponse(
        success=False,
        data=None,
        error=ApiError(
            code="VALIDATION_ERROR",
            message="Request validation failed.",
            details={"errors": exc.errors()},
        ),
    )
    return JSONResponse(status_code=422, content=body.model_dump(mode="json"))


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning("http_error path=%s status=%s", request.url.path, exc.status_code)
    detail = exc.detail
    if isinstance(detail, dict) and {"code", "message", "details"} <= set(detail):
        error = ApiError(**detail)
    else:
        error = ApiError(
            code="HTTP_ERROR",
            message=str(detail),
            details={},
        )
    body = ApiResponse(success=False, data=None, error=error)
    return JSONResponse(status_code=exc.status_code, content=body.model_dump(mode="json"))


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_error path=%s", request.url.path)
    status_code = getattr(exc, "status_code", 500)
    detail = getattr(exc, "detail", None)
    if isinstance(detail, dict) and {"code", "message", "details"} <= set(detail):
        error = ApiError(**detail)
    else:
        error = ApiError(
            code="INTERNAL_ERROR",
            message="An unexpected error occurred.",
            details={},
        )
    body = ApiResponse(success=False, data=None, error=error)
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))
