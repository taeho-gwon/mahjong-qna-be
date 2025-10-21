import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token
from tests.factories import create_test_answer, create_test_question, create_test_user


@pytest.mark.asyncio
class TestAnswerAPI:
    async def test_create_answer(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        test_user,
        auth_headers: dict,
    ):
        question = await create_test_question(db_session, test_user.id)
        await db_session.commit()

        answer_data = {
            "content": "이것은 테스트 답변입니다. 최소 10자 이상이어야 합니다.",
        }
        response = await api_client.post(
            f"/questions/{question.id}/answers",
            json=answer_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["question_id"] == question.id
        assert data["content"] == answer_data["content"]

    async def test_create_answer_without_auth(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        test_user,
    ):
        question = await create_test_question(db_session, test_user.id)
        await db_session.commit()

        answer_data = {
            "content": "인증 없이 답변을 작성합니다. 최소 10자 이상.",
        }
        response = await api_client.post(
            f"/questions/{question.id}/answers",
            json=answer_data,
        )

        assert response.status_code == 403

    async def test_create_answer_question_not_found(
        self,
        api_client: AsyncClient,
        auth_headers: dict,
    ):
        answer_data = {
            "content": "존재하지 않는 질문에 답변합니다. 최소 10자 이상.",
        }
        response = await api_client.post(
            "/questions/999999/answers",
            json=answer_data,
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_create_answer_validation_error(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        test_user,
        auth_headers: dict,
    ):
        question = await create_test_question(db_session, test_user.id)
        await db_session.commit()

        invalid_data = {
            "content": "짧음",
        }
        response = await api_client.post(
            f"/questions/{question.id}/answers",
            json=invalid_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_list_answers(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        test_user,
    ):
        question = await create_test_question(db_session, test_user.id)

        for i in range(3):
            await create_test_answer(
                db_session,
                question.id,
                test_user.id,
                content=f"답변 {i + 1}번입니다. 최소 10자 이상.",
            )
        await db_session.commit()

        response = await api_client.get(f"/questions/{question.id}/answers")

        assert response.status_code == 200
        assert len(response.json()) == 3

    async def test_list_answers_question_not_found(self, api_client: AsyncClient):
        response = await api_client.get("/questions/999999/answers")

        assert response.status_code == 404

    async def test_get_answer(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        test_user,
    ):
        question = await create_test_question(db_session, test_user.id)
        answer = await create_test_answer(db_session, question.id, test_user.id)
        await db_session.commit()

        response = await api_client.get(f"/questions/{question.id}/answers/{answer.id}")

        assert response.status_code == 200
        assert response.json()["id"] == answer.id

    async def test_get_answer_not_found(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        test_user,
    ):
        question = await create_test_question(db_session, test_user.id)
        await db_session.commit()

        response = await api_client.get(f"/questions/{question.id}/answers/999999")

        assert response.status_code == 404

    async def test_get_answer_wrong_question(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        test_user,
    ):
        question1 = await create_test_question(db_session, test_user.id)
        answer = await create_test_answer(db_session, question1.id, test_user.id)

        question2 = await create_test_question(db_session, test_user.id, title="두 번째 질문입니다")
        await db_session.commit()

        response = await api_client.get(f"/questions/{question2.id}/answers/{answer.id}")

        assert response.status_code == 400

    async def test_update_answer(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        test_user,
        auth_headers: dict,
    ):
        question = await create_test_question(db_session, test_user.id)
        answer = await create_test_answer(db_session, question.id, test_user.id)
        await db_session.commit()

        update_data = {"content": "수정된 답변 내용입니다. 최소 10자 이상."}
        response = await api_client.patch(
            f"/questions/{question.id}/answers/{answer.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["content"] == update_data["content"]

    async def test_update_answer_without_auth(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        test_user,
    ):
        question = await create_test_question(db_session, test_user.id)
        answer = await create_test_answer(db_session, question.id, test_user.id)
        await db_session.commit()

        update_data = {"content": "수정 시도합니다. 최소 10자 이상."}
        response = await api_client.patch(
            f"/questions/{question.id}/answers/{answer.id}",
            json=update_data,
        )

        assert response.status_code == 403

    async def test_update_answer_not_owner(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        test_user,
    ):
        question = await create_test_question(db_session, test_user.id)
        answer = await create_test_answer(db_session, question.id, test_user.id)
        await db_session.commit()

        user2 = await create_test_user(db_session, username="user2")
        await db_session.commit()

        token = create_access_token(data={"sub": user2.id})
        headers = {"Authorization": f"Bearer {token}"}

        update_data = {"content": "수정 시도합니다. 최소 10자 이상."}
        response = await api_client.patch(
            f"/questions/{question.id}/answers/{answer.id}",
            json=update_data,
            headers=headers,
        )

        assert response.status_code == 403

    async def test_update_answer_not_found(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        test_user,
        auth_headers: dict,
    ):
        question = await create_test_question(db_session, test_user.id)
        await db_session.commit()

        update_data = {"content": "수정 시도합니다. 최소 10자 이상."}
        response = await api_client.patch(
            f"/questions/{question.id}/answers/999999",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_update_answer_wrong_question(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        test_user,
        auth_headers: dict,
    ):
        question1 = await create_test_question(db_session, test_user.id)
        answer = await create_test_answer(db_session, question1.id, test_user.id)

        question2 = await create_test_question(db_session, test_user.id, title="두 번째 질문입니다")
        await db_session.commit()

        update_data = {"content": "수정 시도합니다. 최소 10자 이상."}
        response = await api_client.patch(
            f"/questions/{question2.id}/answers/{answer.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 400

    async def test_delete_answer(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        test_user,
        auth_headers: dict,
    ):
        question = await create_test_question(db_session, test_user.id)
        answer = await create_test_answer(db_session, question.id, test_user.id)
        await db_session.commit()

        response = await api_client.delete(
            f"/questions/{question.id}/answers/{answer.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

    async def test_delete_answer_without_auth(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        test_user,
    ):
        question = await create_test_question(db_session, test_user.id)
        answer = await create_test_answer(db_session, question.id, test_user.id)
        await db_session.commit()

        response = await api_client.delete(f"/questions/{question.id}/answers/{answer.id}")

        assert response.status_code == 403

    async def test_delete_answer_not_found(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        test_user,
        auth_headers: dict,
    ):
        question = await create_test_question(db_session, test_user.id)
        await db_session.commit()

        response = await api_client.delete(
            f"/questions/{question.id}/answers/999999",
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_cascade_delete(
        self,
        api_client: AsyncClient,
        db_session: AsyncSession,
        test_user,
        auth_headers: dict,
    ):
        question = await create_test_question(db_session, test_user.id)

        for i in range(3):
            await create_test_answer(
                db_session,
                question.id,
                test_user.id,
                content=f"답변 {i + 1}번입니다. 최소 10자 이상.",
            )
        await db_session.commit()

        delete_response = await api_client.delete(
            f"/questions/{question.id}",
            headers=auth_headers,
        )
        assert delete_response.status_code == 204

        list_response = await api_client.get(f"/questions/{question.id}/answers")
        assert list_response.status_code == 404
