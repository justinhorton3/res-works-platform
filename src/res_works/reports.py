"""Review report assembly for a project and a selected rule profile."""

from collections.abc import Iterable

from .models import ObservedFact, Requirement, ValidationReport
from .validation import evaluate_requirements


def build_validation_report(
    project_id: str,
    rule_profile_id: str,
    requirements: Iterable[Requirement],
    facts: Iterable[ObservedFact],
) -> ValidationReport:
    selected = [item for item in requirements if item.rule_profile_id == rule_profile_id]
    return ValidationReport(
        project_id=project_id,
        rule_profile_id=rule_profile_id,
        results=evaluate_requirements(selected, facts),
    )
