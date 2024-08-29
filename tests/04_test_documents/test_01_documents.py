import pytest
import pytest_asyncio
from httpx import AsyncClient

from tests.utils import print_response, remove_uuid


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000/api/v1") as client:
        yield client


@pytest.mark.asyncio
async def test_get_unknown_documents(client):
    response = await client.get("/documents?project_id=8&component_id=74")
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}
