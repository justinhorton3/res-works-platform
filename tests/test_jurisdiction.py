import pytest

from res_works.jurisdiction import classify_project, load_rule_profiles, resolve_rule_profile


def test_classification_preserves_county_and_municipality() -> None:
    classification = classify_project("remodel", county=" Benton ", municipality="Rogers")
    assert classification.project_type == "remodel"
    assert classification.county == "Benton"
    assert classification.municipality == "Rogers"


def test_unknown_project_type_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported project type"):
        classify_project("speculative", county="Benton")


def test_profiles_are_explicitly_resolved_and_unverified_profiles_remain_unverified() -> None:
    profiles = load_rule_profiles("reference/jurisdiction-profiles.json")
    profile = resolve_rule_profile(profiles, "washington-county-baseline")
    assert profile.status == "needs_ahj_confirmation"
    with pytest.raises(ValueError, match="Unknown jurisdiction profile"):
        resolve_rule_profile(profiles, "unknown")
