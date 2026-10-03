from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr
from pydantic.fields import Field


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)


class TokenResponse(BaseModel):
    access_token: str
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
