"""Core data models for Gardenbot."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

# --- Coordinate system ---


class Coordinate(BaseModel):
    """A point in feet from the user-defined origin."""

    x: float
    y: float


Polygon = list[Coordinate]


# --- Enums ---


class SunExposure(str, Enum):
    full_sun = "full_sun"
    partial_sun = "partial_sun"
    shade = "shade"


class AreaType(str, Enum):
    flower_bed = "flower_bed"
    shrub_bed = "shrub_bed"
    tree_area = "tree_area"
    garden = "garden"
    lawn = "lawn"
    rock_gravel = "rock_gravel"
    patio = "patio"
    walkway = "walkway"
    driveway = "driveway"
    water_feature = "water_feature"
    utility = "utility"
    other = "other"


class StructureType(str, Enum):
    house = "house"
    shed = "shed"
    fence = "fence"
    pergola = "pergola"
    trellis = "trellis"
    retaining_wall = "retaining_wall"
    utility_box = "utility_box"
    other = "other"


class ProposalState(str, Enum):
    draft = "draft"
    accepted = "accepted"
    implemented = "implemented"


class ChangeAction(str, Enum):
    add = "add"
    remove = "remove"
    modify = "modify"
    move = "move"


class ChangeTargetType(str, Enum):
    area = "area"
    structure = "structure"
    planting = "planting"


# --- Core models ---


class Planting(BaseModel):
    """A plant placed within an area."""

    id: str
    plant_id: str
    position: Coordinate
    quantity: int = 1
    date_planted: Optional[date] = None
    notes: str = ""


class Area(BaseModel):
    """A ground-level zone in the yard."""

    id: str
    name: str
    type: AreaType
    shape: Polygon
    sun_exposure: Optional[SunExposure] = None
    notes: str = ""
    plantings: list[Planting] = Field(default_factory=list)


class Structure(BaseModel):
    """A vertical built object in the yard."""

    id: str
    name: str
    type: StructureType
    footprint: Polygon
    notes: str = ""


class Yard(BaseModel):
    """Top-level yard document."""

    id: str
    name: str
    boundary: Polygon
    orientation: Optional[float] = None  # compass bearing in degrees
    origin_description: str = ""
    areas: list[Area] = Field(default_factory=list)
    structures: list[Structure] = Field(default_factory=list)


# --- Plant database ---


class Plant(BaseModel):
    """A plant entry in the database."""

    id: str
    common_name: str
    botanical_name: str = ""
    perennial: bool = True  # True=perennial, False=annual
    bloom_time: str = ""  # e.g. "early spring", "mid-summer"
    mature_size_ft: Optional[float] = None  # diameter at maturity in feet
    color: str = ""
    companion_plants: list[str] = Field(default_factory=list)
    care_notes: str = ""


# --- Proposal models ---


class Change(BaseModel):
    """A single change operation within a proposal."""

    id: str
    action: ChangeAction
    target_type: ChangeTargetType
    target_id: Optional[str] = None  # null for 'add'
    before: Optional[dict] = None  # snapshot before change
    after: Optional[dict] = None  # desired state after change
    notes: str = ""


class ProposalVersion(BaseModel):
    """A saved draft version of a proposal."""

    version_number: int
    saved_at: datetime
    changes: list[Change] = Field(default_factory=list)
    cost_proposed: Optional[float] = None
    label: str = ""


class ProposalCost(BaseModel):
    """Cost tracking for a proposal."""

    proposed: Optional[float] = None
    actual: Optional[float] = None
    notes: str = ""


class Proposal(BaseModel):
    """A planned set of changes to the yard layout."""

    id: str
    name: str
    description: str = ""
    state: ProposalState = ProposalState.draft
    created_at: datetime
    updated_at: datetime
    baseline_snapshot: Yard  # frozen yard state at proposal creation
    changes: list[Change] = Field(default_factory=list)
    versions: list[ProposalVersion] = Field(default_factory=list)
    cost: ProposalCost = Field(default_factory=ProposalCost)
    metadata: dict = Field(default_factory=dict)
