"""Compare explicit plan expectations with DXF evidence conservatively."""

from collections import Counter
from collections.abc import Iterable

from .models import DxfEntityRecord, DxfPlanComparison, PlanGeometry


def compare_plan_to_dxf(
    plan: PlanGeometry, plan_id: str, dxf_filename: str, records: Iterable[DxfEntityRecord]
) -> DxfPlanComparison:
    records = list(records)
    categories = Counter(record.category for record in records)
    expected = {"walls", "doors", "windows", "stairs", "cabinets"}
    plan_categories = set()
    if plan.walls:
        plan_categories.add("walls")
    if plan.openings:
        plan_categories.update(opening.kind + "s" for opening in plan.openings)
    if plan.stairs:
        plan_categories.add("stairs")
    findings = [
        f"DXF has no extracted {category} records"
        for category in sorted(expected)
        if category in plan_categories and not categories.get(category)
    ]
    findings.append("Coordinate-system and floor/view alignment require review before geometric comparison.")
    return DxfPlanComparison(
        plan_id=plan_id,
        dxf_filename=dxf_filename,
        plan_categories=sorted(plan_categories),
        dxf_categories=dict(sorted(categories.items())),
        findings=findings,
    )
