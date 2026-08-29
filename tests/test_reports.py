from res_works.models import ConstraintLevel, FactKind, ObservedFact, Requirement, ValidationStatus
from res_works.reports import build_validation_report


def test_report_evaluates_only_selected_profile_and_counts_statuses() -> None:
    requirements = [
        Requirement(
            id="r1", rule_profile_id="arkansas-baseline", title="Egress", level=ConstraintLevel.MUST,
            trigger="room.type=sleeping_room", requirement="Review", evidence_required=["window.clear_opening"],
        ),
        Requirement(
            id="r2", rule_profile_id="other", title="Other", level=ConstraintLevel.MUST,
            trigger="room.type=sleeping_room", requirement="Review",
        ),
    ]
    facts = [ObservedFact(id="f1", key="room.type", value="sleeping_room", kind=FactKind.OBSERVED)]
    report = build_validation_report("sweeter-build", "arkansas-baseline", requirements, facts)

    assert len(report.results) == 1
    assert report.results[0].status is ValidationStatus.NOT_VERIFIED
    assert report.counts == {"not_verified": 1}
