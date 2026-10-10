from __future__ import annotations

from typing import Any

from agenteval.traces.schema import ExecutionTrace, TraceStep, TraceUsage
from agenteval.traces.validator import validate_trace_dict


def normalize_trace(raw: dict[str, Any]) -> ExecutionTrace:
    """Map AgentOS, ResearchFlow, or simple traces to ExecutionTrace."""
    if _looks_simple(raw):
        return validate_trace_dict(raw)

    if "trace" in raw and isinstance(raw["trace"], dict):
        return validate_trace_dict(_from_agentos_envelope(raw))

    if "state" in raw and isinstance(raw["state"], dict):
        return validate_trace_dict(_from_researchflow(raw))

    if raw.get("trace_version") or raw.get("tool_calls"):
        return validate_trace_dict(_from_agentos_inner(raw))

    return validate_trace_dict(_from_generic(raw))


def _looks_simple(raw: dict[str, Any]) -> bool:
    return bool(raw.get("run_id")) and "steps" in raw and "trace_version" not in raw


def _from_agentos_envelope(raw: dict[str, Any]) -> dict[str, Any]:
    inner = raw["trace"]
    return _from_agentos_inner(
        {
            **inner,
            "run_id": inner.get("run_id") or raw.get("run_id"),
        }
    )


def _from_agentos_inner(raw: dict[str, Any]) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    for index, call in enumerate(raw.get("tool_calls") or [], start=1):
        if not isinstance(call, dict):
            continue
        result = call.get("result") or {}
        ok = True
        if isinstance(result, dict) and result.get("success") is False:
            ok = False
        steps.append(
            {
                "step": index,
                "tool": str(call.get("tool_name") or "unknown"),
                "arguments": call.get("arguments") or {},
                "status": "success" if ok else "failed",
            }
        )
    latency = sum(
        float(e.get("latency_ms") or 0)
        for e in raw.get("events") or []
        if isinstance(e, dict)
    )
    usage_raw = raw.get("usage") or {}
    inp = raw.get("input") or {}
    query = inp.get("query") if isinstance(inp, dict) else str(inp)
    retrievals = []
    for call in raw.get("tool_calls") or []:
        if not isinstance(call, dict):
            continue
        name = str(call.get("tool_name") or "")
        if name in {"document_search", "web_search"}:
            retrievals.append({"source": name, "query": (call.get("arguments") or {}).get("query")})
    return {
        "run_id": str(raw.get("run_id") or "unknown"),
        "system": "agentos",
        "system_version": raw.get("system_version"),
        "input": query or "",
        "steps": steps,
        "retrievals": retrievals,
        "final_answer": str(raw.get("final_response") or raw.get("final_answer") or ""),
        "usage": {
            "input_tokens": int(usage_raw.get("input_tokens") or 0),
            "output_tokens": int(usage_raw.get("output_tokens") or 0),
            "llm_calls": int(usage_raw.get("llm_calls") or 0),
            "tool_calls": int(usage_raw.get("tool_calls") or len(steps)),
            "latency_ms": float(usage_raw.get("latency_ms") or latency),
            "estimated_cost": float(usage_raw.get("estimated_cost") or 0.0),
        },
        "status": raw.get("status") or "completed",
    }


def _from_researchflow(raw: dict[str, Any]) -> dict[str, Any]:
    state = raw["state"]
    run_id = str(raw.get("run_id") or state.get("run_id") or "unknown")
    retrievals = []
    doc_ids: list[str] = []
    for rank, item in enumerate(state.get("evidence") or [], start=1):
        if not isinstance(item, dict):
            continue
        doc_id = item.get("document_id") or item.get("source") or ""
        retrievals.append(
            {
                "source": doc_id,
                "rank": rank,
                "relevance": item.get("score"),
            }
        )
        if doc_id:
            doc_ids.append(str(doc_id))
    return {
        "run_id": run_id,
        "system": "researchflow",
        "input": str(state.get("question") or state.get("user_question") or ""),
        "steps": [],
        "retrievals": retrievals,
        "final_answer": _report_text(state),
        "usage": TraceUsage().model_dump(),
        "status": "completed" if state.get("validation_status") != "failed" else "failed",
        "metadata": {"rag_document_ids": doc_ids},
    }


def _from_generic(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": str(raw.get("run_id") or "unknown"),
        "system": str(raw.get("system") or "generic"),
        "input": raw.get("input") or "",
        "steps": raw.get("steps") or [],
        "retrievals": raw.get("retrievals") or [],
        "final_answer": str(raw.get("final_answer") or raw.get("final_response") or ""),
        "usage": raw.get("usage") or {},
        "status": raw.get("status") or "completed",
        "metadata": raw.get("metadata") or {},
    }


def _report_text(state: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("final_report", "draft_report"):
        report = state.get(key) or {}
        if not isinstance(report, dict):
            continue
        for field in ("executive_summary", "conclusion"):
            value = report.get(field)
            if isinstance(value, str) and value.strip():
                parts.append(value.strip())
    return " ".join(parts)
