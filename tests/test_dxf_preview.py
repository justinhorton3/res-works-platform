from pathlib import Path

import ezdxf

from res_works.dxf_preview import _is_floor_plan_layer, render_dxf_preview


def test_preview_excludes_plot_plan_and_framing_layers() -> None:
    assert _is_floor_plan_layer("Walls_  Normal-1") is True
    assert _is_floor_plan_layer("Dimensions_ Plan-0") is True
    assert _is_floor_plan_layer("Text_ Plot Plan-1") is False
    assert _is_floor_plan_layer("Framing_ Labels-1") is False


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
    assert 'data-source="plan.dxf"' in svg
    assert 'data-handle=' in svg
    assert "vector-effect=\"non-scaling-stroke\"" in svg
