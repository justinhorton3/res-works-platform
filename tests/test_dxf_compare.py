from res_works.dxf_compare import compare_plan_to_dxf
from res_works.models import DxfEntityRecord, PlanGeometry, Rect, Room


def test_comparison_reports_categories_and_alignment_limitation() -> None:
    plan = PlanGeometry(
        envelope=Rect(x=0, y=0, width=30, depth=54),
        rooms=[Room(id="living", name="Living", kind="living_room", geometry=Rect(x=0, y=0, width=30, depth=20))],
    )
    records = [DxfEntityRecord(handle="1", entity_type="LINE", raw_layer="Walls_  Normal-1", normalized_layer="Walls_  Normal", category="walls")]
    comparison = compare_plan_to_dxf(plan, "sweeter-build", "plan.dxf", records)
    assert comparison.dxf_categories == {"walls": 1}
    assert comparison.plan_categories == []
    assert comparison.findings == ["Coordinate-system and floor/view alignment require review before geometric comparison."]
