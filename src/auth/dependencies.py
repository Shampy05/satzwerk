from typing import Annotated

import jwt
from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth.models import User
from src.config import settings
from src.dependencies import DbDep
from src.exceptions import AppException

security = HTTPBearer()


async def get_current_user(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)], db: DbDep
) -> User:
    try:
        payload = jwt.decode(
            token.credentials, settings.SECRET_KEY, algorithms=settings.ALGORITHM
        )

        user_id = payload.get("sub")
        if user_id is None:
            raise AppException(
                "Invalid token payload", status_code=status.HTTP_401_UNAUTHORIZED
            )
    except jwt.ExpiredSignatureError:
        raise AppException(
            "Token has expired. Please log in again.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    except jwt.InvalidSignatureError:
        raise AppException(
            "Invalid authentication token.", status_code=status.HTTP_401_UNAUTHORIZED
        )

    user = await db.get(User, int(user_id))
    if not user:
        raise AppException("User not found", status_code=status.HTTP_401_UNAUTHORIZED)

    return user
