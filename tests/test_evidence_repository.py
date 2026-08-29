from pathlib import Path

from res_works.ingest import ingest_artifact
from res_works.repository import ProjectRepository


def test_page_evidence_is_persisted_and_ordered(tmp_path: Path) -> None:
    source = tmp_path / "plan.pdf"
    source.write_bytes(b"not a pdf")
    snapshot = ingest_artifact(source, "sweeter-build", tmp_path / "files")
    repository = ProjectRepository(tmp_path / "res-works.sqlite3")
    from res_works.models import PdfPageEvidence

    evidence = [
        PdfPageEvidence(snapshot_id=snapshot.id, page_number=2, text="second", character_count=6, has_text=True),
        PdfPageEvidence(snapshot_id=snapshot.id, page_number=1, text="first", character_count=5, has_text=True),
    ]
    for item in evidence:
        repository.save_page_evidence(item)

    assert [item.page_number for item in repository.list_page_evidence(snapshot.id)] == [1, 2]
    repository.close()
