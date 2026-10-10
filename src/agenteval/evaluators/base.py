from __future__ import annotations

from abc import ABC, abstractmethod

from agenteval.core.models import MetricResult
from agenteval.datasets.models import EvaluationCase
from agenteval.traces.schema import EvaluationTrace


class Evaluator(ABC):
    name: str

    @abstractmethod
    def evaluate(self, case: EvaluationCase, trace: EvaluationTrace) -> MetricResult:
        ...
