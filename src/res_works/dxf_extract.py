"""Extract traceable architectural entities from a Chief DXF export."""

import re
from pathlib import Path

import ezdxf

from .models import DxfEntityRecord

_CATEGORIES = {
    "Walls": "walls",
    "Doors": "doors",
    "Windows": "windows",
    "Dimensions": "dimensions",
    "Room Labels": "room_labels",
    "Stairs & Ramps": "stairs",
    "Cabinets": "cabinets",
    "Plumbing": "plumbing",
    "Fireplaces": "fireplaces",
}


def normalize_layer(layer: str) -> str:
    return re.sub(r"-\d+$", "", layer)


def _category(layer: str) -> str | None:
    normalized = normalize_layer(layer)
    for prefix, category in _CATEGORIES.items():
        if normalized.startswith(prefix):
            return category
    return None


def extract_architectural_entities(path: str | Path) -> list[DxfEntityRecord]:
    document = ezdxf.readfile(path)
    records: list[DxfEntityRecord] = []
    for entity in document.modelspace():
        category = _category(entity.dxf.layer)
        if category is None:
            continue
        text = None
        if entity.dxftype() == "TEXT":
            text = entity.dxf.text
        elif entity.dxftype() == "MTEXT":
            text = entity.text
        records.append(
            DxfEntityRecord(
                handle=entity.dxf.handle,
                entity_type=entity.dxftype(),
                raw_layer=entity.dxf.layer,
                normalized_layer=normalize_layer(entity.dxf.layer),
                category=category,
                text=text,
            )
        )
    return records


def summarize_dxf_evidence(path: str | Path) -> dict[str, object]:
    """Return measurable CAD evidence without inventing room geometry."""
    records = extract_architectural_entities(path)
    categories: dict[str, int] = {}
    text_samples: dict[str, list[str]] = {}
    dimensions: list[dict[str, object]] = []
    for record in records:
        categories[record.category] = categories.get(record.category, 0) + 1
        if record.text and len(text_samples.setdefault(record.category, [])) < 20:
            text_samples[record.category].append(record.text.strip())
    document = ezdxf.readfile(path)
    for entity in document.modelspace():
        if entity.dxftype() != "DIMENSION":
            continue
        try:
            measurement = float(entity.get_measurement())
        except (AttributeError, TypeError, ValueError):
            measurement = None
        dimensions.append({"handle": entity.dxf.handle, "layer": entity.dxf.layer, "measurement": measurement, "display_text": getattr(entity.dxf, "text", "") or ""})
    return {"entity_count": len(records), "categories": dict(sorted(categories.items())), "text_samples": text_samples, "dimensions": dimensions}
