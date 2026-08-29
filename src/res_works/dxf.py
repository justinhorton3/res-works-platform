"""Read-only DXF inventory for Chief-derived geometry evidence."""

from pathlib import Path

import ezdxf

from .models import DxfInventory


def inventory_dxf(path: str | Path) -> DxfInventory:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(source)
    document = ezdxf.readfile(source)
    counts: dict[str, int] = {}
    dimensions = 0
    text = 0
    for entity in document.modelspace():
        kind = entity.dxftype()
        counts[kind] = counts.get(kind, 0) + 1
        dimensions += kind == "DIMENSION"
        text += kind in {"TEXT", "MTEXT"}
    units = document.header.get("$INSUNITS")
    return DxfInventory(
        filename=source.name,
        units=int(units) if units is not None else None,
        layers=sorted(layer.dxf.name for layer in document.layers),
        entity_counts=dict(sorted(counts.items())),
        dimension_count=dimensions,
        text_count=text,
    )
