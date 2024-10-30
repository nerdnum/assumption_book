import json
from asyncio import run

from httpx import AsyncClient


async def client():
    async with AsyncClient(base_url="http://localhost:8000/api/v1") as client:
        yield client


metrics = [
    {"metric": "Length", "unit": "m"},
    {"metric": "Mass", "unit": "kg"},
    {"metric": "Time", "unit": "s"},
    {"metric": "Temperature", "unit": "K"},
    {"metric": "Electric Current", "unit": "A"},
    {"metric": "Amount of Substance", "unit": "mol"},
    {"metric": "Luminous Intensity", "unit": "cd"},
]


async def save_setting():
    client = AsyncClient(base_url="http://localhost:8000/api/v1")
    for metric in metrics[1:]:
        response = await client.post(
            "/settings",
            json={
                "settingTypeId": 1,
                "description": metric["metric"],
                "title": metric["metric"],
                "value": metric,
            },
        )
        print(response)


if __name__ == "__main__":
    run(save_setting())
