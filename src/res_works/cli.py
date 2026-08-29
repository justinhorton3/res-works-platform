"""Command-line entry points for local RES Works review workflows."""

import argparse
import json
from pathlib import Path

from .ingest import ingest_artifact
from .pdf_review import inventory_pdf
from .models import ObservedFact
from .fact_mapping import facts_from_geometry
from .plan_fixture import load_plan_geometry
from .repository import ProjectRepository
from .reports import build_validation_report
from .rule_catalog import load_requirements


def review_pdf(input_path: str | Path, project_id: str, workspace: str | Path) -> dict[str, object]:
    root = Path(workspace)
    snapshot = ingest_artifact(input_path, project_id, root / "snapshots")
    repository = ProjectRepository(root / "res-works.sqlite3")
    repository.save_snapshot(snapshot)
    pages = inventory_pdf(input_path, snapshot)
    for page in pages:
        repository.save_page_evidence(page)
    repository.close()
    return {
        "project_id": project_id,
        "snapshot_id": snapshot.id,
        "filename": snapshot.filename,
        "pages": len(pages),
        "pages_with_text": sum(page.has_text for page in pages),
    }


def main() -> None:
    parser = argparse.ArgumentParser(prog="res-works")
    subparsers = parser.add_subparsers(dest="command", required=True)
    review = subparsers.add_parser("review-pdf", help="ingest and inventory a PDF")
    review.add_argument("input", type=Path)
    review.add_argument("--project-id", required=True)
    review.add_argument("--workspace", type=Path, default=Path("storage"))
    project = subparsers.add_parser("review-project", help="review a PDF against a rule catalog")
    project.add_argument("input", type=Path)
    project.add_argument("--project-id", required=True)
    project.add_argument("--workspace", type=Path, default=Path("storage"))
    project.add_argument("--requirements", type=Path, default=Path("reference/arkansas-baseline-requirements.json"))
    project.add_argument("--facts", type=Path, default=Path("projects/sweeter-build/observed-facts.json"))
    project.add_argument("--plan", type=Path, default=Path("projects/sweeter-build/plan.json"))
    args = parser.parse_args()
    if args.command == "review-pdf":
        print(json.dumps(review_pdf(args.input, args.project_id, args.workspace), sort_keys=True))
    elif args.command == "review-project":
        pdf_report = review_pdf(args.input, args.project_id, args.workspace)
        source_facts = [ObservedFact.model_validate(item) for item in json.loads(args.facts.read_text())]
        geometry_facts = facts_from_geometry(load_plan_geometry(args.plan), args.project_id)
        facts = list({fact.id: fact for fact in source_facts + geometry_facts}.values())
        plan = load_plan_geometry(args.plan)
        report = build_validation_report(
            args.project_id,
            "arkansas-baseline",
            load_requirements(args.requirements),
            facts,
            plan,
        )
        print(json.dumps({**pdf_report, "fact_count": len(facts), "geometry_error_count": len(report.geometry_errors), "validation": report.model_dump(mode="json"), "counts": report.counts}, sort_keys=True))


if __name__ == "__main__":
    main()
