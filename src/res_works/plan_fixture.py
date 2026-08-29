"""Load explicit plan geometry fixtures for regression and review."""

import json
from pathlib import Path

from .models import PlanGeometry


def load_plan_geometry(path: str | Path) -> PlanGeometry:
    return PlanGeometry.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))
