"""JSON file-based persistence layer for Gardenbot."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Optional

from gardenbot.models.yard import Plant, Proposal, Yard

DATA_DIR = Path(os.environ.get("GARDENBOT_DATA_DIR", "./data"))

YARDS_DIR = DATA_DIR / "yards"
PLANTS_FILE = DATA_DIR / "plants.json"

# Pattern for valid IDs: UUID format or simple alphanumeric with hyphens
_SAFE_ID_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


def _validate_id(value: str) -> str:
    """Validate that an ID is safe for use in file paths."""
    if not value or not _SAFE_ID_RE.match(value):
        raise ValueError(f"Invalid ID: {value!r}")
    return value


def _ensure_dirs() -> None:
    """Create data directories if they don't exist."""
    YARDS_DIR.mkdir(parents=True, exist_ok=True)


def _yard_file(yard_id: str) -> Path:
    _validate_id(yard_id)
    return YARDS_DIR / f"{yard_id}.json"


def _proposals_dir(yard_id: str) -> Path:
    _validate_id(yard_id)
    return YARDS_DIR / yard_id / "proposals"


# --- Yard CRUD ---


def list_yards() -> list[Yard]:
    """List all yards."""
    _ensure_dirs()
    yards: list[Yard] = []
    for path in YARDS_DIR.glob("*.json"):
        yards.append(Yard.model_validate_json(path.read_text()))
    return yards


def get_yard(yard_id: str) -> Optional[Yard]:
    """Get a yard by ID."""
    path = _yard_file(yard_id)
    if not path.exists():
        return None
    return Yard.model_validate_json(path.read_text())


def save_yard(yard: Yard) -> Yard:
    """Create or update a yard."""
    _ensure_dirs()
    path = _yard_file(yard.id)
    path.write_text(yard.model_dump_json(indent=2))
    return yard


def delete_yard(yard_id: str) -> bool:
    """Delete a yard and its proposals. Returns True if it existed."""
    path = _yard_file(yard_id)
    if not path.exists():
        return False
    path.unlink()
    # Remove proposals directory if it exists
    proposals_dir = _proposals_dir(yard_id)
    if proposals_dir.exists():
        for p in proposals_dir.glob("*.json"):
            p.unlink()
        proposals_dir.rmdir()
    yard_dir = YARDS_DIR / yard_id
    if yard_dir.exists():
        yard_dir.rmdir()
    return True


# --- Plant CRUD ---


def _load_plants() -> list[Plant]:
    """Load plants from the plants file."""
    if not PLANTS_FILE.exists():
        return []
    data = json.loads(PLANTS_FILE.read_text())
    return [Plant.model_validate(p) for p in data]


def _save_plants(plants: list[Plant]) -> None:
    """Save plants to the plants file."""
    _ensure_dirs()
    PLANTS_FILE.write_text(json.dumps([p.model_dump() for p in plants], indent=2))


def list_plants() -> list[Plant]:
    """List all plants."""
    return _load_plants()


def get_plant(plant_id: str) -> Optional[Plant]:
    """Get a plant by ID."""
    for plant in _load_plants():
        if plant.id == plant_id:
            return plant
    return None


def save_plant(plant: Plant) -> Plant:
    """Create or update a plant."""
    plants = _load_plants()
    for i, p in enumerate(plants):
        if p.id == plant.id:
            plants[i] = plant
            _save_plants(plants)
            return plant
    plants.append(plant)
    _save_plants(plants)
    return plant


def search_plants(query: str) -> list[Plant]:
    """Search plants by common or botanical name."""
    q = query.lower()
    return [
        p for p in _load_plants() if q in p.common_name.lower() or q in p.botanical_name.lower()
    ]


# --- Proposal CRUD ---


def _ensure_proposals_dir(yard_id: str) -> Path:
    d = _proposals_dir(yard_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def list_proposals(yard_id: str) -> list[Proposal]:
    """List all proposals for a yard."""
    d = _proposals_dir(yard_id)
    if not d.exists():
        return []
    proposals: list[Proposal] = []
    for path in d.glob("*.json"):
        proposals.append(Proposal.model_validate_json(path.read_text()))
    return proposals


def get_proposal(yard_id: str, proposal_id: str) -> Optional[Proposal]:
    """Get a proposal by ID."""
    _validate_id(proposal_id)
    path = _proposals_dir(yard_id) / f"{proposal_id}.json"
    if not path.exists():
        return None
    return Proposal.model_validate_json(path.read_text())


def save_proposal(yard_id: str, proposal: Proposal) -> Proposal:
    """Create or update a proposal."""
    _validate_id(proposal.id)
    d = _ensure_proposals_dir(yard_id)
    path = d / f"{proposal.id}.json"
    path.write_text(proposal.model_dump_json(indent=2))
    return proposal


def delete_proposal(yard_id: str, proposal_id: str) -> bool:
    """Delete a proposal. Returns True if it existed."""
    _validate_id(proposal_id)
    path = _proposals_dir(yard_id) / f"{proposal_id}.json"
    if not path.exists():
        return False
    path.unlink()
    return True
