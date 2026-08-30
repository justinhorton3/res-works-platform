"""Command-line entry points for local RES Works review workflows."""

import argparse
import json
from pathlib import Path

from .ingest import ingest_artifact
from .pdf_review import inventory_pdf
from .models import DocumentationItem, ObservedFact
from .fact_mapping import facts_from_geometry
from .plan_fixture import load_plan_geometry
from .repository import ProjectRepository
from .reports import build_validation_report
from .recommendations import recommend_documentation
from .rule_catalog import load_requirements
from .watcher import poll_exports, watch_exports


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
    project.add_argument("--documentation-library", type=Path, default=Path("reference/documentation-library.json"))
    watch = subparsers.add_parser("watch-once", help="scan a Chief export folder once")
    watch.add_argument("folder", type=Path)
    loop = subparsers.add_parser("watch", help="watch a Chief export folder and emit changes")
    loop.add_argument("folder", type=Path)
    loop.add_argument("--interval", type=float, default=2.0)
    loop.add_argument("--polls", type=int, default=1, help="number of polls; use 0 to run until interrupted")
    args = parser.parse_args()
    if args.command == "watch":
        changes = []
        polls = args.polls or None
        watch_exports(args.folder, changes.append, interval_seconds=args.interval, max_polls=polls)
        print(json.dumps({"folder": str(args.folder), "polls": polls, "changes": [{"path": str(item.path), "byte_size": item.byte_size, "sha256": item.sha256} for item in changes]}, sort_keys=True))
    elif args.command == "watch-once":
        state, changes = poll_exports(args.folder)
        print(json.dumps({"folder": str(args.folder), "observed": len(state), "changes": [{"path": str(item.path), "byte_size": item.byte_size, "sha256": item.sha256} for item in changes]}, sort_keys=True))
    elif args.command == "review-pdf":
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
        documentation = [
            DocumentationItem.model_validate(item)
            for item in json.loads(args.documentation_library.read_text())
        ]
        recommendations = recommend_documentation(args.project_id, documentation, facts)
        print(json.dumps({
            **pdf_report,
            "fact_count": len(facts),
            "geometry_error_count": len(report.geometry_errors),
            "validation": report.model_dump(mode="json"),
            "counts": report.counts,
            "recommendation_count": len(recommendations),
            "recommendations": [item.model_dump(mode="json") for item in recommendations],
        }, sort_keys=True))


if __name__ == "__main__":
    main()
