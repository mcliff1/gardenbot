"""AI / Ollama integration routes."""

from typing import Optional

import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from gardenbot.config import settings

router = APIRouter()


class AIQuery(BaseModel):
    """Request body for AI queries."""

    message: str
    context: Optional[str] = None


@router.get("/status")
async def ai_status():
    """Check connectivity to the Ollama server."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models = [m["name"] for m in data.get("models", [])]
                return {"connected": True, "models": models}
    except (httpx.ConnectError, httpx.TimeoutException):
        pass
    return {"connected": False, "models": []}


@router.post("/query")
async def ai_query(body: AIQuery):
    """Query the AI for suggestions, critique, schedule, or natural language answers."""
    try:
        prompt = body.message
        if body.context:
            prompt = f"Context about the garden:\n{body.context}\n\nUser question: {body.message}"

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{settings.ollama_base_url}/api/generate",
                json={
                    "model": settings.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                return {"response": data.get("response", "")}
            else:
                return {"error": f"Ollama returned status {resp.status_code}"}
    except httpx.ConnectError:
        return {"error": f"Cannot connect to Ollama at {settings.ollama_base_url}"}
    except httpx.TimeoutException:
        return {"error": "AI request timed out"}
