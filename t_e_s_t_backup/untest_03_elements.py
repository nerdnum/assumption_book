import pytest
import pytest_asyncio
from httpx import AsyncClient
from tests.utils import remove_uuid, print_response


@pytest_asyncio.fixture
async def prepared_projects(app):
    # check if project with id 1 exists
    projects = []

    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.get('/api/projects/')

        if len(response.json()) >= 2:
            projects.append(response.json()[0])
            projects.append(response.json()[1])
        elif len(response.json()) == 1:
            projects.append(response.json()[0])
            response = await client.post('/api/projects/', json={
                "title": "Project 2",
                "description": "Project 2 Description"
            })
            projects.append(response.json())
        else:
            response = await client.post('/api/projects/', json={
                "title": "Project 1",
                "description": "Project 1 Description"
            })
            projects.append(response.json())
        if response.status_code == 404:
            response = await client.post('/api/projects/', json={
                "title": "Project 2",
                "description": "Project 2 Description"
            })

    yield projects


@pytest_asyncio.fixture
async def prepared_element_types(app):

    element_types = []

    # check if element type with id 1 exists
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.get('/api/element_types/')
        if len(response.json()) >= 2:
            element_types.append(response.json()[0])
            element_types.append(response.json()[1])
        elif len(response.json()) == 1:
            element_types.append(response.json()[0])
            response = await client.post('/api/element_types/', json={
                "title": "Element Type 2",
                "description": "Element Type 2 Description"
            })
            element_types.append(response.json())
        else:
            response = await client.post('/api/element_types/', json={
                "title": "Element Type 1",
                "description": "Element Type 1 Description"
            })
            element_types.append(response.json())
            response = await client.post('/api/element_types/', json={
                "title": "Element Type 2",
                "description": "Element Type 2 Description"
            })
            element_types.append(response.json())

    yield element_types


@pytest.mark.asyncio
async def test_get_elements(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.get('/api/elements/')
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_elements(app, prepared_projects, prepared_element_types):

    type_0_id = prepared_element_types[0]["id"]
    type_1_id = prepared_element_types[1]["id"]

    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.post('/api/elements/', json={
            "title": "Element 1",
            "description": "Element 1 Description",
            "project_id": 1,
            "element_type_id": type_0_id
        })
    assert response.status_code == 201
    response_json = remove_uuid(response.json())
    assert response_json == {
        "id": 1,
        "title": "Element 1",
        "description": "Element 1 Description",
        "project_id": 1,
        "element_type_id": type_0_id
    }

    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.post('/api/elements/', json={
            "title": "Element 2",
            "description": "Element 2 Description",
            "project_id": 1,
            "element_type_id": type_1_id
        })
    assert response.status_code == 201
    response_json = remove_uuid(response.json())
    assert response_json == {
        "id": 2,
        "title": "Element 2",
        "description": "Element 2 Description",
        "project_id": 1,
        "element_type_id": type_1_id
    }


@pytest.mark.asyncio
async def test_create_element_only_with_title(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.post('/api/elements/', json={
            "title": "Element 2",
        })
    assert response.status_code == 422
    assert response.json() == {'detail':
                               [{'input': {'title': 'Element 2'}, 'loc': ['body', 'project_id'], 'msg': 'Field required', 'type': 'missing'},
                                {'input': {'title': 'Element 2'}, 'loc': ['body', 'element_type_id'], 'msg': 'Field required', 'type': 'missing'}]}


@pytest.mark.asyncio
async def test_create_element_with_duplicate_title(app, prepared_projects):
    ###
    # The project title does not have to be unique in the table,
    # but it needs to be unique in the project.
    # There for title together with project_id must be unique.
    ###
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.get('/api/elements/1')
        existing_element = response.json()

    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.post('/api/elements/', json={
            "title": existing_element["title"],  # the same title
            "description": "Element 1 with differenct description",
            "project_id": existing_element["project_id"],  # same id
            "element_type_id": 1
        })
    assert response.status_code == 400
    testing_text = f"Element 'Element 1' already exists in project '{
        prepared_projects[0]['title']}'"
    assert response.json() == {
        'detail': testing_text}


@pytest.mark.asyncio
async def test_create_element_with_empty_title(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.post('/api/elements/', json={
            "title": "",
            "description": "Element 1 with differenct description",
            "project_id": 1,
            "element_type_id": 1
        })
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'Title field cannot be empty'}


@pytest.mark.asyncio
async def test_get_elements_list_length(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.get('/api/elements/')
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_get_element_by_id(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.get('/api/elements/1')
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        "id": 1,
        "title": "Element 1",
        "description": "Element 1 Description",
        "project_id": 1,
        "element_type_id": 1
    }


@pytest.mark.asyncio
async def test_update_complete_element(app, prepared_projects, prepared_element_types):

    project_id = prepared_projects[1]["id"]
    type_1_id = prepared_element_types[1]["id"]

    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.put('/api/elements/1', json={
            "title": "Element 1 Updated",
            "description": "Element 1 Description Updated",
            "project_id": project_id,
            "element_type_id": type_1_id
        })
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        "id": 1,
        "title": "Element 1 Updated",
        "description": "Element 1 Description Updated",
        "project_id": project_id,
        "element_type_id": type_1_id
    }


@pytest.mark.asyncio
async def test_update_element_with_duplicate_title(app):
    ###
    # Having that same title on two different projects is allowed.
    ###

    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.get('/api/elements/1')
    element_1 = response.json()

    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.get('/api/elements/2')
    element_2 = response.json()

    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.put('/api/elements/1', json={
            "title": element_2["title"],
        })
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        "id": element_1["id"],
        "title": element_2["title"],
        "description": element_1["description"],
        "project_id": element_1["project_id"],
        "element_type_id": element_1["element_type_id"]
    }


@pytest.mark.asyncio
async def test_update_element_with_empty_title(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.put('/api/elements/1', json={
            "title": "",
        })
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'Title field cannot be empty'}


@pytest.mark.asyncio
async def test_update_element_description(app):

    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.get('/api/elements/2')
    element_2 = response.json()

    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.put('/api/elements/' + str(element_2["id"]), json={
            "description": "Element 2 now has a description",
        })
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        "id": element_2["id"],
        "title": element_2["title"],
        "description": "Element 2 now has a description",
        "project_id": element_2["project_id"],
        "element_type_id": element_2["element_type_id"]
    }


@pytest.mark.asyncio
async def test_update_element_project_id(app, prepared_projects):
    project_id = prepared_projects[1]["id"]
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.put('/api/elements/2', json={
            "project_id": project_id,
        })
    assert response.status_code == 400
    assert response.json() == {
        'detail': "Element 'Element 2' already exists in project 'Project 2'"}


@pytest.mark.asyncio
async def test_update_element_with_nonexistant_project_id(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.put('/api/elements/2', json={
            "project_id": 99,
        })
    assert response.status_code == 400
    assert response.json() == {
        'detail': "Project not found"}


@pytest.mark.asyncio
async def test_update_element_with_nonexistant_element_type_id(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.put('/api/elements/2', json={
            "element_type_id": 99,
        })
    assert response.status_code == 400
    assert response.json() == {
        'detail': "Element type not found"}


@pytest.mark.asyncio
async def test_update_element_element_type_id(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.put('/api/elements/2', json={
            "element_type_id": 1,
        })
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        "id": 2,
        "title": "Element 2",
        "description": "Element 2 now has a description",
        "project_id": 1,
        "element_type_id": 1
    }


@pytest.mark.asyncio
async def test_delete_element(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.delete('/api/elements/2')
    assert response.status_code == 200
    assert response.json() == {'detail': 'Element deleted'}


@pytest.mark.asyncio
async def test_delete_nonexistant_element(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.delete('/api/elements/2')
    assert response.status_code == 400
    assert response.json() == {'detail': 'Element not found'}


@pytest.mark.asyncio
async def test_element_list_now_have_one_item(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.get('/api/elements/')
    assert response.status_code == 200
    assert len(response.json()) == 1
