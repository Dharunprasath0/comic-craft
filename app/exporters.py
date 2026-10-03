"""Compile a finished comic layout into a downloadable PDF."""

from datetime import datetime
from pathlib import Path
import uuid

from fpdf import FPDF
from PIL import Image

from app.config import BASE_DIR, EXPORTS_DIR, FONT_PATH


def _to_latin1(text: str) -> str:
    """Fallback encoding for when a Unicode-capable font is unavailable."""
    return text.encode("latin-1", "replace").decode("latin-1")


def _disk_path(path_value: str) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else BASE_DIR / path


def save_pdf(layout: list) -> str:
    """Create one PDF page per comic panel and return its web-relative path."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    use_unicode_font = FONT_PATH.exists()
    if use_unicode_font:
        pdf.add_font("DejaVu", "", str(FONT_PATH))
        font_name = "DejaVu"
    else:
        font_name = "Helvetica"

    for panel in layout:
        image_path = _disk_path(panel["image_path"])
        story_text = panel["text"]
        title_text = f"Panel {panel['panel']}: {panel.get('title', '')}"

        if not use_unicode_font:
            story_text = _to_latin1(story_text)
            title_text = _to_latin1(title_text)

        pdf.add_page()
        pdf.set_font(font_name, "", 14)
        pdf.cell(0, 10, title_text, new_x="LMARGIN", new_y="NEXT", align="C")

        y_image = 30
        max_width = pdf.w - 20
        max_height = 105
        rendered_height = max_height

        if image_path.exists():
            try:
                with Image.open(image_path) as img:
                    width_px, height_px = img.size
                scale = min(max_width / width_px, max_height / height_px)
                image_width = width_px * scale
                image_height = height_px * scale
                x_image = (pdf.w - image_width) / 2
                pdf.image(
                    str(image_path),
                    x=x_image,
                    y=y_image,
                    w=image_width,
                    h=image_height,
                )
                rendered_height = image_height
            except Exception:
                pdf.set_y(y_image)
                pdf.set_font(font_name, "", 11)
                pdf.multi_cell(0, 8, f"Image could not be rendered: {image_path.name}")
        else:
            pdf.set_y(y_image)
            pdf.set_font(font_name, "", 11)
            pdf.multi_cell(0, 8, f"Image missing: {image_path.name}")

        pdf.set_y(y_image + rendered_height + 10)
        pdf.set_font(font_name, "", 11)
        pdf.multi_cell(0, 7, story_text)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comic_{timestamp}_{uuid.uuid4().hex[:8]}.pdf"
    pdf_path = EXPORTS_DIR / filename
    pdf.output(str(pdf_path))

    return f"static/exports/{filename}"
