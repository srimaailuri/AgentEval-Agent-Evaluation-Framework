import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_researchflow_and_agentos_case_files_have_ten_each() -> None:
    rf = json.loads((ROOT / "data" / "researchflow" / "cases.json").read_text(encoding="utf-8"))
    ao = json.loads((ROOT / "data" / "agentos" / "cases.json").read_text(encoding="utf-8"))
    assert len(rf) == 10
    assert len(ao) == 10
