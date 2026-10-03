"""Gemini image generation for ComicCraft comic panels."""

import re
import uuid

from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, GEMINI_IMAGE_MODEL, PANELS_DIR

_client = None


def _get_client() -> genai.Client:
    """Create one reusable Gemini client for the server process."""
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to Render Environment "
                "variables or to a local .env file."
            )
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def sanitize_filename(prompt: str) -> str:
    """Turn a free-form prompt into a safe, unique PNG filename."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", prompt.strip().lower())[:40].strip("_")
    return f"{slug or 'panel'}_{uuid.uuid4().hex[:8]}.png"


def generate_image(prompt: str, filename: str | None = None) -> str:
    """
    Generate one comic-panel image with Gemini's hosted image model.

    The image is saved under static/panels for preview and PDF creation.
    The returned value is a web-relative path such as
    ``static/panels/example_1234abcd.png``.
    """
    filename = filename or sanitize_filename(prompt)
    output_path = PANELS_DIR / filename

    comic_prompt = (
        "Create a single polished comic-panel illustration based on this scene. "
        "Keep the composition clear and visually engaging. Do not add captions, "
        "speech bubbles, watermarks, UI elements, or written text unless the scene "
        "absolutely requires it. Scene: "
        f"{prompt}"
    )

    client = _get_client()
    response = client.models.generate_content(
        model=GEMINI_IMAGE_MODEL,
        contents=[comic_prompt],
        config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
    )

    for part in (getattr(response, "parts", None) or []):
        try:
            image = part.as_image()
        except Exception:
            image = None
        if image is not None:
            image.save(output_path)
            return f"static/panels/{filename}"

    raise RuntimeError(
        "Gemini image generation returned no image. Check the API key, model "
        "availability, quota/billing, and the prompt, then try again."
    )
