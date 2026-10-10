from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException

from agenteval.api.schemas import (
    EvaluationCreateRequest,
    EvaluationCreateResponse,
    RegressionRequest,
    RunDetailResponse,
    TraceIngestRequest,
)
from agenteval.core.enums import EvaluationRunStatus
from agenteval.core.models import EvaluationRun, utc_now_iso
from agenteval.datasets.loader import load_dataset
from agenteval.evaluation.regression import RegressionThresholds, compare_runs
from agenteval.evaluation.runner import run_evaluation
from agenteval.evaluation.trace_sources import resolve_traces_by_case_id

router = APIRouter()


def _store():
    from agenteval.api.app import get_store

    return get_store()


@router.post("/traces")
def ingest_trace(body: TraceIngestRequest) -> dict:
    trace = _store().save_trace(body.raw_trace, trace_id=body.trace_id)
    return {"run_id": trace.run_id, "system": trace.system}


@router.get("/traces/{run_id}")
def get_trace(run_id: str) -> dict:
    trace = _store().get_trace(run_id)
    if not trace:
        raise HTTPException(status_code=404, detail="trace not found")
    return trace.model_dump(mode="json")


def _execute_evaluation(run_id: str, dataset, traces: dict) -> None:
    store = _store()
    try:
        store.save_run(run_evaluation(dataset, traces, evaluation_run_id=run_id))
    except Exception as exc:
        store.save_run(
            EvaluationRun(
                evaluation_run_id=run_id,
                dataset_id=dataset.dataset_id,
                status=EvaluationRunStatus.FAILED,
                completed_at=utc_now_iso(),
                error=str(exc),
            )
        )


@router.post("/evaluations/run", response_model=EvaluationCreateResponse, status_code=202)
def evaluations_run(body: EvaluationCreateRequest, background_tasks: BackgroundTasks) -> EvaluationCreateResponse:
    store = _store()
    if body.dataset_id:
        dataset = store.get_dataset(body.dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="dataset not found")
    elif body.dataset_path:
        dataset = load_dataset(Path(body.dataset_path))
        store.save_dataset(dataset)
    else:
        raise HTTPException(status_code=400, detail="dataset_id or dataset_path required")

    traces = resolve_traces_by_case_id(body.case_traces, store=store)
    run_id = str(uuid.uuid4())
    store.save_run(
        EvaluationRun(
            evaluation_run_id=run_id,
            dataset_id=dataset.dataset_id,
            status=EvaluationRunStatus.QUEUED,
        )
    )
    background_tasks.add_task(_execute_evaluation, run_id, dataset, traces)
    return EvaluationCreateResponse(evaluation_run_id=run_id, status="queued")


@router.get("/evaluations/{evaluation_id}", response_model=RunDetailResponse)
def get_evaluation(evaluation_id: str) -> RunDetailResponse:
    run = _store().get_run(evaluation_id)
    if not run:
        raise HTTPException(status_code=404, detail="evaluation not found")
    return RunDetailResponse(run=run)


@router.get("/evaluations/{evaluation_id}/results")
def get_evaluation_results(evaluation_id: str) -> dict:
    run = _store().get_run(evaluation_id)
    if not run:
        raise HTTPException(status_code=404, detail="evaluation not found")
    return {
        "evaluation_run_id": run.evaluation_run_id,
        "status": run.status,
        "aggregate_metrics": [a.model_dump(mode="json") for a in run.aggregate_metrics],
        "cases": [c.model_dump(mode="json") for c in run.case_results],
        "overall": _overall_from_run(run),
    }


@router.post("/regression/run")
def regression_run(body: RegressionRequest) -> dict:
    store = _store()
    baseline = store.get_run(body.baseline_run_id)
    candidate = store.get_run(body.candidate_run_id)
    if not baseline or not candidate:
        raise HTTPException(status_code=404, detail="baseline or candidate run not found")
    threshold_models = [
        RegressionThresholds(
            metric=t.metric,
            max_score_drop=t.max_score_drop,
            min_pass_rate=t.min_pass_rate,
            max_latency_increase_ratio=t.max_latency_increase_ratio,
        )
        for t in body.thresholds
    ]
    return compare_runs(baseline, candidate, thresholds=threshold_models or None).model_dump(mode="json")


def _overall_from_run(run: EvaluationRun) -> float | None:
    scores = [c.overall_score for c in run.case_results if c.overall_score is not None]
    if not scores:
        return None
    return round(sum(scores) / len(scores), 4)
