"""Immutable local artifact ingestion and duplicate detection."""

import hashlib
import mimetypes
import shutil
from pathlib import Path

from .models import SourceSnapshot


def ingest_artifact(source: str | Path, project_id: str, destination: str | Path) -> SourceSnapshot:
    source_path = Path(source)
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    target_dir = Path(destination)
    target_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
    target = target_dir / f"{digest[:16]}-{source_path.name}"
    if not target.exists():
        shutil.copy2(source_path, target)
    media_type = mimetypes.guess_type(source_path.name)[0] or "application/octet-stream"
    return SourceSnapshot(
        id=digest,
        project_id=project_id,
        filename=source_path.name,
        media_type=media_type,
        sha256=digest,
        byte_size=source_path.stat().st_size,
    )
