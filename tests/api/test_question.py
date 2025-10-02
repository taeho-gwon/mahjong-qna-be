import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.question import create_question
from app.schemas.question import QuestionCreate


@pytest.mark.asyncio
class TestQuestionAPI:
    async def test_create_question(
        self,
        api_client: AsyncClient,
        sample_question_data: dict,
    ):
        response = await api_client.post("/questions", json=sample_question_data)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["title"] == sample_question_data["title"]

    async def test_create_question_validation_error(self, api_client: AsyncClient):
        invalid_data = {
            "title": "짧음",
            "content": "내용입니다. 최소 10자 이상.",
            "author_nickname": "테스터",
        }
        response = await api_client.post("/questions", json=invalid_data)

        assert response.status_code == 422

    async def test_get_question(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        question_in = QuestionCreate(**sample_question_data)
        question = await create_question(db_session, question_in)
        await db_session.commit()

        response = await api_client.get(f"/questions/{question.id}")

        assert response.status_code == 200
        assert response.json()["id"] == question.id

    async def test_get_question_not_found(self, api_client: AsyncClient):
        response = await api_client.get("/questions/999999")

        assert response.status_code == 404

    async def test_list_questions(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        for i in range(15):
            data = sample_question_data.copy()
            data["title"] = f"테스트 질문 {i + 1}번"
            question_in = QuestionCreate(**data)
            await create_question(db_session, question_in)
        await db_session.commit()

        response = await api_client.get("/questions?page=1&size=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["pagination"]["total"] == 15
        assert data["pagination"]["total_pages"] == 3

    async def test_update_question(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        question_in = QuestionCreate(**sample_question_data)
        question = await create_question(db_session, question_in)
        await db_session.commit()

        update_data = {"title": "수정된 질문 제목입니다"}
        response = await api_client.patch(f"/questions/{question.id}", json=update_data)

        assert response.status_code == 200
        assert response.json()["title"] == update_data["title"]

    async def test_update_question_not_found(self, api_client: AsyncClient):
        response = await api_client.patch("/questions/999999", json={"title": "수정 시도"})

        assert response.status_code == 404

    async def test_delete_question(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        question_in = QuestionCreate(**sample_question_data)
        question = await create_question(db_session, question_in)
        await db_session.commit()

        response = await api_client.delete(f"/questions/{question.id}")

        assert response.status_code == 204

    async def test_delete_question_not_found(self, api_client: AsyncClient):
        response = await api_client.delete("/questions/999999")

        assert response.status_code == 404
