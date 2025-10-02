import asyncio
from collections.abc import AsyncGenerator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)

from app.core.config import get_settings
from app.models.base import Base


settings = get_settings()

TEST_DB_NAME = f"{settings.postgres_db}_test"
TEST_DATABASE_URL = settings.database_url.replace(settings.postgres_db, TEST_DB_NAME)
POSTGRES_URL = settings.database_url.replace(settings.postgres_db, "postgres")


async def create_test_database():
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

    await engine.dispose()


async def drop_test_database():
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

    await engine.dispose()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine(event_loop):
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


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession]:
    async with test_engine.connect() as connection:
        transaction = await connection.begin()

        async_session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
        )

        yield async_session

        await async_session.close()
        await transaction.rollback()


@pytest.fixture
def sample_question_data():
    return {
        "title": "테스트 질문입니다",
        "content": "이것은 테스트용 질문 내용입니다. 최소 10자 이상이어야 합니다.",
        "author_nickname": "테스터",
    }


@pytest.fixture
def sample_answer_data():
    return {
        "content": "이것은 테스트용 답변 내용입니다. 최소 10자 이상이어야 합니다.",
        "author_nickname": "답변자",
    }
