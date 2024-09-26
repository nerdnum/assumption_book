import json

import pytest
import pytest_asyncio

from tests.utils import print_response, remove_uuid


@pytest_asyncio.fixture
async def get_setting_type(client):

    setting_type = None

    found_count = 0

    response = await client.get("/setting-types")

    if len(response.json()) > 0:
        for setting_type_found in response.json():
            if setting_type_found["id"] == 1:  # type: ignore
                found_count += 1
                setting_type = setting_type_found
            if found_count == 1:
                break

    if not setting_type:
        response = await client.post(
            "/setting-types",
            json={
                "title": "Some settings type",
                "description": "Some settings type description",
            },
        )
        setting_type = response.json()

    yield setting_type


@pytest.mark.asyncio
async def test_get_empty_setting_types(client):
    response = await client.get("/setting-types")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_setting_type(client):
    response = await client.post(
        "/setting-types",
        json={
            "title": "Units of Measure",
            "description": "Lists of all the units of measure used in the various projects",
        },
    )
    response_json = remove_uuid(response.json())
    assert response.status_code == 201
    assert response_json == {
        "defaultText": None,
        "description": "Lists of all the units of measure used in the various "
        "projects",
        "id": 1,
        "title": "Units of Measure",
    }


@pytest.mark.asyncio
async def test_read_setting_type_by_id(client):
    response = await client.get("/setting-types/1")
    response_json = remove_uuid(response.json())
    assert response.status_code == 200
    assert response_json == {
        "defaultText": None,
        "description": "Lists of all the units of measure used in the various "
        "projects",
        "id": 1,
        "title": "Units of Measure",
    }


@pytest.mark.asyncio
async def test_read_setting_type_with_none_existant_id(client):
    response = await client.get("/setting-types/77")
    response_json = remove_uuid(response.json())
    assert response.status_code == 404
    assert response_json == {"detail": "Setting type not found"}


@pytest.mark.asyncio
async def test_create_setting_type_without_title(client):
    response = await client.post(
        "/setting-types",
        json={
            "description": "Lists of all the units of measure used in the various projects",
        },
    )
    response_json = remove_uuid(response.json())
    assert response.status_code == 422
    assert response_json == {
        "detail": [
            {
                "input": {
                    "description": "Lists of all the units of measure "
                    "used in the various projects"
                },
                "loc": ["body", "title"],
                "msg": "Field required",
                "type": "missing",
            }
        ]
    }


@pytest.mark.asyncio
async def test_create_setting_type_with_duplicate_title(client):
    response = await client.post(
        "/setting-types",
        json={"title": "Units of Measure", "description": "A different description"},
    )
    response_json = remove_uuid(response.json())
    assert response.status_code == 400
    assert response_json == {"detail": "Setting type with this title already exists"}


@pytest.mark.asyncio
async def test_update_setting_type_title_by_id(client):
    response = await client.put(
        "/setting-types/1",
        json={
            "title": "Different setting type",
            "description": "A different type description",
        },
    )
    response_json = remove_uuid(response.json())
    assert response.status_code == 200
    assert response_json == {
        "defaultText": None,
        "description": "A different type description",
        "id": 1,
        "title": "Different setting type",
    }


@pytest.mark.asyncio
async def test_update_setting_type_default_text_by(client):
    response = await client.put(
        "/setting-types/1", json={"defaultText": "This is some default text"}
    )
    response_json = remove_uuid(response.json())
    assert response.status_code == 200
    assert response_json == {
        "defaultText": "This is some default text",
        "description": "A different type description",
        "id": 1,
        "title": "Different setting type",
    }


@pytest.mark.asyncio
async def test_update_setting_type_with_empty_object(client):
    response = await client.put("/setting-types/1", json={})
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "ctx": {"error": {}},
                "input": {},
                "loc": ["body"],
                "msg": "Value error, At least one of title, description or "
                "default_text must be provided",
                "type": "value_error",
            }
        ]
    }


@pytest.mark.asyncio
async def test_create_and_delete_setting_type(client):
    response = await client.post(
        "/setting-types",
        json={
            "title": "This is a unique new setting type",
            "description": "New unique setting type",
            "defaultText": "Some default text",
        },
    )
    response_json = remove_uuid(response.json())
    assert response.status_code == 201
    assert response_json == {
        "id": 3,
        "title": "This is a unique new setting type",
        "description": "New unique setting type",
        "defaultText": "Some default text",
    }

    response = await client.delete("/setting-types/3")
    assert response.status_code == 200
    assert response.json() == {"detail": "Setting type deleted"}


@pytest.mark.asyncio
async def test_read_empty_settings(client):
    response = await client.get("/settings")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_setting(client, get_setting_type):

    setting_type_id = get_setting_type["id"]

    response = await client.post(
        "/settings",
        json={
            "settingTypeId": setting_type_id,
            "title": "Energy",
            "description": "The UOM for energy",
            "value": "kWh",
        },
    )
    response_json = remove_uuid(response.json())
    assert response.status_code == 201
    assert response_json == {
        "id": 1,
        "settingTypeId": setting_type_id,
        "title": "Energy",
        "description": "The UOM for energy",
        "value": "kWh",
    }


@pytest.mark.asyncio
async def test_read_setting_by_id(client, get_setting_type):

    setting_type_id = get_setting_type["id"]

    response = await client.get("/settings/1")
    response_json = remove_uuid(response.json())
    assert response.status_code == 200
    assert response_json == {
        "id": 1,
        "settingTypeId": setting_type_id,
        "title": "Energy",
        "description": "The UOM for energy",
        "value": "kWh",
    }


@pytest.mark.asyncio
async def test_read_setting_with_none_existant_id(client):
    response = await client.get("/settings/77")
    response_json = remove_uuid(response.json())
    assert response.status_code == 404
    assert response_json == {"detail": "Setting not found"}


@pytest.mark.asyncio
async def test_update_setting_title_and_value(client, get_setting_type):

    setting_type_id = get_setting_type["id"]

    response = await client.put("/settings/1", json={"title": "Power", "value": "kW"})
    response_json = remove_uuid(response.json())
    assert response.status_code == 200
    assert response_json == {
        "id": 1,
        "settingTypeId": setting_type_id,
        "title": "Power",
        "description": "The UOM for energy",
        "value": "kW",
    }


@pytest.mark.asyncio
async def test_create_and_delete_setting(client, get_setting_type):

    setting_type_id = get_setting_type["id"]

    response = await client.post(
        "/settings",
        json={
            "settingTypeId": setting_type_id,
            "title": "Distance",
            "description": "The UOM for distance",
            "value": "km",
        },
    )
    response_json = remove_uuid(response.json())
    assert response.status_code == 201
    assert response_json == {
        "id": 2,
        "settingTypeId": setting_type_id,
        "title": "Distance",
        "description": "The UOM for distance",
        "value": "km",
    }

    response = await client.delete("/settings/2")
    assert response.status_code == 200
    assert response.json() == {"detail": "Setting deleted"}
