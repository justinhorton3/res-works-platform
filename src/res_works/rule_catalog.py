"""Load RES-authored rule summaries without bundling copyrighted code text."""

import json
from pathlib import Path

from .models import Requirement


def load_requirements(path: str | Path) -> list[Requirement]:
    records = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Requirement.model_validate(record) for record in records]
