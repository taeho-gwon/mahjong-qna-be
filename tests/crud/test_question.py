import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.question import (
    delete_question,
    read_question_by_id,
    read_questions,
    update_question,
)
from app.schemas.question import QuestionUpdate
from tests.factories import create_test_question, create_test_user


@pytest.mark.asyncio
class TestQuestionCRUD:
    async def test_create_question(self, db_session: AsyncSession):
        user = await create_test_user(db_session)
        question = await create_test_question(db_session, user.id)

        assert question.id is not None
        assert question.title == "테스트 질문입니다"
        assert question.author_id == user.id

    async def test_read_question_by_id_success(self, db_session: AsyncSession):
        user = await create_test_user(db_session)
        created_question = await create_test_question(db_session, user.id)

        question = await read_question_by_id(db_session, created_question.id)

        assert question is not None
        assert question.id == created_question.id
        assert question.title == created_question.title

    async def test_read_question_by_id_not_found(self, db_session: AsyncSession):
        question = await read_question_by_id(db_session, 999999)

        assert question is None

    async def test_read_questions_pagination(self, db_session: AsyncSession):
        user = await create_test_user(db_session)

        for i in range(5):
            await create_test_question(db_session, user.id, title=f"테스트 질문 {i + 1}번")

        questions, total = await read_questions(db_session, skip=1, limit=2)

        assert total == 5
        assert len(questions) == 2

    async def test_read_questions_empty(self, db_session: AsyncSession):
        questions, total = await read_questions(db_session)

        assert questions == []
        assert total == 0

    async def test_read_questions_default_limit(self, db_session: AsyncSession):
        user = await create_test_user(db_session)

        for i in range(15):
            await create_test_question(db_session, user.id, title=f"테스트 질문 {i + 1}번")

        questions, total = await read_questions(db_session)

        assert total == 15
        assert len(questions) == 10

    async def test_update_question_full(self, db_session: AsyncSession):
        user = await create_test_user(db_session)
        created_question = await create_test_question(db_session, user.id)

        update_data = QuestionUpdate(
            title="수정된 제목입니다",
            content="수정된 내용입니다. 최소 10자 이상이어야 합니다.",
        )
        updated_question = await update_question(
            db_session,
            created_question.id,
            update_data,
        )

        assert updated_question is not None
        assert updated_question.id == created_question.id
        assert updated_question.title == "수정된 제목입니다"
        assert updated_question.content == "수정된 내용입니다. 최소 10자 이상이어야 합니다."
        assert updated_question.author_id == user.id

    async def test_update_question_partial_title(self, db_session: AsyncSession):
        user = await create_test_user(db_session)
        created_question = await create_test_question(db_session, user.id)
        original_content = created_question.content

        update_data = QuestionUpdate(title="제목만 수정했습니다")
        updated_question = await update_question(
            db_session,
            created_question.id,
            update_data,
        )

        assert updated_question is not None
        assert updated_question.title == "제목만 수정했습니다"
        assert updated_question.content == original_content

    async def test_update_question_partial_content(self, db_session: AsyncSession):
        user = await create_test_user(db_session)
        created_question = await create_test_question(db_session, user.id)
        original_title = created_question.title

        update_data = QuestionUpdate(content="내용만 수정했습니다. 최소 10자 이상.")
        updated_question = await update_question(
            db_session,
            created_question.id,
            update_data,
        )

        assert updated_question is not None
        assert updated_question.title == original_title
        assert updated_question.content == "내용만 수정했습니다. 최소 10자 이상."

    async def test_update_question_not_found(self, db_session: AsyncSession):
        update_data = QuestionUpdate(title="수정 시도")
        updated_question = await update_question(db_session, 999999, update_data)

        assert updated_question is None

    async def test_delete_question_success(self, db_session: AsyncSession):
        user = await create_test_user(db_session)
        created_question = await create_test_question(db_session, user.id)
        question_id = created_question.id

        result = await delete_question(db_session, question_id)

        assert result is True
        deleted_question = await read_question_by_id(db_session, question_id)
        assert deleted_question is None

    async def test_delete_question_not_found(self, db_session: AsyncSession):
        result = await delete_question(db_session, 999999)

        assert result is False

    async def test_create_multiple_questions(self, db_session: AsyncSession):
        user = await create_test_user(db_session)

        questions = []
        for i in range(3):
            question = await create_test_question(
                db_session, user.id, title=f"테스트 질문 {i + 1}번"
            )
            questions.append(question)

        question_ids = [q.id for q in questions]
        assert len(question_ids) == len(set(question_ids))
        assert all(q.id is not None for q in questions)

    async def test_read_questions_with_skip_and_limit(self, db_session: AsyncSession):
        user = await create_test_user(db_session)

        for i in range(10):
            await create_test_question(
                db_session, user.id, title=f"페이지네이션 테스트 질문 {i + 1}번"
            )

        page1, total = await read_questions(db_session, skip=0, limit=3)
        assert len(page1) == 3
        assert total == 10

        page2, total = await read_questions(db_session, skip=3, limit=3)
        assert len(page2) == 3
        assert total == 10

        page_last, total = await read_questions(db_session, skip=9, limit=3)
        assert len(page_last) == 1
        assert total == 10
