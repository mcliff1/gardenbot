"""Yard-related API routes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_yards():
    """List all yards."""
    return []


@router.post("/")
async def create_yard():
    """Create a new yard."""
    return {"message": "not implemented"}


@router.get("/{yard_id}")
async def get_yard(yard_id: str):
    """Get a specific yard."""
    return {"id": yard_id}


@router.put("/{yard_id}")
async def update_yard(yard_id: str):
    """Update a yard."""
    return {"id": yard_id}


@router.delete("/{yard_id}")
async def delete_yard(yard_id: str):
    """Delete a yard."""
    return {"deleted": yard_id}


# --- Areas ---


@router.get("/{yard_id}/areas")
async def list_areas(yard_id: str):
    """List areas in a yard."""
    return []


@router.post("/{yard_id}/areas")
async def create_area(yard_id: str):
    """Create an area in a yard."""
    return {"message": "not implemented"}


@router.get("/{yard_id}/areas/{area_id}")
async def get_area(yard_id: str, area_id: str):
    """Get a specific area."""
    return {"id": area_id}


@router.put("/{yard_id}/areas/{area_id}")
async def update_area(yard_id: str, area_id: str):
    """Update an area."""
    return {"id": area_id}


@router.delete("/{yard_id}/areas/{area_id}")
async def delete_area(yard_id: str, area_id: str):
    """Delete an area."""
    return {"deleted": area_id}


# --- Structures ---


@router.get("/{yard_id}/structures")
async def list_structures(yard_id: str):
    """List structures in a yard."""
    return []


@router.post("/{yard_id}/structures")
async def create_structure(yard_id: str):
    """Create a structure in a yard."""
    return {"message": "not implemented"}


@router.get("/{yard_id}/structures/{structure_id}")
async def get_structure(yard_id: str, structure_id: str):
    """Get a specific structure."""
    return {"id": structure_id}


@router.put("/{yard_id}/structures/{structure_id}")
async def update_structure(yard_id: str, structure_id: str):
    """Update a structure."""
    return {"id": structure_id}


@router.delete("/{yard_id}/structures/{structure_id}")
async def delete_structure(yard_id: str, structure_id: str):
    """Delete a structure."""
    return {"deleted": structure_id}
