from fastapi import APIRouter, status

import src.auth.service as auth_service
from src.auth.schemas import RegistrationData, RegistrationResponse, UserRegister
from src.dependencies import DbDep

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(user_data: UserRegister, db: DbDep):
    user = await auth_service.register_user(db, user_data)

    return RegistrationResponse(
        message="Verification code sent to your email",
        data=RegistrationData.model_validate(user),
    )


@auth_router.post("/auth/verify-code")
async def verify_code():
    pass


@auth_router.post("/auth/token")
async def token():
    pass


@auth_router.get("/auth/me")
async def login():
    pass
