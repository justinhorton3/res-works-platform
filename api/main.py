"""Local RES Works HTTP service."""

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from res_works.ingest import ingest_artifact
from res_works.models import AnalysisRun
from res_works.pdf_review import inventory_pdf
from res_works.repository import ProjectRepository

WORKSPACE = Path("/data")
PROJECT_ID = "sweeter-build"

app = FastAPI(title="RES Works API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "res-works-api"}


@app.post("/projects/{project_id}/files")
async def upload_file(project_id: str, file: UploadFile = File(...)) -> dict[str, object]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A filename is required")
    incoming = WORKSPACE / "incoming" / project_id
    incoming.mkdir(parents=True, exist_ok=True)
    target = incoming / Path(file.filename).name
    target.write_bytes(await file.read())
    snapshot = ingest_artifact(target, project_id, WORKSPACE / "snapshots")
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    repository.save_snapshot(snapshot)
    repository.close()
    return {"id": snapshot.id, "filename": snapshot.filename, "byte_size": snapshot.byte_size, "status": "stored"}


@app.post("/projects/{project_id}/runs")
def start_analysis(project_id: str, snapshot_id: str) -> dict[str, object]:
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    snapshot = repository.get_snapshot(snapshot_id)
    if snapshot is None or snapshot.project_id != project_id:
        repository.close()
        raise HTTPException(status_code=404, detail="Source snapshot not found")
    source = WORKSPACE / "incoming" / project_id / snapshot.filename
    result: dict[str, object] = {"message": "Evidence snapshot ready for review", "pages": 0, "evidence": []}
    if snapshot.media_type == "application/pdf":
        pages = inventory_pdf(source, snapshot)
        for page in pages:
            repository.save_page_evidence(page)
        result = {"message": "PDF pages indexed for review", "pages": len(pages), "evidence": [page.model_dump(mode="json") for page in pages]}
    run = AnalysisRun(id=f"run-{snapshot_id[:16]}", project_id=project_id, source_snapshot_ids=[snapshot_id], status="completed")
    repository.save_analysis_run(run)
    repository.close()
    return {"id": run.id, "status": run.status, "source_snapshot_ids": run.source_snapshot_ids, "result": result}


@app.get("/projects/{project_id}/snapshots/{snapshot_id}/source")
def get_source(project_id: str, snapshot_id: str) -> FileResponse:
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    snapshot = repository.get_snapshot(snapshot_id)
    repository.close()
    if snapshot is None or snapshot.project_id != project_id:
        raise HTTPException(status_code=404, detail="Source snapshot not found")
    source = WORKSPACE / "incoming" / project_id / snapshot.filename
    if not source.is_file():
        raise HTTPException(status_code=404, detail="Source file not found")
    return FileResponse(source, media_type=snapshot.media_type, filename=snapshot.filename)


@app.get("/projects/{project_id}/runs/{run_id}")
def get_analysis(project_id: str, run_id: str) -> AnalysisRun:
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    run = repository.get_analysis_run(run_id)
    repository.close()
    if run is None or run.project_id != project_id:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    return run
