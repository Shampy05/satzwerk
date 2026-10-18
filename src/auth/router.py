from fastapi import APIRouter, BackgroundTasks, status

import src.auth.service as auth_service
from src.auth.email import email_service
from src.auth.exceptions import InvalidTokenException
from src.auth.models import User
from src.auth.schema import (
    ForgotPasswordPayload,
    LoginPayload,
    RefreshPayload,
    RegistrationData,
    RegistrationResponse,
    ResendCodePayload,
    ResetPasswordPayload,
    TokenResponse,
    UserRegister,
    VerifyCodeRequest,
    VerifyCodeResponse,
)
from src.auth.security import create_tokens, verify_refresh_tokens
from src.dependencies import DbDep

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserRegister, background_tasks: BackgroundTasks, db: DbDep
):
    user, verification_code = await auth_service.register_user(db, user_data)

    background_tasks.add_task(
        email_service.send_verification_code,
        email_to=user_data.email,
        code=verification_code,
    )

    return RegistrationResponse(
        message="Verification code sent to your email",
        data=RegistrationData.model_validate(user),
    )


@auth_router.post(
    "/verify-code",
    response_model=VerifyCodeResponse,
    status_code=status.HTTP_200_OK,
)
async def verify_code(payload: VerifyCodeRequest, db: DbDep):
    await auth_service.verify_user_email(db, payload.identifier, payload.code)

    return VerifyCodeResponse(message="Account successfully verified.")


@auth_router.post(
    "/resend-code", response_model=VerifyCodeResponse, status_code=status.HTTP_200_OK
)
async def resend_code(
    payload: ResendCodePayload, background_tasks: BackgroundTasks, db: DbDep
):
    user, code = await auth_service.resend_verification_code(db, payload.identifier)

    background_tasks.add_task(
        email_service.send_verification_code, email_to=user.email, code=code
    )

    return VerifyCodeResponse(message="A new verification code has been sent.")


@auth_router.post("/login", response_model=TokenResponse)
async def login(payload: LoginPayload, db: DbDep):
    user = await auth_service.authenticate_user(
        db=db, identifier=payload.identifier, password=payload.password
    )

    access_token, refresh_token = create_tokens(subject=user.id)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@auth_router.post("/refresh", response_model=RefreshPayload)
async def refresh(payload: RefreshPayload, db: DbDep):
    user_id = verify_refresh_tokens(payload.refresh_token)

    user = await db.get(User, int(user_id))
    if not user:
        raise InvalidTokenException("User no longer exists.")

    access_token, refresh_token = create_tokens(subject=user.id)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@auth_router.post(
    "/forgot-password",
    response_model=VerifyCodeResponse,
    status_code=status.HTTP_200_OK,
)
async def forgot_password(
    payload: ForgotPasswordPayload, background_tasks: BackgroundTasks, db: DbDep
):
    user, token = await auth_service.request_password_reset(db, payload.identifier)

    if user and token:
        reset_link = f"http://localhost:3000/reset-password?token={token}"

        background_tasks.add_task(
            email_service.send_password_reset_email,
            email_to=user.email,
            link=reset_link,
        )

    return VerifyCodeResponse(
        message="If an account with that identifier exists, a password link has been sent."
    )


@auth_router.post(
    "/reset-password", response_model=VerifyCodeResponse, status_code=status.HTTP_200_OK
)
async def reset_password(payload: ResetPasswordPayload, db: DbDep):
    await auth_service.reset_password(db, payload.token, payload.new_password)

    return VerifyCodeResponse(
        message="Your password has been successfully reset. You can now log in."
    )
