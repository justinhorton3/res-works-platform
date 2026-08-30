from res_works.handoff import apply_decisions, build_change_set, build_chief_handoff, render_handoff_markdown
from res_works.models import ApprovalDecision, ApprovalStatus, Recommendation


def test_handoff_contains_only_explicitly_approved_recommendations() -> None:
    recommendations = [
        Recommendation(
            id="rec-egress", project_id="sweeter-build",
            documentation_item_id="callout-egress-review", reason="egress review",
        ),
        Recommendation(
            id="rec-note", project_id="sweeter-build",
            documentation_item_id="note-existing-conditions", reason="remodel note",
        ),
    ]
    decided = apply_decisions(
        recommendations,
        [ApprovalDecision(recommendation_id="rec-egress", decision="approve", decided_by="designer")],
    )
    change_set = build_change_set("sweeter-build", "snapshot-1", decided)
    handoff = build_chief_handoff(change_set, recommendations=recommendations)

    assert change_set.recommendation_ids == ["rec-egress"]
    assert change_set.status == "draft"
    assert handoff.native_write_performed is False
    assert handoff.recommendation_ids == ["rec-egress"]
    assert handoff.items[0]["id"] == "rec-egress"
    markdown = render_handoff_markdown(handoff)
    assert "Approved items" in markdown
    assert "rec-egress" in markdown
    assert "Native file write performed: **No**" in markdown
    assert decided[1].status is ApprovalStatus.PROPOSED


def test_change_set_id_is_reproducible() -> None:
    recommendation = Recommendation(
        id="rec-1", project_id="p", documentation_item_id="item", reason="reason",
        status=ApprovalStatus.APPROVED,
    )
    first = build_change_set("p", "snapshot", [recommendation])
    second = build_change_set("p", "snapshot", [recommendation])
    assert first.id == second.id
