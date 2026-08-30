from fastapi.testclient import TestClient

from api.main import app


def test_health_endpoint() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analysis_run_endpoint_returns_completed_review_state(tmp_path, monkeypatch) -> None:
    import api.main as module
    module.WORKSPACE = tmp_path
    response = TestClient(app).post("/projects/test/runs?snapshot_id=abc123")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
