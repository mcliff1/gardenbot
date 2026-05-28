"""Gardenbot FastAPI application."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from gardenbot.routers import ai, plants, proposals, web, yards

app = FastAPI(
    title="Gardenbot",
    description="AI-assisted landscaping and garden planning",
    version="0.1.0",
)

# Static files — resolve relative to project root
_project_root = Path(__file__).resolve().parent.parent.parent
_static_dir = _project_root / "static"
if _static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")

# Register API routers
app.include_router(yards.router, prefix="/yards", tags=["yards"])
app.include_router(plants.router, prefix="/plants", tags=["plants"])
app.include_router(proposals.router, prefix="/yards/{yard_id}/proposals", tags=["proposals"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])

# Register web UI router
app.include_router(web.router, prefix="/ui", tags=["web"])


@app.get("/")
async def root():
    """Redirect to web UI dashboard."""
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/ui/")


def cli():
    """Entry point for the gardenbot CLI."""
    import uvicorn

    uvicorn.run("gardenbot.main:app", host="0.0.0.0", port=8000, reload=True)

