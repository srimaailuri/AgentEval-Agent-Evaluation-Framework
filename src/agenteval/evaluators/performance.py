from __future__ import annotations

from agenteval.core.models import MetricResult
from agenteval.datasets.models import EvaluationCase
from agenteval.evaluators.base import Evaluator
from agenteval.traces.schema import ExecutionTrace


class LatencyEvaluator(Evaluator):
    name = "latency_ms"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        latency_ms = float(trace.usage.latency_ms or 0.0)
        max_ms = case.evaluation.thresholds.get("latency_max_ms", 120_000.0)
        passed = latency_ms <= max_ms
        return MetricResult(
            metric=self.name,
            score=1.0 if passed else 0.0,
            passed=passed,
            details={"latency_ms": latency_ms, "latency_max_ms": max_ms},
        )


class TokenUsageEvaluator(Evaluator):
    name = "total_tokens"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        total = trace.usage.input_tokens + trace.usage.output_tokens
        max_tokens = case.evaluation.thresholds.get("token_max", 0)
        passed = total <= max_tokens if max_tokens > 0 else True
        return MetricResult(
            metric=self.name,
            score=1.0 if passed else 0.0,
            passed=passed,
            details={"input_tokens": trace.usage.input_tokens, "output_tokens": trace.usage.output_tokens, "total": total},
        )


class CostPerSuccessfulTaskEvaluator(Evaluator):
    name = "cost_per_successful_task"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        cost = float(trace.usage.estimated_cost or 0.0)
        success = trace.status == "completed" and bool(trace.final_answer.strip())
        if not success:
            return MetricResult(metric=self.name, score=0.0, passed=False, details={"completed": False})
        max_cost = case.evaluation.thresholds.get("cost_max_usd", 0.0)
        passed = cost <= max_cost if max_cost > 0 else True
        return MetricResult(
            metric=self.name,
            score=1.0 if passed else 0.0,
            passed=passed,
            details={"estimated_cost": cost, "completed": True},
        )


class EstimatedCostEvaluator(Evaluator):
    name = "estimated_cost"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        cost = float(trace.usage.estimated_cost or 0.0)
        max_cost = case.evaluation.thresholds.get("cost_max_usd", 0.0)
        passed = cost <= max_cost if max_cost > 0 else True
        return MetricResult(
            metric=self.name,
            score=1.0 if passed else 0.0,
            passed=passed,
            details={"estimated_cost": cost},
        )
