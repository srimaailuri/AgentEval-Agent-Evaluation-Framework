from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any

from agenteval.config import get_settings
from agenteval.core.models import EvaluationRun
from agenteval.datasets.models import EvaluationDataset
from agenteval.traces.normalizer import normalize_trace
from agenteval.traces.schema import ExecutionTrace


class EvaluationStore:
    """SQLite-backed persistence for datasets, traces, and evaluation runs."""

    def __init__(self, db_path: Path | None = None) -> None:
        settings = get_settings()
        if db_path is None:
            url = settings.database_url
            if url.startswith("sqlite:///"):
                db_path = Path(url.replace("sqlite:///", ""))
            else:
                db_path = settings.data_dir / "agenteval.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._path = db_path
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS datasets (
                    dataset_id TEXT PRIMARY KEY,
                    version TEXT,
                    payload TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS traces (
                    trace_id TEXT PRIMARY KEY,
                    system TEXT,
                    payload TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS evaluation_runs (
                    evaluation_run_id TEXT PRIMARY KEY,
                    dataset_id TEXT,
                    status TEXT,
                    payload TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    def save_dataset(self, dataset: EvaluationDataset) -> str:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO datasets (dataset_id, version, payload) VALUES (?, ?, ?)",
                (dataset.dataset_id, dataset.version, dataset.model_dump_json()),
            )
        return dataset.dataset_id

    def get_dataset(self, dataset_id: str) -> EvaluationDataset | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT payload FROM datasets WHERE dataset_id = ?", (dataset_id,)
            ).fetchone()
        if not row:
            return None
        return EvaluationDataset.model_validate_json(row["payload"])

    def save_trace(self, raw: dict[str, Any], trace_id: str | None = None) -> ExecutionTrace:
        trace = normalize_trace(raw)
        tid = trace_id or trace.run_id or str(uuid.uuid4())
        trace = trace.model_copy(update={"run_id": tid})
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO traces (trace_id, system, payload) VALUES (?, ?, ?)",
                (tid, trace.system, trace.model_dump_json()),
            )
        return trace

    def get_trace(self, trace_id: str) -> ExecutionTrace | None:
        with self._connect() as conn:
            row = conn.execute("SELECT payload FROM traces WHERE trace_id = ?", (trace_id,)).fetchone()
        if not row:
            return None
        return ExecutionTrace.model_validate_json(row["payload"])

    def save_run(self, run: EvaluationRun) -> str:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO evaluation_runs
                (evaluation_run_id, dataset_id, status, payload)
                VALUES (?, ?, ?, ?)
                """,
                (
                    run.evaluation_run_id,
                    run.dataset_id,
                    str(run.status),
                    run.model_dump_json(),
                ),
            )
        return run.evaluation_run_id

    def get_run(self, evaluation_run_id: str) -> EvaluationRun | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT payload FROM evaluation_runs WHERE evaluation_run_id = ?",
                (evaluation_run_id,),
            ).fetchone()
        if not row:
            return None
        return EvaluationRun.model_validate_json(row["payload"])

    def list_runs(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT evaluation_run_id FROM evaluation_runs ORDER BY created_at DESC"
            ).fetchall()
        return [r["evaluation_run_id"] for r in rows]
