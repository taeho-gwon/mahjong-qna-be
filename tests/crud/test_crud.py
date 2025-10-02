import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.question import (
    create_question,
    delete_question,
    read_question_by_id,
    read_questions,
    update_question,
)
from app.schemas.question import QuestionCreate, QuestionUpdate


@pytest.mark.asyncio
class TestQuestionCRUD:
    async def test_create_question(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        question_in = QuestionCreate(**sample_question_data)
        question = await create_question(db_session, question_in)

        assert question.id is not None
        assert question.title == sample_question_data["title"]
        assert question.content == sample_question_data["content"]
        assert question.author_nickname == sample_question_data["author_nickname"]
        assert question.created_at is not None

    async def test_read_question_by_id_success(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        question_in = QuestionCreate(**sample_question_data)
        created_question = await create_question(db_session, question_in)

        question = await read_question_by_id(db_session, created_question.id)

        assert question is not None
        assert question.id == created_question.id
        assert question.title == sample_question_data["title"]

    async def test_read_question_by_id_not_found(self, db_session: AsyncSession):
        question = await read_question_by_id(db_session, 999999)

        assert question is None

    async def test_read_questions_pagination(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        num_questions = 5
        for i in range(num_questions):
            data = sample_question_data.copy()
            data["title"] = f"테스트 질문 {i + 1}"
            question_in = QuestionCreate(**data)
            await create_question(db_session, question_in)

        questions, total = await read_questions(db_session, skip=1, limit=2)

        assert total == num_questions
        assert len(questions) == 2
        assert questions[0].created_at >= questions[1].created_at

    async def test_read_questions_empty(self, db_session: AsyncSession):
        questions, total = await read_questions(db_session)

        assert questions == []
        assert total == 0

    async def test_update_question_success(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        question_in = QuestionCreate(**sample_question_data)
        created_question = await create_question(db_session, question_in)

        update_data = QuestionUpdate(
            title="수정된 제목",
            content="수정된 내용입니다. 최소 10자 이상이어야 합니다.",
        )
        updated_question = await update_question(
            db_session,
            created_question.id,
            update_data,
        )

        assert updated_question is not None
        assert updated_question.id == created_question.id
        assert updated_question.title == "수정된 제목"
        assert updated_question.content == "수정된 내용입니다. 최소 10자 이상이어야 합니다."
        assert updated_question.author_nickname == sample_question_data["author_nickname"]

    async def test_update_question_partial(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        question_in = QuestionCreate(**sample_question_data)
        created_question = await create_question(db_session, question_in)
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

    async def test_update_question_not_found(self, db_session: AsyncSession):
        update_data = QuestionUpdate(title="수정 시도")
        updated_question = await update_question(db_session, 999999, update_data)

        assert updated_question is None

    async def test_delete_question_success(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        question_in = QuestionCreate(**sample_question_data)
        created_question = await create_question(db_session, question_in)
        question_id = created_question.id

        result = await delete_question(db_session, question_id)

        assert result is True
        deleted_question = await read_question_by_id(db_session, question_id)
        assert deleted_question is None

    async def test_delete_question_not_found(self, db_session: AsyncSession):
        result = await delete_question(db_session, 999999)

        assert result is False

    async def test_question_created_at_auto_set(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        question_in = QuestionCreate(**sample_question_data)
        question = await create_question(db_session, question_in)

        assert question.created_at is not None
