import logging
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings


settings = get_settings()

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=300,
    poolclass=NullPool,
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"데이터베이스 세션 오류: {e}")
            await session.rollback()
            raise


async def test_connection() -> bool:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT version()"))
            version_info = result.fetchone()
            if version_info:
                logger.info(f"데이터베이스 연결 성공! PostgreSQL 버전: {version_info[0][:50]}...")
                return True
            return False
    except Exception as e:
        logger.error(f"데이터베이스 연결 테스트 실패: {e}")
        return False


def get_db_info() -> dict:
    return {
        "database_url": settings.database_url.replace(settings.postgres_password, "***"),
        "pool_class": "NullPool",
        "echo": engine.echo,
    }
