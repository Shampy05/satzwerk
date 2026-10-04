from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE


class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        field: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.field = field


async def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, AppException):
        raise exc

    content = {"error": "domain_error", "message": exc.message}

    if exc.field:
        content["field"] = exc.field

    return JSONResponse(status_code=exc.status_code, content=content)


class DatabaseUnavailableException(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Database connection failed or is unreachable.",
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
        )
