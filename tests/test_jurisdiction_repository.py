from pathlib import Path

from res_works.models import CodeSource, ConstraintLevel, Requirement, RuleProfile
from res_works.repository import ProjectRepository


def test_jurisdiction_records_round_trip_with_provenance(tmp_path: Path) -> None:
    repository = ProjectRepository(tmp_path / "res-works.sqlite3")
    source = CodeSource(
        id="arkansas-afpc-2021",
        title="Arkansas Fire Prevention Code",
        publisher="Arkansas State Fire Marshal",
        edition="2021",
        jurisdiction="Arkansas",
    )
    profile = RuleProfile(
        id="arkansas-baseline",
        jurisdiction="Arkansas",
        building_code="2021 Arkansas Fire Prevention Code",
        sources=[source.id],
        status="needs_ahj_confirmation",
    )
    requirement = Requirement(
        id="egress-review",
        rule_profile_id=profile.id,
        title="Egress review",
        level=ConstraintLevel.MUST,
        trigger="sleeping_room",
        requirement="Confirm emergency escape and rescue opening documentation.",
        source_id=source.id,
    )

    repository.save_code_source(source)
    repository.save_rule_profile(profile)
    repository.save_requirement(requirement)

    assert repository.get_code_source(source.id) == source
    assert repository.get_rule_profile(profile.id) == profile
    assert repository.get_requirement(requirement.id) == requirement
    repository.close()
