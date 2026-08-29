from pathlib import Path

from res_works.ingest import ingest_artifact
from res_works.repository import ProjectRepository


def test_snapshot_is_persisted_by_content_identity(tmp_path: Path) -> None:
    source = tmp_path / "plan.pdf"
    source.write_bytes(b"same content")
    snapshot = ingest_artifact(source, "sweeter-build", tmp_path / "files")
    repository = ProjectRepository(tmp_path / "res-works.sqlite3")
    repository.save_snapshot(snapshot)
    repository.save_snapshot(snapshot)

    assert repository.get_snapshot(snapshot.id) == snapshot
    repository.close()
