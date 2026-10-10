from __future__ import annotations

from agenteval.core.models import MetricResult
from agenteval.datasets.models import EvaluationCase
from agenteval.evaluators.base import Evaluator
from agenteval.evaluators.utils import normalize_document_stem, retrieval_document_ids
from agenteval.traces.schema import ExecutionTrace


class RecallAtKEvaluator(Evaluator):
    name = "recall_at_k"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        expected = [normalize_document_stem(d) for d in case.expected.documents if d.strip()]
        if not expected:
            return MetricResult(metric=self.name, score=1.0, passed=True, details={"note": "no expected documents"})
        k = case.evaluation.k
        retrieved = [normalize_document_stem(d) for d in retrieval_document_ids(trace)[:k]]
        expected_set = set(expected)
        hits = expected_set & set(retrieved)
        score = len(hits) / len(expected_set)
        return MetricResult(
            metric=self.name,
            score=round(score, 4),
            passed=score >= case.evaluation.thresholds.get(self.name, 1.0),
            details={"expected": expected, "retrieved_at_k": retrieved, "hits": sorted(hits), "k": k},
        )


class ExpectedDocumentRecallEvaluator(Evaluator):
    name = "expected_document_recall"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        expected = [normalize_document_stem(d) for d in case.expected.documents if d.strip()]
        if not expected:
            return MetricResult(metric=self.name, score=1.0, passed=True, details={"expected_count": 0})
        seen = {normalize_document_stem(d) for d in retrieval_document_ids(trace) if d.strip()}
        expected_set = set(expected)
        hits = sorted(expected_set & seen)
        score = len(hits) / len(expected_set)
        return MetricResult(
            metric=self.name,
            score=round(score, 4),
            passed=score >= case.evaluation.thresholds.get(self.name, 1.0),
            details={"hits": hits, "misses": sorted(expected_set - seen)},
        )


class PrecisionAtKEvaluator(Evaluator):
    name = "precision_at_k"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        expected = {normalize_document_stem(d) for d in case.expected.documents if d.strip()}
        k = case.evaluation.k
        retrieved = [normalize_document_stem(d) for d in retrieval_document_ids(trace)[:k]]
        if not retrieved:
            score = 0.0 if expected else 1.0
        else:
            relevant = sum(1 for doc in retrieved if doc in expected) if expected else len(retrieved)
            score = relevant / len(retrieved)
        return MetricResult(
            metric=self.name,
            score=round(score, 4),
            passed=score >= case.evaluation.thresholds.get(self.name, 0.5),
            details={"retrieved_at_k": retrieved, "k": k},
        )


class MRREvaluator(Evaluator):
    name = "mrr"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        expected = {normalize_document_stem(d) for d in case.expected.documents if d.strip()}
        if not expected:
            return MetricResult(metric=self.name, score=1.0, passed=True)
        retrieved = [normalize_document_stem(d) for d in retrieval_document_ids(trace)]
        rr = 0.0
        for rank, doc in enumerate(retrieved, start=1):
            if doc in expected:
                rr = 1.0 / rank
                break
        return MetricResult(
            metric=self.name,
            score=round(rr, 4),
            passed=rr >= case.evaluation.thresholds.get(self.name, 0.5),
            details={"retrieved": retrieved},
        )


class HitRateAtKEvaluator(Evaluator):
    name = "hit_rate_at_k"

    def evaluate(self, case: EvaluationCase, trace: ExecutionTrace) -> MetricResult:
        expected = {normalize_document_stem(d) for d in case.expected.documents if d.strip()}
        if not expected:
            return MetricResult(metric=self.name, score=1.0, passed=True)
        k = case.evaluation.k
        retrieved = [normalize_document_stem(d) for d in retrieval_document_ids(trace)[:k]]
        hit = any(doc in expected for doc in retrieved)
        score = 1.0 if hit else 0.0
        return MetricResult(
            metric=self.name,
            score=score,
            passed=hit,
            details={"k": k, "retrieved_at_k": retrieved},
        )
