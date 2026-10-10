from __future__ import annotations

from collections import defaultdict

from agenteval.core.models import AggregateMetrics, CaseEvaluationResult, MetricResult


def aggregate_case_metrics(metrics: list[MetricResult]) -> tuple[float | None, bool | None]:
    scored = [m for m in metrics if not m.skipped]
    if not scored:
        return None, None
    mean = sum(m.score for m in scored) / len(scored)
    passed = all(m.passed for m in scored)
    return round(mean, 4), passed


def aggregate_run_metrics(case_results: list[CaseEvaluationResult]) -> list[AggregateMetrics]:
    buckets: dict[str, list[MetricResult]] = defaultdict(list)
    for case in case_results:
        for metric in case.metrics:
            if not metric.skipped:
                buckets[metric.metric].append(metric)
    return [
        AggregateMetrics(
            metric=name,
            mean_score=round(sum(m.score for m in items) / len(items), 4),
            pass_rate=round(sum(1 for m in items if m.passed) / len(items), 4),
            count=len(items),
        )
        for name, items in sorted(buckets.items())
    ]
