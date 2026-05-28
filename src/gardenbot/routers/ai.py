"""AI / Ollama integration routes."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/query")
async def ai_query():
    """Query the AI for suggestions, critique, schedule, or natural language answers."""
    return {"message": "not implemented"}
