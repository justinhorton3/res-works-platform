"""Read-only inventory of Chief Architect .caproj project packages."""

import hashlib
import json
import zipfile
from pathlib import Path

from .models import CaprojInventory


def inventory_caproj(path: str | Path) -> CaprojInventory:
    package = Path(path)
    if not package.is_file():
        raise FileNotFoundError(package)
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    with zipfile.ZipFile(package) as archive:
        names = archive.namelist()
        if "manifest.json" not in names:
            raise ValueError("caproj package does not contain manifest.json")
        manifest = json.loads(archive.read("manifest.json"))
    native = [name for name in names if name.lower().endswith((".plan", ".layout"))]
    return CaprojInventory(
        filename=package.name,
        sha256=digest,
        byte_size=package.stat().st_size,
        manifest_version=manifest.get("manifest_version"),
        schema_version=manifest.get("schema_version"),
        native_plan_files=[name for name in native if name.lower().endswith(".plan")],
        native_layout_files=[name for name in native if name.lower().endswith(".layout")],
        resource_count=len(manifest.get("resources", [])),
        export_errors=manifest.get("export_errors", []),
        missing_resources=[
            str(item)
            for item in manifest.get("missing_resource_parents", [])
            + manifest.get("missing_resource_relinks", [])
        ],
    )
