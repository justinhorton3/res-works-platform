"""Review report assembly for a project and a selected rule profile."""

from collections.abc import Iterable

from .models import ObservedFact, PlanGeometry, Requirement, ValidationReport
from .geometry import validate_geometry
from .validation import evaluate_requirements


def build_validation_report(
    project_id: str,
    rule_profile_id: str,
    requirements: Iterable[Requirement],
    facts: Iterable[ObservedFact],
    plan: PlanGeometry | None = None,
) -> ValidationReport:
    selected = [item for item in requirements if item.rule_profile_id == rule_profile_id]
    return ValidationReport(
        project_id=project_id,
        rule_profile_id=rule_profile_id,
        results=evaluate_requirements(selected, facts),
        geometry_errors=validate_geometry(plan) if plan else [],
    )
