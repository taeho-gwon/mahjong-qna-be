import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_password
from app.crud.user import create_user, get_user_by_id, get_user_by_username
from app.schemas.user import UserSignup


@pytest.mark.asyncio
class TestUserCRUD:
    async def test_create_user(self, db_session: AsyncSession):
        user_in = UserSignup(username="newuser", password="password1234")
        user = await create_user(db_session, user_in)

        assert user.id is not None
        assert user.username == "newuser"
        assert user.hashed_password is not None
        assert user.hashed_password != "password1234"
        assert verify_password("password1234", user.hashed_password)

    async def test_create_user_password_hashing(self, db_session: AsyncSession):
        user_in = UserSignup(username="testuser", password="mypassword")
        user = await create_user(db_session, user_in)

        assert user.hashed_password != "mypassword"
        assert verify_password("mypassword", user.hashed_password)
        assert not verify_password("wrongpassword", user.hashed_password)

    async def test_get_user_by_username_success(self, db_session: AsyncSession):
        user_in = UserSignup(username="findme", password="password1234")
        created_user = await create_user(db_session, user_in)
        await db_session.flush()

        found_user = await get_user_by_username(db_session, "findme")

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.username == "findme"

    async def test_get_user_by_username_not_found(self, db_session: AsyncSession):
        user = await get_user_by_username(db_session, "nonexistent")

        assert user is None

    async def test_get_user_by_id_success(self, db_session: AsyncSession):
        user_in = UserSignup(username="idtest", password="password1234")
        created_user = await create_user(db_session, user_in)
        await db_session.flush()

        found_user = await get_user_by_id(db_session, created_user.id)

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.username == "idtest"

    async def test_get_user_by_id_not_found(self, db_session: AsyncSession):
        user = await get_user_by_id(db_session, 999999)

        assert user is None

    async def test_username_case_sensitive(self, db_session: AsyncSession):
        user_in = UserSignup(username="TestUser", password="password1234")
        await create_user(db_session, user_in)
        await db_session.flush()

        found_upper = await get_user_by_username(db_session, "TestUser")
        assert found_upper is not None

        found_lower = await get_user_by_username(db_session, "testuser")
        assert found_lower is None

    async def test_create_multiple_users(self, db_session: AsyncSession):
        users = []
        for i in range(3):
            user_in = UserSignup(username=f"user{i}", password="password1234")
            user = await create_user(db_session, user_in)
            users.append(user)
            await db_session.flush()

        user_ids = [u.id for u in users]
        assert len(user_ids) == len(set(user_ids))

        for i, user in enumerate(users):
            found_user = await get_user_by_username(db_session, f"user{i}")
            assert found_user is not None
            assert found_user.id == user.id
