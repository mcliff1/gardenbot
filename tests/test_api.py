"""Basic tests for the Gardenbot API."""

import tempfile

import pytest
from httpx import ASGITransport, AsyncClient

# Reusable test boundaries
BOUNDARY_100x80 = [
    {"x": 0, "y": 0}, {"x": 100, "y": 0},
    {"x": 100, "y": 80}, {"x": 0, "y": 80},
]
BOUNDARY_50x50 = [
    {"x": 0, "y": 0}, {"x": 50, "y": 0},
    {"x": 50, "y": 50}, {"x": 0, "y": 50},
]
BOUNDARY_60x40 = [
    {"x": 0, "y": 0}, {"x": 60, "y": 0},
    {"x": 60, "y": 40}, {"x": 0, "y": 40},
]


@pytest.fixture(autouse=True)
def tmp_data_dir(monkeypatch):
    """Use a temp directory for data storage during tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("GARDENBOT_DATA_DIR", tmpdir)
        # Reload storage module to pick up new env var
        import gardenbot.services.storage as storage_mod

        storage_mod.DATA_DIR = __import__("pathlib").Path(tmpdir)
        storage_mod.YARDS_DIR = storage_mod.DATA_DIR / "yards"
        storage_mod.PLANTS_FILE = storage_mod.DATA_DIR / "plants.json"
        yield tmpdir


@pytest.fixture
async def client():
    from gardenbot.main import app

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
async def test_list_yards_empty(client):
    response = await client.get("/yards/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_plants_empty(client):
    response = await client.get("/plants/")
    assert response.status_code == 200
    assert response.json() == []


# --- Yard CRUD ---


@pytest.mark.asyncio
async def test_yard_crud(client):
    # Create
    resp = await client.post(
        "/yards/",
        json={
            "name": "My Yard",
            "boundary": BOUNDARY_100x80,
            "origin_description": "NW corner",
        },
    )
    assert resp.status_code == 201
    yard = resp.json()
    yard_id = yard["id"]
    assert yard["name"] == "My Yard"
    assert len(yard["boundary"]) == 4

    # List
    resp = await client.get("/yards/")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # Get
    resp = await client.get(f"/yards/{yard_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "My Yard"

    # Update
    resp = await client.put(f"/yards/{yard_id}", json={"name": "Updated Yard"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Yard"

    # Delete
    resp = await client.delete(f"/yards/{yard_id}")
    assert resp.status_code == 200
    assert resp.json()["deleted"] == yard_id

    # Verify gone
    resp = await client.get(f"/yards/{yard_id}")
    assert resp.status_code == 404


# --- Area CRUD ---


@pytest.mark.asyncio
async def test_area_crud(client):
    # Setup: create a yard
    resp = await client.post(
        "/yards/",
        json={
            "name": "Test Yard",
            "boundary": BOUNDARY_50x50,
        },
    )
    yard_id = resp.json()["id"]

    # Create area
    resp = await client.post(
        f"/yards/{yard_id}/areas",
        json={
            "name": "Front Bed",
            "type": "flower_bed",
            "shape": [{"x": 5, "y": 5}, {"x": 20, "y": 5}, {"x": 20, "y": 10}, {"x": 5, "y": 10}],
            "sun_exposure": "full_sun",
        },
    )
    assert resp.status_code == 201
    area = resp.json()
    area_id = area["id"]
    assert area["name"] == "Front Bed"
    assert area["type"] == "flower_bed"

    # List areas
    resp = await client.get(f"/yards/{yard_id}/areas")
    assert len(resp.json()) == 1

    # Update area
    resp = await client.put(f"/yards/{yard_id}/areas/{area_id}", json={"name": "Side Bed"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Side Bed"

    # Delete area
    resp = await client.delete(f"/yards/{yard_id}/areas/{area_id}")
    assert resp.status_code == 200

    resp = await client.get(f"/yards/{yard_id}/areas")
    assert resp.json() == []


# --- Structure CRUD ---


@pytest.mark.asyncio
async def test_structure_crud(client):
    resp = await client.post(
        "/yards/",
        json={
            "name": "Struct Yard",
            "boundary": BOUNDARY_50x50,
        },
    )
    yard_id = resp.json()["id"]

    # Create structure
    resp = await client.post(
        f"/yards/{yard_id}/structures",
        json={
            "name": "House",
            "type": "house",
            "footprint": [
                {"x": 10, "y": 10}, {"x": 40, "y": 10},
                {"x": 40, "y": 35}, {"x": 10, "y": 35},
            ],
        },
    )
    assert resp.status_code == 201
    structure = resp.json()
    assert structure["name"] == "House"

    # Update
    resp = await client.put(
        f"/yards/{yard_id}/structures/{structure['id']}",
        json={"notes": "Main dwelling"},
    )
    assert resp.status_code == 200
    assert resp.json()["notes"] == "Main dwelling"

    # Delete
    resp = await client.delete(f"/yards/{yard_id}/structures/{structure['id']}")
    assert resp.status_code == 200


# --- Plant CRUD ---


@pytest.mark.asyncio
async def test_plant_crud(client):
    resp = await client.post(
        "/plants/",
        json={
            "common_name": "Lavender",
            "botanical_name": "Lavandula",
            "perennial": True,
            "bloom_time": "mid-summer",
            "color": "purple",
        },
    )
    assert resp.status_code == 201
    plant = resp.json()
    assert plant["common_name"] == "Lavender"

    # Get
    resp = await client.get(f"/plants/{plant['id']}")
    assert resp.status_code == 200

    # Search
    resp = await client.get("/plants/search?q=laven")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # List
    resp = await client.get("/plants/")
    assert len(resp.json()) == 1


# --- Proposal lifecycle ---


@pytest.mark.asyncio
async def test_proposal_lifecycle(client):
    # Create yard
    resp = await client.post(
        "/yards/",
        json={
            "name": "Proposal Yard",
            "boundary": BOUNDARY_60x40,
        },
    )
    yard_id = resp.json()["id"]

    # Create proposal
    resp = await client.post(
        f"/yards/{yard_id}/proposals/",
        json={"name": "Add patio", "description": "New stone patio in back"},
    )
    assert resp.status_code == 201
    proposal = resp.json()
    proposal_id = proposal["id"]
    assert proposal["state"] == "draft"
    assert proposal["baseline_snapshot"]["id"] == yard_id

    # Update with changes
    resp = await client.put(
        f"/yards/{yard_id}/proposals/{proposal_id}",
        json={
            "changes": [
                {
                    "action": "add",
                    "target_type": "area",
                    "after": {
                        "id": "new-patio",
                        "name": "Back Patio",
                        "type": "patio",
                        "shape": [
                            {"x": 30, "y": 20}, {"x": 55, "y": 20},
                            {"x": 55, "y": 35}, {"x": 30, "y": 35},
                        ],
                    },
                    "notes": "12x15 flagstone patio",
                }
            ],
            "cost_proposed": 5000.0,
        },
    )
    assert resp.status_code == 200
    assert len(resp.json()["changes"]) == 1
    assert resp.json()["cost"]["proposed"] == 5000.0

    # Save version
    resp = await client.post(f"/yards/{yard_id}/proposals/{proposal_id}/versions")
    assert resp.status_code == 201
    assert resp.json()["version_number"] == 1

    # Transition to accepted
    resp = await client.patch(
        f"/yards/{yard_id}/proposals/{proposal_id}/state",
        json={"state": "accepted"},
    )
    assert resp.status_code == 200
    assert resp.json()["state"] == "accepted"

    # Cannot update when accepted
    resp = await client.put(
        f"/yards/{yard_id}/proposals/{proposal_id}",
        json={"name": "Should fail"},
    )
    assert resp.status_code == 400

    # Transition to implemented
    resp = await client.patch(
        f"/yards/{yard_id}/proposals/{proposal_id}/state",
        json={"state": "implemented"},
    )
    assert resp.status_code == 200
    assert resp.json()["state"] == "implemented"

    # Cannot transition from implemented
    resp = await client.patch(
        f"/yards/{yard_id}/proposals/{proposal_id}/state",
        json={"state": "draft"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_proposal_render(client):
    # Create yard with an area
    resp = await client.post(
        "/yards/",
        json={
            "name": "Render Yard",
            "boundary": BOUNDARY_50x50,
        },
    )
    yard_id = resp.json()["id"]

    # Add an area to the yard
    resp = await client.post(
        f"/yards/{yard_id}/areas",
        json={
            "name": "Lawn",
            "type": "lawn",
            "shape": [{"x": 0, "y": 0}, {"x": 50, "y": 0}, {"x": 50, "y": 50}],
        },
    )
    area_id = resp.json()["id"]

    # Create proposal (captures current yard with the area as baseline)
    resp = await client.post(
        f"/yards/{yard_id}/proposals/",
        json={"name": "Remove lawn"},
    )
    proposal_id = resp.json()["id"]

    # Add change to remove the area
    resp = await client.put(
        f"/yards/{yard_id}/proposals/{proposal_id}",
        json={
            "changes": [
                {"action": "remove", "target_type": "area", "target_id": area_id}
            ]
        },
    )
    assert resp.status_code == 200

    # Render shows the area removed
    resp = await client.get(f"/yards/{yard_id}/proposals/{proposal_id}/render")
    assert resp.status_code == 200
    rendered = resp.json()
    assert len(rendered["areas"]) == 0

    # Diff shows the change
    resp = await client.get(f"/yards/{yard_id}/proposals/{proposal_id}/diff")
    assert resp.status_code == 200
    diff = resp.json()
    assert diff["changes_count"] == 1


# --- Error cases ---


@pytest.mark.asyncio
async def test_404_on_missing_yard(client):
    resp = await client.get("/yards/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_404_on_missing_area(client):
    resp = await client.post(
        "/yards/",
        json={
            "name": "Y",
            "boundary": [{"x": 0, "y": 0}, {"x": 10, "y": 0}, {"x": 10, "y": 10}],
        },
    )
    yard_id = resp.json()["id"]
    resp = await client.get(f"/yards/{yard_id}/areas/nope")
    assert resp.status_code == 404
