import json
from pathlib import Path

from agenteval.datasets.loader import load_dataset
from agenteval.evaluation.runner import run_evaluation

ROOT = Path(__file__).resolve().parents[2]


def test_end_to_end_agent_sample() -> None:
    dataset = load_dataset(ROOT / "data" / "datasets" / "sample_agent.json")
    traces = json.loads((ROOT / "data" / "sample_traces" / "agentos_ag001.json").read_text())
    run = run_evaluation(dataset, traces)
    assert run.case_results[0].passed is True
    assert run.case_results[0].errors == []
