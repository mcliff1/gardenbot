"""Web UI routes serving Jinja2 HTML pages."""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from gardenbot.config import settings

router = APIRouter()

_templates_dir = Path(__file__).resolve().parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(_templates_dir))


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render the dashboard page."""
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "active_page": "dashboard"},
    )


@router.get("/yards", response_class=HTMLResponse)
async def yards_page(request: Request):
    """Render the yards management page."""
    return templates.TemplateResponse(
        "yards.html",
        {"request": request, "active_page": "yards"},
    )


@router.get("/plants", response_class=HTMLResponse)
async def plants_page(request: Request):
    """Render the plants database page."""
    return templates.TemplateResponse(
        "plants.html",
        {"request": request, "active_page": "plants"},
    )


@router.get("/ai", response_class=HTMLResponse)
async def ai_page(request: Request):
    """Render the AI assistant page."""
    return templates.TemplateResponse(
        "ai.html",
        {
            "request": request,
            "active_page": "ai",
            "ollama_model": settings.ollama_model,
            "ollama_url": settings.ollama_base_url,
        },
    )
