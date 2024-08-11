import pytest
import pytest_asyncio
from httpx import AsyncClient
from tests.utils import remove_uuid, print_response


@pytest.mark.asyncio
async def test_get_element_types(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.get('/api/element_types/')
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_element_types(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.post('/api/element_types/', json={
            "title": "Element Type 1",
            "description": "Element Type 1 Description",
            "default_text": "This is default text for element type 1"
        })
    assert response.status_code == 201
    response_json = remove_uuid(response.json())
    assert response_json == {
        "id": 1,
        "title": "Element Type 1",
        "description": "Element Type 1 Description",
        "default_text": "This is default text for element type 1"
    }


@pytest.mark.asyncio
async def test_create_element_type_only_with_title(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.post('/api/element_types/', json={
            "title": "Element Type 2",
        })
    assert response.status_code == 201
    response_json = remove_uuid(response.json())
    assert response_json == {
        "id": 2,
        "title": "Element Type 2",
        "description": None,
        "default_text": None
    }


@pytest.mark.asyncio
async def test_create_element_type_with_duplicate_title(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.post('/api/element_types/', json={
            "title": "Element Type 1",
        })
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'Element type with this title already exists'}


@pytest.mark.asyncio
async def test_create_element_type_with_empty_json(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.post('/api/element_types/', json={})
    assert response.status_code == 422
    assert response.json() == {'detail': [{'type': 'missing', 'loc': [
        'body', 'title'], 'msg': 'Field required', 'input': {}}]}


@pytest.mark.asyncio
async def test_create_element_type_with_empty_title(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.post('/api/element_types/', json={
            "title": ""
        })
    assert response.status_code == 422
    assert response.json() == {'detail': 'Title field cannot be empty'}


@pytest.mark.asyncio
async def test_get_element_types_list_length(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.get('/api/element_types/')
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_get_element_type_by_id(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.get('/api/element_types/1')
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        "id": 1,
        "title": "Element Type 1",
        "description": "Element Type 1 Description",
        "default_text": "This is default text for element type 1"
    }


@pytest.mark.asyncio
async def test_update_element_type(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.put('/api/element_types/1', json={
            "title": "Element Type 1 Updated",
            "description": "Element Type 1 Description Updated",
            "default_text": "This is default text for element type 1 updated"
        })
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        "id": 1,
        "title": "Element Type 1 Updated",
        "description": "Element Type 1 Description Updated",
        "default_text": "This is default text for element type 1 updated"
    }


@pytest.mark.asyncio
async def test_update_element_type_with_duplicate_title(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.put('/api/element_types/1', json={
            "title": "Element Type 2",
        })
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'Element type with this title already exists'}


@pytest.mark.asyncio
async def test_update_element_type_with_empty_title(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.put('/api/element_types/1', json={
            "title": "",
        })
    assert response.status_code == 422
    assert response.json() == {'detail':
                               [{'type': 'value_error', 'loc': [
                                   'body'], 'msg': 'Value error, At least one of title, description or default_text must be provided',
                                 'input': {'title': ''}, 'ctx': {'error': {}}}]}


@pytest.mark.asyncio
async def test_update_element_type_description(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.put('/api/element_types/2', json={
            "description": "Element Type 2 now have a description",
        })
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        "id": 2,
        "title": "Element Type 2",
        "description": "Element Type 2 now have a description",
        "default_text": None
    }


@pytest.mark.asyncio
async def test_update_element_type_default_text(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.put('/api/element_types/2', json={
            "default_text": "Element Type 2 now have default text",
        })
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        "id": 2,
        "title": "Element Type 2",
        "description": "Element Type 2 now have a description",
        "default_text": "Element Type 2 now have default text"
    }


@pytest.mark.asyncio
async def test_delete_element_type(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.delete('/api/element_types/2')
    assert response.status_code == 200
    assert response.json() == {'detail': 'Element type deleted'}
