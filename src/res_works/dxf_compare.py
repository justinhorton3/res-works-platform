"""Compare explicit plan expectations with DXF evidence conservatively."""

from collections import Counter
from collections.abc import Iterable

from .models import DxfEntityRecord, DxfPlanComparison, PlanGeometry


def compare_dimension_sets(sources: Iterable[dict[str, object]]) -> dict[str, object]:
    """Compare normalized DXF dimensions while retaining source provenance."""
    source_list = list(sources)
    values: dict[str, list[dict[str, object]]] = {}
    for source in source_list:
        for dimension in source.get("dimensions", []):
            normalized = dimension.get("normalized") or dimension.get("display_text")
            if normalized:
                values.setdefault(str(normalized), []).append({"filename": source["filename"], "handle": dimension.get("handle")})
    repeated = {value: items for value, items in values.items() if len(items) > 1}
    findings = []
    if len(source_list) > 1 and not repeated:
        findings.append("No repeated normalized dimensions were found across the supplied DXF sources.")
    return {"source_count": len(source_list), "repeated_dimensions": repeated, "finding_count": len(findings), "findings": findings}


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
