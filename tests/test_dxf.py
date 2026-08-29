from pathlib import Path

import ezdxf

from res_works.dxf import inventory_dxf


def test_dxf_inventory_records_layers_entities_and_units(tmp_path: Path) -> None:
    path = tmp_path / "plan.dxf"
    document = ezdxf.new("R2018")
    document.header["$INSUNITS"] = 2
    document.layers.add("A-WALL")
    space = document.modelspace()
    space.add_line((0, 0), (10, 0), dxfattribs={"layer": "A-WALL"})
    space.add_text("Living Room")
    with path.open("w") as stream:
        document.write(stream)

    inventory = inventory_dxf(path)
    assert inventory.units == 2
    assert "A-WALL" in inventory.layers
    assert inventory.entity_counts == {"LINE": 1, "TEXT": 1}
    assert inventory.text_count == 1
    assert inventory.dimension_count == 0


def test_missing_dxf_is_rejected(tmp_path: Path) -> None:
    try:
        inventory_dxf(tmp_path / "missing.dxf")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("missing DXF must be rejected")
