"""Central configuration for ComicCraft."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Gemini is used only for text generation (outline + narration).
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_FLASH_MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-3.5-flash-lite").strip()
GEMINI_PRO_MODEL = os.getenv("GEMINI_PRO_MODEL", "gemini-3.5-flash-lite").strip()

# Cloudflare Workers AI is used for free-tier image generation.
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
CLOUDFLARE_IMAGE_MODEL = os.getenv(
    "CLOUDFLARE_IMAGE_MODEL", "@cf/black-forest-labs/flux-1-schnell"
).strip()
CLOUDFLARE_IMAGE_STEPS = int(os.getenv("CLOUDFLARE_IMAGE_STEPS", "4"))

STATIC_DIR = BASE_DIR / "static"
PANELS_DIR = STATIC_DIR / "panels"
EXPORTS_DIR = STATIC_DIR / "exports"
FONTS_DIR = STATIC_DIR / "fonts"
FONT_PATH = FONTS_DIR / "DejaVuSans.ttf"

for _dir in (STATIC_DIR, PANELS_DIR, EXPORTS_DIR, FONTS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)
