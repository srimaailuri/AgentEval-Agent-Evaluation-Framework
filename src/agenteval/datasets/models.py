from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ExpectedOutcome(BaseModel):
    answer: str | None = None
    topics: list[str] = Field(default_factory=list)
    documents: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    tool_sequence: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    task_completed: bool | None = None
    required_approval: bool | None = None
    tool_arguments: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Expected arguments per tool name, e.g. query_database.status=blocked",
    )
    output_format: str | None = None


class EvaluationConfig(BaseModel):
    metrics: list[str] = Field(default_factory=list)
    k: int = 5
    thresholds: dict[str, float] = Field(default_factory=dict)


class EvaluationCase(BaseModel):
    id: str
    name: str | None = None
    input: dict[str, Any] = Field(default_factory=dict)
    expected: ExpectedOutcome = Field(default_factory=ExpectedOutcome)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvaluationDataset(BaseModel):
    dataset_id: str
    version: str = "1.0"
    description: str | None = None
    cases: list[EvaluationCase] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
