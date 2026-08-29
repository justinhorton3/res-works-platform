"""Local PDF page rendering for visual review evidence."""

import hashlib
from pathlib import Path

import pypdfium2 as pdfium

from .models import SourceSnapshot


def render_pdf_pages(
    path: str | Path, snapshot: SourceSnapshot, destination: str | Path, scale: float = 1.5
) -> list[Path]:
    pdf_path = Path(path)
    if not pdf_path.is_file():
        raise FileNotFoundError(pdf_path)
    if hashlib.sha256(pdf_path.read_bytes()).hexdigest() != snapshot.sha256:
        raise ValueError("PDF does not match the source snapshot hash")
    target_dir = Path(destination) / snapshot.id
    target_dir.mkdir(parents=True, exist_ok=True)
    document = pdfium.PdfDocument(str(pdf_path))
    rendered: list[Path] = []
    for index in range(len(document)):
        page = document[index]
        bitmap = page.render(scale=scale)
        output = target_dir / f"page-{index + 1:03d}.png"
        bitmap.to_pil().save(output, format="PNG")
        rendered.append(output)
    return rendered
