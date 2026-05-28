"""Proposal API routes."""

import uuid
from copy import deepcopy
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from gardenbot.models.schemas import ChangeInput, ProposalCreate, ProposalUpdate, StateTransition
from gardenbot.models.yard import Change, Proposal, ProposalCost, ProposalState, ProposalVersion
from gardenbot.services import storage

router = APIRouter()


def _get_yard_or_404(yard_id: str):
    yard = storage.get_yard(yard_id)
    if not yard:
        raise HTTPException(status_code=404, detail="Yard not found")
    return yard


def _get_proposal_or_404(yard_id: str, proposal_id: str) -> Proposal:
    proposal = storage.get_proposal(yard_id, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal


def _build_change(inp: ChangeInput, yard) -> Change:
    """Build a Change model from input, auto-capturing 'before' from baseline."""
    before = None
    if inp.target_id and inp.action in ("modify", "remove", "move"):
        # Look up the target in the yard to capture before state
        if inp.target_type.value == "area":
            for a in yard.areas:
                if a.id == inp.target_id:
                    before = a.model_dump()
                    break
        elif inp.target_type.value == "structure":
            for s in yard.structures:
                if s.id == inp.target_id:
                    before = s.model_dump()
                    break
        elif inp.target_type.value == "planting":
            for a in yard.areas:
                for p in a.plantings:
                    if p.id == inp.target_id:
                        before = p.model_dump()
                        break
    return Change(
        id=str(uuid.uuid4()),
        action=inp.action,
        target_type=inp.target_type,
        target_id=inp.target_id,
        before=before,
        after=inp.after,
        notes=inp.notes,
    )


@router.get("/")
async def list_proposals(yard_id: str):
    """List all proposals for a yard."""
    _get_yard_or_404(yard_id)
    return [p.model_dump() for p in storage.list_proposals(yard_id)]


@router.post("/", status_code=201)
async def create_proposal(yard_id: str, body: ProposalCreate):
    """Create a new proposal (auto-captures baseline snapshot)."""
    yard = _get_yard_or_404(yard_id)
    now = datetime.now(timezone.utc)
    proposal = Proposal(
        id=str(uuid.uuid4()),
        name=body.name,
        description=body.description,
        state=ProposalState.draft,
        created_at=now,
        updated_at=now,
        baseline_snapshot=deepcopy(yard),
        cost=ProposalCost(),
    )
    storage.save_proposal(yard_id, proposal)
    return proposal.model_dump()


@router.get("/{proposal_id}")
async def get_proposal(yard_id: str, proposal_id: str):
    """Get a specific proposal."""
    _get_yard_or_404(yard_id)
    proposal = _get_proposal_or_404(yard_id, proposal_id)
    return proposal.model_dump()


@router.put("/{proposal_id}")
async def update_proposal(yard_id: str, proposal_id: str, body: ProposalUpdate):
    """Update proposal changes (draft state only)."""
    _get_yard_or_404(yard_id)
    proposal = _get_proposal_or_404(yard_id, proposal_id)
    if proposal.state != ProposalState.draft:
        raise HTTPException(status_code=400, detail="Can only update proposals in draft state")
    if body.name is not None:
        proposal.name = body.name
    if body.description is not None:
        proposal.description = body.description
    if body.changes is not None:
        proposal.changes = [_build_change(c, proposal.baseline_snapshot) for c in body.changes]
    if body.cost_proposed is not None:
        proposal.cost.proposed = body.cost_proposed
    if body.metadata is not None:
        proposal.metadata = body.metadata
    proposal.updated_at = datetime.now(timezone.utc)
    storage.save_proposal(yard_id, proposal)
    return proposal.model_dump()


@router.patch("/{proposal_id}/state")
async def transition_state(yard_id: str, proposal_id: str, body: StateTransition):
    """Transition proposal state (draft → accepted → implemented)."""
    _get_yard_or_404(yard_id)
    proposal = _get_proposal_or_404(yard_id, proposal_id)

    valid_transitions = {
        ProposalState.draft: {ProposalState.accepted},
        ProposalState.accepted: {ProposalState.draft, ProposalState.implemented},
        ProposalState.implemented: set(),
    }

    if body.state not in valid_transitions.get(proposal.state, set()):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {proposal.state.value} to {body.state.value}",
        )

    proposal.state = body.state
    proposal.updated_at = datetime.now(timezone.utc)
    storage.save_proposal(yard_id, proposal)
    return proposal.model_dump()


@router.get("/{proposal_id}/versions")
async def list_versions(yard_id: str, proposal_id: str):
    """List saved draft versions."""
    _get_yard_or_404(yard_id)
    proposal = _get_proposal_or_404(yard_id, proposal_id)
    return [v.model_dump() for v in proposal.versions]


@router.post("/{proposal_id}/versions", status_code=201)
async def save_version(yard_id: str, proposal_id: str):
    """Save current draft as a version."""
    _get_yard_or_404(yard_id)
    proposal = _get_proposal_or_404(yard_id, proposal_id)
    if proposal.state != ProposalState.draft:
        raise HTTPException(status_code=400, detail="Can only save versions in draft state")

    version_number = len(proposal.versions) + 1
    version = ProposalVersion(
        version_number=version_number,
        saved_at=datetime.now(timezone.utc),
        changes=deepcopy(proposal.changes),
        cost_proposed=proposal.cost.proposed,
        label=f"v{version_number}",
    )
    proposal.versions.append(version)
    proposal.updated_at = datetime.now(timezone.utc)
    storage.save_proposal(yard_id, proposal)
    return version.model_dump()


@router.get("/{proposal_id}/render")
async def render_proposal(yard_id: str, proposal_id: str):
    """Render the 'after' view (baseline + changes applied)."""
    _get_yard_or_404(yard_id)
    proposal = _get_proposal_or_404(yard_id, proposal_id)

    # Start with the baseline snapshot and apply changes
    result = deepcopy(proposal.baseline_snapshot)

    for change in proposal.changes:
        if change.action == "add" and change.after:
            if change.target_type.value == "area":
                result.areas.append(
                    type(result.areas[0]).model_validate(change.after)
                    if result.areas
                    else change.after
                )
            elif change.target_type.value == "structure":
                result.structures.append(
                    type(result.structures[0]).model_validate(change.after)
                    if result.structures
                    else change.after
                )
        elif change.action == "remove" and change.target_id:
            if change.target_type.value == "area":
                result.areas = [a for a in result.areas if a.id != change.target_id]
            elif change.target_type.value == "structure":
                result.structures = [s for s in result.structures if s.id != change.target_id]
        elif change.action in ("modify", "move") and change.target_id and change.after:
            if change.target_type.value == "area":
                for i, a in enumerate(result.areas):
                    if a.id == change.target_id:
                        for k, v in change.after.items():
                            setattr(result.areas[i], k, v)
                        break
            elif change.target_type.value == "structure":
                for i, s in enumerate(result.structures):
                    if s.id == change.target_id:
                        for k, v in change.after.items():
                            setattr(result.structures[i], k, v)
                        break

    return result.model_dump()


@router.get("/{proposal_id}/diff")
async def diff_proposal(yard_id: str, proposal_id: str):
    """Get diff (before vs. after summary)."""
    _get_yard_or_404(yard_id)
    proposal = _get_proposal_or_404(yard_id, proposal_id)
    return {
        "proposal_id": proposal.id,
        "state": proposal.state.value,
        "changes_count": len(proposal.changes),
        "changes": [
            {
                "action": c.action.value,
                "target_type": c.target_type.value,
                "target_id": c.target_id,
                "before": c.before,
                "after": c.after,
            }
            for c in proposal.changes
        ],
    }
