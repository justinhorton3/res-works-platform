"""Local RES Works HTTP service."""

import json
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from res_works.ingest import ingest_artifact
from res_works.models import AnalysisRun, ApprovalDecision, DocumentationItem, FactKind, ObservedFact
from res_works.caproj import caproj_contents_report, extract_native_files, inventory_caproj
from res_works.dxf import inventory_dxf
from res_works.dxf_extract import extract_architectural_entities
from res_works.fact_mapping import facts_from_geometry
from res_works.plan_fixture import load_plan_geometry
from res_works.recommendations import recommend_documentation
from res_works.reports import build_validation_report
from res_works.rule_catalog import load_requirements
from res_works.pdf_review import inventory_pdf
from res_works.repository import ProjectRepository

WORKSPACE = Path("/data")
PROJECT_ID = "sweeter-build"


def recommendations_for_facts(project_id: str, facts: list[ObservedFact]) -> list[dict[str, object]]:
    library = [DocumentationItem.model_validate(item) for item in json.loads(Path("reference/documentation-library.json").read_text())]
    return [item.model_dump(mode="json") for item in recommend_documentation(project_id, library, facts)]

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


@app.post("/projects/{project_id}/recommendations/{recommendation_id}/decision")
def save_recommendation_decision(project_id: str, recommendation_id: str, decision: ApprovalDecision) -> ApprovalDecision:
    if decision.recommendation_id != recommendation_id:
        raise HTTPException(status_code=400, detail="Recommendation ID does not match path")
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    repository.save_approval_decision(decision)
    repository.close()
    return decision


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
    elif source.suffix.lower() == ".caproj":
        inventory = inventory_caproj(source)
        extracted = extract_native_files(source, WORKSPACE / "extracted" / project_id / snapshot.id)
        facts = [ObservedFact(id="fact-chief-package", key="chief.package", value=True, kind=FactKind.OBSERVED, source_ref=snapshot.id, confidence="high")]
        result = {"message": "Chief package inventoried; additional exports required for analysis", "pages": 0, "inventory": inventory.model_dump(mode="json"), "native_files": extracted, "contents_report": caproj_contents_report(inventory), "fact_count": 0, "recommendations": recommendations_for_facts(project_id, facts)}
    elif source.suffix.lower() == ".dxf":
        inventory = inventory_dxf(source)
        entities = extract_architectural_entities(source)
        facts = [ObservedFact(id="fact-cad-dxf", key="cad.dxf", value=True, kind=FactKind.OBSERVED, source_ref=snapshot.id, confidence="high")]
        result = {"message": "DXF geometry evidence extracted for review", "pages": 0, "inventory": inventory.model_dump(mode="json"), "architectural_entity_count": len(entities), "fact_count": len(facts), "recommendations": recommendations_for_facts(project_id, facts)}
    elif source.suffix.lower() == ".dwg":
        result = {"message": "DWG stored; conversion to DXF is required before analysis", "pages": 0, "unsupported": True}
    elif source.suffix.lower() == ".json":
        try:
            plan = load_plan_geometry(source)
            facts = facts_from_geometry(plan, project_id)
            requirements = load_requirements(Path("reference/arkansas-baseline-requirements.json"))
            report = build_validation_report(project_id, "arkansas-baseline", requirements, facts, plan)
            recommendations = recommendations_for_facts(project_id, facts)
            result = {"message": "Plan geometry validated for review", "pages": 0, "fact_count": len(facts), "geometry_errors": report.geometry_errors, "validation": report.model_dump(mode="json"), "recommendations": recommendations}
        except (ValueError, OSError, json.JSONDecodeError) as error:
            result = {"message": f"Plan JSON could not be analyzed: {error}", "pages": 0, "unsupported": True}
    run = AnalysisRun(id=f"run-{snapshot_id[:16]}", project_id=project_id, source_snapshot_ids=[snapshot_id], status="completed", result=result)
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


@app.get("/projects/{project_id}/runs")
def list_analyses(project_id: str) -> list[AnalysisRun]:
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    runs = repository.list_analysis_runs(project_id)
    repository.close()
    return runs
