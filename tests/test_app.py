"""Offline smoke tests. External Gemini calls are replaced with instant fakes."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

import app.routes as routes
from app.config import PANELS_DIR
from app.main import app

FAKE_OUTLINE = [
    {
        "panel": i,
        "title": f"Panel {i} Title",
        "scene_description": f"Scene description for panel {i}.",
        "image_prompt": f"A test illustration prompt for panel {i}.",
    }
    for i in range(1, 6)
]

FAKE_STORY = "\n\n".join(
    f"**Panel {i}: Panel {i} Title**\n"
    f"**CAPTION:** Ambient caption {i}.\n"
    f"**NARRATION:** Something happens in panel {i}.\n"
    f"**IMAGE PROMPT:** A test illustration prompt for panel {i}."
    for i in range(1, 6)
)


@pytest.fixture(autouse=True)
def patch_ai_calls(monkeypatch):
    monkeypatch.setattr(routes, "generate_outline", lambda prompt: FAKE_OUTLINE)
    monkeypatch.setattr(routes, "generate_story", lambda outline: FAKE_STORY)

    def fake_generate_image(prompt, filename=None):
        path = PANELS_DIR / "test_panel.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (64, 64), color=(120, 160, 200)).save(path)
        return "static/panels/test_panel.png"

    monkeypatch.setattr(routes, "generate_image", fake_generate_image)
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_homepage_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Create Your Comic" in response.text


def test_generate_comic_via_form(client):
    response = client.post(
        "/generate",
        data={
            "prompt": "A brave fox explores an enchanted forest.",
            "character_name": "Free",
            "setting": "forest",
            "tone": "dramatic",
            "style": "realistic",
        },
    )
    assert response.status_code == 200
    assert "Your Comic Preview" in response.text
    assert "Panel 1" in response.text
    assert "Panel 5" in response.text


def test_generate_comic_via_json(client):
    response = client.post(
        "/generate-comic/json",
        json={
            "prompt": "A brave fox explores an enchanted forest.",
            "character_name": "Free",
            "setting": "forest",
            "tone": "dramatic",
            "style": "realistic",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["layout"]) == 5
    assert data["layout"][0]["title"] == "Panel 1 Title"
    assert data["pdf_path"].startswith("/static/exports/")
    assert Path(data["pdf_path"].lstrip("/")).exists()


def test_json_route_uses_defaults_when_optional_fields_omitted(client):
    response = client.post("/generate-comic/json", json={"prompt": "A robot learns to paint."})
    assert response.status_code == 200
    assert len(response.json()["layout"]) == 5


def test_export_success_page(client):
    response = client.get("/export-success", params={"pdf_path": "/static/exports/example.pdf"})
    assert response.status_code == 200
    assert "Comic Exported Successfully" in response.text
