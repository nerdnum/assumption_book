import pytest
import pytest_asyncio
from httpx import AsyncClient
from tests.utils import remove_uuid
import jwt
from app.config import get_config


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000/api/v1") as client:
        yield client


@pytest.mark.asyncio
async def test_get_users(client):  # Expect empty list as db has just been created
    response = await client.get('/users')
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_users(client):
    response = await client.post('/users', json={
        'username': 'testuser1',
        'email': 'testuser1@example.com',
        'fullName': 'First Test User'
    })
    assert response.status_code == 201
    response_json = remove_uuid(response.json())
    assert response_json == {
        'id': 1,
        'username': 'testuser1',
        'email': 'testuser1@example.com',
        'fullName': 'First Test User'
    }

    response = await client.post('/users', json={
        'username': 'testuser2',
        'email': 'testuser2@example.com',
        'fullName': 'Second Test User'
    })
    assert response.status_code == 201
    response_json = remove_uuid(response.json())
    assert response_json == {
        'id': 2,
        'username': 'testuser2',
        'email': 'testuser2@example.com',
        'fullName': 'Second Test User'
    }

    response = await client.post('/users', json={
        'username': 'testuser3',
        'email': 'testuser3@example.com',
        'fullName': 'Third Test User'
    })
    assert response.status_code == 201
    response_json = remove_uuid(response.json())
    assert response_json == {
        'id': 3,
        'username': 'testuser3',
        'email': 'testuser3@example.com',
        'fullName': 'Third Test User'
    }


@pytest.mark.asyncio
async def test_create_user_with_empty_email_field(client):
    response = await client.post('/users', json={
        'username': 'testuser1',
        'email': '',
        'fullName': 'First Test User'
    })
    assert response.status_code == 422
    assert response.json()['detail'][0]["loc"] == ['body', 'email',]


@pytest.mark.asyncio
async def test_delete_user(client):
    response = await client.delete('/users/2')
    assert response.status_code == 200
    assert response.json() == {"detail": "User deleted"}


@pytest.mark.asyncio
async def test_delete_nonexistant_user(client):
    response = await client.delete('/users/2')
    assert response.status_code == 400
    assert response.json() == {'detail': 'User not found'}


@pytest.mark.asyncio
# Expect one user after creating one user
async def test_get_users_for_none_empty_list(client):
    response = await client.get('/users')
    assert response.status_code == 200
    assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_create_user_duplicate(client):
    response = await client.post('/users', json={
        'username': 'testuser3',
        'email': 'testuser3@example.com',
        'fullName': 'Third Test User'
    })
    assert response.status_code == 400
    assert response.json() == {'detail': 'User with that email already exists'}


@pytest.mark.asyncio
async def test_update_user_username(client):
    response = await client.put('/users/3', json={
        'username': 'testuser3_update'})
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        'id': 3,
        'username': 'testuser3_update',
        'email': 'testuser3@example.com',
        'fullName': 'Third Test User'
    }


@pytest.mark.asyncio
async def test_update_user_fullName(client):
    response = await client.put('/users/3', json={
        'fullName': 'Third Test User Updated'})
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        'id': 3,
        'username': 'testuser3_update',
        'email': 'testuser3@example.com',
        'fullName': 'Third Test User Updated'
    }


@pytest.mark.asyncio
async def test_update_user_email(client):
    response = await client.put('/users/3', json={
        'email': 'testuser3.update@example.com'})
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        'id': 3,
        'username': 'testuser3_update',
        'email': 'testuser3.update@example.com',
        'fullName': 'Third Test User Updated'
    }


@pytest.mark.asyncio
async def test_update_user_with_duplicate_email(client):
    response = await client.put('/users/3', json={
        'email': 'testuser1@example.com'})
    assert response.status_code == 400
    assert response.json() == {"detail": "User with that email already exists"}


@pytest.mark.asyncio
async def test_update_user_everything(client):
    response = await client.put('/users/3', json={
        'username': 'testuser_three',
        'email': 'testuser.three@example.com',
        'fullName': 'Third User All Updated'
    })
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        'id': 3,
        'username': 'testuser_three',
        'email': 'testuser.three@example.com',
        'fullName': 'Third User All Updated'
    }


@pytest.mark.asyncio
async def test_get_user_by_id(client):
    # Test gettting an existing user by id
    response = await client.get('/users/1')
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        'id': 1,
        'username': 'testuser1',
        'email': 'testuser1@example.com',
        'fullName': 'First Test User',
    }
    # Test for non-existing user
    response = await client.get('/users/99')
    assert response.status_code == 400
    assert response.json() == {'detail': 'User not found'}


@pytest.mark.asyncio
async def test_get_user_by_username(client):
    # Test gettting an existing user by username
    response = await client.get('/users/username/testuser1')
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        'id': 1,
        'username': 'testuser1',
        'email': 'testuser1@example.com',
        'fullName': 'First Test User',
    }
    # Test for non-existing user
    response = await client.get('/users/username/nonexistinguser')
    assert response.status_code == 400
    assert response.json() == {'detail': 'User not found'}


@pytest.mark.asyncio
async def test_get_user_by_uuid(client):
    # Get the uuid of the first user
    response = await client.get('/users/username/testuser1')
    user_json = response.json()
    uuid = response.json()["uuid"]

    # Test gettting an existing user by uuid
    response = await client.get('/users/uuid/' + uuid)
    assert response.status_code == 200
    assert response.json() == user_json

    # Test for non-existing user
    response = await client.get('/users/uuid/nonexistinguuid')
    assert response.status_code == 400
    assert response.json() == {'detail': 'User not found'}


@pytest.mark.asyncio
async def test_get_role_for_user_with_no_roles(client):
    response = await client.get('/users/1/roles')
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        'id': 1,
        'username': 'testuser1',
        'email': 'testuser1@example.com',
        'fullName': 'First Test User',
        'roles': []
    }


@pytest.mark.asyncio
async def test_create_password_for_user(client):
    response = await client.post('/auth/users/1/set_auth', json={
        "password": "test!wer1"
    })
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json["id"] == 1
    assert response_json["username"] == 'testuser1'
    assert response_json["email"] == 'testuser1@example.com'


@pytest.mark.asyncio
async def test_user_login_for_inactive_user(client):
    response = await client.post('/auth/token', data={
        "username": "testuser1",
        "password": "test!wer1"
    })
    assert response.status_code == 401
    assert response.json() == {'detail': 'Inactive user'}


@pytest.mark.asyncio
async def test_activiting_user(client):
    response = await client.put('/users/activate/1')
    assert response.status_code == 200
    assert response.json() == {'detail': 'User activated'}


@pytest.mark.asyncio
async def test_getting_info_for_unauthenticated_user_from_protect_route(client):
    response = await client.get('/auth/me')
    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}


@pytest.mark.asyncio
async def test_user_login_and_getting_user_info_from_protected_route(client):
    response = await client.post('/auth/token', data={
        "username": "testuser1",
        "password": "test!wer1"
    })

    config = get_config()
    token = response.json()['access_token']
    decoded = jwt.decode(token, config['secret_key'], algorithms=['HS256'])

    assert response.status_code == 200
    assert decoded['sub'] == 'testuser1'

    # Test assessing a protects endpoint
    return_token = 'Bearer ' + token
    headers = {'Authorization': return_token}
    response = await client.get('/auth/me', headers=headers)
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        'id': 1,
        'username': 'testuser1',
        'email': 'testuser1@example.com',
        'fullName': 'First Test User',
    }


@pytest.mark.asyncio
async def test_deactiviting_user(client):
    response = await client.put('/users/deactivate/1')
    assert response.status_code == 200
    assert response.json() == {'detail': 'User deactivated'}


@pytest.mark.asyncio
async def test_user_login_for_inactive_user_again(client):
    response = await client.post('/auth/token', data={
        "username": "testuser1",
        "password": "test!wer1"
    })
    assert response.status_code == 401
    assert response.json() == {'detail': 'Inactive user'}
