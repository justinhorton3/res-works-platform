from pathlib import Path

import ezdxf

from res_works.dxf_preview import render_dxf_preview


def test_render_dxf_preview_creates_svg_with_geometry_and_labels(tmp_path: Path) -> None:
    source = tmp_path / "plan.dxf"
    output = tmp_path / "preview.svg"
    document = ezdxf.new("R2018")
    document.modelspace().add_line((0, 0), (10, 0))
    document.modelspace().add_text("Kitchen", dxfattribs={"insert": (2, 2)})
    document.saveas(source)
    render_dxf_preview(source, output)
    svg = output.read_text()
    assert "<svg" in svg
    assert "Kitchen" in svg
    assert "<line" in svg
