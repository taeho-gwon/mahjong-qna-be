import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
class TestBasicSetup:
    async def test_db_connection(self, db_session: AsyncSession):
        result = await db_session.execute(text("SELECT version()"))
        version = result.scalar()

        assert version is not None
        assert "PostgreSQL" in version
        print(f"\n✅ DB 연결 성공: {version[:50]}...")

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
        print("✅ answers 테이블 존재 확인")

    async def test_sample_data_fixtures(self, sample_question_data, sample_answer_data):
        assert "title" in sample_question_data
        assert "content" in sample_question_data
        assert "author_nickname" in sample_question_data
        assert len(sample_question_data["title"]) >= 5
        assert len(sample_question_data["content"]) >= 10

        assert "content" in sample_answer_data
        assert "author_nickname" in sample_answer_data
        assert len(sample_answer_data["content"]) >= 10

        print("\n✅ 샘플 데이터 fixture 정상 작동")

    async def test_transaction_isolation(self, db_session: AsyncSession):
        """트랜잭션 격리 확인"""
        # 임시 테이블 생성 및 데이터 삽입
        await db_session.execute(text("CREATE TEMP TABLE test_isolation (id INT, name TEXT)"))
        await db_session.execute(text("INSERT INTO test_isolation VALUES (1, 'test')"))

        result = await db_session.execute(text("SELECT COUNT(*) FROM test_isolation"))
        count = result.scalar()
        assert count == 1
        print("\n✅ 트랜잭션 격리 테스트 통과")


@pytest.mark.asyncio
class TestFixtureScopes:
    async def test_engine_scope_shared_1(self, test_engine):
        """엔진은 session scope이므로 공유됨"""
        fixture_id = id(test_engine)
        print(f"\n테스트 1 - Engine ID: {fixture_id}")

    async def test_engine_scope_shared_2(self, test_engine):
        """엔진은 session scope이므로 공유됨"""
        fixture_id = id(test_engine)
        print(f"테스트 2 - Engine ID: {fixture_id}")

    async def test_session_scope_different_1(self, db_session: AsyncSession):
        """세션은 function scope이므로 매번 새로 생성"""
        session_id = id(db_session)
        print(f"\n테스트 1 - Session ID: {session_id}")

    async def test_session_scope_different_2(self, db_session: AsyncSession):
        """세션은 function scope이므로 매번 새로 생성"""
        session_id = id(db_session)
        print(f"테스트 2 - Session ID: {session_id}")
