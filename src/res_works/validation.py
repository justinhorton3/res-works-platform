"""Conservative, deterministic evaluation of structured project facts."""

from collections.abc import Iterable

from .models import FactKind, ObservedFact, Requirement, ValidationResult, ValidationStatus


def evaluate_requirement(
    requirement: Requirement, facts: Iterable[ObservedFact]
) -> ValidationResult:
    available = list(facts)
    trigger_key, _, trigger_value = requirement.trigger.partition("=")
    triggered = [
        fact
        for fact in available
        if fact.key == trigger_key
        and (not trigger_value or str(fact.value) == trigger_value)
    ]
    if not triggered:
        return ValidationResult(
            requirement_id=requirement.id,
            status=ValidationStatus.NOT_APPLICABLE,
            message="Trigger condition is not present in the supplied facts.",
            source_id=requirement.source_id,
        )

    matched = [fact for fact in available if fact.key in requirement.evidence_required]
    missing = [key for key in requirement.evidence_required if key not in {fact.key for fact in matched}]
    evidence_ids = [fact.id for fact in triggered + matched]
    if missing or any(fact.kind in (FactKind.UNKNOWN, FactKind.INFERRED) for fact in matched):
        detail = f"Missing evidence: {', '.join(missing)}." if missing else "Evidence requires confirmation."
        return ValidationResult(
            requirement_id=requirement.id,
            status=ValidationStatus.NOT_VERIFIED,
            message=detail,
            evidence_fact_ids=evidence_ids,
            source_id=requirement.source_id,
        )
    return ValidationResult(
        requirement_id=requirement.id,
        status=ValidationStatus.PASS,
        message="Required evidence is present; professional review remains required.",
        evidence_fact_ids=evidence_ids,
        source_id=requirement.source_id,
    )


def evaluate_requirements(
    requirements: Iterable[Requirement], facts: Iterable[ObservedFact]
) -> list[ValidationResult]:
    fact_list = list(facts)
    return [evaluate_requirement(requirement, fact_list) for requirement in requirements]
