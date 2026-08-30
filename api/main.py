"""Local RES Works HTTP service."""

import json
import shutil
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from res_works.ingest import ingest_artifact
from res_works.models import AnalysisRun, ApprovalDecision, DocumentationItem, FactKind, ObservedFact
from res_works.caproj import caproj_contents_report, extract_native_files, inventory_caproj
from res_works.dxf import inventory_dxf
from res_works.dxf_extract import extract_architectural_entities, summarize_dxf_evidence
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


def evidence_coverage(snapshots: list[object]) -> dict[str, object]:
    names = {getattr(item, "filename", "").lower() for item in snapshots}
    has_dxf = any(name.endswith(".dxf") for name in names)
    has_dwg = any(name.endswith(".dwg") for name in names)
    has_pdf = any(name.endswith(".pdf") for name in names)
    return {
        "geometry": {"status": "available" if has_dxf or has_dwg else "missing", "sources": sorted(name for name in names if name.endswith((".dxf", ".dwg")))},
        "visual": {"status": "available" if has_pdf else "missing", "sources": sorted(name for name in names if name.endswith(".pdf"))},
        "schedules": {"status": "available" if has_pdf else "missing", "sources": sorted(name for name in names if name.endswith(".pdf"))},
        "energy": {"status": "missing", "sources": []},
    }


def analyze_project_bundle(project_id: str, snapshots: list[object]) -> dict[str, object]:
    """Run the available source-specific analyzers for one project bundle."""
    geometry: list[dict[str, object]] = []
    pdfs: list[dict[str, object]] = []
    findings: list[dict[str, object]] = []
    for item in snapshots:
        source = WORKSPACE / "incoming" / project_id / item.filename
        suffix = source.suffix.lower()
        if suffix == ".dxf":
            inventory = inventory_dxf(source)
            entities = extract_architectural_entities(source)
            categories: dict[str, int] = {}
            for entity in entities:
                categories[entity.category] = categories.get(entity.category, 0) + 1
            geometry.append({"snapshot_id": item.id, "filename": item.filename, "inventory": inventory.model_dump(mode="json"), "entity_categories": dict(sorted(categories.items())), "evidence_summary": summarize_dxf_evidence(source)})
            if not inventory.dimension_count:
                findings.append({"severity": "warning", "message": "DXF contains no DIMENSION entities; dimensional verification requires review.", "source_snapshot_id": item.id, "source_filename": item.filename})
        elif suffix == ".dwg":
            geometry.append({"snapshot_id": item.id, "filename": item.filename, "status": "present_not_parsed", "evidence_summary": {"entity_count": 0, "categories": {}, "text_samples": {}}})
            findings.append({"severity": "info", "message": "DWG is present but requires conversion or supported DWG parsing before entity comparison.", "source_snapshot_id": item.id, "source_filename": item.filename})
        elif item.media_type == "application/pdf":
            pages = inventory_pdf(source, item)
            for page in pages:
                repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
                repository.save_page_evidence(page)
                repository.close()
            pdfs.append({"snapshot_id": item.id, "filename": item.filename, "pages": len(pages), "text_pages": sum(page.has_text for page in pages)})
            if not any(page.has_text for page in pages):
                findings.append({"severity": "info", "message": "PDF has no extractable text; visual page review is required.", "source_snapshot_id": item.id, "source_filename": item.filename})
    if geometry and not pdfs:
        findings.append({"severity": "warning", "message": "CAD geometry is present without a PDF reference for visual reconciliation."})
    if pdfs and not geometry:
        findings.append({"severity": "warning", "message": "PDF reference is present without DXF geometry for entity reconciliation."})
    return {"geometry": geometry, "pdf": pdfs, "findings": findings, "finding_count": len(findings), "note": "Findings are linked to source files; dimensional and visual conflicts require confirmation."}

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


@app.delete("/projects/{project_id}/snapshots/{snapshot_id}")
def delete_snapshot(project_id: str, snapshot_id: str) -> dict[str, str]:
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    snapshot = repository.get_snapshot(snapshot_id)
    if snapshot is None or snapshot.project_id != project_id:
        repository.close()
        raise HTTPException(status_code=404, detail="Source snapshot not found")
    repository.delete_snapshot(snapshot_id)
    repository.close()
    for path in (WORKSPACE / "incoming" / project_id / snapshot.filename, WORKSPACE / "snapshots" / f"{snapshot_id}-{snapshot.filename}"):
        if path.is_file():
            path.unlink()
    shutil.rmtree(WORKSPACE / "extracted" / project_id / snapshot_id, ignore_errors=True)
    return {"id": snapshot_id, "status": "deleted"}


@app.delete("/projects/{project_id}/snapshots")
def clear_snapshots(project_id: str) -> dict[str, int | str]:
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    snapshots = repository.list_snapshots(project_id)
    for snapshot in snapshots:
        repository.delete_snapshot(snapshot.id)
        for path in (WORKSPACE / "incoming" / project_id / snapshot.filename, WORKSPACE / "snapshots" / f"{snapshot.id}-{snapshot.filename}"):
            if path.is_file():
                path.unlink()
        shutil.rmtree(WORKSPACE / "extracted" / project_id / snapshot.id, ignore_errors=True)
    repository.close()
    return {"project_id": project_id, "deleted": len(snapshots), "status": "cleared"}


@app.post("/projects/{project_id}/runs")
def start_analysis(project_id: str, snapshot_id: str) -> dict[str, object]:
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    snapshot = repository.get_snapshot(snapshot_id)
    if snapshot is None or snapshot.project_id != project_id:
        repository.close()
        raise HTTPException(status_code=404, detail="Source snapshot not found")
    project_snapshots = repository.list_snapshots(project_id)
    evidence_bundle = [{"snapshot_id": item.id, "filename": item.filename, "media_type": item.media_type, "byte_size": item.byte_size} for item in project_snapshots]
    bundle_analysis = analyze_project_bundle(project_id, project_snapshots)
    source = WORKSPACE / "incoming" / project_id / snapshot.filename
    result: dict[str, object] = {"message": "Evidence snapshot ready for review", "pages": 0, "evidence": []}
    if snapshot.media_type == "application/pdf":
        pages = inventory_pdf(source, snapshot)
        for page in pages:
            repository.save_page_evidence(page)
        result = {"message": "Project evidence bundle indexed for review", "pages": len(pages), "evidence": [page.model_dump(mode="json") for page in pages], "evidence_bundle": evidence_bundle, "bundle_analysis": bundle_analysis}
    elif source.suffix.lower() == ".caproj":
        inventory = inventory_caproj(source)
        extracted = extract_native_files(source, WORKSPACE / "extracted" / project_id / snapshot.id)
        facts = [ObservedFact(id="fact-chief-package", key="chief.package", value=True, kind=FactKind.OBSERVED, source_ref=snapshot.id, confidence="high")]
        coverage = evidence_coverage(project_snapshots)
        result = {"message": "Chief package inventoried; project evidence bundle detected", "pages": 0, "inventory": inventory.model_dump(mode="json"), "native_files": extracted, "contents_report": caproj_contents_report(inventory), "evidence_bundle": evidence_bundle, "evidence_coverage": coverage, "bundle_analysis": bundle_analysis, "fact_count": 0, "recommendations": recommendations_for_facts(project_id, facts)}
    elif source.suffix.lower() == ".dxf":
        inventory = inventory_dxf(source)
        entities = extract_architectural_entities(source)
        facts = [ObservedFact(id="fact-cad-dxf", key="cad.dxf", value=True, kind=FactKind.OBSERVED, source_ref=snapshot.id, confidence="high")]
        result = {"message": "Project geometry evidence extracted for review", "pages": 0, "inventory": inventory.model_dump(mode="json"), "architectural_entity_count": len(entities), "fact_count": len(facts), "evidence_bundle": evidence_bundle, "bundle_analysis": bundle_analysis, "recommendations": recommendations_for_facts(project_id, facts)}
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
