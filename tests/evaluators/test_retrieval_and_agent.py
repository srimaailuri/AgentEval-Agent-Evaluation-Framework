from agenteval.datasets.models import EvaluationCase, ExpectedOutcome, EvaluationConfig
from agenteval.evaluators.agent import ToolSelectionEvaluator
from agenteval.evaluators.retrieval import ExpectedDocumentRecallEvaluator
from agenteval.traces.schema import ExecutionTrace, TraceStep


def test_expected_document_recall() -> None:
    case = EvaluationCase(
        id="t1",
        input={"question": "q"},
        expected=ExpectedOutcome(documents=["RAG.pdf"]),
        evaluation=EvaluationConfig(metrics=["expected_document_recall"]),
    )
    trace = ExecutionTrace(
        run_id="1",
        system="researchflow",
        retrievals=[{"source": "RAG.pdf"}],
        metadata={"rag_document_ids": ["RAG.pdf"]},
    )
    result = ExpectedDocumentRecallEvaluator().evaluate(case, trace)
    assert result.score == 1.0


def test_tool_selection_capabilities() -> None:
    case = EvaluationCase(
        id="t2",
        input={"question": "q"},
        expected=ExpectedOutcome(tools=["github", "postgresql"]),
        evaluation=EvaluationConfig(metrics=["tool_selection_accuracy"]),
    )
    trace = ExecutionTrace(
        run_id="2",
        system="agentos",
        steps=[
            TraceStep(step=1, tool="mcp.search_issues", status="success"),
            TraceStep(step=2, tool="query_database", status="success"),
        ],
    )
    result = ToolSelectionEvaluator().evaluate(case, trace)
    assert result.score == 1.0
