from pathlib import Path

from agenteval.datasets.loader import load_dataset

ROOT = Path(__file__).resolve().parents[2]


def test_load_sample_agent_dataset() -> None:
    dataset = load_dataset(ROOT / "data" / "datasets" / "sample_agent.json")
    assert dataset.dataset_id == "sample_agent"
    assert len(dataset.cases) == 1
    assert dataset.cases[0].id == "AG001"
