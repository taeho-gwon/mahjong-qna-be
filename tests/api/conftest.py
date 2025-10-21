import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.main import app


@pytest.fixture
async def api_client(db_session: AsyncSession):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def auth_headers(test_user, db_session):
    from app.core.auth import create_access_token

    token = create_access_token(data={"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}
