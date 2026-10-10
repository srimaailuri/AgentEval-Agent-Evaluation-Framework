from __future__ import annotations

from agenteval.core.models import MetricResult
from agenteval.datasets.models import EvaluationCase
from agenteval.evaluators.base import Evaluator
from agenteval.evaluators.utils import tool_capabilities
from agenteval.traces.schema import ExecutionTrace


class ToolSelectionEvaluator(Evaluator):
    name = "tool_selection_accuracy"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        expected = {t.lower() for t in case.expected.tools if t.strip()}
        if not expected:
            return MetricResult(metric=self.name, score=1.0, passed=True, details={"note": "no expected tools"})
        actual = tool_capabilities(trace)
        hits = expected & actual
        score = len(hits) / len(expected)
        return MetricResult(
            metric=self.name,
            score=round(score, 4),
            passed=score >= case.evaluation.thresholds.get(self.name, 1.0),
            details={"expected": sorted(expected), "actual": sorted(actual)},
        )


class ToolCallSuccessEvaluator(Evaluator):
    name = "tool_success_rate"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        if not trace.steps:
            return MetricResult(metric=self.name, score=1.0, passed=True, details={"total": 0})
        success = sum(1 for s in trace.steps if s.status == "success")
        score = success / len(trace.steps)
        return MetricResult(
            metric=self.name,
            score=round(score, 4),
            passed=score >= case.evaluation.thresholds.get(self.name, 1.0),
            details={"successful": success, "total": len(trace.steps)},
        )


class TaskCompletionEvaluator(Evaluator):
    name = "task_completion"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        completed = trace.status == "completed" and bool(trace.final_answer.strip())
        if case.expected.task_completed is None:
            score = 1.0 if completed else 0.0
        else:
            score = 1.0 if completed == case.expected.task_completed else 0.0
        return MetricResult(
            metric=self.name,
            score=score,
            passed=score >= case.evaluation.thresholds.get(self.name, 1.0),
            details={"status": trace.status},
        )


class ToolArgumentCorrectnessEvaluator(Evaluator):
    name = "tool_argument_correctness"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        expected_by_tool = case.expected.tool_arguments
        if not expected_by_tool:
            return MetricResult(metric=self.name, score=1.0, passed=True, details={"note": "no expected arguments"})
        checks: list[bool] = []
        details: dict[str, dict] = {}
        for step in trace.steps:
            exp = expected_by_tool.get(step.tool) or expected_by_tool.get(_short_tool(step.tool))
            if not exp:
                continue
            ok = all(step.arguments.get(k) == v for k, v in exp.items())
            checks.append(ok)
            details[step.tool] = {"expected": exp, "actual": step.arguments, "match": ok}
        if not checks:
            return MetricResult(metric=self.name, score=0.0, passed=False, details={"error": "no matching tool steps"})
        score = sum(checks) / len(checks)
        return MetricResult(
            metric=self.name,
            score=round(score, 4),
            passed=score >= case.evaluation.thresholds.get(self.name, 1.0),
            details=details,
        )


class TrajectoryQualityEvaluator(Evaluator):
    name = "trajectory_quality"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        tools = [s.tool for s in trace.steps]
        if len(tools) <= 1:
            return MetricResult(metric=self.name, score=1.0, passed=True, details={"tools": tools})
        repeats = sum(1 for i in range(1, len(tools)) if tools[i] == tools[i - 1])
        penalty = repeats / max(len(tools) - 1, 1)
        score = max(0.0, 1.0 - penalty)
        return MetricResult(
            metric=self.name,
            score=round(score, 4),
            passed=score >= case.evaluation.thresholds.get(self.name, 0.5),
            details={"tools": tools, "consecutive_repeats": repeats},
        )


class FailureRecoveryEvaluator(Evaluator):
    name = "failure_recovery"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        statuses = [s.status for s in trace.steps]
        if not statuses:
            return MetricResult(metric=self.name, score=1.0, passed=True, details={"note": "no steps"})
        if "failed" not in statuses:
            return MetricResult(metric=self.name, score=1.0, passed=True, details={"note": "no failures"})
        failed_index = next(i for i, s in enumerate(statuses) if s == "failed")
        recovered = any(s == "success" for s in statuses[failed_index + 1 :]) or trace.status == "completed"
        score = 1.0 if recovered else 0.0
        return MetricResult(
            metric=self.name,
            score=score,
            passed=recovered,
            details={"statuses": statuses, "recovered": recovered},
        )


def _short_tool(name: str) -> str:
    return name.split(".")[-1] if "." in name else name


class ToolEfficiencyEvaluator(Evaluator):
    name = "tool_efficiency"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        max_calls = int(case.evaluation.thresholds.get("max_tool_calls", 0))
        count = len(trace.steps)
        if max_calls <= 0:
            return MetricResult(metric=self.name, score=1.0, passed=True, details={"tool_calls": count})
        score = 1.0 if count <= max_calls else max(0.0, max_calls / count)
        return MetricResult(
            metric=self.name,
            score=round(score, 4),
            passed=count <= max_calls,
            details={"tool_calls": count, "max_tool_calls": max_calls},
        )
