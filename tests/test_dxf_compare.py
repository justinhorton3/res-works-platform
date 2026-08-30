from res_works.dxf_compare import compare_dimension_sets, compare_plan_to_dxf
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


def test_dimension_sets_preserve_repeated_source_handles() -> None:
    result = compare_dimension_sets([
        {"filename": "full.dxf", "dimensions": [{"normalized": '28\'- 8"', "handle": "A"}]},
        {"filename": "sheet.dxf", "dimensions": [{"normalized": '28\'- 8"', "handle": "B"}]},
    ])
    assert result["repeated_dimensions"]['28\'- 8"'] == [{"filename": "full.dxf", "handle": "A"}, {"filename": "sheet.dxf", "handle": "B"}]
    assert result["matched_source_count"] == 2
    assert result["finding_details"] == []


def test_dimension_sets_report_unmatched_source_without_calling_it_a_conflict() -> None:
    result = compare_dimension_sets([
        {"filename": "full.dxf", "dimensions": [{"normalized": '28\'- 8"', "handle": "A"}]},
        {"filename": "sheet.dxf", "dimensions": [{"normalized": '30\'- 0"', "handle": "B"}]},
    ])
    assert result["repeated_dimensions"] == {}
    assert result["finding_details"][0]["code"] == "no_cross_source_matches"
    assert result["finding_details"][0]["severity"] == "warning"
