import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.main import app


@pytest.fixture
async def api_client(db_session: AsyncSession):
    """
    API 테스트용 HTTP 클라이언트

    FastAPI의 get_session 의존성을 테스트 세션으로 오버라이드하여
    API 요청과 직접 CRUD 호출이 같은 트랜잭션을 공유하도록 함
    """

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
