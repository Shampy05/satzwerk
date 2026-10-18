from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from pydantic.fields import Field


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def validate_password_byte_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password cannot exceed 72 bytes in utf-8 encoding")
        return value


class VerifyCodeRequest(BaseModel):
    identifier: str = Field(..., description="Email or username")
    code: str = Field(min_length=6, max_length=6)


class VerifyCodeResponse(BaseModel):
    message: str


class LoginPayload(BaseModel):
    identifier: str = Field(..., description="Email or username")
    password: str


class ResendCodePayload(BaseModel):
    identifier: str = Field(..., description="Email or username")


class RefreshPayload(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegistrationData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_verified: bool


class RegistrationResponse(BaseModel):
    status: Literal["success"] = "success"
    message: str
    data: RegistrationData


class ForgotPasswordPayload(BaseModel):
    identifier: str = Field(..., description="Email or username")


class ResetPasswordPayload(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
