"""Safe primitives for watching a local Chief export directory."""

import hashlib
import json
import mimetypes
import time
import urllib.request
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


def poll_exports(
    folder: str | Path,
    previous: dict[Path, FileObservation] | None = None,
) -> tuple[dict[Path, FileObservation], list[FileObservation]]:
    """Take one hash-backed poll and return updated state plus stable changes."""
    current = [observe_file(path, include_hash=True) for path in discover_exports(folder)]
    state = {observation.path: observation for observation in current}
    return state, stable_changes(previous or {}, current)


def watch_exports(
    folder: str | Path,
    on_change,
    *,
    interval_seconds: float = 2.0,
    max_polls: int | None = None,
) -> int:
    """Poll until stopped, dispatching each stable export change once."""
    previous: dict[Path, FileObservation] = {}
    polls = 0
    while max_polls is None or polls < max_polls:
        previous, changes = poll_exports(folder, previous)
        for observation in changes:
            on_change(observation)
        polls += 1
        if max_polls is None or polls < max_polls:
            time.sleep(interval_seconds)
    return polls


def dispatch_to_api(observation: FileObservation, *, api_url: str, project_id: str) -> dict[str, object]:
    """Upload one stable export and start its analysis run through the API."""
    boundary = f"----resworks-{observation.sha256 or 'change'}"
    payload = observation.path.read_bytes()
    content_type = mimetypes.guess_type(observation.path.name)[0] or "application/octet-stream"
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{observation.path.name}\"\r\nContent-Type: {content_type}\r\n\r\n").encode() + payload + f"\r\n--{boundary}--\r\n".encode()
    request = urllib.request.Request(f"{api_url.rstrip('/')}/projects/{project_id}/files", data=body, method="POST", headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(request, timeout=60) as response:
        snapshot = json.loads(response.read())
    run_request = urllib.request.Request(f"{api_url.rstrip('/')}/projects/{project_id}/runs?snapshot_id={snapshot['id']}", method="POST")
    with urllib.request.urlopen(run_request, timeout=120) as response:
        run = json.loads(response.read())
    return {"snapshot_id": snapshot["id"], "run_id": run["id"], "status": run["status"], "filename": observation.path.name}
