import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.answer import create_answer
from app.crud.question import create_question
from app.schemas.answer import AnswerCreate
from app.schemas.question import QuestionCreate


@pytest.mark.asyncio
class TestAnswerAPI:
    @pytest.fixture
    async def question_id(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
    ) -> int:
        question_in = QuestionCreate(**sample_question_data)
        question = await create_question(db_session, question_in)
        await db_session.commit()
        return question.id

    async def test_create_answer(
        self,
        api_client: AsyncClient,
        question_id: int,
        sample_answer_data: dict,
    ):
        response = await api_client.post(
            f"/questions/{question_id}/answers",
            json=sample_answer_data,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["question_id"] == question_id

    async def test_create_answer_question_not_found(
        self,
        api_client: AsyncClient,
        sample_answer_data: dict,
    ):
        response = await api_client.post(
            "/questions/999999/answers",
            json=sample_answer_data,
        )

        assert response.status_code == 404

    async def test_create_answer_validation_error(
        self,
        api_client: AsyncClient,
        question_id: int,
    ):
        invalid_data = {
            "content": "짧음",
            "author_nickname": "답변자",
        }
        response = await api_client.post(
            f"/questions/{question_id}/answers",
            json=invalid_data,
        )

        assert response.status_code == 422

    async def test_list_answers(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        question_id: int,
        sample_answer_data: dict,
    ):
        for i in range(3):
            data = sample_answer_data.copy()
            data["content"] = f"답변 {i + 1}번입니다. 최소 10자 이상."
            answer_in = AnswerCreate(**data)
            await create_answer(db_session, question_id, answer_in)
        await db_session.commit()

        response = await api_client.get(f"/questions/{question_id}/answers")

        assert response.status_code == 200
        assert len(response.json()) == 3

    async def test_list_answers_question_not_found(self, api_client: AsyncClient):
        response = await api_client.get("/questions/999999/answers")

        assert response.status_code == 404

    async def test_get_answer(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        question_id: int,
        sample_answer_data: dict,
    ):
        answer_in = AnswerCreate(**sample_answer_data)
        answer = await create_answer(db_session, question_id, answer_in)
        await db_session.commit()

        response = await api_client.get(f"/questions/{question_id}/answers/{answer.id}")

        assert response.status_code == 200
        assert response.json()["id"] == answer.id

    async def test_get_answer_not_found(
        self,
        api_client: AsyncClient,
        question_id: int,
    ):
        response = await api_client.get(f"/questions/{question_id}/answers/999999")

        assert response.status_code == 404

    async def test_get_answer_wrong_question(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        sample_question_data: dict,
        sample_answer_data: dict,
    ):
        question1_in = QuestionCreate(**sample_question_data)
        question1 = await create_question(db_session, question1_in)
        answer_in = AnswerCreate(**sample_answer_data)
        answer = await create_answer(db_session, question1.id, answer_in)

        data2 = sample_question_data.copy()
        data2["title"] = "두 번째 질문입니다"
        question2_in = QuestionCreate(**data2)
        question2 = await create_question(db_session, question2_in)
        await db_session.commit()

        response = await api_client.get(f"/questions/{question2.id}/answers/{answer.id}")

        assert response.status_code == 400

    async def test_update_answer(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        question_id: int,
        sample_answer_data: dict,
    ):
        answer_in = AnswerCreate(**sample_answer_data)
        answer = await create_answer(db_session, question_id, answer_in)
        await db_session.commit()

        update_data = {"content": "수정된 답변 내용입니다. 최소 10자 이상."}
        response = await api_client.patch(
            f"/questions/{question_id}/answers/{answer.id}",
            json=update_data,
        )

        assert response.status_code == 200
        assert response.json()["content"] == update_data["content"]

    async def test_update_answer_not_found(
        self,
        api_client: AsyncClient,
        question_id: int,
    ):
        update_data = {"content": "수정 시도합니다. 최소 10자 이상."}
        response = await api_client.patch(
            f"/questions/{question_id}/answers/999999",
            json=update_data,
        )

        assert response.status_code == 404

    async def test_update_answer_wrong_question(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        sample_question_data: dict,
        sample_answer_data: dict,
    ):
        question1_in = QuestionCreate(**sample_question_data)
        question1 = await create_question(db_session, question1_in)
        answer_in = AnswerCreate(**sample_answer_data)
        answer = await create_answer(db_session, question1.id, answer_in)

        data2 = sample_question_data.copy()
        data2["title"] = "두 번째 질문입니다"
        question2_in = QuestionCreate(**data2)
        question2 = await create_question(db_session, question2_in)
        await db_session.commit()

        update_data = {"content": "수정 시도합니다. 최소 10자 이상."}
        response = await api_client.patch(
            f"/questions/{question2.id}/answers/{answer.id}",
            json=update_data,
        )

        assert response.status_code == 400

    async def test_delete_answer(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        question_id: int,
        sample_answer_data: dict,
    ):
        answer_in = AnswerCreate(**sample_answer_data)
        answer = await create_answer(db_session, question_id, answer_in)
        await db_session.commit()

        response = await api_client.delete(f"/questions/{question_id}/answers/{answer.id}")

        assert response.status_code == 204

    async def test_delete_answer_not_found(
        self,
        api_client: AsyncClient,
        question_id: int,
    ):
        response = await api_client.delete(f"/questions/{question_id}/answers/999999")

        assert response.status_code == 404

    async def test_cascade_delete(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        sample_question_data: dict,
        sample_answer_data: dict,
    ):
        question_in = QuestionCreate(**sample_question_data)
        question = await create_question(db_session, question_in)

        for i in range(3):
            data = sample_answer_data.copy()
            data["content"] = f"답변 {i + 1}번입니다. 최소 10자 이상."
            answer_in = AnswerCreate(**data)
            await create_answer(db_session, question.id, answer_in)
        await db_session.commit()

        delete_response = await api_client.delete(f"/questions/{question.id}")
        assert delete_response.status_code == 204

        list_response = await api_client.get(f"/questions/{question.id}/answers")
        assert list_response.status_code == 404
