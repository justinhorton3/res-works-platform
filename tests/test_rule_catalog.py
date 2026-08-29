from pathlib import Path

from res_works.rule_catalog import load_requirements


def test_arkansas_baseline_catalog_is_explicit_and_source_linked() -> None:
    path = Path("reference/arkansas-baseline-requirements.json")
    requirements = load_requirements(path)
    assert len(requirements) == 4
    assert all(item.rule_profile_id == "arkansas-baseline" for item in requirements)
    assert all(item.source_id == "arkansas-afpc-2021" for item in requirements)
    assert all(item.evidence_required for item in requirements)
