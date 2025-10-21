from datetime import timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, decode_access_token
from tests.factories import create_test_user


@pytest.mark.asyncio
class TestAuthAPI:
    async def test_signup_success(self, api_client: AsyncClient):
        signup_data = {
            "username": "newuser",
            "password": "password1234",
        }
        response = await api_client.post("/auth/signup", json=signup_data)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["username"] == "newuser"
        assert "password" not in data
        assert "hashed_password" not in data

    async def test_signup_duplicate_username(
        self, api_client: AsyncClient, db_session: AsyncSession
    ):
        await create_test_user(db_session, username="existinguser")
        await db_session.commit()

        signup_data = {
            "username": "existinguser",
            "password": "password1234",
        }
        response = await api_client.post("/auth/signup", json=signup_data)

        assert response.status_code == 400
        assert "이미 존재하는" in response.json()["detail"]

    async def test_signup_validation_error_short_username(self, api_client: AsyncClient):
        signup_data = {
            "username": "ab",
            "password": "password1234",
        }
        response = await api_client.post("/auth/signup", json=signup_data)

        assert response.status_code == 422

    async def test_signup_validation_error_short_password(self, api_client: AsyncClient):
        signup_data = {
            "username": "validuser",
            "password": "123",
        }
        response = await api_client.post("/auth/signup", json=signup_data)

        assert response.status_code == 422

    async def test_login_success(self, api_client: AsyncClient, db_session: AsyncSession):
        await create_test_user(db_session, username="loginuser", password="mypassword")
        await db_session.commit()

        login_data = {
            "username": "loginuser",
            "password": "mypassword",
        }
        response = await api_client.post("/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    async def test_login_wrong_password(self, api_client: AsyncClient, db_session: AsyncSession):
        await create_test_user(db_session, username="user1", password="correctpass")
        await db_session.commit()

        login_data = {
            "username": "user1",
            "password": "wrongpass",
        }
        response = await api_client.post("/auth/login", json=login_data)

        assert response.status_code == 401
        assert "잘못되었습니다" in response.json()["detail"]

    async def test_login_nonexistent_user(self, api_client: AsyncClient):
        login_data = {
            "username": "nonexistent",
            "password": "somepassword",
        }
        response = await api_client.post("/auth/login", json=login_data)

        assert response.status_code == 401
        assert "잘못되었습니다" in response.json()["detail"]

    async def test_get_me_success(self, api_client: AsyncClient, db_session: AsyncSession):
        user = await create_test_user(db_session, username="meuser")
        await db_session.commit()

        token = create_access_token(data={"sub": user.id})
        headers = {"Authorization": f"Bearer {token}"}

        response = await api_client.get("/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["username"] == "meuser"

    async def test_get_me_without_token(self, api_client: AsyncClient):
        response = await api_client.get("/auth/me")

        assert response.status_code == 403

    async def test_get_me_invalid_token(self, api_client: AsyncClient):
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = await api_client.get("/auth/me", headers=headers)

        assert response.status_code == 401

    async def test_get_me_expired_token(self, api_client: AsyncClient, db_session: AsyncSession):
        user = await create_test_user(db_session)
        await db_session.commit()

        expired_token = create_access_token(
            data={"sub": user.id}, expires_delta=timedelta(minutes=-1)
        )
        headers = {"Authorization": f"Bearer {expired_token}"}

        response = await api_client.get("/auth/me", headers=headers)

        assert response.status_code == 401

    async def test_login_and_use_token(self, api_client: AsyncClient, _db_session: AsyncSession):
        signup_data = {"username": "fullflowuser", "password": "mypassword123"}
        signup_response = await api_client.post("/auth/signup", json=signup_data)
        assert signup_response.status_code == 201

        login_data = {"username": "fullflowuser", "password": "mypassword123"}
        login_response = await api_client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        me_response = await api_client.get("/auth/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["username"] == "fullflowuser"

        question_data = {
            "title": "토큰 테스트 질문입니다",
            "content": "토큰을 사용한 질문 생성 테스트입니다. 최소 10자 이상.",
        }
        question_response = await api_client.post("/questions", json=question_data, headers=headers)
        assert question_response.status_code == 201
        assert question_response.json()["author"]["username"] == "fullflowuser"

    async def test_token_contains_correct_user_id(
        self, api_client: AsyncClient, db_session: AsyncSession
    ):
        user = await create_test_user(db_session, username="tokentest")
        await db_session.commit()

        login_data = {"username": "tokentest", "password": "testpass1234"}
        response = await api_client.post("/auth/login", json=login_data)

        token = response.json()["access_token"]

        payload = decode_access_token(token)

        assert payload is not None
        assert payload["sub"] == user.id
