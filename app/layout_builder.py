"""
Combines the generated images and the full comic story text into a single,
ordered list of panel dictionaries ready for the preview page and the PDF
exporter.
"""


def build_comic_layout(image_paths: list, full_story: str, outline: list) -> list:
    """
    Organizes the generated images and full comic story into a structured layout.

    Args:
        image_paths (list): List of image file paths, one per panel, in
                             the same order as `outline`.
        full_story (str): The complete generated comic story text, formatted
                           as one "**Panel N: Title**" block per panel (see
                           gemini_pro.generate_story).
        outline (list): The panel outline data from generate_outline().

    Returns:
        list: A list of dictionaries, one per panel, each containing
              "panel", "title", "image_path", "text" (caption/narration/
              image-prompt lines), and "scene_description".
    """
    # Split the full story into individual panel segments
    story_panels = full_story.split("**Panel")
    story_panels = [f"**Panel{panel}" for panel in story_panels if panel.strip()]

    # Build layout panel by panel
    layout = []
    for idx, (image, text, panel_info) in enumerate(
        zip(image_paths, story_panels, outline), start=1
    ):
        layout.append({
            "panel": idx,
            "title": panel_info.get("title", f"Panel {idx}"),
            "image_path": image,
            # Remove the "**Panel N: Title**" header line, keep the rest.
            "text": "\n".join(text.strip().splitlines()[1:]).strip(),
            "scene_description": panel_info.get("scene_description", ""),
        })

    return layout
