import pytest

from res_works.jurisdiction import classify_project, load_rule_profiles, profile_scope, resolve_rule_profile


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


def test_all_profiles_require_explicit_ahj_confirmation() -> None:
    profiles = load_rule_profiles("reference/jurisdiction-profiles.json")
    assert {profile.status for profile in profiles} == {"needs_ahj_confirmation"}


def test_municipal_profiles_identify_inherited_county_and_pending_overlay() -> None:
    profiles = load_rule_profiles("reference/jurisdiction-profiles.json")
    profile = resolve_rule_profile(profiles, "benton-bentonville-overlay")
    assert profile.municipality == "Bentonville"
    assert profile.inherits_profile_id == "benton-county-baseline"
    assert profile.overlay_status == "pending"


def test_profile_scope_never_marks_pending_overlay_verified() -> None:
    profile = resolve_rule_profile(load_rule_profiles("reference/jurisdiction-profiles.json"), "benton-bentonville-overlay")
    scope = profile_scope(profile)
    assert scope["source_ids"] == ["arkansas-afpc-2021", "benton-county-regulations"]
    assert scope["verified_for_approval"] is False
