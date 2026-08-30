from fastapi.testclient import TestClient

from api.main import app
from res_works.models import AnalysisRun
from res_works.repository import ProjectRepository


def test_health_endpoint() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_validation_returns_project_classification_and_conservative_scope(tmp_path) -> None:
    import api.main as module
    module.WORKSPACE = tmp_path
    source = b'{"envelope":{"x":0,"y":0,"width":20,"depth":20},"rooms":[],"walls":[],"openings":[],"stairs":[],"porches":[]}'
    client = TestClient(app)
    upload = client.post("/projects/test/files", files={"file": ("plan.json", source, "application/json")})
    response = client.post(f"/projects/test/validation?snapshot_id={upload.json()['id']}&profile_id=benton-bentonville-overlay&project_type=remodel")
    assert response.status_code == 200
    payload = response.json()
    assert payload["classification"]["project_type"] == "remodel"
    assert payload["scope"]["overlay_status"] == "pending"
    assert payload["scope"]["verified_for_approval"] is False


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


def test_source_endpoint_serves_uploaded_pdf(tmp_path) -> None:
    import api.main as module
    module.WORKSPACE = tmp_path
    client = TestClient(app)
    upload = client.post("/projects/test/files", files={"file": ("plan.pdf", b"%PDF-1.4", "application/pdf")})
    snapshot_id = upload.json()["id"]
    response = client.get(f"/projects/test/snapshots/{snapshot_id}/source")
    assert response.status_code == 200
    assert response.content == b"%PDF-1.4"


def test_dwg_analysis_reports_conversion_boundary(tmp_path) -> None:
    import api.main as module
    module.WORKSPACE = tmp_path
    client = TestClient(app)
    upload = client.post("/projects/test/files", files={"file": ("plan.dwg", b"dwg", "application/octet-stream")})
    response = client.post(f"/projects/test/runs?snapshot_id={upload.json()['id']}")
    assert response.json()["result"]["unsupported"] is True


def test_plan_json_analysis_returns_geometry_results(tmp_path) -> None:
    import api.main as module
    module.WORKSPACE = tmp_path
    client = TestClient(app)
    plan = {"envelope": {"x": 0, "y": 0, "width": 20, "depth": 20}, "rooms": [], "walls": [], "openings": [], "stairs": [], "porches": []}
    upload = client.post("/projects/test/files", files={"file": ("plan.json", __import__('json').dumps(plan), "application/json")})
    response = client.post(f"/projects/test/runs?snapshot_id={upload.json()['id']}")
    assert response.status_code == 200
    assert response.json()["result"]["fact_count"] >= 1
    assert response.json()["result"]["geometry_errors"] == []


def test_analysis_run_get_includes_persisted_result(tmp_path) -> None:
    import api.main as module
    module.WORKSPACE = tmp_path
    client = TestClient(app)
    upload = client.post("/projects/test/files", files={"file": ("plan.json", b'{"envelope":{"x":0,"y":0,"width":20,"depth":20},"rooms":[],"walls":[],"openings":[],"stairs":[],"porches":[]}', "application/json")})
    run = client.post(f"/projects/test/runs?snapshot_id={upload.json()['id']}").json()
    response = client.get(f"/projects/test/runs/{run['id']}")
    assert response.status_code == 200
    assert response.json()["result"]["fact_count"] >= 1


def test_analysis_runs_can_be_listed_for_reopening_project(tmp_path) -> None:
    import api.main as module
    module.WORKSPACE = tmp_path
    client = TestClient(app)
    upload = client.post("/projects/test/files", files={"file": ("plan.json", b'{"envelope":{"x":0,"y":0,"width":20,"depth":20},"rooms":[],"walls":[],"openings":[],"stairs":[],"porches":[]}', "application/json")})
    client.post(f"/projects/test/runs?snapshot_id={upload.json()['id']}")
    response = client.get("/projects/test/runs")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_recommendation_decision_is_saved_by_api(tmp_path) -> None:
    import api.main as module
    module.WORKSPACE = tmp_path
    client = TestClient(app)
    payload = {"recommendation_id": "rec-1", "decision": "approve", "decided_by": "designer"}
    response = client.post("/projects/test/recommendations/rec-1/decision", json=payload)
    assert response.status_code == 200
    assert response.json()["decision"] == "approve"
    second = client.post("/projects/test/recommendations/rec-1/decision", json={"recommendation_id": "rec-1", "decision": "defer", "decided_by": "designer"})
    assert second.status_code == 200
    history = client.get("/projects/test/recommendations/rec-1/history")
    assert [item["decision"] for item in history.json()] == ["approve", "defer"]


def test_handoff_download_and_checkpoint_are_approval_gated(tmp_path) -> None:
    import api.main as module
    module.WORKSPACE = tmp_path
    repository = ProjectRepository(tmp_path / "res-works.sqlite3")
    repository.save_analysis_run(AnalysisRun(id="run-1", project_id="test", source_snapshot_ids=["snap-1"], status="completed", result={"recommendations": [{"id": "rec-1", "project_id": "test", "documentation_item_id": "note-1", "reason": "observed", "title": "Note", "proposed_text": "Use the approved note", "status": "proposed"}]}))
    repository.close()
    client = TestClient(app)
    decision = client.post("/projects/test/recommendations/rec-1/decision", json={"recommendation_id": "rec-1", "decision": "approve", "decided_by": "designer"})
    assert decision.status_code == 200
    handoff = client.get("/projects/test/runs/run-1/handoff")
    assert handoff.status_code == 200
    assert "rec-1" in handoff.text
    checkpoint = client.post("/projects/test/runs/run-1/checkpoints")
    assert checkpoint.status_code == 200
    recovered = client.post(f"/projects/test/checkpoints/{checkpoint.json()['id']}/recover")
    assert recovered.json()["status"] == "recovered"
