from pathlib import Path

from res_works.ingest import ingest_artifact


def test_ingest_creates_immutable_hashed_snapshot(tmp_path: Path) -> None:
    source = tmp_path / "SweeterBuild_08.04.26.pdf"
    source.write_bytes(b"private PDF fixture bytes")
    destination = tmp_path / "snapshots"

    first = ingest_artifact(source, "sweeter-build", destination)
    second = ingest_artifact(source, "sweeter-build", destination)

    assert first == second
    assert first.filename == "SweeterBuild_08.04.26.pdf"
    assert first.media_type == "application/pdf"
    assert len(list(destination.iterdir())) == 1
    assert first.byte_size == source.stat().st_size


def test_ingest_rejects_missing_artifact(tmp_path: Path) -> None:
    try:
        ingest_artifact(tmp_path / "missing.pdf", "sweeter-build", tmp_path / "snapshots")
    except FileNotFoundError as error:
        assert str(error).endswith("missing.pdf")
    else:
        raise AssertionError("missing artifacts must be rejected")
