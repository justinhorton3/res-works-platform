import json
import zipfile
from pathlib import Path

import pytest

from res_works.caproj import inventory_caproj


def test_caproj_inventory_finds_native_files_and_resources(tmp_path: Path) -> None:
    package = tmp_path / "Sweeter Build.caproj"
    manifest = {
        "manifest_version": 5,
        "schema_version": 20,
        "resources": [{"resource": {"name": "wall"}}],
        "export_errors": [],
        "missing_resource_relinks": [],
    }
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("manifest.json", json.dumps(manifest))
        archive.writestr("Projects/Sweeter Build/Sweeter_LOT27.plan", b"native plan")
        archive.writestr("Projects/Sweeter Build/Sweeter_LOT27.layout", b"native layout")

    inventory = inventory_caproj(package)
    assert inventory.manifest_version == 5
    assert inventory.native_plan_files == ["Projects/Sweeter Build/Sweeter_LOT27.plan"]
    assert inventory.native_layout_files == ["Projects/Sweeter Build/Sweeter_LOT27.layout"]
    assert inventory.resource_count == 1
    assert len(inventory.sha256) == 64


def test_caproj_requires_manifest(tmp_path: Path) -> None:
    package = tmp_path / "invalid.caproj"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("readme.txt", "invalid")
    with pytest.raises(ValueError, match="manifest.json"):
        inventory_caproj(package)
