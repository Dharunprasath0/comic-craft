"""HTTP routes and the end-to-end ComicCraft generation pipeline."""

import traceback

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.config import BASE_DIR
from app.exporters import save_pdf
from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class PromptRequest(BaseModel):
    """JSON body accepted by /generate-comic/json."""

    prompt: str = Field(..., min_length=1, max_length=1500, description="Main story idea.")
    character_name: str = Field("Hero", max_length=100)
    setting: str = Field("forest", max_length=100)
    tone: str = Field("dramatic", max_length=100)
    style: str = Field("anime", max_length=100)


def _build_full_prompt(prompt: str, character_name: str, setting: str, tone: str, style: str) -> str:
    return (
        f"{prompt}\n"
        f"The main character is {character_name}. "
        f"The setting is {setting}. "
        f"The tone is {tone}. The art style is {style}."
    )


def _run_comic_pipeline(full_prompt: str) -> dict:
    """Run outline -> story -> 5 hosted images -> layout -> PDF."""
    outline = generate_outline(full_prompt)

    if outline and isinstance(outline, list) and isinstance(outline[0], dict) and "error" in outline[0]:
        raise RuntimeError(outline[0]["error"])

    if not isinstance(outline, list) or len(outline) != 5 or not all(
        isinstance(panel, dict)
        and all(key in panel for key in ("panel", "title", "scene_description", "image_prompt"))
        for panel in outline
    ):
        raise ValueError("Gemini returned an invalid comic outline. Please try again.")

    full_story = generate_story(outline)
    if not full_story or full_story.startswith("Error generating story:"):
        raise RuntimeError(full_story or "Gemini returned an empty story.")

    images = [generate_image(panel["image_prompt"]) for panel in outline]
    layout = build_comic_layout(images, full_story, outline)

    if len(layout) != 5:
        raise ValueError("The generated story could not be split into all 5 comic panels. Please try again.")

    pdf_path = save_pdf(layout)
    return {"layout": layout, "pdf_path": "/" + pdf_path.replace("\\", "/")}


@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@router.post("/generate", response_class=HTMLResponse)
async def generate_comic(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    style: str = Form(...),
):
    try:
        if not prompt.strip():
            raise ValueError("Story prompt cannot be empty.")
        if len(prompt) > 1500:
            raise ValueError("Story prompt is too long. Keep it under 1500 characters.")

        result = _run_comic_pipeline(
            _build_full_prompt(prompt, character_name, setting, tone, style)
        )
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={"layout": result["layout"], "pdf_path": result["pdf_path"]},
        )
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/generate-comic/json")
async def generate_comic_json(payload: PromptRequest):
    try:
        result = _run_comic_pipeline(
            _build_full_prompt(
                payload.prompt,
                payload.character_name,
                payload.setting,
                payload.tone,
                payload.style,
            )
        )
        return JSONResponse(result)
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, pdf_path: str = ""):
    return templates.TemplateResponse(
        request=request, name="export_success.html", context={"pdf_path": pdf_path}
    )
