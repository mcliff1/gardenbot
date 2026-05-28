"""Basic tests for the Gardenbot API."""

import pytest
from httpx import ASGITransport, AsyncClient

from gardenbot.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "gardenbot"
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_list_yards(client):
    response = await client.get("/yards/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_plants(client):
    response = await client.get("/plants/")
    assert response.status_code == 200
    assert response.json() == []
