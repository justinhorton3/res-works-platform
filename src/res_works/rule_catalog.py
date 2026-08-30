"""Load RES-authored rule summaries without bundling copyrighted code text."""

import json
from pathlib import Path

from .models import Requirement


def load_requirements(path: str | Path) -> list[Requirement]:
    records = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Requirement.model_validate(record) for record in records]


def requirements_for_profile(requirements: list[Requirement], profile_id: str) -> list[Requirement]:
    """Apply shared baseline requirements to a selected county profile."""
    selected = [item for item in requirements if item.rule_profile_id == profile_id]
    if selected:
        return selected
    baseline = [item for item in requirements if item.rule_profile_id == "arkansas-baseline"]
    return [item.model_copy(update={"rule_profile_id": profile_id}) for item in baseline]
