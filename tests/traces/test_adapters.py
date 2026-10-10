from agenteval.traces.normalizer import normalize_trace


def test_agentos_adapter_envelope() -> None:
    raw = {
        "run_id": "r1",
        "trace": {
            "trace_version": "1.0",
            "run_id": "r1",
            "system": "agentos",
            "tool_calls": [{"tool_name": "query_database", "result": {"success": True}}],
            "final_response": "ok",
            "status": "completed",
        },
    }
    trace = normalize_trace(raw)
    assert trace.system == "agentos"
    assert trace.steps[0].tool == "query_database"
    assert trace.final_answer == "ok"


def test_researchflow_adapter_state() -> None:
    raw = {
        "run_id": "rf1",
        "state": {
            "question": "What is RAG?",
            "evidence": [{"document_id": "RAG.pdf", "source_type": "rag"}],
            "final_report": {"executive_summary": "parametric and non-parametric memory reduce hallucination"},
        },
    }
    trace = normalize_trace(raw)
    assert trace.system == "researchflow"
    assert "parametric" in trace.final_answer
    assert trace.metadata["rag_document_ids"] == ["RAG.pdf"]


def test_researchflow_agenteval_export_payload() -> None:
    raw = {
        "run_id": "rf-export",
        "system": "researchflow",
        "input": "What is RAG?",
        "steps": [],
        "retrievals": [{"source": "RAG.pdf", "rank": 1}],
        "final_answer": "Retrieval augments generation with external knowledge.",
        "usage": {"latency_ms": 100, "tool_calls": 0},
        "status": "completed",
    }
    trace = normalize_trace(raw)
    assert trace.system == "researchflow"
    assert trace.metadata.get("rag_document_ids") is None or trace.retrievals


def test_researchflow_state_user_question() -> None:
    raw = {
        "run_id": "rf2",
        "state": {"user_question": "Explain agents", "evidence": [], "final_report": {}},
    }
    trace = normalize_trace(raw)
    assert trace.input == "Explain agents"


def test_simple_trace_format() -> None:
    raw = {
        "run_id": "s1",
        "system": "agentos",
        "input": "hello",
        "steps": [{"step": 1, "tool": "github_search", "status": "success"}],
        "final_answer": "done",
        "status": "completed",
    }
    trace = normalize_trace(raw)
    assert trace.steps[0].tool == "github_search"
