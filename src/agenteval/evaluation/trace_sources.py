from __future__ import annotations

from typing import Any

from agenteval.storage.store import EvaluationStore


def resolve_traces_by_case_id(
    case_traces: list[dict[str, Any]],
    *,
    store: EvaluationStore | None = None,
) -> dict[str, dict[str, Any]]:
    """
    Build case_id -> raw trace payloads for the evaluation runner.

    Each item may supply ``raw_trace`` inline or ``run_id`` / ``trace_id`` to load
    from persistence after ``POST /traces``.
    """
    traces: dict[str, dict[str, Any]] = {}
    for item in case_traces:
        case_id = str(item.get("case_id") or "").strip()
        if not case_id:
            continue
        raw = item.get("raw_trace")
        if raw is not None:
            traces[case_id] = raw
            continue
        trace_ref = item.get("run_id") or item.get("trace_id")
        if trace_ref and store is not None:
            stored = store.get_trace(str(trace_ref))
            if stored is not None:
                traces[case_id] = stored.model_dump(mode="json")
    return traces
