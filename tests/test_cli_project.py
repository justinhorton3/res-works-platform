import json
import subprocess
import sys
from pathlib import Path

from pypdf import PdfWriter


def test_review_project_command_combines_pdf_and_validation(tmp_path: Path) -> None:
    source = tmp_path / "sweeter-build.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with source.open("wb") as stream:
        writer.write(stream)

    result = subprocess.run(
        [sys.executable, "-m", "res_works.cli", "review-project", str(source),
         "--project-id", "sweeter-build", "--workspace", str(tmp_path / "workspace"),
         "--requirements", "reference/arkansas-baseline-requirements.json",
         "--facts", "projects/sweeter-build/observed-facts.json"],
        check=True, capture_output=True, text=True,
    )
    report = json.loads(result.stdout)
    assert report["pages"] == 1
    assert report["fact_count"] == 7
    assert report["counts"]["not_verified"] == 3
    assert report["counts"].get("pass", 0) == 0
    assert report["recommendation_count"] == 1
    assert report["recommendations"][0]["documentation_item_id"] == "callout-egress-review"
