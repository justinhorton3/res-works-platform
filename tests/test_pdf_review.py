from pathlib import Path

import pytest
from pypdf import PdfWriter

from res_works.ingest import ingest_artifact
from res_works.pdf_review import inventory_pdf


def test_pdf_inventory_links_each_page_to_snapshot(tmp_path: Path) -> None:
    source = tmp_path / "sweeter-build.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with source.open("wb") as stream:
        writer.write(stream)

    snapshot = ingest_artifact(source, "sweeter-build", tmp_path / "files")
    pages = inventory_pdf(source, snapshot)

    assert len(pages) == 1
    assert pages[0].snapshot_id == snapshot.id
    assert pages[0].page_number == 1
    assert pages[0].has_text is False


def test_pdf_inventory_rejects_changed_source(tmp_path: Path) -> None:
    source = tmp_path / "plan.pdf"
    source.write_bytes(b"original")
    snapshot = ingest_artifact(source, "sweeter-build", tmp_path / "files")
    source.write_bytes(b"changed")

    with pytest.raises(ValueError, match="snapshot hash"):
        inventory_pdf(source, snapshot)
