import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000/api/v1") as client:
        yield client


@pytest_asyncio.fixture
async def prepare_users_and_roles(client):

    # Check if there are users in the database
    response = await client.get('/users')

    # If there are no users, create a user
    if response.status_code == 200 and len(response.json()) == 0:
        response = await client.post('/users', json={
            'username': 'testuser1',
            'email': 'testuser1@example.com',
            'full_name': 'First Test User'
        })

    # Check if there are roles in the database
    response = await client.get('/roles')

    # If there are no roles, create a role
    if response.status_code == 200 and len(response.json()) == 0:
        response = await client.post('/roles', json={
            'name': 'Super User',
            'description': 'A very busy user!'
        })


@pytest.mark.asyncio
@pytest.mark.usefixtures('prepare_users_and_roles')
async def test_add_user_to_role(client):
    response = await client.get('/users/1')
    user = response.json()

    response = await client.get('/roles/1')
    role = response.json()

    role_with_user = role.copy()
    role_with_user.update({'users': [user]})

    response = await client.post(f'/roles/{role["id"]}/user/{user["id"]}')
    assert response.status_code == 201
    assert response.json() == role_with_user


@pytest.mark.asyncio
async def test_add_duplicate_user_to_role(client):

    response = await client.post(f'/roles/1/user/1')
    assert response.status_code == 400
    assert response.json() == {
        "detail": "User -> Role association already exists"
    }


@pytest.mark.asyncio
async def test_add_user_to_nonexsitant_role(client):
    response = await client.post(f'/roles/99/user/1')
    assert response.status_code == 400
    assert response.json() == {"detail": "Role not found"}


@pytest.mark.asyncio
async def test_add_nonexistant_user_to_role(client):
    response = await client.post(f'/roles/1/user/99')
    assert response.status_code == 400
    assert response.json() == {"detail": "User not found"}


@pytest.mark.asyncio
async def test_add_role_for_user(client):
    # vs adding a user to a role
    # create new role in database
    response = await client.post('/users', json={
        'username': 'testuser2',
        'email': 'testuser2@example.com',
        'full_name': 'Second Test User'
    })
    assert response.status_code == 201
    user = response.json()

    response = await client.post('/roles', json={
        'name': 'super_user',
        'desription': 'Super User'
    })
    assert response.status_code == 201
    role = response.json()

    # add role to user
    user_with_role = user.copy()
    user_with_role.update({'roles': [role]})

    response = await client.post(f'/users/{user["id"]}/role/{role["id"]}')
    assert response.status_code == 201
    assert response.json() == user_with_role


@pytest.mark.asyncio
async def test_add_nonexistant_role_for_user(client):
    response = await client.post(f'/users/1/role/99')
    assert response.status_code == 400
    assert response.json() == {"detail": "Role not found"}


@pytest.mark.asyncio
async def test_add_role_for_nonexistant_user(client):
    response = await client.post(f'/users/99/role/1')
    assert response.status_code == 400
    assert response.json() == {"detail": "User not found"}


@pytest.mark.asyncio
async def test_remove_user_from_role(client):
    response = await client.delete(f'/roles/1/user/1')
    assert response.status_code == 200
    assert response.json() == {"detail": "User removed from role"}


@pytest.mark.asyncio
async def test_remove_nonexistant_user_role(client):
    response = await client.delete(f'/roles/1/user/1')
    assert response.status_code == 400
    assert response.json() == {
        "detail": "User - Role association does not exist"}


@pytest.mark.asyncio
async def test_remove_nonexistant_user_from_role(client):
    response = await client.delete(f'/roles/1/user/88')
    assert response.status_code == 400
    assert response.json() == {"detail": "User not found"}


@pytest.mark.asyncio
async def test_remove_user_from_nonexistant_role(client):
    response = await client.delete(f'/roles/88/user/1')
    assert response.status_code == 400
    assert response.json() == {"detail": "Role not found"}


@pytest.mark.asyncio
async def test_remove_user_from_nonexistant_role(client):
    response = await client.delete(f'/users/1/role/88')
    assert response.status_code == 400
    assert response.json() == {"detail": "Role not found"}


@pytest.mark.asyncio
async def test_remove_nonexistant_user_from_role(client):
    response = await client.delete(f'/users/88/role/1')
    assert response.status_code == 400
    assert response.json() == {"detail": "User not found"}
