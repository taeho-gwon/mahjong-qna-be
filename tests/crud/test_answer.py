import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.answer import (
    delete_answer,
    read_answer_by_id,
    read_answers_by_question_id,
    update_answer,
)
from app.crud.question import delete_question
from app.schemas.answer import AnswerUpdate
from tests.factories import create_test_answer, create_test_question, create_test_user


@pytest.mark.asyncio
class TestAnswerCRUD:
    async def test_create_answer(self, db_session: AsyncSession):
        user = await create_test_user(db_session)
        question = await create_test_question(db_session, user.id)
        answer = await create_test_answer(db_session, question.id, user.id)

        assert answer.id is not None
        assert answer.question_id == question.id
        assert answer.author_id == user.id

    async def test_read_answer_by_id_success(self, db_session: AsyncSession):
        user = await create_test_user(db_session)
        question = await create_test_question(db_session, user.id)
        created_answer = await create_test_answer(db_session, question.id, user.id)

        answer = await read_answer_by_id(db_session, created_answer.id)

        assert answer is not None
        assert answer.id == created_answer.id
        assert answer.question_id == question.id

    async def test_read_answer_by_id_not_found(self, db_session: AsyncSession):
        answer = await read_answer_by_id(db_session, 999999)

        assert answer is None

    async def test_read_answers_by_question_id(self, db_session: AsyncSession):
        user = await create_test_user(db_session)
        question = await create_test_question(db_session, user.id)

        for i in range(3):
            await create_test_answer(
                db_session,
                question.id,
                user.id,
                content=f"답변 내용 {i + 1}번입니다. 최소 10자 이상.",
            )

        answers, total = await read_answers_by_question_id(db_session, question.id)

        assert total == 3
        assert len(answers) == 3
        assert all(a.question_id == question.id for a in answers)

    async def test_read_answers_pagination(self, db_session: AsyncSession):
        user = await create_test_user(db_session)
        question = await create_test_question(db_session, user.id)

        for i in range(5):
            await create_test_answer(
                db_session,
                question.id,
                user.id,
                content=f"답변 {i + 1}번 - 최소 10자 이상의 내용.",
            )

        page1, total = await read_answers_by_question_id(db_session, question.id, skip=0, limit=2)
        assert len(page1) == 2
        assert total == 5

        page2, total = await read_answers_by_question_id(db_session, question.id, skip=2, limit=2)
        assert len(page2) == 2
        assert total == 5

    async def test_update_answer(self, db_session: AsyncSession):
        user = await create_test_user(db_session)
        question = await create_test_question(db_session, user.id)
        created_answer = await create_test_answer(db_session, question.id, user.id)

        update_data = AnswerUpdate(content="수정된 답변 내용입니다. 최소 10자 이상.")
        updated_answer = await update_answer(
            db_session,
            created_answer.id,
            update_data,
        )

        assert updated_answer is not None
        assert updated_answer.id == created_answer.id
        assert updated_answer.content == "수정된 답변 내용입니다. 최소 10자 이상."
        assert updated_answer.question_id == question.id
        assert updated_answer.author_id == user.id

    async def test_update_answer_not_found(self, db_session: AsyncSession):
        update_data = AnswerUpdate(content="수정 시도 - 최소 10자 이상입니다.")
        updated_answer = await update_answer(db_session, 999999, update_data)

        assert updated_answer is None

    async def test_delete_answer_success(self, db_session: AsyncSession):
        user = await create_test_user(db_session)
        question = await create_test_question(db_session, user.id)
        created_answer = await create_test_answer(db_session, question.id, user.id)
        answer_id = created_answer.id

        result = await delete_answer(db_session, answer_id)

        assert result is True
        deleted_answer = await read_answer_by_id(db_session, answer_id)
        assert deleted_answer is None

    async def test_delete_answer_not_found(self, db_session: AsyncSession):
        result = await delete_answer(db_session, 999999)

        assert result is False

    async def test_cascade_delete_on_question_deletion(self, db_session: AsyncSession):
        user = await create_test_user(db_session)
        question = await create_test_question(db_session, user.id)
        answer = await create_test_answer(db_session, question.id, user.id)
        answer_id = answer.id

        await delete_question(db_session, question.id)

        deleted_answer = await read_answer_by_id(db_session, answer_id)
        assert deleted_answer is None

    async def test_multiple_answers_for_same_question(self, db_session: AsyncSession):
        user = await create_test_user(db_session)
        question = await create_test_question(db_session, user.id)

        answer_ids = []
        for i in range(3):
            answer = await create_test_answer(
                db_session,
                question.id,
                user.id,
                content=f"답변 {i + 1}번입니다. 최소 10자 이상.",
            )
            answer_ids.append(answer.id)

        answers, total = await read_answers_by_question_id(db_session, question.id)
        assert total == 3
        assert len(answers) == 3
        assert all(answer.question_id == question.id for answer in answers)
        assert len(answer_ids) == len(set(answer_ids))

    async def test_read_answers_with_skip_and_limit(self, db_session: AsyncSession):
        user = await create_test_user(db_session)
        question = await create_test_question(db_session, user.id)

        for i in range(10):
            await create_test_answer(
                db_session,
                question.id,
                user.id,
                content=f"페이지네이션 테스트 답변 {i + 1}번 내용.",
            )

        page1, total = await read_answers_by_question_id(db_session, question.id, skip=0, limit=3)
        assert len(page1) == 3
        assert total == 10

        page2, total = await read_answers_by_question_id(db_session, question.id, skip=3, limit=3)
        assert len(page2) == 3
        assert total == 10

        page_last, total = await read_answers_by_question_id(
            db_session, question.id, skip=9, limit=3
        )
        assert len(page_last) == 1
        assert total == 10
