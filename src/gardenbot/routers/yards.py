"""Yard-related API routes."""

import uuid

from fastapi import APIRouter, HTTPException

from gardenbot.models.schemas import (
    AreaCreate,
    AreaUpdate,
    PlantingCreate,
    PlantingUpdate,
    StructureCreate,
    StructureUpdate,
    YardCreate,
    YardUpdate,
)
from gardenbot.models.yard import Area, Planting, Structure, Yard
from gardenbot.services import storage

router = APIRouter()


@router.get("/")
async def list_yards():
    """List all yards."""
    return [y.model_dump() for y in storage.list_yards()]


@router.post("/", status_code=201)
async def create_yard(body: YardCreate):
    """Create a new yard."""
    yard = Yard(
        id=str(uuid.uuid4()),
        name=body.name,
        boundary=body.boundary,
        orientation=body.orientation,
        origin_description=body.origin_description,
    )
    storage.save_yard(yard)
    return yard.model_dump()


@router.get("/{yard_id}")
async def get_yard(yard_id: str):
    """Get a specific yard."""
    yard = storage.get_yard(yard_id)
    if not yard:
        raise HTTPException(status_code=404, detail="Yard not found")
    return yard.model_dump()


@router.put("/{yard_id}")
async def update_yard(yard_id: str, body: YardUpdate):
    """Update a yard."""
    yard = storage.get_yard(yard_id)
    if not yard:
        raise HTTPException(status_code=404, detail="Yard not found")
    if body.name is not None:
        yard.name = body.name
    if body.boundary is not None:
        yard.boundary = body.boundary
    if body.orientation is not None:
        yard.orientation = body.orientation
    if body.origin_description is not None:
        yard.origin_description = body.origin_description
    storage.save_yard(yard)
    return yard.model_dump()


@router.delete("/{yard_id}")
async def delete_yard(yard_id: str):
    """Delete a yard."""
    if not storage.delete_yard(yard_id):
        raise HTTPException(status_code=404, detail="Yard not found")
    return {"deleted": yard_id}


# --- Areas ---


def _get_yard_or_404(yard_id: str) -> Yard:
    yard = storage.get_yard(yard_id)
    if not yard:
        raise HTTPException(status_code=404, detail="Yard not found")
    return yard


@router.get("/{yard_id}/areas")
async def list_areas(yard_id: str):
    """List areas in a yard."""
    yard = _get_yard_or_404(yard_id)
    return [a.model_dump() for a in yard.areas]


@router.post("/{yard_id}/areas", status_code=201)
async def create_area(yard_id: str, body: AreaCreate):
    """Create an area in a yard."""
    yard = _get_yard_or_404(yard_id)
    area = Area(
        id=str(uuid.uuid4()),
        name=body.name,
        type=body.type,
        shape=body.shape,
        sun_exposure=body.sun_exposure,
        notes=body.notes,
    )
    yard.areas.append(area)
    storage.save_yard(yard)
    return area.model_dump()


@router.get("/{yard_id}/areas/{area_id}")
async def get_area(yard_id: str, area_id: str):
    """Get a specific area."""
    yard = _get_yard_or_404(yard_id)
    for area in yard.areas:
        if area.id == area_id:
            return area.model_dump()
    raise HTTPException(status_code=404, detail="Area not found")


@router.put("/{yard_id}/areas/{area_id}")
async def update_area(yard_id: str, area_id: str, body: AreaUpdate):
    """Update an area."""
    yard = _get_yard_or_404(yard_id)
    for area in yard.areas:
        if area.id == area_id:
            if body.name is not None:
                area.name = body.name
            if body.type is not None:
                area.type = body.type
            if body.shape is not None:
                area.shape = body.shape
            if body.sun_exposure is not None:
                area.sun_exposure = body.sun_exposure
            if body.notes is not None:
                area.notes = body.notes
            storage.save_yard(yard)
            return area.model_dump()
    raise HTTPException(status_code=404, detail="Area not found")


@router.delete("/{yard_id}/areas/{area_id}")
async def delete_area(yard_id: str, area_id: str):
    """Delete an area."""
    yard = _get_yard_or_404(yard_id)
    for i, area in enumerate(yard.areas):
        if area.id == area_id:
            yard.areas.pop(i)
            storage.save_yard(yard)
            return {"deleted": area_id}
    raise HTTPException(status_code=404, detail="Area not found")


# --- Structures ---


@router.get("/{yard_id}/structures")
async def list_structures(yard_id: str):
    """List structures in a yard."""
    yard = _get_yard_or_404(yard_id)
    return [s.model_dump() for s in yard.structures]


@router.post("/{yard_id}/structures", status_code=201)
async def create_structure(yard_id: str, body: StructureCreate):
    """Create a structure in a yard."""
    yard = _get_yard_or_404(yard_id)
    structure = Structure(
        id=str(uuid.uuid4()),
        name=body.name,
        type=body.type,
        footprint=body.footprint,
        notes=body.notes,
    )
    yard.structures.append(structure)
    storage.save_yard(yard)
    return structure.model_dump()


@router.get("/{yard_id}/structures/{structure_id}")
async def get_structure(yard_id: str, structure_id: str):
    """Get a specific structure."""
    yard = _get_yard_or_404(yard_id)
    for s in yard.structures:
        if s.id == structure_id:
            return s.model_dump()
    raise HTTPException(status_code=404, detail="Structure not found")


@router.put("/{yard_id}/structures/{structure_id}")
async def update_structure(yard_id: str, structure_id: str, body: StructureUpdate):
    """Update a structure."""
    yard = _get_yard_or_404(yard_id)
    for s in yard.structures:
        if s.id == structure_id:
            if body.name is not None:
                s.name = body.name
            if body.type is not None:
                s.type = body.type
            if body.footprint is not None:
                s.footprint = body.footprint
            if body.notes is not None:
                s.notes = body.notes
            storage.save_yard(yard)
            return s.model_dump()
    raise HTTPException(status_code=404, detail="Structure not found")


@router.delete("/{yard_id}/structures/{structure_id}")
async def delete_structure(yard_id: str, structure_id: str):
    """Delete a structure."""
    yard = _get_yard_or_404(yard_id)
    for i, s in enumerate(yard.structures):
        if s.id == structure_id:
            yard.structures.pop(i)
            storage.save_yard(yard)
            return {"deleted": structure_id}
    raise HTTPException(status_code=404, detail="Structure not found")


# --- Plantings ---


def _get_area_or_404(yard: Yard, area_id: str) -> Area:
    for area in yard.areas:
        if area.id == area_id:
            return area
    raise HTTPException(status_code=404, detail="Area not found")


@router.get("/{yard_id}/areas/{area_id}/plantings")
async def list_plantings(yard_id: str, area_id: str):
    """List plantings in an area."""
    yard = _get_yard_or_404(yard_id)
    area = _get_area_or_404(yard, area_id)
    return [p.model_dump() for p in area.plantings]


@router.post("/{yard_id}/areas/{area_id}/plantings", status_code=201)
async def create_planting(yard_id: str, area_id: str, body: PlantingCreate):
    """Create a planting in an area."""
    yard = _get_yard_or_404(yard_id)
    area = _get_area_or_404(yard, area_id)
    planting = Planting(
        id=str(uuid.uuid4()),
        plant_id=body.plant_id,
        position=body.position,
        quantity=body.quantity,
        notes=body.notes,
    )
    area.plantings.append(planting)
    storage.save_yard(yard)
    return planting.model_dump()


@router.get("/{yard_id}/areas/{area_id}/plantings/{planting_id}")
async def get_planting(yard_id: str, area_id: str, planting_id: str):
    """Get a specific planting."""
    yard = _get_yard_or_404(yard_id)
    area = _get_area_or_404(yard, area_id)
    for p in area.plantings:
        if p.id == planting_id:
            return p.model_dump()
    raise HTTPException(status_code=404, detail="Planting not found")


@router.put("/{yard_id}/areas/{area_id}/plantings/{planting_id}")
async def update_planting(yard_id: str, area_id: str, planting_id: str, body: PlantingUpdate):
    """Update a planting."""
    yard = _get_yard_or_404(yard_id)
    area = _get_area_or_404(yard, area_id)
    for p in area.plantings:
        if p.id == planting_id:
            if body.plant_id is not None:
                p.plant_id = body.plant_id
            if body.position is not None:
                p.position = body.position
            if body.quantity is not None:
                p.quantity = body.quantity
            if body.notes is not None:
                p.notes = body.notes
            storage.save_yard(yard)
            return p.model_dump()
    raise HTTPException(status_code=404, detail="Planting not found")


@router.delete("/{yard_id}/areas/{area_id}/plantings/{planting_id}")
async def delete_planting(yard_id: str, area_id: str, planting_id: str):
    """Delete a planting."""
    yard = _get_yard_or_404(yard_id)
    area = _get_area_or_404(yard, area_id)
    for i, p in enumerate(area.plantings):
        if p.id == planting_id:
            area.plantings.pop(i)
            storage.save_yard(yard)
            return {"deleted": planting_id}
    raise HTTPException(status_code=404, detail="Planting not found")
