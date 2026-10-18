import asyncio
import secrets
import string

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import (
    DuplicateEntityException,
    InvalidCredentialsException,
    InvalidTokenException,
    InvalidVerificationException,
    RateLimitException,
    UnverifiedAccountException,
)
from src.auth.models import User
from src.auth.schema import UserRegister
from src.auth.security import hash_password, verify_password
from src.cache import valkey_client
from src.config import settings


def generate_six_digit_code() -> str:
    return "".join(secrets.choice(string.digits) for _ in range(6))


async def get_user_by_email_or_username(
    db: AsyncSession, email: str, username: str
) -> User | None:
    query = select(User).where(or_(User.email == email, User.username == username))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_indentifier(db: AsyncSession, identifier: str) -> User | None:
    if "@" in identifier:
        query = select(User).where(User.email == identifier)
    else:
        query = select(User).where(User.username == identifier)

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def register_user(db: AsyncSession, user_data: UserRegister) -> tuple[User, str]:
    existing = await get_user_by_email_or_username(
        db, user_data.email, user_data.username
    )

    if existing:
        if existing.email == user_data.email:
            raise DuplicateEntityException(field="email", value=user_data.email)
        raise DuplicateEntityException(field="username", value=user_data.username)

    hashed_pw = await asyncio.to_thread(hash_password, user_data.password)

    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_pw,
    )

    db.add(new_user)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise DuplicateEntityException("username or email", value=user_data.email)

    await db.refresh(new_user)

    code = generate_six_digit_code()
    await valkey_client.set(f"email_verification:{new_user.id}", code, ex=900)

    return new_user, code


async def verify_user_email(db: AsyncSession, identifier: str, code: str) -> None:
    user = await get_user_by_indentifier(db=db, identifier=identifier)

    if not user:
        raise InvalidVerificationException("Invalid identifier or verification code.")

    if user.is_verified:
        raise InvalidVerificationException("This account is already verified.")

    cache_key = f"email_verification:{user.id}"
    stored_code = await valkey_client.get(cache_key)

    if not stored_code or stored_code != code:
        raise InvalidVerificationException()

    user.is_verified = True
    await db.commit()

    await valkey_client.delete(cache_key)


async def authenticate_user(db: AsyncSession, identifier: str, password: str) -> User:
    user = await get_user_by_indentifier(db=db, identifier=identifier)
    if not user:
        raise InvalidCredentialsException()

    is_valid = await asyncio.to_thread(verify_password, password, user.hashed_password)
    if not is_valid:
        raise InvalidCredentialsException()

    if not user.is_verified:
        raise UnverifiedAccountException()

    return user


async def resend_verification_code(
    db: AsyncSession, identifier: str
) -> tuple[User, str]:
    user = await get_user_by_indentifier(db, identifier)

    if not user:
        raise InvalidVerificationException("Invalid identifier.")

    if user.is_verified:
        raise InvalidVerificationException("The user is already verified.")

    lock_key = f"resend_lock:{user.id}"
    is_locked = await valkey_client.get(lock_key)

    if is_locked:
        raise RateLimitException("Please wait 60s before requesting a new code.")

    new_code = generate_six_digit_code()

    await valkey_client.set(
        f"email_verification:{user.id}", new_code, ex=settings.OTP_EXPIRATION_SECONDS
    )

    await valkey_client.set(lock_key, "locked", ex=settings.OTP_COOLDOWN_SECONDS)

    return user, new_code


async def request_password_reset(
    db: AsyncSession, identifier: str
) -> tuple[User | None, str | None]:
    user = await get_user_by_indentifier(db, identifier)

    if not user:
        return None, None

    reset_token = secrets.token_urlsafe(32)

    await valkey_client.set(f"password_reset:{reset_token}", user.id, ex=900)

    return user, reset_token


async def reset_password(db: AsyncSession, token: str, new_password: str) -> None:
    cache_key = f"password_reset:{token}"

    user_id = await valkey_client.get(cache_key)
    if not user_id:
        raise InvalidTokenException(
            "The password reset link is invalid or has expired."
        )

    user = await db.get(User, int(user_id))
    if not user:
        raise InvalidTokenException("User no longer exists.")

    hashed_pw = await asyncio.to_thread(hash_password, new_password)

    user.hashed_password = hashed_pw
    await db.commit()

    await valkey_client.delete(cache_key)
