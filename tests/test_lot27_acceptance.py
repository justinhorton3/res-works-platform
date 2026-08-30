import json
from pathlib import Path

from res_works.fact_mapping import facts_from_geometry
from res_works.jurisdiction import load_rule_profiles, resolve_rule_profile
from res_works.plan_fixture import load_plan_geometry
from res_works.reports import build_validation_report
from res_works.rule_catalog import load_requirements, requirements_for_profile


ROOT = Path(__file__).parents[1]


def test_lot27_fixture_acceptance_has_geometry_and_conservative_validation() -> None:
    manifest = json.loads((ROOT / "projects/sweeter-build/manifest.json").read_text())
    plan = load_plan_geometry(ROOT / "projects/sweeter-build/plan.json")
    profiles = load_rule_profiles(ROOT / "reference/jurisdiction-profiles.json")
    profile = resolve_rule_profile(profiles, manifest["jurisdiction_profile_id"])
    facts = facts_from_geometry(plan, manifest["id"])
    requirements = requirements_for_profile(load_requirements(ROOT / "reference/arkansas-baseline-requirements.json"), profile.id)
    report = build_validation_report(manifest["id"], profile.id, requirements, facts, plan)

    assert len(plan.rooms) >= 7
    assert any(stair.width == 4.0 for stair in plan.stairs)
    assert report.project_id == "sweeter-build"
    assert profile.status == "needs_ahj_confirmation"
    assert report.counts["not_verified"] >= 1
