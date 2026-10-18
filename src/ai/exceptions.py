from fastapi import status

from src.exceptions import AppException


class CardGenerationFailedException(AppException):
    def __init__(
        self,
        message: str = "Failed to generate a valid card",
        status_code: int = status.HTTP_422_UNPROCESSABLE_CONTENT,
    ) -> None:
        super().__init__(message, status_code)
