"""Gardenbot FastAPI application."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from gardenbot.routers import ai, plants, proposals, yards

app = FastAPI(
    title="Gardenbot",
    description="AI-assisted landscaping and garden planning",
    version="0.1.0",
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Register routers
app.include_router(yards.router, prefix="/yards", tags=["yards"])
app.include_router(plants.router, prefix="/plants", tags=["plants"])
app.include_router(proposals.router, prefix="/yards/{yard_id}/proposals", tags=["proposals"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])


@app.get("/")
async def root():
    """Health check / landing page."""
    return {"status": "ok", "app": "gardenbot", "version": "0.1.0"}


def cli():
    """Entry point for the gardenbot CLI."""
    import uvicorn

    uvicorn.run("gardenbot.main:app", host="0.0.0.0", port=8000, reload=True)
