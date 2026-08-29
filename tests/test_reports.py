from res_works.models import ConstraintLevel, FactKind, ObservedFact, PlanGeometry, Rect, Requirement, Room, ValidationStatus
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


def test_report_includes_geometry_errors() -> None:
    plan = PlanGeometry(
        envelope=Rect(x=0, y=0, width=10, depth=10),
        rooms=[Room(id="bad", name="Bad", kind="room", geometry=Rect(x=9, y=9, width=2, depth=2))],
    )
    report = build_validation_report("p", "arkansas-baseline", [], [], plan)
    assert report.geometry_errors == ["room bad extends outside the envelope"]
