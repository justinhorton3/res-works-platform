from datetime import date

import pytest
from pydantic import ValidationError

from res_works.models import (
    ApprovalStatus,
    CodeSource,
    ConstraintLevel,
    DocumentationItem,
    FactKind,
    ObservedFact,
    ProjectManifest,
    Recommendation,
    Requirement,
    RuleProfile,
)


def test_project_manifest_serializes_deterministically() -> None:
    manifest = ProjectManifest(id="sweeter-build", name="Sweeter Build")
    assert manifest.model_dump_json() == manifest.model_dump_json()
    assert manifest.chief_version == "X18"


def test_code_source_preserves_provenance() -> None:
    source = CodeSource(
        id="arkansas-afpc-2021",
        title="Arkansas Fire Prevention Code",
        publisher="Arkansas State Fire Marshal",
        edition="2021",
        jurisdiction="Arkansas",
        accessed_on=date(2026, 8, 29),
    )
    assert source.licensed_content is False
    assert source.edition == "2021"


def test_requirement_has_explicit_constraint_level() -> None:
    requirement = Requirement(
        id="egress-bedroom-window",
        rule_profile_id="arkansas-baseline",
        title="Sleeping room egress",
        level=ConstraintLevel.MUST,
        trigger="sleeping_room",
        requirement="Provide a compliant emergency escape and rescue opening",
        evidence_required=["window geometry", "clear opening"],
    )
    assert requirement.level is ConstraintLevel.MUST


def test_documentation_item_does_not_accept_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        DocumentationItem(
            id="note-001",
            title="General note",
            text="Coordinate work.",
            category="general_note",
            municipal_metadata="do not print",
        )


def test_recommendation_links_facts_and_library_content() -> None:
    fact = ObservedFact(
        id="fact-1", key="project.type", value="remodel", kind=FactKind.CONFIRMED
    )
    recommendation = Recommendation(
        id="rec-1",
        project_id="sweeter-build",
        documentation_item_id="note-existing-conditions",
        reason="The project is a remodel.",
        evidence_fact_ids=[fact.id],
        confidence="high",
        status=ApprovalStatus.PROPOSED,
    )
    assert recommendation.evidence_fact_ids == ["fact-1"]
