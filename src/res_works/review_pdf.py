"""Create immutable-source review PDF revisions with a consolidated appendix."""

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen.canvas import Canvas

from .models import ReviewAnnotation


def build_review_pdf(source: str | Path, destination: str | Path, annotations: list[ReviewAnnotation]) -> Path:
    reader = PdfReader(source)
    writer = PdfWriter()
    grouped: dict[int, list[ReviewAnnotation]] = {}
    for annotation in annotations:
        grouped.setdefault(annotation.page_number, []).append(annotation)
    for page_number, page in enumerate(reader.pages, start=1):
        if page_number in grouped:
            overlay = BytesIO()
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)
            canvas = Canvas(overlay, pagesize=(width, height))
            for annotation in grouped[page_number]:
                x = (annotation.x or 0) / 100 * width
                y = height - (annotation.y or 0) / 100 * height
                canvas.setFillColorRGB(0.85, 0.05, 0.05)
                canvas.setStrokeColorRGB(0.85, 0.05, 0.05)
                if annotation.annotation_type == "rectangle":
                    canvas.rect(x, y - 24, (annotation.width or 12) / 100 * width, (annotation.height or 8) / 100 * height, fill=0)
                elif annotation.annotation_type == "arrow":
                    canvas.line(x - 36, y + 36, x, y)
                    canvas.line(x, y, x - 8, y + 2)
                    canvas.line(x, y, x - 2, y + 8)
                else:
                    canvas.circle(x, y, 8, fill=0)
                canvas.setFont("Helvetica", 9)
                canvas.drawString(x + 10, y + 3, annotation.note[:120])
            canvas.save()
            overlay.seek(0)
            page.merge_page(PdfReader(overlay).pages[0])
        writer.add_page(page)
    appendix = BytesIO()
    canvas = Canvas(appendix, pagesize=(612, 792))
    canvas.setFont("Helvetica-Bold", 16)
    canvas.drawString(48, 744, "RES Works - Consolidated Review Notes")
    canvas.setFont("Helvetica", 10)
    y = 716
    for index, annotation in enumerate(annotations, start=1):
        if y < 60:
            canvas.showPage()
            y = 744
        canvas.drawString(48, y, f"{index}. Page {annotation.page_number} - {annotation.note[:105]}")
        y -= 18
    canvas.save()
    writer.add_page(PdfReader(appendix).pages[0])
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as stream:
        writer.write(stream)
    return target
