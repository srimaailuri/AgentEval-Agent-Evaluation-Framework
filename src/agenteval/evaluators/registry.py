from __future__ import annotations

from agenteval.core.exceptions import EvaluatorNotFoundError
from agenteval.evaluators.agent import (
    FailureRecoveryEvaluator,
    TaskCompletionEvaluator,
    ToolArgumentCorrectnessEvaluator,
    ToolCallSuccessEvaluator,
    ToolEfficiencyEvaluator,
    ToolSelectionEvaluator,
    TrajectoryQualityEvaluator,
)
from agenteval.evaluators.answer import (
    AnswerCorrectnessEvaluator,
    AnswerRelevanceEvaluator,
    GroundednessEvaluator,
    OutputFormatEvaluator,
    TopicRecallEvaluator,
)
from agenteval.evaluators.base import Evaluator
from agenteval.evaluators.performance import (
    CostPerSuccessfulTaskEvaluator,
    EstimatedCostEvaluator,
    LatencyEvaluator,
    TokenUsageEvaluator,
)
from agenteval.evaluators.retrieval import (
    ExpectedDocumentRecallEvaluator,
    HitRateAtKEvaluator,
    MRREvaluator,
    PrecisionAtKEvaluator,
    RecallAtKEvaluator,
)


def build_default_registry() -> dict[str, Evaluator]:
    evaluators: list[Evaluator] = [
        RecallAtKEvaluator(),
        ExpectedDocumentRecallEvaluator(),
        PrecisionAtKEvaluator(),
        MRREvaluator(),
        HitRateAtKEvaluator(),
        ToolSelectionEvaluator(),
        ToolArgumentCorrectnessEvaluator(),
        ToolCallSuccessEvaluator(),
        TaskCompletionEvaluator(),
        ToolEfficiencyEvaluator(),
        TrajectoryQualityEvaluator(),
        FailureRecoveryEvaluator(),
        AnswerCorrectnessEvaluator(),
        TopicRecallEvaluator(),
        AnswerRelevanceEvaluator(),
        GroundednessEvaluator(),
        OutputFormatEvaluator(),
        LatencyEvaluator(),
        TokenUsageEvaluator(),
        EstimatedCostEvaluator(),
        CostPerSuccessfulTaskEvaluator(),
    ]
    return {e.name: e for e in evaluators}


def get_evaluator(metric: str, registry: dict[str, Evaluator] | None = None) -> Evaluator:
    reg = registry or build_default_registry()
    if metric not in reg:
        raise EvaluatorNotFoundError(f"No evaluator registered for metric: {metric}")
    return reg[metric]
