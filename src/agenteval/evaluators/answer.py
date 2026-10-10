from __future__ import annotations

from agenteval.config import get_settings
from agenteval.core.models import MetricResult
from agenteval.datasets.models import EvaluationCase
from agenteval.evaluators.base import Evaluator
from agenteval.evaluators.utils import answer_similarity, topic_is_present
from agenteval.traces.schema import ExecutionTrace


class AnswerCorrectnessEvaluator(Evaluator):
    name = "answer_correctness"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        expected = case.expected.answer or ""
        if not expected.strip():
            return MetricResult(metric=self.name, score=1.0, passed=True, details={"note": "no expected answer"})
        score = answer_similarity(expected, trace.final_answer)
        threshold = case.evaluation.thresholds.get(self.name, get_settings().answer_pass_similarity)
        return MetricResult(metric=self.name, score=score, passed=score >= threshold, details={"threshold": threshold})


class TopicRecallEvaluator(Evaluator):
    name = "topic_recall"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        topics = case.expected.topics
        if not topics:
            return MetricResult(metric=self.name, score=1.0, passed=True)
        hits = [t for t in topics if topic_is_present(trace.final_answer, t)]
        score = len(hits) / len(topics)
        threshold = case.evaluation.thresholds.get(self.name, get_settings().topic_pass_recall)
        return MetricResult(
            metric=self.name,
            score=round(score, 4),
            passed=score >= threshold,
            details={"hits": hits, "misses": [t for t in topics if t not in hits]},
        )


class AnswerRelevanceEvaluator(Evaluator):
    name = "answer_relevance"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        question = str(case.input.get("question") or case.input.get("query") or trace.input or "")
        if not question.strip():
            return MetricResult(metric=self.name, score=1.0, passed=True)
        score = answer_similarity(question, trace.final_answer)
        return MetricResult(
            metric=self.name,
            score=score,
            passed=score >= case.evaluation.thresholds.get(self.name, 0.3),
        )


class OutputFormatEvaluator(Evaluator):
    name = "output_format"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        fmt = (case.expected.output_format or case.metadata.get("output_format") or "").lower()
        if not fmt:
            return MetricResult(metric=self.name, score=1.0, passed=True, details={"note": "no format required"})
        text = trace.final_answer.strip()
        passed = False
        if fmt == "json":
            import json

            try:
                json.loads(text)
                passed = True
            except json.JSONDecodeError:
                passed = False
        elif fmt == "markdown_table":
            passed = "|" in text and "---" in text
        elif fmt == "bullets":
            passed = any(line.strip().startswith(("-", "*")) for line in text.splitlines())
        else:
            passed = True
        return MetricResult(metric=self.name, score=1.0 if passed else 0.0, passed=passed, details={"format": fmt})


class GroundednessEvaluator(Evaluator):
    name = "groundedness"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        if get_settings().enable_llm_judge:
            return MetricResult(
                metric=self.name,
                score=0.0,
                passed=False,
                skipped=True,
                skip_reason="use LLM judge when ENABLE_LLM_JUDGE=true",
            )
        has_evidence = bool(trace.retrievals) or bool(trace.steps)
        has_answer = bool(trace.final_answer.strip())
        if not has_answer:
            score = 0.0
        elif has_evidence:
            score = 1.0
        else:
            score = 0.5
        return MetricResult(
            metric=self.name,
            score=score,
            passed=score >= case.evaluation.thresholds.get(self.name, 0.5),
            details={"heuristic": True, "has_evidence": has_evidence},
        )
