"""Small, local SVG preview for traceable DXF review evidence."""

from html import escape
from pathlib import Path

import ezdxf


def render_dxf_preview(path: str | Path, output: str | Path) -> Path:
    document = ezdxf.readfile(path)
    lines: list[tuple[float, float, float, float]] = []
    labels: list[tuple[float, float, str]] = []
    for entity in document.modelspace():
        kind = entity.dxftype()
        if kind == "LINE":
            lines.append((entity.dxf.start.x, entity.dxf.start.y, entity.dxf.end.x, entity.dxf.end.y))
        elif kind in {"TEXT", "MTEXT"}:
            point = entity.dxf.insert
            text = entity.dxf.text if kind == "TEXT" else entity.text
            if text:
                labels.append((point.x, point.y, text.replace("\n", " ")[:80]))
    points = [(x, y) for x1, y1, x2, y2 in lines for x, y in ((x1, y1), (x2, y2))] or [(0, 0), (100, 100)]
    min_x, max_x = min(x for x, _ in points), max(x for x, _ in points)
    min_y, max_y = min(y for _, y in points), max(y for _, y in points)
    pad = max(max_x - min_x, max_y - min_y, 1) * 0.03
    min_x, max_x, min_y, max_y = min_x - pad, max_x + pad, min_y - pad, max_y + pad
    width, height = max_x - min_x, max_y - min_y
    elements = [f'<rect width="100%" height="100%" fill="white"/>']
    for x1, y1, x2, y2 in lines:
        elements.append(f'<line x1="{x1}" y1="{-y1}" x2="{x2}" y2="{-y2}" stroke="#172033" stroke-width="0.18"/>')
    for x, y, text in labels[:200]:
        elements.append(f'<text x="{x}" y="{-y}" font-size="1.2" fill="#2563eb">{escape(text)}</text>')
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{min_x} {-max_y} {width} {height}" preserveAspectRatio="xMidYMid meet">{"".join(elements)}</svg>')
    return destination
