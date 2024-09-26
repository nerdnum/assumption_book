import pytest
import pytest_asyncio
from httpx import AsyncClient

from tests.utils import print_response, remove_uuid


def uuid_present(response):
    return response.json().get("uuid", None) is not None


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000/api/v1") as client:
        yield client


@pytest_asyncio.fixture
async def get_projects(client):

    projects = {}

    found_count = 0

    response = await client.get("/projects")

    if len(response.json()) > 0:
        for project in response.json():
            if project["title"] == "Fixture Project 1":
                found_count += 1
                projects["project_a"] = project
            if project["title"] == "Fixture Project 2":
                found_count += 1
                projects["project_b"] = project
            if found_count == 2:
                break

    if not projects:
        response = await client.post(
            "/projects",
            json={
                "title": "Fixture Project 1",
                "description": "Fixture Project 1 for testing components",
                "projectManager": "Fixture Project 1 Manager",
                "logoUrl": "https://www.example.com/logo1.png",
            },
        )
        projects["project_a"] = response.json()

    if found_count < 2:
        response = await client.post(
            "/projects",
            json={
                "title": "Fixture Project 2",
                "description": "Fixture Project 2 for testing components",
                "projectManager": "Fixture Project 2 Manager",
                "logoUrl": "https://www.example.com/logo2.png",
            },
        )
        projects["project_b"] = response.json()

    yield projects


@pytest_asyncio.fixture
async def get_component(client, get_projects):

    project_id = get_projects["project_a"]["id"]
    a_component = None

    response = await client.get(f"/projects/{project_id}/components")
    for component in response.json():
        if component["title"] == "Level 0 component from fixture":
            a_component = component
            break

    if a_component is None:
        response = await client.post(
            f"/projects/{project_id}/components",
            json={
                "title": "Level 0 component from fixture",
                "description": "Level 0 component from fixture",
                "level": 0,
            },
        )
        a_component = response.json()

    yield a_component


@pytest.mark.asyncio
async def test_get_components(client, get_projects):
    # project_a
    # project_b
    project_id = get_projects["project_a"]["id"]
    response = await client.get(f"/projects/{project_id}/components")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_fixture_project_exists(client, get_projects):
    # project_a
    # project_b
    project_id = get_projects["project_a"]["id"]
    response = await client.get(f"/projects/{project_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_fixture_component_exists(client, get_projects, get_component):
    # project_a - comp(id:1, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]
    component_id = get_component["id"]
    response = await client.get(f"/projects/{project_id}/components/{component_id}")
    assert response.status_code == 200


# Test variations on level 0 components and project_id


@pytest.mark.asyncio
async def test_create_level_0_component_by_project_id(client, get_projects):

    project_id = get_projects["project_a"]["id"]

    response = await client.post(
        f"/projects/{project_id}/components",
        json={
            "title": "Level 0 component",
            "description": "Level 0 component",
            "level": 0,
        },
    )
    assert response.status_code == 201
    uuid = response.json().get("uuid", None)
    assert uuid is not None
    response_json = remove_uuid(response.json())
    assert response_json == {
        "description": "Level 0 component",
        "id": 2,
        "level": 0,
        "parentId": None,
        "projectId": project_id,
        "sequence": 2,
        "title": "Level 0 component",
    }
    # project_a - comp(id:1, lvl:0)
    #           + comp(id:2, lvl:0)
    # project_b


@pytest.mark.asyncio
async def test_read_level_0_component_by_id(client, get_projects):
    # project_a - comp(id:1, lvl:0)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]

    response = await client.get(f"/projects/{project_id}/components/2")
    assert response.status_code == 200
    assert uuid_present(response)
    response_json = remove_uuid(response.json())
    assert response_json == {
        "description": "Level 0 component",
        "id": 2,
        "level": 0,
        "parentId": None,
        "projectId": project_id,
        "sequence": 2,
        "title": "Level 0 component",
    }


@pytest.mark.asyncio
async def test_read_none_existant_component_with_id(client, get_projects):
    # project_a - comp(id:1, lvl:0)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]  # type: ignore

    response = await client.get(f"/projects/{project_id}/components/99")
    assert response.status_code == 400
    assert response.json() == {"detail": "Component not found"}


@pytest.mark.asyncio
async def test_create_level_0_component_by_project_id_with_duplicate_title(
    client, get_projects
):
    # project_a - comp(id:1, lvl:0)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]

    response = await client.post(
        f"/projects/{project_id}/components",
        json={
            "title": "Level 0 component",
            "description": "Level 0 component",
            "level": 0,
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": "Level 0 component",
                "loc": ["body", "title"],
                "msg": "A level 0 component with title 'Level 0 component' "
                "already exists for this project",
                "type": "value_error",
            }
        ]
    }


@pytest.mark.asyncio
async def test_create_level_0_component_with_conflicting_project_id_in_body(
    client, get_projects
):
    # project_a - comp(id:1, lvl:0)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id_one = get_projects["project_a"]["id"]
    project_id_two = get_projects["project_b"]["id"]

    response = await client.post(
        f"/projects/{project_id_one}/components",
        json={
            "projectId": project_id_two,
            "title": "Another Level 0 component",
            "description": "Another Level 0 component",
            "level": 0,
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Project ID in json body does not match project ID in URL"
    }


@pytest.mark.asyncio
async def test_create_level_0_component_with_nonexistant_project_id_in_path(
    client, get_projects
):
    # project_a - comp(id:1, lvl:0)
    #           + comp(id:2, lvl:0)
    # project_b
    response = await client.post(
        f"/projects/99/components",
        json={
            "title": "Level 0 component",
            "description": "Level 0 component",
            "level": 0,
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Project not found"}


@pytest.mark.asyncio
async def test_create_level_0_component_with_missing_project_id_in_path(
    client, get_projects
):
    # project_a - comp(id:1, lvl:0)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]
    response = await client.post(
        f"/projects//components",
        json={
            "title": "Level 0 component",
            "description": "Level 0 component",
            "level": 0,
        },
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


@pytest.mark.asyncio
async def test_create_level_0_component_with_neg_project_id_in_path(
    client, get_projects
):
    # project_a - comp(id:1, lvl:0)
    #           + comp(id:2, lvl:0)
    # project_b
    response = await client.post(
        f"/projects/-2/components",
        json={
            "title": "Level 0 component",
            "description": "Level 0 component",
            "level": 0,
        },
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


@pytest.mark.asyncio
async def test_create_component_with_neg_level(client, get_projects):
    # project_a - comp(id:1, lvl:0)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]
    response = await client.post(
        f"/projects/{project_id}/components",
        json={
            "title": "Level -2 component",
            "description": "Level -2 component",
            "level": -2,
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "ctx": {"error": {}},
                "input": -2,
                "loc": ["body", "level"],
                "msg": "Value error, Value must be greater than or equal to 0",
                "type": "value_error",
            }
        ]
    }


@pytest.mark.asyncio
async def test_create_level_0_component_with_parent_id_in_the_path(
    client, get_projects, get_component
):
    # project_a - comp(id:1, lvl:0)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]
    component_id = get_component["id"]
    response = await client.post(
        f"/projects/{project_id}/components/{component_id}",
        json={
            "title": "Level 0 component",
            "description": "Level 0 component",
            "level": 0,
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "A level 0 component cannot have a parent ID"}


@pytest.mark.asyncio
async def test_create_level_0_component_with_parent_id_in_the_body(
    client, get_projects, get_component
):
    # project_a - comp(id:1, lvl:0)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]
    component_id = get_component["id"]
    response = await client.post(
        f"/projects/{project_id}/components",
        json={
            "parentId": component_id,
            "title": "Level 0 component",
            "description": "Level 0 component",
            "level": 0,
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "ctx": {"error": {}},
                "input": {
                    "description": "Level 0 component",
                    "level": 0,
                    "parentId": 1,
                    "title": "Level 0 component",
                },
                "loc": ["body"],
                "msg": "Value error, A level 0 component cannot have a parent",
                "type": "value_error",
            }
        ]
    }


# Test creating projects with variations on title


@pytest.mark.asyncio
async def test_create_component_without_title(client, get_projects):
    # project_a - comp(id:1, lvl:0)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]

    response = await client.post(
        f"/projects/{project_id}/components",
        json={"description": "Component without a title", "level": 0},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "title"],
                "msg": "Field required",
                "input": {"description": "Component without a title", "level": 0},
            }
        ]
    }


@pytest.mark.asyncio
async def test_create_component_with_empty_title(client, get_projects):
    # project_a - comp(id:1, lvl:0)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]

    response = await client.post(
        f"/projects/{project_id}/components",
        json={"title": "", "description": "Component without a title", "level": 0},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "ctx": {"min_length": 3},
                "input": "",
                "loc": ["body", "title"],
                "msg": "String should have at least 3 characters",
                "type": "string_too_short",
            }
        ]
    }


@pytest.mark.asyncio
async def test_create_component_with_short_title(client, get_projects):
    # project_a - comp(id:1, lvl:0)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]

    response = await client.post(
        f"/projects/{project_id}/components",
        json={"title": "Ti", "description": "Component without a title", "level": 0},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "ctx": {"min_length": 3},
                "input": "Ti",
                "loc": ["body", "title"],
                "msg": "String should have at least 3 characters",
                "type": "string_too_short",
            }
        ]
    }


@pytest.mark.asyncio
async def test_create_component_with_long_title(client, get_projects):
    # project_a - comp(id:1, lvl:0)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]

    response = await client.post(
        f"/projects/{project_id}/components",
        json={
            "title": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad",
            "description": "Component without a title",
            "level": 0,
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "ctx": {"max_length": 100},
                "input": "Lorem ipsum dolor sit amet, consectetur adipiscing "
                "elit, sed do eiusmod tempor incididunt ut labore et "
                "dolore magna aliqua. Ut enim ad",
                "loc": ["body", "title"],
                "msg": "String should have at most 100 characters",
                "type": "string_too_long",
            }
        ]
    }


# Test creating higher level components with variants in parent_id


@pytest.mark.asyncio
async def test_create_level_1_component_without_parent_id(client):
    # project_a - comp(id:1, lvl:0)
    #           + comp(id:2, lvl:0)
    # project_b
    projects = await client.get("/projects")
    project_id = projects.json()[0]["id"]

    response = await client.post(
        f"/projects/{project_id}/components",
        json={
            "title": "Level 1 component",
            "description": "Level 1 component",
            "level": 1,
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": None,
                "loc": ["body", "parent_id"],
                "msg": "A component at levels 1 or higher must have a parent",
                "type": "value_error",
            }
        ]
    }


@pytest.mark.asyncio
async def test_create_level_2_component_without_parent_id(client):
    # project_a - comp(id:1, lvl:0)
    #           + comp(id:2, lvl:0)
    # project_b
    projects = await client.get("/projects")
    project_id = projects.json()[0]["id"]

    response = await client.post(
        f"/projects/{project_id}/components",
        json={
            "title": "Level 2 component",
            "description": "Level 2 component",
            "level": 2,
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": None,
                "loc": ["body", "parent_id"],
                "msg": "A component at levels 1 or higher must have a parent",
                "type": "value_error",
            }
        ]
    }


@pytest.mark.asyncio
async def test_create_level_1_component_with_parent_id_in_the_path_and_body_mistmatch(
    client, get_projects, get_component
):
    # project_a - comp(id:1, lvl:0)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]
    component_id = get_component["id"]
    response = await client.post(
        f"/projects/{project_id}/components/{component_id}",
        json={
            "parentId": 88,
            "title": "Level 1 component",
            "description": "Level 1 component",
            "level": 1,
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Parent ID in json body does not match parent ID in URL"
    }


@pytest.mark.asyncio
async def test_create_level_1_component_with_negative_parent_id(client):
    # project_a - comp(id:1, lvl:0)
    #           + comp(id:2, lvl:0)
    # project_b
    projects = await client.get("/projects")
    project_id = projects.json()[0]["id"]

    response = await client.post(
        f"/projects/{project_id}/components",
        json={
            "parentId": -7,
            "title": "Level 1 component",
            "description": "Level 1 component",
            "level": 1,
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "ctx": {"error": {}},
                "input": -7,
                "loc": ["body", "parentId"],
                "msg": "Value error, Value must be greater than or equal to 0",
                "type": "value_error",
            }
        ]
    }


@pytest.mark.asyncio
async def test_create_level_1_component_with_parent_id(
    client, get_projects, get_component
):
    # project_a - comp(id:1, lvl:0)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]
    component_id = get_component["id"]

    response = await client.post(
        f"/projects/{project_id}/components/{component_id}",
        json={
            "title": "First Level 1 Component",
            "description": "First Level 1 Component",
            "level": 1,
        },
    )
    assert response.status_code == 201
    assert uuid_present(response)
    response_json = remove_uuid(response.json())
    assert response_json == {
        "id": 3,
        "projectId": project_id,
        "parentId": component_id,
        "sequence": 1,
        "title": "First Level 1 Component",
        "description": "First Level 1 Component",
        "level": 1,
    }
    # project_a - comp(id:1, lvl:0) - comp(id:3, lvl:1)
    #           + comp(id:2, lvl:0)
    # project_b


@pytest.mark.asyncio
async def test_create_second_level_1_component_with_parent_id(
    client, get_projects, get_component
):
    # project_a - comp(id:1, lvl:0) - comp(id:3, lvl:1)
    #                               + comp(id:4, lvl:1)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]
    component_id = get_component["id"]

    response = await client.post(
        f"/projects/{project_id}/components/{component_id}",
        json={
            "title": "Second Level 1 component",
            "description": "Second Level 1 component",
            "level": 1,
        },
    )
    assert response.status_code == 201
    assert uuid_present(response)
    response_json = remove_uuid(response.json())
    assert response_json == {
        "id": 4,
        "projectId": project_id,
        "parentId": component_id,
        "sequence": 2,
        "title": "Second Level 1 component",
        "description": "Second Level 1 component",
        "level": 1,
    }


@pytest.mark.asyncio
async def test_create_level_1_component_with_duplicate_title_for_parent_id(
    client, get_projects, get_component
):
    # project_a - comp(id:1, lvl:0) - comp(id:3, lvl:1)
    #                               + comp(id:4, lvl:1)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]
    component_id = get_component["id"]

    response = await client.post(
        f"/projects/{project_id}/components/{component_id}",
        json={
            "title": "First Level 1 Component",
            "description": "First Level 1 Component",
            "level": 1,
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": "First Level 1 Component",
                "loc": ["body", "title"],
                "msg": "A level child component with title 'First Level 1 "
                "Component' already exists for this component",
                "type": "value_error",
            }
        ]
    }


@pytest.mark.asyncio
async def test_get_level_0_component_with_descendants(
    client, get_projects, get_component
):
    # project_a - comp(id:1, lvl:0) - comp(id:3, lvl:1)
    #                               + comp(id:4, lvl:1)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]
    component_id = get_component["id"]
    response = await client.get(
        f"/projects/{project_id}/components/{component_id}/descendants"
    )
    assert response.status_code == 200

    response_json = response.json()
    for descendant in response_json:
        del descendant["uuid"]

    assert response_json == [
        {
            "description": "First Level 1 Component",
            "id": 3,
            "level": 1,
            "parentId": 1,
            "projectId": project_id,
            "sequence": 1,
            "title": "First Level 1 Component",
        },
        {
            "description": "Second Level 1 component",
            "id": 4,
            "level": 1,
            "parentId": 1,
            "projectId": project_id,
            "sequence": 2,
            "title": "Second Level 1 component",
        },
    ]


@pytest.mark.asyncio
async def test_root_components_of_project(client, get_projects):
    # project_a - comp(id:1, lvl:0) - comp(id:3, lvl:1)
    #                               + comp(id:4, lvl:1)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]
    response = await client.get(f"/projects/{project_id}/components/root-components")
    assert response.status_code == 200

    response_json = response.json()
    for item in response_json:
        del item["uuid"]

    assert response_json == [
        {
            "description": "Level 0 component from fixture",
            "id": 1,
            "level": 0,
            "parentId": None,
            "projectId": project_id,
            "sequence": 1,
            "title": "Level 0 component from fixture",
        },
        {
            "description": "Level 0 component",
            "id": 2,
            "level": 0,
            "parentId": None,
            "projectId": project_id,
            "sequence": 2,
            "title": "Level 0 component",
        },
    ]


@pytest.mark.asyncio
async def test_create_level_3_component_with_level_0_parent_id(
    client, get_projects, get_component
):
    # project_a - comp(id:1, lvl:0) - comp(id:3, lvl:1)
    #                               + comp(id:4, lvl:1)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]
    component_id = get_component["id"]

    response = await client.post(
        f"/projects/{project_id}/components/{component_id}",
        json={
            "title": "Level 3 component",
            "description": "Level 3 component",
            "level": 3,
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": 1,
                "loc": ["body", "parent_id"],
                "msg": "Component level can only be one higher than the parent level",
                "type": "value_error",
            }
        ]
    }


@pytest.mark.asyncio
async def test_create_level_0_component_with_duplicate_sequence_no(
    client, get_projects
):
    # project_a - comp(id:1, lvl:0) - comp(id:3, lvl:1)
    #                               + comp(id:4, lvl:1)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]

    response = await client.post(
        f"/projects/{project_id}/components",
        json={
            "title": "Yet another Level 0 component",
            "description": "Yet another Level 0 component",
            "level": 0,
            "sequence": 1,
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": 1,
                "loc": ["body", "sequence"],
                "msg": "Component with this sequence number already exists for this "
                "parent ID",
                "type": "value_error",
            }
        ]
    }


@pytest.mark.asyncio
async def test_create_level_2_component_without_a_title(
    client, get_projects, get_component
):
    # project_a - comp(id:1, lvl:0) - comp(id:3, lvl:1)
    #                               + comp(id:4, lvl:1)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]
    component_id = get_component["id"]

    response = await client.post(
        f"/projects/{project_id}/components/{component_id}",
        json={
            "description": "Level 2 component",
            "level": 2,
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "title"],
                "msg": "Field required",
                "input": {"description": "Level 2 component", "level": 2},
            }
        ]
    }


@pytest.mark.asyncio
async def test_update_component_with_new_title(client, get_projects, get_component):
    # project_a - comp(id:1, lvl:0) - comp(id:3, lvl:1)
    #                               + comp(id:4, lvl:1)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]
    component = get_component

    predicted_component = component
    predicted_component["title"] = "Updated title"

    response = await client.put(
        f'/projects/{project_id}/components/{component["id"]}',
        json={"title": "Updated title"},
    )
    assert response.status_code == 200
    assert response.json() == predicted_component


@pytest.mark.asyncio
async def test_update_level_0_component_with_duplicate_title(client, get_projects):
    # project_a - comp(id:1, lvl:0) - comp(id:3, lvl:1)
    #                               + comp(id:4, lvl:1)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]

    response = await client.get(f"/projects/{project_id}/components/root-components")
    descendants = response.json()
    assert len(descendants) >= 2
    project_one = descendants[0]
    project_two = descendants[1]

    response = await client.put(
        f'/projects/{project_id}/components/{project_one["id"]}',
        json={"title": project_two["title"]},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": "Level 0 component",
                "loc": ["body", "title"],
                "msg": "A level 0 component with title 'Level 0 component' "
                "already exists for this project",
                "type": "value_error",
            }
        ]
    }


@pytest.mark.asyncio
async def test_update_level_1_component_with_duplicate_title(client, get_projects):
    # project_a - comp(id:1, lvl:0) - comp(id:3, lvl:1)
    #                               + comp(id:4, lvl:1)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]

    response = await client.get(f"/projects/{project_id}/components/root-components")
    descendants = response.json()
    project_one = descendants[0]
    project_two = descendants[1]

    response = await client.put(
        f'/projects/{project_id}/components/{project_one["id"]}',
        json={"title": project_two["title"]},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": "Level 0 component",
                "loc": ["body", "title"],
                "msg": "A level 0 component with title 'Level 0 component' "
                "already exists for this project",
                "type": "value_error",
            }
        ]
    }


@pytest.mark.asyncio
async def test_update_component_with_new_description(client, get_projects):
    # project_a - comp(id:1, lvl:0) - comp(id:3, lvl:1)
    #                               + comp(id:4, lvl:1)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]

    response = await client.get(f"/projects/{project_id}/components/3")
    predicted_component = response.json()
    predicted_component["description"] = "This in a longish updated description"

    response = await client.put(
        f"/projects/{project_id}/components/3",
        json={"description": "This in a longish updated description"},
    )
    assert response.status_code == 200
    assert response.json() == predicted_component


@pytest.mark.asyncio
async def test_update_component_with_new_parent_id(client, get_projects):
    # project_a - comp(id:1, lvl:0) - comp(id:3, lvl:1)
    #                               + comp(id:4, lvl:1)
    #           + comp(id:2, lvl:0)
    # project_b
    project_id = get_projects["project_a"]["id"]

    response = await client.get(f"/projects/{project_id}/components/root-components")
    assert response.status_code == 200
    components = response.json()
    assert len(components) >= 2
    component_one = components[0]
    component_two = components[1]

    response = await client.get(
        f'/projects/{project_id}/components/{component_one["id"]}/descendants'
    )
    component_one_descendants = response.json()

    component_one_first_descendant = component_one_descendants[0]
    component_one_first_descendant["parentId"] = component_two["id"]
    predicted_component = component_one_first_descendant

    response = await client.put(
        f'/projects/{project_id}/components/{component_one_first_descendant["id"]}',
        json={"parentId": component_two["id"]},
    )
    assert response.status_code == 200
    assert response.json() == predicted_component


@pytest.mark.asyncio
async def test_update_component_with_new_parent_id_but_duplicate_sequence(
    client, get_projects
):
    # project_a - comp(id:1, lvl:0) - comp(id:4, lvl:1)
    #           + comp(id:2, lvl:0) - comp(id:3, lvl:1)
    # project_b
    project_id = get_projects["project_a"]["id"]

    # create component with sequence 1 under Id 4
    response = await client.post(
        f"/projects/{project_id}/components/4",
        json={
            "title": "Component 1.4.1",
            "description": "First compoment under level 1 component with Id 4",
            "level": 2,
        },
    )
    assert response.status_code == 201
    component_1_4_1 = response.json()
    assert component_1_4_1["parentId"] == 4
    assert component_1_4_1["sequence"] == 1

    # project_a - comp(id:1, lvl:0) - comp(id:4, lvl:1) - comp(id:5, lvl:2, seq:1)
    #           + comp(id:2, lvl:0) - comp(id:3, lvl:1)
    # project_b

    # create component with sequence 1 under Id 3
    project_id = get_projects["project_a"]["id"]
    response = await client.post(
        f"/projects/{project_id}/components/3",
        json={
            "title": "Component 2.3.1",
            "description": "First compoment under level 1 component with Id 3",
            "level": 2,
        },
    )
    assert response.status_code == 201
    component_2_3_1 = response.json()
    assert component_2_3_1["parentId"] == 3
    assert component_2_3_1["sequence"] == 1

    # project_a - comp(id:1, lvl:0) - comp(id:4, lvl:1) - comp(id:5, lvl:2, seq:1)
    #           + comp(id:2, lvl:0) - comp(id:3, lvl:1) - comp(id:6, lvl:2, seq:1)
    # project_b

    # Try to move component 1.4.1 with sequence 1 to under component 2.3 with sequence clashing
    # with component 2.3.1
    response = await client.put(
        f'/projects/{project_id}/components/{component_1_4_1["id"]}',
        json={"parentId": 3},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": 1,
                "loc": ["body", "sequence"],
                "msg": "Component with this sequence number already exists for "
                "this parent ID",
                "type": "value_error",
            }
        ]
    }


@pytest.mark.asyncio
async def test_update_component_with_none_existant_parent_id_in_the_body(
    client, get_projects
):
    # project_a - comp(id:1, lvl:0) - comp(id:4, lvl:1) - comp(id:5, lvl:2, seq:1)
    #           + comp(id:2, lvl:0) - comp(id:3, lvl:1) - comp(id:6, lvl:2, seq:1)
    # project_b

    lvl_1_component = None

    project_id = get_projects["project_a"]["id"]
    response = await client.get(f"/projects/{project_id}/components")
    components = response.json()
    for component in components:
        if component["level"] == 1:
            lvl_1_component = component
            break

    lvl_1_component["parentId"] = 99
    response = await client.put(
        f'/projects/{project_id}/components/{lvl_1_component["id"]}',
        json=lvl_1_component,
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": 99,
                "loc": ["body", "parent_id"],
                "msg": "Parent component does not exist",
                "type": "value_error",
            }
        ]
    }


@pytest.mark.asyncio
async def test_delete_nonexistent_component(client, get_projects):
    # project_a - comp(id:1, lvl:0) - comp(id:4, lvl:1) - comp(id:5, lvl:2, seq:1)
    #           + comp(id:2, lvl:0) - comp(id:3, lvl:1) - comp(id:6, lvl:2, seq:1)
    # project_b
    project_id = get_projects["project_a"]["id"]
    response = await client.delete(f"/projects/{project_id}/components/99")
    assert response.status_code == 400
    assert response.json() == {"detail": "Component not found"}


@pytest.mark.asyncio
async def test_delete_component_with_descendants(client, get_projects, get_component):
    # project_a - comp(id:1, lvl:0) - comp(id:4, lvl:1) - comp(id:5, lvl:2, seq:1)
    #           + comp(id:2, lvl:0) - comp(id:3, lvl:1) - comp(id:6, lvl:2, seq:1)
    # project_b

    project_id = get_projects["project_a"]["id"]

    response = await client.delete(f"/projects/{project_id}/components/1")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "value_error",
                "loc": ["body", "id"],
                "msg": "Cannot delete a component with descendants",
                "input": 1,
            }
        ]
    }


@pytest.mark.asyncio
async def test_delete_component_without_descendants(
    client, get_projects, get_component
):
    # project_a - comp(id:1, lvl:0) - comp(id:4, lvl:1) - comp(id:5, lvl:2, seq:1)
    #           + comp(id:2, lvl:0) - comp(id:3, lvl:1) - comp(id:6, lvl:2, seq:1)
    # project_b

    project_id = get_projects["project_a"]["id"]

    response = await client.delete(f"/projects/{project_id}/components/5")

    assert response.status_code == 200
    response_json = remove_uuid(response.json())
    assert response_json == {
        "description": "First compoment under level 1 component with Id 4",
        "id": 5,
        "level": 2,
        "parentId": 4,
        "projectId": project_id,
        "sequence": 1,
        "title": "Component 1.4.1",
    }
