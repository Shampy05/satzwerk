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


class InvalidVerificationException(AppException):
    def __init__(
        self,
        message: str = "Invalid or expired verification code.",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        super().__init__(message, status_code)


class InvalidCredentialsException(AppException):
    def __init__(
        self,
        message: str = "Invalid email/username or password.",
        status_code: int = status.HTTP_401_UNAUTHORIZED,
    ) -> None:
        super().__init__(message, status_code)


class UnverifiedAccountException(AppException):
    def __init__(
        self,
        message: str = "Please verify your account before logging in.",
        status_code: int = status.HTTP_403_FORBIDDEN,
    ) -> None:
        super().__init__(message, status_code)


class RateLimitException(AppException):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_429_TOO_MANY_REQUESTS,
    ) -> None:
        super().__init__(message, status_code)


class InvalidTokenException(AppException):
    def __init__(
        self,
        message: str = "Invalid or expired token.",
        status_code: int = status.HTTP_401_UNAUTHORIZED,
    ) -> None:
        super().__init__(message, status_code)
