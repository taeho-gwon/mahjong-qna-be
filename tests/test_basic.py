import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import create_test_answer, create_test_question, create_test_user


@pytest.mark.asyncio
class TestBasicSetup:
    async def test_db_connection(self, db_session: AsyncSession):
        result = await db_session.execute(text("SELECT version()"))
        version = result.scalar()

        assert version is not None
        assert "PostgreSQL" in version

    async def test_tables_exist(self, db_session: AsyncSession):
        result = await db_session.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'questions'
                )
                """
            )
        )
        exists = result.scalar()
        assert exists is True
        print("\n✅ questions 테이블 존재 확인")

        result = await db_session.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'answers'
                )
                """
            )
        )
        exists = result.scalar()
        assert exists is True

    async def test_factory_functions(self, db_session: AsyncSession):
        user = await create_test_user(db_session)
        assert user.id is not None
        assert user.username == "testuser"

        question = await create_test_question(db_session, user.id)
        assert question.id is not None
        assert len(question.title) >= 5
        assert len(question.content) >= 10
        assert question.author_id == user.id

        answer = await create_test_answer(db_session, question.id, user.id)
        assert answer.id is not None
        assert len(answer.content) >= 10
        assert answer.question_id == question.id
        assert answer.author_id == user.id

    async def test_transaction_isolation(self, db_session: AsyncSession):
        await db_session.execute(text("CREATE TEMP TABLE test_isolation (id INT, name TEXT)"))
        await db_session.execute(text("INSERT INTO test_isolation VALUES (1, 'test')"))

        result = await db_session.execute(text("SELECT COUNT(*) FROM test_isolation"))
        count = result.scalar()
        assert count == 1


@pytest.mark.asyncio
class TestFixtureScopes:
    async def test_engine_scope_shared_1(self, test_engine):
        fixture_id = id(test_engine)
        print(f"\n테스트 1 - Engine ID: {fixture_id}")

    async def test_engine_scope_shared_2(self, test_engine):
        fixture_id = id(test_engine)
        print(f"테스트 2 - Engine ID: {fixture_id}")

    async def test_session_scope_different_1(self, db_session: AsyncSession):
        session_id = id(db_session)
        print(f"\n테스트 1 - Session ID: {session_id}")

    async def test_session_scope_different_2(self, db_session: AsyncSession):
        session_id = id(db_session)
        print(f"테스트 2 - Session ID: {session_id}")
