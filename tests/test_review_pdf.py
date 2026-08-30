from pathlib import Path

from pypdf import PdfReader, PdfWriter

from res_works.models import ReviewAnnotation
from res_works.review_pdf import build_review_pdf


def test_review_pdf_preserves_source_and_appends_notes_page(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with source.open("wb") as stream:
        writer.write(stream)
    output = tmp_path / "review.pdf"
    annotation = ReviewAnnotation(id="a1", run_id="run-1", snapshot_id="pdf-1", page_number=1, note="Verify stair callout", x=25, y=30)

    build_review_pdf(source, output, [annotation])

    assert len(PdfReader(source).pages) == 1
    reviewed = PdfReader(output)
    assert len(reviewed.pages) == 2
    assert "Verify stair callout" in "\n".join(page.extract_text() or "" for page in reviewed.pages)
