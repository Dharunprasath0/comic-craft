"""
Gemini Flash integration: turns a user's story idea into a structured,
5-panel comic outline.
"""

import json

from google import genai

from app.config import GEMINI_API_KEY, GEMINI_FLASH_MODEL

_client = None


def _get_client() -> genai.Client:
    """Lazily creates a single shared Gemini client for this process."""
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to your .env file "
                "(see .env.example)."
            )
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def generate_outline(user_prompt: str) -> list:
    """
    Generates a 5-panel comic layout based on the user's story idea using Gemini.

    Args:
        user_prompt (str): The user's comic idea prompt.

    Returns:
        list: A list of dictionaries, one for each panel, each containing
              "panel", "title", "scene_description", and "image_prompt".
              On failure, returns a single-item list with an "error" key
              instead of raising, so callers can surface it cleanly.
    """
    prompt = f"""
You are a professional AI comic planner.

Your task is to generate a *strictly formatted* JSON array containing 5 panel descriptions for a comic based on the story idea below:

STORY: "{user_prompt}"

Each JSON object must include:
- "panel" (integer)
- "title" (string)
- "scene_description" (string)
- "image_prompt" (string)

Respond ONLY in this valid JSON format, without any explanations or markdown:
[
  {{
    "panel": 1,
    "title": "Title here",
    "scene_description": "Scene description here",
    "image_prompt": "Detailed visual prompt for an AI image generator"
  }},
  ...
]
"""

    output_text = ""
    try:
        client = _get_client()
        response = client.models.generate_content(
            model=GEMINI_FLASH_MODEL,
            contents=prompt,
        )
        output_text = response.text.strip()

        print("\n🔵 RAW GEMINI RESPONSE 🔵\n", output_text)

        # Remove any markdown code-fence formatting if present
        if output_text.startswith("```json"):
            output_text = output_text.replace("```json", "").replace("```", "").strip()
        elif output_text.startswith("```"):
            output_text = output_text.replace("```", "").strip()

        panel_data = json.loads(output_text)

        # Additional structure validation
        if not isinstance(panel_data, list):
            raise ValueError("Gemini response is not a list.")

        for panel in panel_data:
            if not isinstance(panel, dict) or not all(
                key in panel for key in ("panel", "title", "scene_description", "image_prompt")
            ):
                raise ValueError(f"Invalid panel format or missing keys: {panel}")

        return panel_data

    except json.JSONDecodeError as e:
        print("❌ JSON Decode Error:", e)
        print("❌ Full Text Received:\n", output_text)
        return [{"error": f"JSON parsing failed: {str(e)}"}]

    except Exception as e:
        print("❌ Unexpected Error:", e)
        return [{"error": f"Generation failed: {str(e)}"}]
