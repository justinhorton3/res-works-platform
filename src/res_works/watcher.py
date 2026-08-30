"""Safe primitives for watching a local Chief export directory."""

import hashlib
from dataclasses import dataclass
from pathlib import Path


SUPPORTED_EXPORTS = {".caproj", ".plan", ".layout", ".pdf", ".dxf", ".dwg"}


@dataclass(frozen=True)
class FileObservation:
    path: Path
    byte_size: int
    sha256: str | None = None


def discover_exports(folder: str | Path) -> list[Path]:
    """Return supported files in deterministic order, without recursion."""
    root = Path(folder)
    if not root.is_dir():
        return []
    return sorted(
        (path for path in root.iterdir() if path.is_file() and path.suffix.lower() in SUPPORTED_EXPORTS),
        key=lambda path: path.name.lower(),
    )


def observe_file(path: str | Path, *, include_hash: bool = False) -> FileObservation:
    """Capture a file's current size and optionally its content identity."""
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(file_path)
    digest = None
    if include_hash:
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
    return FileObservation(file_path, file_path.stat().st_size, digest)


def is_stable(previous: FileObservation, current: FileObservation) -> bool:
    """Return true only when the same path and byte size persist between polls."""
    return previous.path == current.path and previous.byte_size == current.byte_size


def stable_changes(
    previous: dict[Path, FileObservation],
    current: list[FileObservation],
) -> list[FileObservation]:
    """Return deterministic new/changed exports ready for one analysis trigger.

    A same-sized rewrite is only considered changed when hashes are supplied
    and differ. This prevents duplicate runs when a watcher sees the same
    stable export on consecutive polls.
    """
    changed: list[FileObservation] = []
    for observation in sorted(current, key=lambda item: item.path.name.lower()):
        old = previous.get(observation.path)
        if old is None or old.byte_size != observation.byte_size or (
            old.sha256 is not None and observation.sha256 is not None and old.sha256 != observation.sha256
        ):
            changed.append(observation)
    return changed
