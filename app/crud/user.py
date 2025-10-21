from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import hash_password
from app.models.user import User
from app.schemas.user import UserSignup


async def create_user(db: AsyncSession, user_in: UserSignup) -> User:
    hashed_password = hash_password(user_in.password)

    user = User(
        username=user_in.username,
        hashed_password=hashed_password,
    )

    db.add(user)
    await db.flush()
    await db.refresh(user)

    return user


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
