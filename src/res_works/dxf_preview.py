"""Clean, scale-preserving SVG preview for traceable Floor 1 DXF evidence."""

import re
from html import escape
from pathlib import Path

import ezdxf

from .dxf_extract import normalize_layer


def _is_floor_plan_layer(layer: str) -> bool:
    name = normalize_layer(layer).lower()
    if name.strip() == "0":
        return True
    excluded = ("plot plan", "terrain", "camera", "revision", "framing", "roof", "ceiling", "floor truss", "header")
    if any(term in name for term in excluded):
        return False
    return any(term in name for term in ("wall", "door", "window", "stair", "cabinet", "dimension", "room label", "plumbing", "electrical", "fireplace", "casing", "opening"))


def clean_chief_text(value: str) -> str:
    """Remove Chief inline formatting while retaining human-readable text."""
    text = value.replace("\\P", " ").replace("\\~", " ").replace('\\"', '"')
    text = re.sub(r"\\[fF][^;]*;", "", text)
    text = re.sub(r"\\[CcHhKkTtWw][^;]*;", "", text)
    text = re.sub(r"[{}]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def render_dxf_preview(path: str | Path, output: str | Path) -> Path:
    document = ezdxf.readfile(path)
    lines: list[tuple[float, float, float, float, str, str]] = []
    labels: list[tuple[float, float, str, str, str]] = []
    seen_dimensions: set[tuple[int, int, str]] = set()
    for entity in document.modelspace():
        kind = entity.dxftype()
        layer = entity.dxf.layer
        if kind == "LINE" and _is_floor_plan_layer(layer):
            lines.append((entity.dxf.start.x, entity.dxf.start.y, entity.dxf.end.x, entity.dxf.end.y, entity.dxf.handle, layer))
        elif kind in {"TEXT", "MTEXT"} and _is_floor_plan_layer(layer) and ("room label" in normalize_layer(layer).lower() or normalize_layer(layer).strip() == "0"):
            point = entity.dxf.insert
            text = clean_chief_text(entity.dxf.text if kind == "TEXT" else entity.text)
            if text and len(text) <= 80:
                labels.append((point.x, point.y, text, entity.dxf.handle, layer))
        elif kind == "DIMENSION" and _is_floor_plan_layer(layer):
            try:
                point = entity.dxf.defpoint
                text = clean_chief_text(getattr(entity.dxf, "text", "") or "") or f"{entity.get_measurement():.2f}"
                key = (round(point.x), round(point.y), text)
                if key not in seen_dimensions:
                    seen_dimensions.add(key)
                    labels.append((point.x, point.y, text, entity.dxf.handle, layer))
            except (AttributeError, TypeError, ValueError):
                continue
    points = [(x, y) for x1, y1, x2, y2, _, _ in lines for x, y in ((x1, y1), (x2, y2))] or [(0, 0), (100, 100)]
    min_x, max_x = min(x for x, _ in points), max(x for x, _ in points)
    min_y, max_y = min(y for _, y in points), max(y for _, y in points)
    pad = max(max_x - min_x, max_y - min_y, 1) * 0.03
    min_x, max_x, min_y, max_y = min_x - pad, max_x + pad, min_y - pad, max_y + pad
    svg_width, svg_height = max_x - min_x, max_y - min_y
    units = document.header.get("$INSUNITS")
    elements = [f'<rect width="100%" height="100%" fill="white"/><metadata>Clean Floor 1 architectural preview; source handles retained in element metadata. INSUNITS={units or "unknown"}</metadata>']
    for x1, y1, x2, y2, handle, layer in lines:
        normalized = normalize_layer(layer).lower()
        stroke = "#172033" if "wall" in normalized else "#64748b"
        stroke_width = "0.28" if "wall" in normalized else "0.12"
        elements.append(f'<line data-handle="{escape(handle)}" data-layer="{escape(layer)}" x1="{x1}" y1="{-y1}" x2="{x2}" y2="{-y2}" stroke="{stroke}" stroke-width="{stroke_width}" vector-effect="non-scaling-stroke"><title>{escape(layer)} · handle {escape(handle)}</title></line>')
    for x, y, text, handle, layer in labels[:250]:
        dimension = "dimension" in normalize_layer(layer).lower()
        color = "#475569" if dimension else "#0f172a"
        size = "0.9" if dimension else "1.4"
        elements.append(f'<text data-handle="{escape(handle)}" data-layer="{escape(layer)}" x="{x}" y="{-y}" font-size="{size}" fill="{color}"><title>{escape(layer)} · handle {escape(handle)}</title>{escape(text)}</text>')
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{min_x} {-max_y} {svg_width} {svg_height}" width="{svg_width:g}" height="{svg_height:g}" preserveAspectRatio="xMidYMid meet" data-source="{escape(Path(path).name)}" data-units="{escape(str(units or "unknown"))}">{"".join(elements)}</svg>')
    return destination
