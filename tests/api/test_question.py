import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token
from tests.factories import create_test_question, create_test_user


@pytest.mark.asyncio
class TestQuestionAPI:
    async def test_create_question(
        self,
        api_client: AsyncClient,
        auth_headers: dict,
    ):
        question_data = {
            "title": "API 테스트 질문입니다",
            "content": "이것은 API 테스트용 질문 내용입니다. 최소 10자 이상.",
        }
        response = await api_client.post("/questions", json=question_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["title"] == question_data["title"]

    async def test_create_question_without_auth(self, api_client: AsyncClient):
        question_data = {
            "title": "인증 없는 질문",
            "content": "인증 헤더 없이 요청합니다. 최소 10자 이상.",
        }
        response = await api_client.post("/questions", json=question_data)

        assert response.status_code == 403

    async def test_create_question_validation_error(
        self, api_client: AsyncClient, auth_headers: dict
    ):
        invalid_data = {
            "title": "짧음",
            "content": "내용입니다. 최소 10자 이상.",
        }
        response = await api_client.post("/questions", json=invalid_data, headers=auth_headers)

        assert response.status_code == 422

    async def test_get_question(self, api_client: AsyncClient, db_session: AsyncSession, test_user):
        question = await create_test_question(db_session, test_user.id)
        await db_session.commit()

        response = await api_client.get(f"/questions/{question.id}")

        assert response.status_code == 200
        assert response.json()["id"] == question.id

    async def test_get_question_not_found(self, api_client: AsyncClient):
        response = await api_client.get("/questions/999999")

        assert response.status_code == 404

    async def test_list_questions(
        self, api_client: AsyncClient, db_session: AsyncSession, test_user
    ):
        for i in range(15):
            await create_test_question(db_session, test_user.id, title=f"테스트 질문 {i + 1}번")
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
        test_user,
        auth_headers: dict,
    ):
        question = await create_test_question(db_session, test_user.id)
        await db_session.commit()

        update_data = {"title": "수정된 질문 제목입니다"}
        response = await api_client.patch(
            f"/questions/{question.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["title"] == update_data["title"]

    async def test_update_question_without_auth(
        self, api_client: AsyncClient, db_session: AsyncSession, test_user
    ):
        question = await create_test_question(db_session, test_user.id)
        await db_session.commit()

        update_data = {"title": "수정 시도"}
        response = await api_client.patch(f"/questions/{question.id}", json=update_data)

        assert response.status_code == 403

    async def test_update_question_not_owner(
        self, api_client: AsyncClient, db_session: AsyncSession, test_user
    ):
        question = await create_test_question(db_session, test_user.id)
        await db_session.commit()

        user2 = await create_test_user(db_session, username="user2")
        await db_session.commit()

        token = create_access_token(data={"sub": user2.id})
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {"title": "수정 시도"}
        response = await api_client.patch(
            f"/questions/{question.id}", json=update_data, headers=headers
        )

        assert response.status_code == 403

    async def test_update_question_not_found(self, api_client: AsyncClient, auth_headers: dict):
        response = await api_client.patch(
            "/questions/999999", json={"title": "수정 시도"}, headers=auth_headers
        )

        assert response.status_code == 404

    async def test_delete_question(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        test_user,
        auth_headers: dict,
    ):
        question = await create_test_question(db_session, test_user.id)
        await db_session.commit()

        response = await api_client.delete(f"/questions/{question.id}", headers=auth_headers)

        assert response.status_code == 204

    async def test_delete_question_without_auth(
        self, api_client: AsyncClient, db_session: AsyncSession, test_user
    ):
        question = await create_test_question(db_session, test_user.id)
        await db_session.commit()

        response = await api_client.delete(f"/questions/{question.id}")

        assert response.status_code == 403

    async def test_delete_question_not_found(self, api_client: AsyncClient, auth_headers: dict):
        response = await api_client.delete("/questions/999999", headers=auth_headers)

        assert response.status_code == 404
