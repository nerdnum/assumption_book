import pytest
import pytest_asyncio
from httpx import AsyncClient
from tests.utils import remove_uuid, print_response
from slugify import slugify


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000/api/v1") as client:
        yield client


@pytest.mark.asyncio
async def test_get_projects(client):
    response = await client.get('/projects')
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_projects(client):

    project_name = 'Project 1'
    response = await client.post('/projects',
                                 json={"title": project_name,
                                       "description": "Project 1 Description",
                                       "projectManager": "Project Manager 1"})

    assert response.status_code == 201
    response_json = remove_uuid(response.json())
    assert response_json == {"id": 1,
                             "title": "Project 1",
                             "slug": "project-1",
                             "description": "Project 1 Description",
                             "projectManager": "Project Manager 1",
                             "logoUrl": None
                             }

    project_name = 'Project 2'
    response = await client.post('/projects',
                                 json={"title": project_name,
                                       "description": "Project 2 Description",
                                       "projectManager": "Project Manager 2"})
    assert response.status_code == 201
    response_json = remove_uuid(response.json())
    assert response_json == {"id": 2,
                             "title": project_name,
                             "slug": slugify(project_name),
                             "description": "Project 2 Description",
                             "projectManager": "Project Manager 2",
                             "logoUrl": None
                             }


@pytest.mark.asyncio
async def test_create_project_with_custom_slug(client):
    project_name = 'Project 3'
    response = await client.post('/projects',
                                 json={"title": project_name,
                                       "slug": "project-3-custom-slug",
                                       "description": "Project 3 Description",
                                       "projectManager": "Project Manager 3"})

    assert response.status_code == 201
    response_json = remove_uuid(response.json())
    assert response_json == {"id": 3,
                             "title": project_name,
                             "slug": "project-3-custom-slug",
                             "description": "Project 3 Description",
                             "projectManager": "Project Manager 3",
                             "logoUrl": None
                             }


@pytest.mark.asyncio
async def test_create_project_with_slug_on_path(client):
    project_name = 'Project 4'
    response = await client.post('/projects/project-4',
                                 json={"title": 'Project 4',
                                       "slug": "project-4-custom-slug",
                                       "description": "Project 4 Description",
                                       "projectManager": "Project Manager 4"})

    assert response.status_code == 201
    response_json = remove_uuid(response.json())
    assert response_json == {"id": 4,
                             "title": 'Project 4',
                             "slug": "project-4",  # slug on path takes precedence
                             "description": "Project 4 Description",
                             "projectManager": "Project Manager 4",
                             "logoUrl": None
                             }


@pytest.mark.asyncio
async def tests_trying_to_create_a_duplicate_project_title(client):

    response = await client.post('/projects',
                                 json={"title": "Project 1",
                                       "description": "Project 1 Description",
                                       "projectManager": "Project Manager 1"})
    assert response.status_code == 404
    assert response.json() == "Project with this title already exists"


@pytest.mark.asyncio
async def test_get_projects_list_length(client):

    response = await client.get('/projects')
    assert response.status_code == 200
    assert len(response.json()) == 4


@pytest.mark.asyncio
async def test_get_project_by_id(client):

    response = await client.get('/projects/1')
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {"id": 1,
                             "title": "Project 1",
                             "slug": "project-1",
                             "description": "Project 1 Description",
                             "projectManager": "Project Manager 1",
                             "logoUrl": None
                             }


@pytest.mark.asyncio
async def test_get_project_by_slug(client):

    response = await client.get('/projects/project-1')
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {"id": 1,
                             "title": "Project 1",
                             "slug": "project-1",
                             "description": "Project 1 Description",
                             "projectManager": "Project Manager 1",
                             "logoUrl": None
                             }


@pytest.mark.asyncio
async def test_update_project_by_id(client):

    response = await client.put('/projects/1',
                                json={"title": "Project 1 Updated",
                                      "description": "Project 1 Description Updated",
                                      "projectManager": "Project Manager 1 Updated"})
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {"id": 1,
                             "title": "Project 1 Updated",
                             "slug": "project-1-updated",
                             "description": "Project 1 Description Updated",
                             "projectManager": "Project Manager 1 Updated",
                             "logoUrl": None
                             }


@pytest.mark.asyncio
async def test_update_project_by_slug(client):

    response = await client.put('/projects/project-1-updated',
                                json={"title": "Project 1 Updated",
                                      "description": "Project 1 Description Updated",
                                      "projectManager": "Project Manager 1 Updated"})
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {"id": 1,
                             "title": "Project 1 Updated",
                             "slug": "project-1-updated",
                             "description": "Project 1 Description Updated",
                             "projectManager": "Project Manager 1 Updated",
                             "logoUrl": None
                             }


@pytest.mark.asyncio
async def test_update_project_by_none_existant_slug(client):

    response = await client.put('/projects/project-1',
                                json={"title": "Project 1 Updated",
                                      "description": "Project 1 Description Updated",
                                      "projectManager": "Project Manager 1 Updated"})
    assert response.status_code == 400
    response_json = remove_uuid(response.json())
    assert response_json == {'detail': 'Project not found'}


@pytest.mark.asyncio
async def test_update_project_title_only_by_id(client):

    response = await client.put('/projects/1',
                                json={"title": "Project 1 Updated Only"})
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {"id": 1,
                             "slug": "project-1-updated-only",
                             "title": "Project 1 Updated Only",
                             "description": "Project 1 Description Updated",
                             "projectManager": "Project Manager 1 Updated",
                             "logoUrl": None
                             }


@pytest.mark.asyncio
async def test_update_project_description_only_by_id(client):

    response = await client.put('/projects/1',
                                json={"description": "Project 1 Description Updated Only"})
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {"id": 1,
                             "slug": "project-1-updated-only",
                             "title": "Project 1 Updated Only",
                             "description": "Project 1 Description Updated Only",
                             "projectManager": "Project Manager 1 Updated",
                             "logoUrl": None
                             }


@pytest.mark.asyncio
async def test_update_project_project_manager_only_by_id(client):

    response = await client.put('/projects/1',
                                json={"projectManager": "Project Manager 1 Updated Only"})
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {"id": 1,
                             "slug": "project-1-updated-only",
                             "title": "Project 1 Updated Only",
                             "description": "Project 1 Description Updated Only",
                             "projectManager": "Project Manager 1 Updated Only",
                             "logoUrl": None
                             }


@pytest.mark.asyncio
async def test_update_project_logo_url_only_by_id(client):

    response = await client.put('/projects/1',
                                json={"logoUrl": "new/logo/url"})
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {"id": 1,
                             "slug": "project-1-updated-only",
                             "title": "Project 1 Updated Only",
                             "description": "Project 1 Description Updated Only",
                             "projectManager": "Project Manager 1 Updated Only",
                             "logoUrl": "new/logo/url"
                             }


@pytest.mark.asyncio
async def test_delete_project_by_id(client):
    response = await client.delete('/projects/2')
    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {'title': 'Project 2',
                             'description': 'Project 2 Description',
                             'slug': 'project-2',
                             'projectManager': 'Project Manager 2',
                             'logoUrl': None,
                             'id': 2
                             }


@pytest.mark.asyncio
async def test_delete_project_by_slug(client):
    response = await client.delete('/projects/project-1-updated-only')
    assert response.status_code == 200

    response_json = remove_uuid(response.json())
    assert response_json == {'title': 'Project 1 Updated Only',
                             'description': 'Project 1 Description Updated Only',
                             'slug': 'project-1-updated-only',
                             'projectManager': 'Project Manager 1 Updated Only',
                             'logoUrl': 'new/logo/url',
                             'id': 1
                             }


@pytest.mark.asyncio
async def test_delete_nonexistant_project(client):
    response = await client.delete('/projects/2')
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}


@pytest.mark.asyncio
async def test_delete_nonexistant_project_by_slug(client):
    response = await client.delete('/projects/project-1-updated-only')
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}


@pytest.mark.asyncio
async def test_cleanup_projects(client):
    projects = await client.get('/projects')
    for project in projects.json():
        await client.delete(f'/projects/{project["id"]}')

    projects = await client.get('/projects')
    assert projects.json() == []
