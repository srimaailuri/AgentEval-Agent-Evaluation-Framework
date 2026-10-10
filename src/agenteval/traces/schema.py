from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class TraceUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    llm_calls: int = 0
    tool_calls: int = 0
    latency_ms: float = 0.0
    estimated_cost: float = 0.0


class TraceStep(BaseModel):
    step: int
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    status: str = "success"


class ExecutionTrace(BaseModel):
    """Common execution trace (see project overview section 6)."""

    run_id: str
    system: str = "generic"
    system_version: str | None = None
    input: str = ""
    steps: list[TraceStep] = Field(default_factory=list)
    retrievals: list[dict[str, Any]] = Field(default_factory=list)
    final_answer: str = ""
    usage: TraceUsage = Field(default_factory=TraceUsage)
    status: Literal["pending", "completed", "failed", "waiting_for_approval"] = "completed"
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("input", mode="before")
    @classmethod
    def _coerce_input(cls, value: Any) -> str:
        if isinstance(value, dict):
            return str(value.get("query") or value.get("question") or "")
        return str(value or "")

    @property
    def final_response(self) -> str:
        """Alias used by answer evaluators."""
        return self.final_answer


# Backward-compatible name
EvaluationTrace = ExecutionTrace
