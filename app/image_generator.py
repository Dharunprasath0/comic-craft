"""Cloudflare Workers AI image generation for ComicCraft comic panels."""

import base64
import re
import uuid

import requests

from app.config import (
    CLOUDFLARE_ACCOUNT_ID,
    CLOUDFLARE_API_TOKEN,
    CLOUDFLARE_IMAGE_MODEL,
    CLOUDFLARE_IMAGE_STEPS,
    PANELS_DIR,
)


def sanitize_filename(prompt: str) -> str:
    """Turn a free-form prompt into a safe, unique JPEG filename."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", prompt.strip().lower())[:40].strip("_")
    return f"{slug or 'panel'}_{uuid.uuid4().hex[:8]}.jpg"


def _cloudflare_url() -> str:
    if not CLOUDFLARE_ACCOUNT_ID:
        raise RuntimeError(
            "CLOUDFLARE_ACCOUNT_ID is not set. Add it in Render Environment variables."
        )
    if not CLOUDFLARE_API_TOKEN:
        raise RuntimeError(
            "CLOUDFLARE_API_TOKEN is not set. Add it in Render Environment variables."
        )
    return (
        "https://api.cloudflare.com/client/v4/accounts/"
        f"{CLOUDFLARE_ACCOUNT_ID}/ai/run/{CLOUDFLARE_IMAGE_MODEL}"
    )


def generate_image(prompt: str, filename: str | None = None) -> str:
    """
    Generate one comic panel using Cloudflare Workers AI FLUX.1 Schnell.

    The generated image is saved under static/panels so the existing preview
    and PDF-export pipeline can continue to work unchanged.
    """
    filename = filename or sanitize_filename(prompt)
    output_path = PANELS_DIR / filename

    comic_prompt = (
        "Single polished comic-panel illustration, strong visual storytelling, "
        "clear composition, consistent character design, no captions, no speech "
        "bubbles, no watermark, no UI text. Scene: "
        f"{prompt}"
    )

    payload = {
        "prompt": comic_prompt[:2048],
        "steps": max(1, min(CLOUDFLARE_IMAGE_STEPS, 8)),
    }

    try:
        response = requests.post(
            _cloudflare_url(),
            headers={
                "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=120,
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"Cloudflare image request failed: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(
            f"Cloudflare returned an invalid response (HTTP {response.status_code})."
        ) from exc

    if not response.ok or not data.get("success", False):
        errors = data.get("errors") or []
        message = "; ".join(
            str(item.get("message", item)) if isinstance(item, dict) else str(item)
            for item in errors
        ) or data.get("message") or response.text[:500]

        if response.status_code == 429:
            raise RuntimeError(
                "Cloudflare Workers AI free-tier rate/quota limit was reached. "
                "Wait for the daily quota reset and try again."
            )
        raise RuntimeError(
            f"Cloudflare image generation failed (HTTP {response.status_code}): {message}"
        )

    image_b64 = (data.get("result") or {}).get("image")
    if not image_b64:
        raise RuntimeError("Cloudflare image generation returned no image data.")

    try:
        image_bytes = base64.b64decode(image_b64)
    except Exception as exc:
        raise RuntimeError("Cloudflare returned invalid image data.") from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(image_bytes)
    return f"static/panels/{filename}"
