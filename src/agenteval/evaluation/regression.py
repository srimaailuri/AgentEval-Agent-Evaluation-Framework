from __future__ import annotations

from pydantic import BaseModel, Field

from agenteval.core.models import EvaluationRun


class RegressionThresholds(BaseModel):
    metric: str
    max_score_drop: float = 0.05
    min_pass_rate: float = 0.8
    max_latency_increase_ratio: float = 0.2


class RegressionComparison(BaseModel):
    baseline_run_id: str
    candidate_run_id: str
    regressions: list[str] = Field(default_factory=list)
    passed: bool = True
    details: dict[str, dict[str, float]] = Field(default_factory=dict)


def compare_runs(
    baseline: EvaluationRun,
    candidate: EvaluationRun,
    thresholds: list[RegressionThresholds] | None = None,
) -> RegressionComparison:
    thresholds = thresholds or []
    threshold_by_metric = {t.metric: t for t in thresholds}
    base_map = {a.metric: a for a in baseline.aggregate_metrics}
    cand_map = {a.metric: a for a in candidate.aggregate_metrics}
    regressions: list[str] = []
    details: dict[str, dict[str, float]] = {}

    for metric, base_agg in base_map.items():
        cand_agg = cand_map.get(metric)
        if not cand_agg:
            continue
        drop = base_agg.mean_score - cand_agg.mean_score
        details[metric] = {
            "baseline_mean": base_agg.mean_score,
            "candidate_mean": cand_agg.mean_score,
            "score_drop": round(drop, 4),
            "baseline_pass_rate": base_agg.pass_rate,
            "candidate_pass_rate": cand_agg.pass_rate,
        }
        rule = threshold_by_metric.get(metric)
        if rule and drop > rule.max_score_drop:
            regressions.append(f"{metric}: score dropped by {drop:.4f}")
        if rule and cand_agg.pass_rate < rule.min_pass_rate:
            regressions.append(f"{metric}: pass_rate below threshold")

    return RegressionComparison(
        baseline_run_id=baseline.evaluation_run_id,
        candidate_run_id=candidate.evaluation_run_id,
        regressions=regressions,
        passed=len(regressions) == 0,
        details=details,
    )
