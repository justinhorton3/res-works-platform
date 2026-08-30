"""Local RES Works HTTP service."""

import json
import shutil
import zipfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware

from res_works.ingest import ingest_artifact
from res_works.models import AnalysisRun, ApprovalDecision, DocumentationItem, FactKind, HandoffCheckpoint, ObservedFact, Recommendation, ReviewAnnotation
from res_works.caproj import caproj_contents_report, extract_native_files, inventory_caproj
from res_works.dxf import inventory_dxf
from res_works.dxf_extract import extract_architectural_entities, summarize_dxf_evidence
from res_works.dxf_preview import render_dxf_preview
from res_works.dxf_compare import compare_dimension_sets
from res_works.fact_mapping import facts_from_geometry
from res_works.plan_fixture import load_plan_geometry
from res_works.recommendations import recommend_documentation
from res_works.reports import build_validation_report
from res_works.rule_catalog import load_requirements, requirements_for_profile
from res_works.jurisdiction import classify_project, load_rule_profiles, profile_scope, resolve_rule_profile
from res_works.pdf_review import inventory_pdf
from res_works.pdf_render import render_pdf_pages
from res_works.repository import ProjectRepository
from res_works.handoff import apply_decisions, build_change_set, build_chief_handoff, render_handoff_html, render_handoff_markdown
from res_works.review_pdf import build_review_pdf

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
        "geometry": {"status": "available" if has_dxf else "missing", "sources": sorted(name for name in names if name.endswith(".dxf")), "optional_sources": sorted(name for name in names if name.endswith(".dwg"))},
        "visual": {"status": "available" if has_pdf else "missing", "sources": sorted(name for name in names if name.endswith(".pdf"))},
        "schedules": {"status": "available" if has_pdf else "missing", "sources": sorted(name for name in names if name.endswith(".pdf"))},
        "energy": {"status": "missing", "sources": []},
    }


def analyze_project_bundle(project_id: str, snapshots: list[object]) -> dict[str, object]:
    """Run the available source-specific analyzers for one project bundle."""
    geometry: list[dict[str, object]] = []
    pdfs: list[dict[str, object]] = []
    findings: list[dict[str, object]] = []
    dimension_sources: list[dict[str, object]] = []
    for item in snapshots:
        source = WORKSPACE / "incoming" / project_id / item.filename
        suffix = source.suffix.lower()
        if suffix == ".dxf":
            inventory = inventory_dxf(source)
            entities = extract_architectural_entities(source)
            categories: dict[str, int] = {}
            for entity in entities:
                categories[entity.category] = categories.get(entity.category, 0) + 1
            summary = summarize_dxf_evidence(source)
            dimension_sources.append({"filename": item.filename, "snapshot_id": item.id, **summary})
            preview = render_dxf_preview(source, WORKSPACE / "previews" / project_id / f"{item.id}.svg")
            geometry.append({"snapshot_id": item.id, "filename": item.filename, "inventory": inventory.model_dump(mode="json"), "entity_categories": dict(sorted(categories.items())), "evidence_summary": summary, "preview_url": f"/projects/{project_id}/snapshots/{item.id}/preview"})
            if not inventory.dimension_count:
                findings.append({"severity": "warning", "message": "DXF contains no DIMENSION entities; dimensional verification requires review.", "source_snapshot_id": item.id, "source_filename": item.filename})
        elif suffix == ".dwg":
            geometry.append({"snapshot_id": item.id, "filename": item.filename, "status": "present_not_parsed", "evidence_summary": {"entity_count": 0, "categories": {}, "text_samples": {}}})
            findings.append({"severity": "coverage", "message": "DWG is present but optional; export DXF from Chief for geometry validation.", "source_snapshot_id": item.id, "source_filename": item.filename})
        elif suffix == ".pdf":
            pages = inventory_pdf(source, item)
            for page in pages:
                repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
                repository.save_page_evidence(page)
                repository.close()
            rendered_pages = render_pdf_pages(source, item, WORKSPACE / "previews" / project_id)
            pdfs.append({"snapshot_id": item.id, "filename": item.filename, "pages": len(pages), "text_pages": sum(page.has_text for page in pages), "page_references": [{"page_number": page.page_number, "snapshot_id": page.snapshot_id, "locator": f"page {page.page_number}"} for page in pages], "page_previews": [{"page_number": index + 1, "url": f"/projects/{project_id}/snapshots/{item.id}/pages/{index + 1}/preview"} for index in range(len(rendered_pages))]})
            if not any(page.has_text for page in pages):
                findings.append({"severity": "info", "message": "PDF has no extractable text; visual page review is required.", "source_snapshot_id": item.id, "source_filename": item.filename})
    if geometry and not pdfs:
        findings.append({"severity": "warning", "message": "CAD geometry is present without a PDF reference for visual reconciliation."})
    if pdfs and not geometry:
        findings.append({"severity": "warning", "message": "PDF reference is present without DXF geometry for entity reconciliation."})
    dimension_comparison = compare_dimension_sets(dimension_sources)
    return {"geometry": geometry, "pdf": pdfs, "dimension_comparison": dimension_comparison, "findings": findings, "finding_count": len(findings), "note": "Findings are linked to source files; dimensional and visual conflicts require confirmation."}

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


@app.get("/jurisdictions")
def list_jurisdictions() -> list[dict[str, object]]:
    """List selectable profiles, including their conservative verification state."""
    profiles = load_rule_profiles(Path("reference/jurisdiction-profiles.json"))
    return [{**profile.model_dump(mode="json"), "scope": profile_scope(profile)} for profile in profiles]


@app.post("/projects/{project_id}/validation")
def validate_project(project_id: str, snapshot_id: str, profile_id: str = "arkansas-baseline", project_type: str = "new_construction", county: str | None = None, municipality: str | None = None) -> dict[str, object]:
    """Validate a JSON plan against an explicit jurisdiction profile."""
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    snapshot = repository.get_snapshot(snapshot_id)
    repository.close()
    if snapshot is None or snapshot.project_id != project_id:
        raise HTTPException(status_code=404, detail="Source snapshot not found")
    source = WORKSPACE / "incoming" / project_id / snapshot.filename
    if source.suffix.lower() != ".json":
        raise HTTPException(status_code=400, detail="Validation requires a PLAN JSON source")
    try:
        profile = resolve_rule_profile(load_rule_profiles(Path("reference/jurisdiction-profiles.json")), profile_id)
        classification = classify_project(project_type, county=county or profile.county or "Arkansas", municipality=municipality or profile.municipality)
        plan = load_plan_geometry(source)
        facts = facts_from_geometry(plan, project_id)
        facts.extend([
            ObservedFact(id="fact-project-residential", key="project.type", value="residential", kind=FactKind.OBSERVED, confidence="high"),
            ObservedFact(id="fact-project-classification", key="project.project_type", value=classification.project_type, kind=FactKind.CONFIRMED, confidence="high"),
        ])
        requirements = requirements_for_profile(load_requirements(Path("reference/arkansas-baseline-requirements.json")), profile.id)
        report = build_validation_report(project_id, profile.id, requirements, facts, plan)
    except (ValueError, OSError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"profile": profile.model_dump(mode="json"), "scope": profile_scope(profile), "classification": classification.model_dump(mode="json"), "classification_status": profile.status, "report": report.model_dump(mode="json"), "notice": "Results are evidence checks only; AHJ and professional review are required."}


@app.post("/projects/{project_id}/recommendations/{recommendation_id}/decision")
def save_recommendation_decision(project_id: str, recommendation_id: str, decision: ApprovalDecision) -> ApprovalDecision:
    if decision.recommendation_id != recommendation_id:
        raise HTTPException(status_code=400, detail="Recommendation ID does not match path")
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    repository.save_approval_decision(decision)
    repository.close()
    return decision


@app.post("/projects/{project_id}/runs/{run_id}/annotations")
def save_review_annotation(project_id: str, run_id: str, annotation: ReviewAnnotation) -> ReviewAnnotation:
    if annotation.run_id != run_id:
        raise HTTPException(status_code=400, detail="Annotation run ID does not match path")
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    run = repository.get_analysis_run(run_id)
    if run is None or run.project_id != project_id:
        repository.close()
        raise HTTPException(status_code=404, detail="Analysis run not found")
    repository.save_annotation(annotation)
    repository.close()
    return annotation


@app.get("/projects/{project_id}/runs/{run_id}/annotations")
def list_review_annotations(project_id: str, run_id: str) -> list[ReviewAnnotation]:
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    run = repository.get_analysis_run(run_id)
    if run is None or run.project_id != project_id:
        repository.close()
        raise HTTPException(status_code=404, detail="Analysis run not found")
    annotations = repository.list_annotations(run_id)
    repository.close()
    return annotations


@app.post("/projects/{project_id}/runs/{run_id}/review-pdf")
def create_review_pdf(project_id: str, run_id: str) -> FileResponse:
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    run = repository.get_analysis_run(run_id)
    annotations = repository.list_annotations(run_id) if run else []
    snapshots = repository.list_snapshots(project_id) if run else []
    snapshot = next((item for item in snapshots if item and item.filename.lower().endswith(".pdf")), None)
    repository.close()
    if run is None or run.project_id != project_id or snapshot is None or not snapshot.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=404, detail="A PDF source is required for this review run")
    source = WORKSPACE / "incoming" / project_id / snapshot.filename
    output = WORKSPACE / "review-revisions" / project_id / f"{run_id}-review.pdf"
    build_review_pdf(source, output, annotations)
    return FileResponse(output, media_type="application/pdf", filename=f"{project_id}-{run_id}-review.pdf")


@app.get("/projects/{project_id}/recommendations/{recommendation_id}/history")
def recommendation_history(project_id: str, recommendation_id: str) -> list[ApprovalDecision]:
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    history = repository.list_approval_history(recommendation_id)
    repository.close()
    return history


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
    existing = repository.get_snapshot(snapshot.id)
    if existing is not None and existing.project_id != project_id:
        target.unlink(missing_ok=True)
        repository.close()
        raise HTTPException(
            status_code=409,
            detail=(
                f"This file is already associated with project '{existing.project_id}'. "
                "Clear the source from that project or upload a distinct export."
            ),
        )
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
def start_analysis(project_id: str, snapshot_id: str, profile_id: str = "arkansas-baseline") -> dict[str, object]:
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    snapshot = repository.get_snapshot(snapshot_id)
    if snapshot is None or snapshot.project_id != project_id:
        repository.close()
        raise HTTPException(status_code=404, detail="Source snapshot not found")
    project_snapshots = repository.list_snapshots(project_id)
    evidence_bundle = [{"snapshot_id": item.id, "filename": item.filename, "media_type": item.media_type, "byte_size": item.byte_size} for item in project_snapshots]
    try:
        bundle_analysis = analyze_project_bundle(project_id, project_snapshots)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        bundle_analysis = {"geometry": [], "pdf": [], "findings": [{"severity": "error", "message": f"Evidence analysis could not complete: {error}"}], "finding_count": 1, "note": "The source was stored; correct the source or export and retry analysis."}
    source = WORKSPACE / "incoming" / project_id / snapshot.filename
    result: dict[str, object] = {"message": "Evidence snapshot ready for review", "pages": 0, "evidence": []}
    if snapshot.media_type == "application/pdf":
        pages = inventory_pdf(source, snapshot)
        for page in pages:
            repository.save_page_evidence(page)
        result = {"message": "Project evidence bundle indexed for review", "pages": len(pages), "evidence": [page.model_dump(mode="json") for page in pages], "evidence_bundle": evidence_bundle, "bundle_analysis": bundle_analysis}
    elif source.suffix.lower() == ".caproj":
        try:
            inventory = inventory_caproj(source)
            extracted = extract_native_files(source, WORKSPACE / "extracted" / project_id / snapshot.id)
        except (OSError, ValueError, zipfile.BadZipFile) as error:
            run = AnalysisRun(id=f"run-{snapshot_id[:16]}", project_id=project_id, source_snapshot_ids=[snapshot_id], status="failed", result={"message": f"CAPROJ could not be read: {error}", "pages": 0, "unsupported": True, "evidence_bundle": evidence_bundle, "bundle_analysis": bundle_analysis})
            repository.save_analysis_run(run)
            repository.close()
            return {"id": run.id, "status": run.status, "source_snapshot_ids": run.source_snapshot_ids, "result": run.result}
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
            profile = resolve_rule_profile(load_rule_profiles(Path("reference/jurisdiction-profiles.json")), profile_id)
            requirements = requirements_for_profile(load_requirements(Path("reference/arkansas-baseline-requirements.json")), profile.id)
            report = build_validation_report(project_id, profile.id, requirements, facts, plan)
            recommendations = recommendations_for_facts(project_id, facts)
            result = {"message": f"Plan geometry validated for {profile.jurisdiction}", "pages": 0, "fact_count": len(facts), "geometry_errors": report.geometry_errors, "validation": report.model_dump(mode="json"), "jurisdiction_profile": profile.model_dump(mode="json"), "recommendations": recommendations}
        except (ValueError, OSError, json.JSONDecodeError) as error:
            result = {"message": f"Plan JSON could not be analyzed: {error}", "pages": 0, "unsupported": True}
    result.setdefault("evidence_bundle", evidence_bundle)
    result.setdefault("bundle_analysis", bundle_analysis)
    result.setdefault("evidence_coverage", evidence_coverage(project_snapshots))
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


@app.get("/projects/{project_id}/snapshots/{snapshot_id}/preview")
def get_preview(project_id: str, snapshot_id: str) -> FileResponse:
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    snapshot = repository.get_snapshot(snapshot_id)
    repository.close()
    if snapshot is None or snapshot.project_id != project_id or not snapshot.filename.lower().endswith(".dxf"):
        raise HTTPException(status_code=404, detail="DXF preview not found")
    preview = WORKSPACE / "previews" / project_id / f"{snapshot_id}.svg"
    if not preview.is_file():
        source = WORKSPACE / "incoming" / project_id / snapshot.filename
        render_dxf_preview(source, preview)
    return FileResponse(preview, media_type="image/svg+xml", filename=f"{Path(snapshot.filename).stem}.svg")


@app.get("/projects/{project_id}/snapshots/{snapshot_id}/pages/{page_number}/preview")
def get_pdf_page_preview(project_id: str, snapshot_id: str, page_number: int) -> FileResponse:
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    snapshot = repository.get_snapshot(snapshot_id)
    repository.close()
    if snapshot is None or snapshot.project_id != project_id or not snapshot.filename.lower().endswith(".pdf") or page_number < 1:
        raise HTTPException(status_code=404, detail="PDF page preview not found")
    preview = WORKSPACE / "previews" / project_id / snapshot_id / f"page-{page_number:03d}.png"
    if not preview.is_file():
        source = WORKSPACE / "incoming" / project_id / snapshot.filename
        rendered = render_pdf_pages(source, snapshot, WORKSPACE / "previews" / project_id)
        if page_number > len(rendered):
            raise HTTPException(status_code=404, detail="PDF page preview not found")
    return FileResponse(preview, media_type="image/png", filename=f"{Path(snapshot.filename).stem}-page-{page_number}.png")


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


@app.get("/projects/{project_id}/runs/{run_id}/handoff")
def download_handoff(project_id: str, run_id: str, format: str = "html") -> Response:
    """Return an editable Markdown handoff containing approved items only."""
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    run = repository.get_analysis_run(run_id)
    decisions = repository.list_approval_decisions()
    repository.close()
    if run is None or run.project_id != project_id:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    recommendations = [Recommendation.model_validate(item) for item in run.result.get("recommendations", [])]
    decided = apply_decisions(recommendations, decisions)
    source_id = run.source_snapshot_ids[0] if run.source_snapshot_ids else "unknown"
    change_set = build_change_set(project_id, source_id, decided)
    handoff = build_chief_handoff(change_set, recommendations=decided)
    if format == "markdown":
        return Response(render_handoff_markdown(handoff), media_type="text/plain", headers={"Content-Disposition": "inline"})
    return Response(render_handoff_html(handoff), media_type="text/html", headers={"Content-Disposition": "inline"})


@app.post("/projects/{project_id}/runs/{run_id}/checkpoints")
def create_checkpoint(project_id: str, run_id: str) -> HandoffCheckpoint:
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    run = repository.get_analysis_run(run_id)
    if run is None or run.project_id != project_id:
        repository.close()
        raise HTTPException(status_code=404, detail="Analysis run not found")
    recommendations = [Recommendation.model_validate(item) for item in run.result.get("recommendations", [])]
    decisions = repository.list_approval_decisions()
    source_id = run.source_snapshot_ids[0] if run.source_snapshot_ids else "unknown"
    change_set = build_change_set(project_id, source_id, apply_decisions(recommendations, decisions))
    checkpoint = HandoffCheckpoint(id=f"checkpoint-{change_set.id}", project_id=project_id, run_id=run_id, change_set_id=change_set.id)
    repository.save_checkpoint(checkpoint)
    repository.close()
    return checkpoint


@app.post("/projects/{project_id}/checkpoints/{checkpoint_id}/recover")
def recover_checkpoint(project_id: str, checkpoint_id: str) -> HandoffCheckpoint:
    repository = ProjectRepository(WORKSPACE / "res-works.sqlite3")
    checkpoint = repository.get_checkpoint(checkpoint_id)
    if checkpoint is None or checkpoint.project_id != project_id:
        repository.close()
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    recovered = checkpoint.model_copy(update={"status": "recovered"})
    repository.save_checkpoint(recovered)
    repository.close()
    return recovered
