"""Read-only inventory of Chief Architect .caproj project packages."""

import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path

from .models import CaprojInventory


def caproj_contents_report(inventory: CaprojInventory) -> dict[str, object]:
    """Describe what the package can support and which exports are still needed."""
    available = []
    if inventory.native_plan_files:
        available.append("native plan container")
    if inventory.native_layout_files:
        available.append("native layout sheets")
    if inventory.resource_extensions.get("json"):
        available.append("package manifest metadata")
    return {
        "available": available,
        "native_artifacts": {
            "plan": inventory.native_plan_files,
            "layout": inventory.native_layout_files,
        },
        "requires_chief_export": [
            {"kind": "geometry", "export": "Export All Floors (DWG/DXF)", "purpose": "walls, doors, windows, dimensions, stairs, and CAD entities"},
            {"kind": "schedules", "export": "PDF or schedule export", "purpose": "room, door/window, cabinet, fixture, and material schedules"},
            {"kind": "energy", "export": "Thermal Envelope Data or RESCheck", "purpose": "envelope and energy evidence"},
            {"kind": "visual", "export": "Export PDF", "purpose": "page-level visual verification and annotations"},
        ],
        "limitations": ["PLAN and LAYOUT are proprietary binary formats; their contents are preserved but not interpreted as structured geometry yet."],
    }


def extract_native_files(path: str | Path, destination: str | Path) -> dict[str, list[dict[str, object]]]:
    """Extract native Chief plan/layout members for downstream analysis.

    CAPROJ is a ZIP container.  The native files are binary Chief artifacts,
    so extraction is deliberately separate from parsing and preserves the
    archive member names and byte sizes as provenance.
    """
    package = Path(path)
    target_root = Path(destination)
    target_root.mkdir(parents=True, exist_ok=True)
    extracted: dict[str, list[dict[str, object]]] = {"plan": [], "layout": []}
    with zipfile.ZipFile(package) as archive:
        for member in archive.infolist():
            lower = member.filename.lower()
            kind = "plan" if lower.endswith(".plan") else "layout" if lower.endswith(".layout") else None
            if kind is None or member.is_dir():
                continue
            relative = Path(member.filename)
            output = target_root / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, output.open("wb") as destination_file:
                destination_file.write(source.read())
            extracted[kind].append({"archive_path": member.filename, "path": str(output), "byte_size": member.file_size})
    return extracted


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
    extensions = Counter(
        Path(name).suffix.lower().lstrip(".") or "<none>"
        for name in names
        if not name.endswith("/")
    )
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
        project_name=manifest.get("project_name_from_doc"),
        resource_extensions=dict(sorted(extensions.items())),
        exported_file_count=len(manifest.get("exported_files", [])),
        unmanaged_file_count=len(manifest.get("unmanaged_files_in_export", [])),
    )
