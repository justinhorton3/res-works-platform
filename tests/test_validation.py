from res_works.models import ConstraintLevel, FactKind, ObservedFact, Requirement, ValidationStatus
from res_works.validation import evaluate_requirement, evaluate_requirements


def requirement() -> Requirement:
    return Requirement(
        id="egress-review",
        rule_profile_id="arkansas-baseline",
        title="Egress review",
        level=ConstraintLevel.MUST,
        trigger="room.type=sleeping_room",
        requirement="Confirm emergency escape and rescue opening documentation.",
        evidence_required=["window.clear_opening", "window.sill_height"],
        source_id="arkansas-afpc-2021",
    )


def test_missing_evidence_never_passes() -> None:
    facts = [ObservedFact(id="room-1", key="room.type", value="sleeping_room", kind=FactKind.OBSERVED)]
    result = evaluate_requirement(requirement(), facts)
    assert result.status is ValidationStatus.NOT_VERIFIED


def test_complete_confirmed_evidence_passes_with_provenance() -> None:
    facts = [
        ObservedFact(id="room-1", key="room.type", value="sleeping_room", kind=FactKind.CONFIRMED),
        ObservedFact(id="window-1", key="window.clear_opening", value="5.7", kind=FactKind.CONFIRMED),
        ObservedFact(id="window-2", key="window.sill_height", value="42", kind=FactKind.CONFIRMED),
    ]
    result = evaluate_requirement(requirement(), facts)
    assert result.status is ValidationStatus.PASS
    assert result.source_id == "arkansas-afpc-2021"
    assert result.evidence_fact_ids == ["room-1", "window-1", "window-2"]


def test_non_triggered_requirement_is_not_applicable() -> None:
    facts = [ObservedFact(id="room-1", key="room.type", value="living_room", kind=FactKind.OBSERVED)]
    result = evaluate_requirements([requirement()], facts)[0]
    assert result.status is ValidationStatus.NOT_APPLICABLE


def test_inferred_evidence_requires_confirmation() -> None:
    facts = [
        ObservedFact(id="room-1", key="room.type", value="sleeping_room", kind=FactKind.OBSERVED),
        ObservedFact(id="window-1", key="window.clear_opening", value="5.7", kind=FactKind.INFERRED),
        ObservedFact(id="window-2", key="window.sill_height", value="42", kind=FactKind.CONFIRMED),
    ]
    assert evaluate_requirement(requirement(), facts).status is ValidationStatus.NOT_VERIFIED
