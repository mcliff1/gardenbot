"""Plant database API routes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_plants():
    """List all plants in the database."""
    return []


@router.get("/search")
async def search_plants(q: str = ""):
    """Search plants by name or attribute."""
    return []


@router.post("/")
async def create_plant():
    """Add a custom plant entry."""
    return {"message": "not implemented"}


@router.get("/{plant_id}")
async def get_plant(plant_id: str):
    """Get a specific plant."""
    return {"id": plant_id}
