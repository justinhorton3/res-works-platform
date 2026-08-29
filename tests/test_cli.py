import json
import subprocess
import sys
from pathlib import Path

from pypdf import PdfWriter


def test_review_pdf_command_persists_report(tmp_path: Path) -> None:
    source = tmp_path / "sweeter-build.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with source.open("wb") as stream:
        writer.write(stream)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "res_works.cli",
            "review-pdf",
            str(source),
            "--project-id",
            "sweeter-build",
            "--workspace",
            str(tmp_path / "workspace"),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(result.stdout)
    assert report["project_id"] == "sweeter-build"
    assert report["pages"] == 1
    assert (tmp_path / "workspace/res-works.sqlite3").is_file()
