import pytest
import pytest_asyncio
from httpx import AsyncClient
from tests.utils import remove_uuid


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000/api/v1") as client:
        yield client


@pytest.mark.asyncio
async def test_get_roles(client):  # Expect empty list as db has just been created
    response = await client.get('/roles')
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
# Expect empty list as db has just been created
async def test_create_role(client):
    response = await client.post('/roles', json={
        'name': 'admin',
        'description': 'Admin role'
    })
    assert response.status_code == 201
    response_json = remove_uuid(response.json())
    assert response_json == {'id': 1, 'name': 'admin',
                             'description': 'Admin role'}

    response = await client.post('/roles', json={
        'name': 'project_manager',
        'description': 'Project Manager role'
    })
    assert response.status_code == 201
    response_json = remove_uuid(response.json())
    assert response_json == {'id': 2, 'name': 'project_manager',
                             'description': 'Project Manager role'}


@pytest.mark.asyncio
async def test_update_role_name(client):
    response = await client.put('/roles/1', json={
        'name': 'administrator',
    })
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        'id': 1, 'name': 'administrator', 'description': 'Admin role'}


@pytest.mark.asyncio
async def test_update_role_description(client):
    response = await client.put('/roles/1', json={
        'description': 'An important role',
    })
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        'id': 1, 'name': 'administrator', 'description': 'An important role'}


@pytest.mark.asyncio
async def test_update_role_all(client):
    response = await client.put('/roles/1', json={
        'name': 'admin', 'description': 'Admin role'
    })
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        'id': 1, 'name': 'admin', 'description': 'Admin role'}


@pytest.mark.asyncio
async def test_update_role_with_duplicate_name(client):
    response = await client.put('/roles/1', json={
        'name': 'project_manager', 'description': 'Admin role'
    })
    assert response.status_code == 400
    assert response.json() == {'detail': 'Role with that name already exists'}


@pytest.mark.asyncio
async def test_delete_role(client):
    response = await client.delete('/roles/2')
    assert response.status_code == 200
    assert response.json() == {'detail': 'Role deleted'}


@pytest.mark.asyncio
async def test_delete_non_existant_role(client):
    response = await client.delete('/roles/2')
    assert response.status_code == 400
    assert response.json() == {'detail': 'Role not found'}


@pytest.mark.asyncio
async def test_get_non_empty_roles(client):  # Expect list with single item
    response = await client.get('/roles')
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_create_duplicate_role(client):
    response = await client.post('/roles', json={
        'name': 'admin',
        'description': 'Admin role'
    })
    assert response.status_code == 400
    assert response.json() == {'detail': 'Role with that name already exists'}


@pytest.mark.asyncio
async def test_get_role_by_id(client):
    # Test gettting an existing role by id
    response = await client.get('/roles/1')
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {'id': 1, 'name': 'admin',
                             'description': 'Admin role'}

    # Test gettting a non-existing role by id
    response = await client.get('/roles/99')
    assert response.status_code == 400
    assert response.json() == {'detail': 'Role not found'}


@pytest.mark.asyncio
async def test_get_role_by_uuid(client):
    # Get role to get uuid
    response = await client.get('/roles/1')
    test_role = response.json()
    test_uuid = test_role['uuid']

    # Test gettting an existing role by uuid
    response = await client.get('/roles/uuid/' + test_uuid)
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {'id': 1, 'name': 'admin',
                             'description': 'Admin role'}

    # Test gettting a non-existing role by uuid
    response = await client.get('/roles/uuid/1231230123=102311-132')
    assert response.status_code == 400
    assert response.json() == {'detail': 'Role not found'}
