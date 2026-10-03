from fastapi import status

from src.exceptions import AppException


class DuplicateEntityException(AppException):
    def __init__(self, field: str, value: str) -> None:
        super().__init__(
            message=f"An account with this {field} already exists.",
            status_code=status.HTTP_409_CONFLICT,
            field=field,
        )
        self.value = value
