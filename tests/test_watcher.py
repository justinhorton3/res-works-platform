from pathlib import Path

import pytest

from res_works.watcher import discover_exports, is_stable, observe_file, poll_exports, stable_changes


def test_discover_exports_is_local_supported_and_deterministic(tmp_path: Path) -> None:
    (tmp_path / "z-plan.PLAN").write_bytes(b"plan")
    (tmp_path / "a-review.txt").write_bytes(b"ignore")
    (tmp_path / "A-export.PDF").write_bytes(b"pdf")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "hidden.pdf").write_bytes(b"ignore")

    assert [path.name for path in discover_exports(tmp_path)] == ["A-export.PDF", "z-plan.PLAN"]


def test_stability_requires_same_path_and_size(tmp_path: Path) -> None:
    source = tmp_path / "export.caproj"
    source.write_bytes(b"one")
    first = observe_file(source)
    first_hash = observe_file(source, include_hash=True).sha256
    assert is_stable(first, observe_file(source))
    source.write_bytes(b"two")
    assert is_stable(first, observe_file(source))
    assert first_hash != observe_file(source, include_hash=True).sha256


def test_observe_missing_file_fails_clearly(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        observe_file(tmp_path / "missing.pdf")


def test_stable_changes_deduplicates_repeated_observations(tmp_path: Path) -> None:
    source = tmp_path / "export.dxf"
    source.write_bytes(b"one")
    first = observe_file(source, include_hash=True)
    assert stable_changes({first.path: first}, [first]) == []
    source.write_bytes(b"two!")
    changed = observe_file(source, include_hash=True)
    assert stable_changes({first.path: first}, [changed]) == [changed]


def test_poll_exports_returns_state_and_new_export_once(tmp_path: Path) -> None:
    source = tmp_path / "plan.pdf"
    source.write_bytes(b"pdf")
    state, changes = poll_exports(tmp_path)
    assert list(state) == [source]
    assert changes == [state[source]]
    next_state, changes = poll_exports(tmp_path, state)
    assert next_state == state
    assert changes == []
