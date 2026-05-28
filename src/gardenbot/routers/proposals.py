"""Proposal API routes."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_proposals(yard_id: str):
    """List all proposals for a yard."""
    return []


@router.post("/")
async def create_proposal(yard_id: str):
    """Create a new proposal (auto-captures baseline snapshot)."""
    return {"message": "not implemented"}


@router.get("/{proposal_id}")
async def get_proposal(yard_id: str, proposal_id: str):
    """Get a specific proposal."""
    return {"id": proposal_id}


@router.put("/{proposal_id}")
async def update_proposal(yard_id: str, proposal_id: str):
    """Update proposal changes (draft state only)."""
    return {"id": proposal_id}


@router.patch("/{proposal_id}/state")
async def transition_state(yard_id: str, proposal_id: str):
    """Transition proposal state (draft → accepted → implemented)."""
    return {"message": "not implemented"}


@router.get("/{proposal_id}/versions")
async def list_versions(yard_id: str, proposal_id: str):
    """List saved draft versions."""
    return []


@router.post("/{proposal_id}/versions")
async def save_version(yard_id: str, proposal_id: str):
    """Save current draft as a version."""
    return {"message": "not implemented"}


@router.get("/{proposal_id}/render")
async def render_proposal(yard_id: str, proposal_id: str):
    """Render the 'after' view (baseline + changes applied)."""
    return {"message": "not implemented"}


@router.get("/{proposal_id}/diff")
async def diff_proposal(yard_id: str, proposal_id: str):
    """Get visual diff (before vs. after)."""
    return {"message": "not implemented"}
