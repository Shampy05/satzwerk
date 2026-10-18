from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.cache import valkey_client


class TestRegistration:
    @patch("src.auth.router.email_service.send_verification_code")
    @pytest.mark.asyncio
    async def test_register_user_success(self, mock_email, client: AsyncClient):
        payload = {
            "email": "newuser@example.com",
            "username": "newuser123",
            "password": "SecurePassword123",
        }

        response = await client.post("/auth/register", json=payload)

        assert response.status_code == 201
        response_json = response.json()
        data = response_json["data"]
        assert data["email"] == payload["email"]
        assert data["is_verified"] == False

        mock_email.assert_called_once()

        call_kwargs = mock_email.call_args.kwargs
        assert call_kwargs["email_to"] == payload["email"]
        assert "code" in call_kwargs

    @pytest.mark.asyncio
    async def test_register_duplicate_user(self, client: AsyncClient):
        payload = {
            "email": "duplicate@example.com",
            "username": "duplicate_user",
            "password": "SecurePassword123",
        }

        response1 = await client.post("/auth/register", json=payload)
        assert response1.status_code == 201

        response2 = await client.post("/auth/register", json=payload)

        assert response2.status_code == 409

        error_data = response2.json()

        assert error_data["error"] == "domain_error"
        assert error_data["field"] in ["email", "username"]

    @pytest.mark.parametrize(
        "invalid_payload, expected_failed_field",
        [
            (
                {
                    "email": "not-an-email",
                    "username": "valid-user",
                    "password": "SecurePassword123",
                },
                "email",
            ),
            (
                {
                    "email": "valid@exmaple.com",
                    "username": "valid-user",
                    "password": "short",
                },
                "password",
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_register_validation_errors(
        self, invalid_payload: dict, expected_failed_field: str, client: AsyncClient
    ):
        response = await client.post("/auth/register", json=invalid_payload)

        assert response.status_code == 422

        error_detail = response.json()["detail"]
        failed_fields = [error["loc"][-1] for error in error_detail]
        assert expected_failed_field in failed_fields


class TestVerifificationCode:
    @pytest.mark.asyncio
    async def test_verify_code_successful(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        register_payload = {
            "email": "test_verify@example.com",
            "username": "newuser123",
            "password": "SecurePassword123",
        }

        await client.post("/auth/register", json=register_payload)

        result = await db_session.execute(
            select(User).where(User.email == "test_verify@example.com")
        )
        user = result.scalar_one()

        cache_key = f"email_verification:{user.id}"
        code_bytes = await valkey_client.get(cache_key)

        assert code_bytes is not None, "Verification key was not saved to Valkey"

        actual_code = (
            code_bytes.decode("utf-8") if isinstance(code_bytes, bytes) else code_bytes
        )

        verify_payload = {"identifier": "test_verify@example.com", "code": actual_code}
        response = await client.post("/auth/verify-code", json=verify_payload)

        assert response.status_code == 200

        await db_session.refresh(user)
        assert user.is_verified is True

        deleted_code = await valkey_client.get(cache_key)
        assert deleted_code is None

    @pytest.mark.asyncio
    async def test_verify_code_invalid_code(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        await client.post(
            "/auth/register",
            json={
                "email": "badcode@example.com",
                "username": "badcode",
                "password": "SecureCode123",
            },
        )

        payload = {"identifier": "badcode@example.com", "code": "000000"}

        response = await client.post("/auth/verify-code", json=payload)

        assert response.status_code == 400

        result = await db_session.execute(
            select(User).where(User.email == "badcode@example.com")
        )
        user = result.scalar_one()
        assert user.is_verified is False


# @auth_router.post(
#     "/verify-code",
#     response_model=VerifyCodeResponse,
#     status_code=status.HTTP_200_OK,
# )
# async def verify_code(payload: VerifyCodeRequest, db: DbDep):
#     await auth_service.verify_user_email(db, payload.identifier, payload.code)

#     return VerifyCodeResponse(message="Account successfully verified.")


class TestLogin:
    async def test_login_success(self, client: AsyncClient, verified_user: User):
        response = await client.post(
            "/auth/login",
            json={"identifier": verified_user.email, "password": "SecurePassword123!"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_login_unverified_account(
        self, client: AsyncClient, unverified_user: User
    ):
        response = await client.post(
            "/auth/login",
            json={
                "identifier": unverified_user.email,
                "password": "SecurePassword123!",
            },
        )

        assert response.status_code in (401, 403)
        assert (
            response.json()["message"]
            == "Please verify your account before logging in."
        )

    async def test_login_wrong_credentials(
        self, client: AsyncClient, verified_user: User
    ):

        response = await client.post(
            "/auth/login",
            json={
                "identifier": verified_user.email,
                "password": "WrongPassword",
            },
        )

        assert response.status_code == 401


class TestForgotPassword:
    @pytest.mark.asyncio
    async def test_forgot_password_prevents_enumeration(self, client: AsyncClient):
        response = await client.post(
            "/auth/forgot-password", json={"identifier": "ghost@example.com"}
        )

        assert response.status_code == 200
        assert "If an account" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_full_password_reset_flow(
        self, client: AsyncClient, verified_user: User
    ):
        forgot_res = await client.post(
            "/auth/forgot-password", json={"identifier": verified_user.email}
        )
        assert forgot_res.status_code == 200

        keys = await valkey_client.keys("password_reset:*")
        assert len(keys) == 1
        reset_key = keys[0].decode("utf-8") if isinstance(keys[0], bytes) else keys[0]
        token = reset_key.split(":")[1]

        reset_res = await client.post(
            "/auth/reset-password",
            json={"token": token, "new_password": "BrandNewPassword!"},
        )

        assert reset_res.status_code == 200

        token_exists = await valkey_client.exists(reset_key)
        assert not token_exists

        old_login = await client.post(
            "/auth/login",
            json={"identifier": verified_user.email, "password": "SecurePassword123!"},
        )
        assert old_login.status_code == 401

        new_login = await client.post(
            "/auth/login",
            json={"identifier": verified_user.email, "password": "BrandNewPassword!"},
        )
        assert new_login.status_code == 200
        assert "access_token" in new_login.json()
