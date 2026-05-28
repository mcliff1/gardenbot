"""Pydantic schemas for API request/response bodies."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from gardenbot.models.yard import (
    AreaType,
    ChangeAction,
    ChangeTargetType,
    Coordinate,
    Polygon,
    ProposalState,
    StructureType,
    SunExposure,
)

# --- Yard ---


class YardCreate(BaseModel):
    name: str
    boundary: Polygon
    orientation: Optional[float] = None
    origin_description: str = ""


class YardUpdate(BaseModel):
    name: Optional[str] = None
    boundary: Optional[Polygon] = None
    orientation: Optional[float] = None
    origin_description: Optional[str] = None


# --- Area ---


class AreaCreate(BaseModel):
    name: str
    type: AreaType
    shape: Polygon
    sun_exposure: Optional[SunExposure] = None
    notes: str = ""


class AreaUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[AreaType] = None
    shape: Optional[Polygon] = None
    sun_exposure: Optional[SunExposure] = None
    notes: Optional[str] = None


# --- Structure ---


class StructureCreate(BaseModel):
    name: str
    type: StructureType
    footprint: Polygon
    notes: str = ""


class StructureUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[StructureType] = None
    footprint: Optional[Polygon] = None
    notes: Optional[str] = None


# --- Planting ---


class PlantingCreate(BaseModel):
    plant_id: str
    position: Coordinate
    quantity: int = 1
    date_planted: Optional[str] = None
    notes: str = ""


class PlantingUpdate(BaseModel):
    plant_id: Optional[str] = None
    position: Optional[Coordinate] = None
    quantity: Optional[int] = None
    date_planted: Optional[str] = None
    notes: Optional[str] = None


# --- Plant ---


class PlantCreate(BaseModel):
    common_name: str
    botanical_name: str = ""
    perennial: bool = True
    bloom_time: str = ""
    mature_size_ft: Optional[float] = None
    color: str = ""
    companion_plants: list[str] = []
    care_notes: str = ""


# --- Proposal ---


class ChangeInput(BaseModel):
    action: ChangeAction
    target_type: ChangeTargetType
    target_id: Optional[str] = None
    after: Optional[dict] = None
    notes: str = ""


class ProposalCreate(BaseModel):
    name: str
    description: str = ""


class ProposalUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    changes: Optional[list[ChangeInput]] = None
    cost_proposed: Optional[float] = None
    metadata: Optional[dict] = None


class StateTransition(BaseModel):
    state: ProposalState
