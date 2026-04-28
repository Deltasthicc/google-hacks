from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status


class ApiException(HTTPException):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail={
                "code": code,
                "message": message,
                "details": details or {},
            },
        )
