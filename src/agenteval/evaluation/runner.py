from __future__ import annotations

import uuid
from typing import Any

from agenteval.core.enums import EvaluationRunStatus
from agenteval.core.exceptions import EvaluatorNotFoundError
from agenteval.core.models import CaseEvaluationResult, EvaluationRun, MetricResult, utc_now_iso
from agenteval.datasets.models import EvaluationCase, EvaluationDataset
from agenteval.evaluation.aggregator import aggregate_case_metrics, aggregate_run_metrics
from agenteval.evaluators.registry import build_default_registry
from agenteval.traces.normalizer import normalize_trace
from agenteval.traces.schema import ExecutionTrace


def run_evaluation(
    dataset: EvaluationDataset,
    traces_by_case_id: dict[str, dict[str, Any]],
    *,
    evaluation_run_id: str | None = None,
) -> EvaluationRun:
    run_id = evaluation_run_id or str(uuid.uuid4())
    registry = build_default_registry()
    case_results: list[CaseEvaluationResult] = []

    for case in dataset.cases:
        raw = traces_by_case_id.get(case.id)
        if raw is None:
            case_results.append(
                CaseEvaluationResult(case_id=case.id, errors=[f"no trace for case {case.id}"])
            )
            continue
        try:
            trace = normalize_trace(raw)
            metrics = _run_case_metrics(case, trace, registry)
            overall, passed = aggregate_case_metrics(metrics)
            case_results.append(
                CaseEvaluationResult(
                    case_id=case.id,
                    trace_id=trace.run_id,
                    metrics=metrics,
                    overall_score=overall,
                    passed=passed,
                )
            )
        except Exception as exc:
            case_results.append(CaseEvaluationResult(case_id=case.id, errors=[str(exc)]))

    return EvaluationRun(
        evaluation_run_id=run_id,
        dataset_id=dataset.dataset_id,
        status=EvaluationRunStatus.COMPLETED,
        completed_at=utc_now_iso(),
        case_results=case_results,
        aggregate_metrics=aggregate_run_metrics(case_results),
    )


def _run_case_metrics(
    case: EvaluationCase,
    trace: ExecutionTrace,
    registry: dict,
) -> list[MetricResult]:
    metrics_to_run = case.evaluation.metrics or list(registry.keys())
    results: list[MetricResult] = []
    for name in metrics_to_run:
        evaluator = registry.get(name)
        if evaluator is None:
            results.append(
                MetricResult(
                    metric=name,
                    score=0.0,
                    passed=False,
                    skipped=True,
                    skip_reason=f"unknown metric {name}",
                )
            )
            continue
        results.append(evaluator.evaluate(case, trace))
    return results
