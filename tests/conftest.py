import asyncio
from collections.abc import AsyncGenerator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.models.base import Base


settings = get_settings()

TEST_DB_NAME = f"{settings.postgres_db}_test"
TEST_DATABASE_URL = settings.database_url.replace(settings.postgres_db, TEST_DB_NAME)
POSTGRES_URL = settings.database_url.replace(settings.postgres_db, "postgres")


async def create_test_database():
    """테스트 데이터베이스 생성"""
    engine = create_async_engine(
        POSTGRES_URL,
        isolation_level="AUTOCOMMIT",
    )

    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                f"""
                SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}'
                """
            )
        )
        exists = result.scalar()

        if not exists:
            await conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
            print(f"\n✅ 테스트 DB 생성: {TEST_DB_NAME}")
        else:
            print(f"\n✅ 테스트 DB 이미 존재: {TEST_DB_NAME}")

    await engine.dispose()


async def drop_test_database():
    """테스트 데이터베이스 삭제"""
    engine = create_async_engine(
        POSTGRES_URL,
        isolation_level="AUTOCOMMIT",
    )

    async with engine.connect() as conn:
        await conn.execute(
            text(
                f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{TEST_DB_NAME}'
                AND pid <> pg_backend_pid()
                """
            )
        )

        await conn.execute(text(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"'))
        print(f"\n✅ 테스트 DB 삭제: {TEST_DB_NAME}")

    await engine.dispose()


@pytest.fixture(scope="session")
def event_loop():
    """이벤트 루프 fixture"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine(event_loop):
    """테스트 엔진 fixture"""
    await create_test_database()

    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

    # 테스트 DB 삭제 (필요시 주석 해제)
    # await drop_test_database()


@pytest.fixture(scope="session")
def test_session_maker(test_engine):
    """세션 메이커 fixture"""
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture
async def db_session(test_session_maker) -> AsyncGenerator[AsyncSession]:
    """
    데이터베이스 세션 fixture

    CRUD 함수가 commit을 호출하지 않으므로,
    단순히 rollback만으로 테스트 격리가 보장됩니다.
    """
    async with test_session_maker() as session:
        yield session
        await session.rollback()  # ✅ 단순한 rollback으로 격리!


@pytest.fixture
def sample_question_data():
    """샘플 질문 데이터 fixture"""
    return {
        "title": "테스트 질문입니다",
        "content": "이것은 테스트용 질문 내용입니다. 최소 10자 이상이어야 합니다.",
        "author_nickname": "테스터",
    }


@pytest.fixture
def sample_answer_data():
    """샘플 답변 데이터 fixture"""
    return {
        "content": "이것은 테스트용 답변 내용입니다. 최소 10자 이상이어야 합니다.",
        "author_nickname": "답변자",
    }
