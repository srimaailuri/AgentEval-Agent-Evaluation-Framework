from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from agenteval.core.enums import EvaluationRunStatus


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MetricResult(BaseModel):
    metric: str
    score: float
    passed: bool
    details: dict[str, Any] = Field(default_factory=dict)
    skipped: bool = False
    skip_reason: str | None = None


class CaseEvaluationResult(BaseModel):
    case_id: str
    trace_id: str | None = None
    metrics: list[MetricResult] = Field(default_factory=list)
    overall_score: float | None = None
    passed: bool | None = None
    errors: list[str] = Field(default_factory=list)


class AggregateMetrics(BaseModel):
    metric: str
    mean_score: float
    pass_rate: float
    count: int


class EvaluationRun(BaseModel):
    evaluation_run_id: str
    dataset_id: str | None = None
    status: EvaluationRunStatus = EvaluationRunStatus.QUEUED
    created_at: str = Field(default_factory=utc_now_iso)
    completed_at: str | None = None
    case_results: list[CaseEvaluationResult] = Field(default_factory=list)
    aggregate_metrics: list[AggregateMetrics] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
