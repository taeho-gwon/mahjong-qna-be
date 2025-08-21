"""
데이터베이스 연결 및 세션 관리

이 모듈은 SQLAlchemy를 사용하여 PostgreSQL 데이터베이스와의 비동기 연결을 관리합니다.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from typing import AsyncGenerator
import logging

from app.core.config import get_settings

# 설정 로드
settings = get_settings()

# 로깅 설정
logger = logging.getLogger(__name__)

# 비동기 데이터베이스 엔진 생성
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # 개발 환경에서 SQL 쿼리 로깅
    pool_pre_ping=True,  # 연결 상태 확인
    pool_recycle=300,  # 5분마다 연결 재생성 (연결 timeout 방지)
    poolclass=NullPool,  # 비동기 엔진에서는 NullPool 사용
    # psycopg3에서는 server_settings 사용 불가
    # connect_args는 필요시에만 사용
)

# 비동기 세션 팩토리 생성
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    비동기 데이터베이스 세션을 생성하고 반환합니다.

    FastAPI의 의존성 주입(Dependency Injection)에서 사용됩니다.
    자동으로 세션을 관리하고 트랜잭션을 처리합니다.

    Yields:
        AsyncSession: SQLAlchemy 비동기 데이터베이스 세션
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"데이터베이스 세션 오류: {e}")
            await session.rollback()  # 오류 발생시 롤백
            raise


# 호환성을 위한 별칭
get_async_session = get_session


async def test_connection() -> bool:
    """
    데이터베이스 연결을 테스트합니다.

    Returns:
        bool: 연결 성공 여부
    """
    try:
        async with AsyncSessionLocal() as session:
            # PostgreSQL 버전 확인으로 연결 테스트 (더 의미있는 쿼리)
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
    """
    데이터베이스 연결 정보를 반환합니다.

    Returns:
        dict: 데이터베이스 연결 정보 (민감한 정보 제외)
    """
    return {
        "database_url": settings.database_url.replace(
            settings.postgres_password, "***"
        ),  # 패스워드 숨김
        "pool_class": "NullPool",  # 비동기 엔진에서는 NullPool 사용
        "echo": engine.echo,
    }
