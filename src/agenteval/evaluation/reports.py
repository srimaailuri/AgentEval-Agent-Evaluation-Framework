from __future__ import annotations

import json
from pathlib import Path

from agenteval.core.models import EvaluationRun


def write_json_report(run: EvaluationRun, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(run.model_dump(mode="json"), indent=2), encoding="utf-8")
