from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db

DbDep = Annotated[AsyncSession, Depends(get_db)]
