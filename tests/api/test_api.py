from pathlib import Path

from fastapi.testclient import TestClient

from agenteval.api.app import app
from agenteval.storage.store import EvaluationStore


def test_health_and_ready() -> None:
    client = TestClient(app)
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/ready").json()["ready"] is True


def test_trace_ingest_and_dataset(tmp_path: Path, monkeypatch) -> None:
    db = tmp_path / "test.db"
    store = EvaluationStore(db_path=db)
    app.dependency_overrides = {}
    monkeypatch.setattr("agenteval.api.app.get_store", lambda: store)
    client = TestClient(app)
    resp = client.post(
        "/traces",
        json={
            "raw_trace": {
                "run_id": "t1",
                "system": "generic",
                "input": "hello",
                "final_answer": "hello",
                "status": "completed",
            }
        },
    )
    assert resp.status_code == 200
    assert resp.json()["run_id"] == "t1"


def test_evaluation_from_stored_trace(tmp_path: Path, monkeypatch) -> None:
    db = tmp_path / "eval.db"
    store = EvaluationStore(db_path=db)
    monkeypatch.setattr("agenteval.api.app.get_store", lambda: store)
    client = TestClient(app)

    store.save_trace(
        {
            "run_id": "stored-run",
            "system": "agentos",
            "input": "hello",
            "steps": [{"step": 1, "tool": "web_search", "status": "success"}],
            "final_answer": "hello world",
            "status": "completed",
        }
    )
    dataset_path = tmp_path / "ds.json"
    dataset_path.write_text(
        """
{
  "dataset_id": "mini",
  "cases": [{
    "id": "c1",
    "input": {"question": "hello"},
    "expected": {"tools": ["web"]},
    "evaluation": {"metrics": ["tool_selection_accuracy", "task_completion"]}
  }]
}
""".strip(),
        encoding="utf-8",
    )

    create = client.post(
        "/evaluations/run",
        json={
            "dataset_path": str(dataset_path),
            "case_traces": [{"case_id": "c1", "run_id": "stored-run"}],
        },
    )
    assert create.status_code == 202
    eval_id = create.json()["evaluation_run_id"]

    import time

    for _ in range(40):
        detail = client.get(f"/evaluations/{eval_id}").json()
        if detail["run"]["status"] != "queued":
            break
        time.sleep(0.05)

    results = client.get(f"/evaluations/{eval_id}/results")
    assert results.status_code == 200
    assert results.json()["cases"][0]["case_id"] == "c1"
    assert results.json()["cases"][0]["errors"] == []
