"""ComicCraft FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import STATIC_DIR
from app.routes import router

app = FastAPI(
    title="ComicCraft",
    description="AI Comic Story Creator using Gemini text and image models.",
    version="2.0.0",
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/health", include_in_schema=False)
def health():
    """Lightweight endpoint used by Render health checks."""
    return {"status": "ok"}


app.include_router(router)
