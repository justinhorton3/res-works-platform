from pathlib import Path

from res_works.fact_mapping import facts_from_geometry
from res_works.plan_fixture import load_plan_geometry


def test_geometry_mapping_is_deterministic_and_conservative() -> None:
    plan = load_plan_geometry(Path("projects/sweeter-build/plan.json"))
    first = facts_from_geometry(plan, "sweeter-build")
    second = facts_from_geometry(plan, "sweeter-build")

    assert first == second
    assert any(fact.key == "room.type" for fact in first)
    assert any(fact.key == "stair.present" and fact.value is True for fact in first)
    assert any(fact.key == "stair.width" and fact.value == 4.0 for fact in first)
    assert not any(fact.key == "window.clear_opening" for fact in first)
