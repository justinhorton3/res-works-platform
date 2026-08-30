"""Jurisdiction profile loading and explicit project classification."""

import json
from pathlib import Path

from .models import ProjectClassification, RuleProfile


def load_rule_profiles(path: str | Path) -> list[RuleProfile]:
    return [
        RuleProfile.model_validate(record)
        for record in json.loads(Path(path).read_text(encoding="utf-8"))
    ]


def resolve_rule_profile(profiles: list[RuleProfile], profile_id: str) -> RuleProfile:
    for profile in profiles:
        if profile.id == profile_id:
            return profile
    raise ValueError(f"Unknown jurisdiction profile: {profile_id}")


def profile_scope(profile: RuleProfile) -> dict[str, object]:
    """Return explicit scope metadata for conservative rule evaluation."""
    return {
        "profile_id": profile.id,
        "county": profile.county,
        "municipality": profile.municipality,
        "building_code": profile.building_code,
        "source_ids": profile.sources,
        "profile_status": profile.status,
        "overlay_status": profile.overlay_status,
        "verified_for_approval": profile.status == "verified" and profile.overlay_status in {"none", "verified"},
    }


def classify_project(project_type: str, *, county: str, municipality: str | None = None) -> ProjectClassification:
    normalized = project_type.strip().lower()
    if normalized not in {"new_construction", "remodel", "addition"}:
        raise ValueError(f"Unsupported project type: {project_type}")
    return ProjectClassification(
        project_type=normalized,
        county=county.strip(),
        municipality=municipality.strip() if municipality else None,
    )
