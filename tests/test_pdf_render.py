from pathlib import Path

from pypdf import PdfWriter

from res_works.ingest import ingest_artifact
from res_works.pdf_render import render_pdf_pages


def test_render_pdf_pages_creates_stable_preview_paths(tmp_path: Path) -> None:
    source = tmp_path / "sweeter-build.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.add_blank_page(width=612, height=792)
    with source.open("wb") as stream:
        writer.write(stream)

    snapshot = ingest_artifact(source, "sweeter-build", tmp_path / "files")
    pages = render_pdf_pages(source, snapshot, tmp_path / "previews", scale=0.5)

    assert [page.name for page in pages] == ["page-001.png", "page-002.png"]
    assert all(page.is_file() and page.stat().st_size > 0 for page in pages)
