import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.answer import (
    create_answer,
    delete_answer,
    read_answer_by_id,
    read_answers_by_question_id,
    update_answer,
)
from app.crud.question import create_question, delete_question
from app.schemas.answer import AnswerCreate, AnswerUpdate
from app.schemas.question import QuestionCreate


@pytest.mark.asyncio
class TestAnswerCRUD:
    @pytest.fixture
    async def question_id(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
    ) -> int:
        question_in = QuestionCreate(**sample_question_data)
        question = await create_question(db_session, question_in)
        return question.id

    async def test_create_answer(
        self,
        db_session: AsyncSession,
        question_id: int,
        sample_answer_data: dict,
    ):
        answer_in = AnswerCreate(**sample_answer_data)
        answer = await create_answer(db_session, question_id, answer_in)

        assert answer.id is not None
        assert answer.question_id == question_id
        assert answer.content == sample_answer_data["content"]
        assert answer.author_nickname == sample_answer_data["author_nickname"]

    async def test_read_answer_by_id_success(
        self,
        db_session: AsyncSession,
        question_id: int,
        sample_answer_data: dict,
    ):
        answer_in = AnswerCreate(**sample_answer_data)
        created_answer = await create_answer(db_session, question_id, answer_in)
        answer = await read_answer_by_id(db_session, created_answer.id)

        assert answer is not None
        assert answer.id == created_answer.id
        assert answer.question_id == question_id
        assert answer.content == sample_answer_data["content"]

    async def test_read_answer_by_id_not_found(self, db_session: AsyncSession):
        answer = await read_answer_by_id(db_session, 999999)

        assert answer is None

    async def test_read_answers_by_question_id(
        self,
        db_session: AsyncSession,
        question_id: int,
        sample_answer_data: dict,
    ):
        num_answers = 3
        for i in range(num_answers):
            data = sample_answer_data.copy()
            data["content"] = f"답변 내용 {i + 1}번입니다. 최소 10자 이상."
            answer_in = AnswerCreate(**data)
            await create_answer(db_session, question_id, answer_in)

        answers, total = await read_answers_by_question_id(db_session, question_id)

        assert total == num_answers
        assert len(answers) == num_answers
        assert all(a.question_id == question_id for a in answers)

    async def test_read_answers_pagination(
        self,
        db_session: AsyncSession,
        question_id: int,
        sample_answer_data: dict,
    ):
        num_answers = 5
        for i in range(num_answers):
            data = sample_answer_data.copy()
            data["content"] = f"답변 {i + 1}번 - 최소 10자 이상의 내용."
            answer_in = AnswerCreate(**data)
            await create_answer(db_session, question_id, answer_in)

        answers, total = await read_answers_by_question_id(
            db_session,
            question_id,
            skip=1,
            limit=2,
        )

        assert total == num_answers
        assert len(answers) == 2

    async def test_read_answers_empty(
        self,
        db_session: AsyncSession,
        question_id: int,
    ):
        answers, total = await read_answers_by_question_id(db_session, question_id)

        assert answers == []
        assert total == 0

    async def test_read_answers_different_questions(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
        sample_answer_data: dict,
    ):
        question1_in = QuestionCreate(**sample_question_data)
        question1 = await create_question(db_session, question1_in)

        data2 = sample_question_data.copy()
        data2["title"] = "두 번째 질문입니다"
        question2_in = QuestionCreate(**data2)
        question2 = await create_question(db_session, question2_in)

        answer1_in = AnswerCreate(**sample_answer_data)
        await create_answer(db_session, question1.id, answer1_in)

        answer2_data = sample_answer_data.copy()
        answer2_data["content"] = "두 번째 질문에 대한 답변입니다. 최소 10자."
        answer2_in = AnswerCreate(**answer2_data)
        await create_answer(db_session, question2.id, answer2_in)

        answers1, total1 = await read_answers_by_question_id(db_session, question1.id)
        answers2, total2 = await read_answers_by_question_id(db_session, question2.id)

        assert total1 == 1
        assert total2 == 1
        assert answers1[0].question_id == question1.id
        assert answers2[0].question_id == question2.id

    async def test_update_answer_success(
        self,
        db_session: AsyncSession,
        question_id: int,
        sample_answer_data: dict,
    ):
        answer_in = AnswerCreate(**sample_answer_data)
        created_answer = await create_answer(db_session, question_id, answer_in)
        original_author = created_answer.author_nickname

        update_data = AnswerUpdate(content="수정된 답변 내용입니다. 최소 10자 이상.")
        updated_answer = await update_answer(
            db_session,
            created_answer.id,
            update_data,
        )

        assert updated_answer is not None
        assert updated_answer.id == created_answer.id
        assert updated_answer.content == "수정된 답변 내용입니다. 최소 10자 이상."
        assert updated_answer.question_id == question_id
        assert updated_answer.author_nickname == original_author

    async def test_update_answer_not_found(self, db_session: AsyncSession):
        update_data = AnswerUpdate(content="수정 시도 - 최소 10자 이상입니다.")
        updated_answer = await update_answer(db_session, 999999, update_data)
        assert updated_answer is None

    async def test_delete_answer_success(
        self,
        db_session: AsyncSession,
        question_id: int,
        sample_answer_data: dict,
    ):
        answer_in = AnswerCreate(**sample_answer_data)
        created_answer = await create_answer(db_session, question_id, answer_in)
        answer_id = created_answer.id

        result = await delete_answer(db_session, answer_id)

        assert result is True
        deleted_answer = await read_answer_by_id(db_session, answer_id)
        assert deleted_answer is None

    async def test_delete_answer_not_found(self, db_session: AsyncSession):
        result = await delete_answer(db_session, 999999)

        assert result is False

    async def test_cascade_delete_on_question_deletion(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
        sample_answer_data: dict,
    ):
        question_in = QuestionCreate(**sample_question_data)
        question = await create_question(db_session, question_in)

        answer_in = AnswerCreate(**sample_answer_data)
        answer = await create_answer(db_session, question.id, answer_in)
        answer_id = answer.id

        await delete_question(db_session, question.id)

        deleted_answer = await read_answer_by_id(db_session, answer_id)
        assert deleted_answer is None

    async def test_multiple_answers_for_same_question(
        self,
        db_session: AsyncSession,
        question_id: int,
        sample_answer_data: dict,
    ):
        answer_ids = []
        for i in range(3):
            data = sample_answer_data.copy()
            data["content"] = f"답변 {i + 1}번입니다. 최소 10자 이상."
            data["author_nickname"] = f"답변자{i + 1}"
            answer_in = AnswerCreate(**data)
            answer = await create_answer(db_session, question_id, answer_in)
            answer_ids.append(answer.id)

        answers, total = await read_answers_by_question_id(db_session, question_id)
        assert total == 3
        assert len(answers) == 3

        assert all(answer.question_id == question_id for answer in answers)

        assert len(answer_ids) == len(set(answer_ids))

    async def test_read_answers_with_skip_and_limit(
        self,
        db_session: AsyncSession,
        question_id: int,
        sample_answer_data: dict,
    ):
        for i in range(10):
            data = sample_answer_data.copy()
            data["content"] = f"페이지네이션 테스트 답변 {i + 1}번 내용."
            answer_in = AnswerCreate(**data)
            await create_answer(db_session, question_id, answer_in)

        page1, total = await read_answers_by_question_id(db_session, question_id, skip=0, limit=3)
        assert len(page1) == 3
        assert total == 10

        page2, total = await read_answers_by_question_id(db_session, question_id, skip=3, limit=3)
        assert len(page2) == 3
        assert total == 10

        page_last, total = await read_answers_by_question_id(
            db_session, question_id, skip=9, limit=3
        )
        assert len(page_last) == 1
        assert total == 10
