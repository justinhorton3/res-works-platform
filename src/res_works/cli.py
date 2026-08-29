"""Command-line entry points for local RES Works review workflows."""

import argparse
import json
from pathlib import Path

from .ingest import ingest_artifact
from .pdf_review import inventory_pdf
from .repository import ProjectRepository


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
    args = parser.parse_args()
    if args.command == "review-pdf":
        print(json.dumps(review_pdf(args.input, args.project_id, args.workspace), sort_keys=True))


if __name__ == "__main__":
    main()
