import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app import init_app
from app.services.database import sessionmanager


@pytest_asyncio.fixture(scope="session")
async def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    yield loop
    # loop.close()


@pytest.fixture(scope="session", autouse=True)
def test_app(event_loop):
    app = init_app("test_config.json")
    return app


@pytest_asyncio.fixture(scope="session")
async def setup_db(test_app):

    async with sessionmanager.connect() as connection:
        # print("Dropping tables")
        await sessionmanager.drop_all(connection)
        # print("Create tables")
        await sessionmanager.create_all(connection)
    yield
    await sessionmanager.close()


@pytest_asyncio.fixture(scope="function")
async def db(setup_db, test_app):
    async with sessionmanager.session() as session:
        # Created and yield session
        yield session
        # Close session
        await session.close()


@pytest.fixture(scope="function")
def app(test_app, setup_db, db):
    yield test_app


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000/api/v1") as client:
        yield client
