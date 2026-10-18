from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from src.auth.exceptions import InvalidTokenException
from src.config import settings


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    salt = bcrypt.gensalt(rounds=12)

    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")

    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_tokens(subject: str | int) -> tuple[str, str]:
    now = datetime.now(UTC)

    access_exp = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_payload = {"sub": str(subject), "exp": access_exp, "type": "access"}
    access_token = jwt.encode(
        access_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    refresh_exp = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_payload = {"sub": str(subject), "exp": refresh_exp, "type": "refresh"}
    refresh_token = jwt.encode(
        refresh_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return access_token, refresh_token


def verify_refresh_tokens(token: str) -> str:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        if payload.get("type") != "refresh":
            raise InvalidTokenException("Invalid token type.")

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenException("Invalid token payload.")

        return user_id

    except jwt.ExpiredSignatureError:
        raise InvalidTokenException("Session expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise InvalidTokenException("Invalid refresh token.")
