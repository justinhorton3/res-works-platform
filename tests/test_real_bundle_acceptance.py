import json
import zipfile
from pathlib import Path

import ezdxf
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from api.main import app


def test_real_bundle_analyzes_caproj_pdf_and_dxf_together(tmp_path: Path) -> None:
    import api.main as module

    module.WORKSPACE = tmp_path
    client = TestClient(app)
    dxf = tmp_path / "plan.dxf"
    drawing = ezdxf.new("R2018")
    drawing.modelspace().add_line((0, 0), (20, 0), dxfattribs={"layer": "Walls-1"})
    drawing.modelspace().add_text("Kitchen", dxfattribs={"layer": "Room Labels-1"})
    drawing.saveas(dxf)
    pdf = tmp_path / "review.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with pdf.open("wb") as stream:
        writer.write(stream)
    caproj = tmp_path / "project.caproj"
    with zipfile.ZipFile(caproj, "w") as archive:
        archive.writestr("manifest.json", json.dumps({"manifest_version": "1", "resources": [], "exported_files": []}))
        archive.writestr("Projects/Project.plan", b"plan")
        archive.writestr("Projects/Project.layout", b"layout")

    uploads = []
    for path, media_type in [(dxf, "application/dxf"), (pdf, "application/pdf"), (caproj, "application/octet-stream")]:
        response = client.post("/projects/lot27/files", files={"file": (path.name, path.read_bytes(), media_type)})
        assert response.status_code == 200
        uploads.append(response.json()["id"])

    result = client.post(f"/projects/lot27/runs?snapshot_id={uploads[-1]}")
    assert result.status_code == 200
    payload = result.json()["result"]
    assert len(payload["evidence_bundle"]) == 3
    assert payload["bundle_analysis"]["pdf"][0]["pages"] == 1
    assert payload["bundle_analysis"]["pdf"][0]["page_references"] == [{"page_number": 1, "snapshot_id": uploads[1], "locator": "page 1"}]
    assert payload["bundle_analysis"]["pdf"][0]["page_previews"] == [{"page_number": 1, "url": f"/projects/lot27/snapshots/{uploads[1]}/pages/1/preview"}]
    assert payload["bundle_analysis"]["geometry"][0]["evidence_summary"]["entity_count"] == 2
    assert payload["native_files"]["plan"]
    assert payload["native_files"]["layout"]
    assert payload["evidence_coverage"]["geometry"]["status"] == "available"
    assert payload["evidence_coverage"]["geometry"]["optional_sources"] == []
    assert payload["evidence_coverage"]["visual"]["status"] == "available"
