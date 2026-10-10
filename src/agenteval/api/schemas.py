from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agenteval.core.models import EvaluationRun
from agenteval.datasets.models import EvaluationDataset


class DatasetCreateRequest(BaseModel):
    dataset: EvaluationDataset


class TraceIngestRequest(BaseModel):
    raw_trace: dict[str, Any]
    trace_id: str | None = None


class EvaluationCreateRequest(BaseModel):
    dataset_id: str | None = None
    dataset_path: str | None = None
    case_traces: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Each item: {case_id, raw_trace}",
    )


class EvaluationCreateResponse(BaseModel):
    evaluation_run_id: str
    status: str


class RegressionThresholdSpec(BaseModel):
    metric: str
    max_score_drop: float = 0.05
    min_pass_rate: float = 0.8
    max_latency_increase_ratio: float = 0.2


class RegressionRequest(BaseModel):
    baseline_run_id: str
    candidate_run_id: str
    thresholds: list[RegressionThresholdSpec] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str = "ok"


class ReadyResponse(BaseModel):
    ready: bool
    evaluators_loaded: int


class RunDetailResponse(BaseModel):
    run: EvaluationRun
