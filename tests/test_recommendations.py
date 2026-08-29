from res_works.models import DocumentationItem, FactKind, ObservedFact
from res_works.recommendations import recommend_documentation


def test_recommendations_are_deterministic_and_evidence_linked() -> None:
    item = DocumentationItem(
        id="note-remodel", title="Remodel note", text="Verify existing conditions.",
        category="general_note", applies_when=["project.type=remodel"],
    )
    facts = [ObservedFact(id="f1", key="project.type", value="remodel", kind=FactKind.CONFIRMED, confidence="high")]
    first = recommend_documentation("p-1", [item], facts)
    second = recommend_documentation("p-1", [item], facts)
    assert first == second
    assert first[0].evidence_fact_ids == ["f1"]
    assert first[0].id.startswith("rec-")


def test_unmatched_applicability_is_not_recommended() -> None:
    item = DocumentationItem(
        id="note-remodel", title="Remodel note", text="Verify.",
        category="general_note", applies_when=["project.type=remodel"],
    )
    facts = [ObservedFact(id="f1", key="project.type", value="new", kind=FactKind.CONFIRMED)]
    assert recommend_documentation("p-1", [item], facts) == []
