"""Central configuration for ComicCraft."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Required secret. On Render, set this in Environment variables.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Current stable defaults (October 2026). All are overridable in Render/.env.
GEMINI_FLASH_MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-3.8-flash").strip()
GEMINI_PRO_MODEL = os.getenv("GEMINI_PRO_MODEL", "gemini-3.8-flash").strip()
GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image").strip()

STATIC_DIR = BASE_DIR / "static"
PANELS_DIR = STATIC_DIR / "panels"
EXPORTS_DIR = STATIC_DIR / "exports"
FONTS_DIR = STATIC_DIR / "fonts"
FONT_PATH = FONTS_DIR / "DejaVuSans.ttf"

for _dir in (STATIC_DIR, PANELS_DIR, EXPORTS_DIR, FONTS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)
