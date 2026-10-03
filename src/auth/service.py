from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import DuplicateEntityException
from src.auth.models import User
from src.auth.schemas import UserRegister


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def register_user(db: AsyncSession, user_data: UserRegister) -> User:
    existing = await get_user_by_email(db, user_data.email)

    if existing:
        raise DuplicateEntityException(field="username", value=user_data.username)

    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=user_data.password,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
