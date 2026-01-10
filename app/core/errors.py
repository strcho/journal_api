from fastapi import HTTPException, status

from app.schemas.errors import ErrorDetail, ErrorResponse


def http_error(code: str, message: str, status_code: int) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail=ErrorResponse(error=ErrorDetail(code=code, message=message)).dict(),
    )
