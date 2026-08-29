"""Local RES Works HTTP service."""

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from res_works.ingest import ingest_artifact
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
