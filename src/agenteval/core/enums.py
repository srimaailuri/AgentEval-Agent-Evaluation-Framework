from __future__ import annotations

from enum import StrEnum


class EvaluationRunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class MetricName(StrEnum):
    RECALL_AT_K = "recall_at_k"
    EXPECTED_DOCUMENT_RECALL = "expected_document_recall"
    PRECISION_AT_K = "precision_at_k"
    MRR = "mrr"
    TOOL_SELECTION_ACCURACY = "tool_selection_accuracy"
    TOOL_CALL_SUCCESS_RATE = "tool_call_success_rate"
    TASK_COMPLETION = "task_completion"
    ANSWER_CORRECTNESS = "answer_correctness"
    TOPIC_RECALL = "topic_recall"
    LATENCY = "latency"
    TOKEN_USAGE = "token_usage"
    ESTIMATED_COST = "estimated_cost"
    GROUNDEDNESS = "groundedness"
