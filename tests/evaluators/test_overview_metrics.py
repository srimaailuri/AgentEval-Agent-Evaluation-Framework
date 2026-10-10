from agenteval.datasets.models import EvaluationCase, ExpectedOutcome, EvaluationConfig
from agenteval.evaluators.agent import ToolArgumentCorrectnessEvaluator, TrajectoryQualityEvaluator
from agenteval.evaluators.answer import OutputFormatEvaluator
from agenteval.evaluators.retrieval import HitRateAtKEvaluator
from agenteval.traces.schema import ExecutionTrace, TraceStep


def test_hit_rate_at_k() -> None:
    case = EvaluationCase(
        id="h1",
        input={"question": "q"},
        expected=ExpectedOutcome(documents=["a.pdf"]),
        evaluation=EvaluationConfig(metrics=["hit_rate_at_k"], k=3),
    )
    trace = ExecutionTrace(run_id="1", retrievals=[{"source": "b.pdf"}, {"source": "a.pdf"}])
    assert HitRateAtKEvaluator().evaluate(case, trace).score == 1.0


def test_tool_argument_correctness() -> None:
    case = EvaluationCase(
        id="a1",
        input={"question": "q"},
        expected=ExpectedOutcome(tool_arguments={"query_database": {"status": "blocked"}}),
        evaluation=EvaluationConfig(metrics=["tool_argument_correctness"]),
    )
    trace = ExecutionTrace(
        run_id="2",
        steps=[TraceStep(step=1, tool="query_database", arguments={"status": "blocked"}, status="success")],
    )
    assert ToolArgumentCorrectnessEvaluator().evaluate(case, trace).passed


def test_trajectory_penalizes_repeats() -> None:
    case = EvaluationCase(id="t1", input={}, evaluation=EvaluationConfig(metrics=["trajectory_quality"]))
    trace = ExecutionTrace(
        run_id="3",
        steps=[
            TraceStep(step=1, tool="web_search", status="success"),
            TraceStep(step=2, tool="web_search", status="success"),
            TraceStep(step=3, tool="web_search", status="success"),
        ],
    )
    assert TrajectoryQualityEvaluator().evaluate(case, trace).score < 1.0


def test_output_format_bullets() -> None:
    case = EvaluationCase(
        id="f1",
        input={},
        expected=ExpectedOutcome(output_format="bullets"),
        evaluation=EvaluationConfig(metrics=["output_format"]),
    )
    trace = ExecutionTrace(run_id="4", final_answer="- item one\n- item two")
    assert OutputFormatEvaluator().evaluate(case, trace).passed
