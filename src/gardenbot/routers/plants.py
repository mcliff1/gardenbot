"""Plant database API routes."""

import uuid

from fastapi import APIRouter, HTTPException

from gardenbot.models.schemas import PlantCreate
from gardenbot.models.yard import Plant
from gardenbot.services import storage

router = APIRouter()


@router.get("/")
async def list_plants():
    """List all plants in the database."""
    return [p.model_dump() for p in storage.list_plants()]


@router.get("/search")
async def search_plants(q: str = ""):
    """Search plants by name or attribute."""
    if not q:
        return [p.model_dump() for p in storage.list_plants()]
    return [p.model_dump() for p in storage.search_plants(q)]


@router.post("/", status_code=201)
async def create_plant(body: PlantCreate):
    """Add a custom plant entry."""
    plant = Plant(
        id=str(uuid.uuid4()),
        common_name=body.common_name,
        botanical_name=body.botanical_name,
        perennial=body.perennial,
        bloom_time=body.bloom_time,
        mature_size_ft=body.mature_size_ft,
        color=body.color,
        companion_plants=body.companion_plants,
        care_notes=body.care_notes,
    )
    storage.save_plant(plant)
    return plant.model_dump()


@router.get("/{plant_id}")
async def get_plant(plant_id: str):
    """Get a specific plant."""
    plant = storage.get_plant(plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant.model_dump()
