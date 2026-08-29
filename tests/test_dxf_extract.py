from pathlib import Path

import ezdxf

from res_works.dxf_extract import extract_architectural_entities, normalize_layer


def test_normalize_chief_layer_suffix() -> None:
    assert normalize_layer("Walls_  Normal-Interior-4-L2-1") == "Walls_  Normal-Interior-4-L2"


def test_extract_architectural_entities_preserves_handles_and_raw_layers(tmp_path: Path) -> None:
    path = tmp_path / "plan.dxf"
    document = ezdxf.new("R2018")
    space = document.modelspace()
    space.add_line((0, 0), (10, 0), dxfattribs={"layer": "Walls_  Normal-1"})
    space.add_text("Living Room", dxfattribs={"layer": "Room Labels-1"})
    with path.open("w") as stream:
        document.write(stream)

    records = extract_architectural_entities(path)
    assert [record.category for record in records] == ["walls", "room_labels"]
    assert records[0].raw_layer == "Walls_  Normal-1"
    assert records[0].normalized_layer == "Walls_  Normal"
    assert records[0].handle
    assert records[1].text == "Living Room"
