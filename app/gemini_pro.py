"""
Gemini Pro integration: expands a panel outline into full comic narration
and character dialogue.
"""

from google import genai

from app.config import GEMINI_API_KEY, GEMINI_PRO_MODEL

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


def generate_story(outline: list) -> str:
    """
    Generates a detailed comic story with narration and character dialogue
    from a list of comic panel outlines using Gemini Pro.

    Args:
        outline (list): A list of panel dictionaries from generate_outline()
                         (each with "panel", "title", "scene_description",
                         "image_prompt").

    Returns:
        str: The generated comic story text (one "**Panel N: Title**" block
             per panel, so build_comic_layout() can split it back apart), or
             an error message string.
    """
    # Format the panel outline as a numbered list for clarity
    formatted_outline = "\n".join(
        f"Panel {panel.get('panel', i + 1)}: {panel.get('title', '')}\n"
        f"  Scene: {panel.get('scene_description', '')}\n"
        f"  Visual idea: {panel.get('image_prompt', '')}"
        for i, panel in enumerate(outline)
    )

    prompt = f"""
You're a comic book writer.

Given the following panel breakdown, write a comic-style story with engaging narration and character dialogues for each panel.

Panel Outline:
{formatted_outline}

Write your response using EXACTLY this structure, repeated once per panel, with
nothing else before or after it:

**Panel <number>: <panel title>**
**CAPTION:** <a short, ambient description of the environment or background sounds>
**NARRATION:** <the main character's actions, emotions, or dialogue in this scene>
**IMAGE PROMPT:** <a vivid artistic description suitable for an AI image-generation model>

Guidelines:
- Use a fun and engaging tone, like an actual comic book.
- Include narration and clearly marked character lines.
- Keep each panel self-contained but part of a cohesive story.
- Do not repeat the scene description verbatim; focus on caption, narration, and image prompt.
"""

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=GEMINI_PRO_MODEL,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Error generating story: {str(e)}"
