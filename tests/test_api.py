from fastapi.testclient import TestClient

from api.main import app


def test_health_endpoint() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analysis_run_endpoint_returns_completed_review_state(tmp_path) -> None:
    import api.main as module
    module.WORKSPACE = tmp_path
    upload = TestClient(app).post("/projects/test/files", files={"file": ("plan.json", b"{}", "application/json")})
    response = TestClient(app).post(f"/projects/test/runs?snapshot_id={upload.json()['id']}")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_pdf_analysis_indexes_pages(tmp_path, monkeypatch) -> None:
    from pypdf import PdfWriter
    import api.main as module
    module.WORKSPACE = tmp_path
    source = tmp_path / "incoming" / "test" / "plan.pdf"
    source.parent.mkdir(parents=True)
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with source.open("wb") as stream:
        writer.write(stream)
    upload = TestClient(app).post("/projects/test/files", files={"file": ("plan.pdf", source.read_bytes(), "application/pdf")})
    snapshot_id = upload.json()["id"]
    response = TestClient(app).post(f"/projects/test/runs?snapshot_id={snapshot_id}")
    assert response.status_code == 200
    assert response.json()["result"]["pages"] == 1
