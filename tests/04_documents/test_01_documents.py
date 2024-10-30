import json
import os

import pytest
import pytest_asyncio
from httpx import AsyncClient

from tests.utils import print_response, remove_uuid


@pytest_asyncio.fixture
async def get_project(client):

    projects = {}

    found_count = 0

    response = await client.get("/projects")

    if len(response.json()) > 0:
        for project in response.json():
            if project["title"] == "Fixture Project 1":  # type: ignore
                found_count += 1
                projects["project_a"] = project
            if found_count == 1:
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

    yield projects


@pytest_asyncio.fixture
async def get_component(client, get_project):

    project_id = get_project["project_a"]["id"]  # type: ignore
    a_component = None

    response = await client.get(f"/projects/{project_id}/components")
    for component in response.json():
        if component["title"] == "Level 0 component from fixture":  # type: ignore
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


@pytest_asyncio.fixture
async def get_document(client, get_project, get_component):

    project_id = get_project["project_a"]["id"]  # type: ignore
    component_id = get_component["id"]  # type: ignore
    a_document = None

    response = await client.get(
        f"/documents?project_id={project_id}&component_id={component_id}"
    )
    response_json = response.json()
    if len(response_json) > 0:
        a_document = response_json[0]  # type: ignore
    else:
        with open("tests/04_documents/assets/valid_content.json") as json_file:
            doc_json = json.load(json_file)
            response = await client.post(
                "/documents",
                json={
                    "projectId": project_id,
                    "componentId": component_id,
                    "title": "Fixture Document 1",
                    "sequence": 1,
                    "content": doc_json,
                    "context": "Fixture Document 1 context",
                },
            )
            a_document = response.json()

    yield a_document


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://localhost:8000/api/v1") as client:
        yield client


@pytest.mark.asyncio
async def test_get_documents_for_unknown_project(client):
    response = await client.get("/documents?project_id=8&component_id=74")
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}


@pytest.mark.asyncio
async def test_get_documents_for_unknown_component(client, get_project):
    project_id = get_project["project_a"]["id"]  # type: ignore
    response = await client.get(f"/documents?project_id={project_id}&component_id=74")
    assert response.status_code == 404
    assert response.json() == {"detail": "Component not found"}


@pytest.mark.asyncio
async def test_create_document_for_project_component(
    client, get_project, get_component
):
    project_id = get_project["project_a"]["id"]  # type: ignore
    component_id = get_component["id"]  # type: ignore

    with open("tests/04_documents/assets/valid_content.json") as json_file:
        doc_json = json.load(json_file)
        response = await client.post(
            "/documents",
            json={
                "projectId": project_id,
                "componentId": component_id,
                "title": "Fixture Document 1",
                "sequence": 1,
                "content": doc_json,
                "context": "Fixture Document 1 context",
            },
        )
        assert response.status_code == 201
        response_json = remove_uuid(response.json())
        assert response_json == {
            "projectId": project_id,
            "componentId": component_id,
            "title": "Fixture Document 1",
            "sequence": 1,
            "content": doc_json,
            "context": "Fixture Document 1 context",
            "id": 1,
        }


@pytest.mark.asyncio
async def test_create_document_with_duplicate_title_for_project_component(
    client, get_project, get_component
):
    project_id = get_project["project_a"]["id"]  # type: ignore
    component_id = get_component["id"]  # type: ignore

    with open("tests/04_documents/assets/valid_content.json") as json_file:
        doc_json = json.load(json_file)
        response = await client.post(
            "/documents",
            json={
                "projectId": project_id,
                "componentId": component_id,
                "title": "Fixture Document 1",
                "sequence": 1,
                "content": doc_json,
                "context": "Fixture Document 1 context",
            },
        )
        assert response.status_code == 422
        response_json = remove_uuid(response.json())
        assert response_json == {
            "detail": [
                {
                    "input": "Fixture Document 1",
                    "loc": ["body", "title"],
                    "msg": "A document with title 'Fixture Document 1' already "
                    "exists for this component",
                    "type": "value_error",
                }
            ]
        }


@pytest.mark.asyncio
async def test_retrieve_document_for_project_component(
    client, get_project, get_component
):
    project_id = get_project["project_a"]["id"]  # type: ignore
    component_id = get_component["id"]  # type: ignore

    with open("tests/04_documents/assets/valid_content.json") as json_file:
        doc_json = json.load(json_file)
        response = await client.get(
            f"/documents?project_id={project_id}&component_id={component_id}",
        )
        assert response.status_code == 200
        first_doc = remove_uuid(response.json()[0])  # type: ignore
        assert first_doc == {
            "projectId": project_id,
            "componentId": component_id,
            "title": "Fixture Document 1",
            "sequence": 1,
            "content": doc_json,
            "id": 1,
            "context": "Fixture Document 1 context",
        }


# @pytest.mark.asyncio

## After creating more documents, it became clear that not all document parts will have ids. So this test
## will aloways fail. For now I just need to get things done, so this test will be skipped for now.
## 2024-10-24

# async def test_create_document_without_section_id(client, get_project, get_component):
#     project_id = get_project["project_a"]["id"]  # type: ignore
#     component_id = get_component["id"]  # type: ignore

#     with open("tests/04_documents/assets/doc_no_id.json") as json_file:
#         doc_json = json.load(json_file)
#         response = await client.post(
#             "/documents",
#             json={
#                 "projectId": project_id,
#                 "componentId": component_id,
#                 "title": "Fixture Document 1 more",
#                 "sequence": 1,
#                 "content": doc_json,
#                 "context": "Fixture Document 1 context",
#             },
#         )
#         print_response(response)
#         assert response.status_code == 422
#         assert response.json() == {
#             "detail": [
#                 {
#                     "input": {
#                         "level": 2,
#                     },
#                     "loc": ["body", "content", "content", 0, "attrs", "id"],
#                     "msg": "Field required",
#                     "type": "missing",
#                 }
#             ]
#         }


@pytest.mark.asyncio
async def test_create_document_with_none_existant_project_id(client, get_component):
    component_id = get_component["id"]  # type: ignore
    with open("tests/04_documents/assets/valid_content.json") as json_file:
        doc_json = json.load(json_file)
        response = await client.post(
            "/documents",
            json={
                "projectId": 99,
                "componentId": component_id,
                "title": "Title for non-existant project",
                "sequence": 1,
                "content": doc_json,
                "context": "Fixture Document 1 context",
            },
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": [
                {
                    "input": 99,
                    "loc": ["body", "project_id"],
                    "msg": "Project not found",
                    "type": "value_error",
                }
            ]
        }


@pytest.mark.asyncio
async def test_create_document_with_none_existant_component_id(client, get_project):
    project_id = get_project["project_a"]["id"]  # type: ignore
    with open("tests/04_documents/assets/valid_content.json") as json_file:
        doc_json = json.load(json_file)
        response = await client.post(
            "/documents",
            json={
                "projectId": project_id,
                "componentId": 99,
                "title": "Title for non-existant project",
                "sequence": 1,
                "content": doc_json,
                "context": "Fixture Document 1 context",
            },
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": [
                {
                    "input": 99,
                    "loc": ["body", "component_id"],
                    "msg": "Component not found",
                    "type": "value_error",
                }
            ]
        }


@pytest.mark.asyncio
async def test_update_documents_with_new_content(client, get_document):

    submit_json = get_document
    document_id = get_document["id"]  # type: ignore

    with open("tests/04_documents/assets/valid_content_for_update.json") as json_file:
        doc_json = json.load(json_file)
        submit_json["content"] = doc_json  # type: ignore

        response = await client.put(f"/documents/{document_id}", json=submit_json)

        assert response.status_code == 200
        assert response.json() == submit_json


@pytest.mark.asyncio
async def test_get_document_by_id(client):

    response = await client.get("/documents/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1  # type: ignore


@pytest.mark.asyncio
async def test_get_document_by_none_existant_id(client):

    response = await client.get("/documents/99")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}
