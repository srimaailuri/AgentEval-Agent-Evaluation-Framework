from __future__ import annotations

from typing import Any

from agenteval.core.exceptions import TraceValidationError
from agenteval.traces.schema import ExecutionTrace


def validate_trace_dict(raw: dict[str, Any]) -> ExecutionTrace:
    if not isinstance(raw, dict):
        raise TraceValidationError("Trace must be a JSON object")
    if not raw.get("run_id"):
        raise TraceValidationError("run_id is required")
    try:
        return ExecutionTrace.model_validate(raw)
    except Exception as exc:
        raise TraceValidationError(str(exc)) from exc
