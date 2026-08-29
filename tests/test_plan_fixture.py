from pathlib import Path

from res_works.geometry import validate_geometry
from res_works.plan_fixture import load_plan_geometry


def test_sweeter_build_fixture_loads_and_is_geometrically_valid() -> None:
    plan = load_plan_geometry(Path("projects/sweeter-build/plan.json"))
    assert plan.envelope.width == 101.58
    assert len(plan.rooms) == 7
    assert len(plan.openings) == 2
    assert validate_geometry(plan) == []
