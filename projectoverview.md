# AgentEval — LLM & Agent Evaluation Platform

## 1. Project Overview

AgentEval is a standalone evaluation platform for measuring the quality and operational behavior of LLM-powered applications.

It is designed to evaluate systems such as:

- RAG and research workflows
- Tool-using AI agents
- Agentic workflows
- Other LLM applications that can export a standardized execution trace

AgentEval consumes execution traces from external systems, evaluates them against predefined datasets and expected outcomes, calculates evaluation metrics, aggregates results, and supports regression comparison between evaluation runs.

AgentEval does not execute ResearchFlow or AgentOS. Those systems run independently and export execution traces, while AgentEval is responsible for trace normalization, evaluation, aggregation, persistence, and regression analysis.

### Project Relationship

```text
┌─────────────────┐
│  ResearchFlow   │
│  RAG / Research │
│     Workflow    │
└────────┬────────┘
         │
         │ Execution Trace
         ▼
┌──────────────────────────────┐
│          AgentEval           │
│                              │
│  Trace Normalization         │
│          ↓                   │
│  Dataset Evaluation          │
│          ↓                   │
│  Metric Calculation          │
│          ↓                   │
│  Result Aggregation          │
│          ↓                   │
│  Regression Comparison       │
└──────────────▲───────────────┘
               │
               │ Execution Trace
               │
┌──────────────┴───────────────┐
│           AgentOS            │
│      Agent + Tools + MCP     │
└──────────────────────────────┘
```

The platform is intentionally separated from the systems it evaluates so that the same evaluation infrastructure can be reused across multiple LLM applications.

---

## 2. Problem Statement

Evaluating an LLM application only by looking at its final response is often insufficient.

For a RAG system, we need to understand:

- Did the system retrieve the expected documents?
- Were relevant documents ranked highly?
- Did the final answer cover the expected information?
- Was the answer supported by retrieved evidence?

For an agent, we need to understand:

- Did the agent select the appropriate tools?
- Were tool arguments correct?
- Did tool calls succeed?
- Did the agent complete the requested task?
- Did it use unnecessary tool calls?
- Did it recover from tool failures?

For production behavior, we may also need to track:

- Latency
- Token usage
- LLM calls
- Tool calls
- Estimated cost
- Changes between system versions

Without a common evaluation framework, these checks tend to become application-specific and difficult to compare.

AgentEval provides a common trace-based evaluation pipeline that can be used across ResearchFlow, AgentOS, and future LLM applications.

---

## 3. Goals and Scope

### In Scope

AgentEval provides:

- Standardized execution trace ingestion
- Trace validation and normalization
- Dataset-driven evaluation
- Retrieval evaluation
- Agent behavior evaluation
- Answer evaluation
- Performance evaluation
- Evaluation result aggregation
- Basic regression comparison
- FastAPI service
- CLI-based evaluation
- Local persistence
- ResearchFlow integration
- AgentOS integration
- Sample evaluation datasets
- Automated tests

### Out of Scope

AgentEval does not currently aim to provide:

- Execution or orchestration of ResearchFlow
- Execution or orchestration of AgentOS
- Distributed evaluation workers
- Kafka, Pub/Sub, Celery, or similar job infrastructure
- Dashboarding
- Complex plugin frameworks
- Full CI/CD orchestration
- Advanced experiment tracking
- Complex authentication/authorization
- Sophisticated meta-evaluation
- Large-scale LLM-as-a-judge infrastructure

The platform is intentionally focused on evaluation rather than becoming a general-purpose AI observability or experimentation platform.

---

## 4. Relationship With ResearchFlow and AgentOS

AgentEval is an independent project.

### ResearchFlow

ResearchFlow is responsible for:

- Research planning
- Task decomposition
- RAG retrieval
- Evidence evaluation
- Research synthesis
- Citation-aware output

ResearchFlow exports its execution state into an AgentEval-compatible trace.

### AgentOS

AgentOS is responsible for:

- Agent planning
- Task execution
- Dynamic tool selection
- Tool execution
- PostgreSQL interaction
- RAG/document search
- MCP integration
- Memory
- Human-in-the-loop execution

AgentOS exports its execution trace into an AgentEval-compatible trace.

### AgentEval

AgentEval is responsible for:

- Trace ingestion
- Trace normalization
- Dataset loading
- Metric calculation
- Evaluation execution
- Result aggregation
- Regression comparison
- Evaluation result persistence

AgentEval does not import or execute ResearchFlow or AgentOS.

```text
ResearchFlow ────────┐
                     │
                     │ Execution Trace
                     ▼
                 ┌───────────┐
                 │ AgentEval │
                 │           │
                 │ Normalize │
                 │ Evaluate  │
                 │ Aggregate │
                 │ Compare   │
                 │ Persist   │
                 └───────────┘
                     ▲
                     │
                     │ Execution Trace
                     │
AgentOS ─────────────┘
```

---

## 5. High-Level Architecture

```text
                         ┌──────────────────────┐
                         │    ResearchFlow      │
                         │    RAG Workflow      │
                         └──────────┬───────────┘
                                    │
                                    │ Trace
                                    ▼
┌──────────────────────────────────────────────────────────┐
│                       AgentEval                          │
│                                                          │
│  ┌────────────────────┐                                  │
│  │ Trace Ingestion    │                                  │
│  └─────────┬──────────┘                                  │
│            ▼                                             │
│  ┌────────────────────┐                                  │
│  │ Trace Normalizer   │                                  │
│  └─────────┬──────────┘                                  │
│            ▼                                             │
│  ┌────────────────────┐                                  │
│  │ Dataset / Cases    │                                  │
│  └─────────┬──────────┘                                  │
│            ▼                                             │
│  ┌────────────────────┐                                  │
│  │ Evaluation Runner  │                                  │
│  └─────────┬──────────┘                                  │
│            │                                             │
│      ┌─────┼───────────────┬───────────────┐              │
│      ▼     ▼               ▼               ▼              │
│ Retrieval Agent         Answer        Performance        │
│ Evaluation Evaluation   Evaluation     Evaluation         │
│      │     │               │               │              │
│      └─────┴───────────────┴───────────────┘              │
│                        │                                  │
│                        ▼                                  │
│               Result Aggregation                          │
│                        │                                  │
│                        ▼                                  │
│               Regression Analysis                         │
│                                                          │
└──────────────────────────▲───────────────────────────────┘
                           │
                           │ Trace
                           │
                  ┌────────┴────────┐
                  │     AgentOS     │
                  │ Agent + Tools   │
                  └─────────────────┘
```

---

## 6. Core Evaluation Pipeline

The evaluation process follows a consistent pipeline:

```text
Dataset
   │
   ▼
Evaluation Cases
   │
   ▼
Match Case With Trace
   │
   ▼
Normalize Trace
   │
   ▼
Run Selected Evaluators
   │
   ├── Retrieval Evaluation
   ├── Agent Evaluation
   ├── Answer Evaluation
   └── Performance Evaluation
   │
   ▼
Case Evaluation Result
   │
   ▼
Aggregate Results
   │
   ▼
Evaluation Run
   │
   ├── Persist Result
   └── Compare With Baseline
```

AgentEval evaluates traces that are supplied to it. It does not invoke ResearchFlow or AgentOS to generate traces.

The normal workflow is:

```text
Run Target System
       ↓
Export Execution Trace
       ↓
Provide Trace To AgentEval
       ↓
Run Evaluation
       ↓
Analyze Results
```

---

## 7. Execution Trace Contract

AgentEval uses a canonical `ExecutionTrace` model.

The trace provides the information required by different evaluators without exposing the internal implementation of the source system.

### ExecutionTrace

```text
ExecutionTrace
│
├── run_id
├── system
├── system_version
├── input
├── steps
│   └── tool calls
├── retrievals
│   └── retrieved evidence
├── final_answer
├── usage
│   ├── input_tokens
│   ├── output_tokens
│   ├── llm_calls
│   ├── tool_calls
│   ├── latency_ms
│   └── estimated_cost
├── status
└── metadata
```

### TraceStep

Each tool execution can contain:

- Step number
- Tool name
- Arguments
- Execution status

### TraceUsage

The usage object records:

- Input tokens
- Output tokens
- LLM call count
- Tool call count
- Latency
- Estimated cost

This common representation allows evaluators to remain independent from ResearchFlow and AgentOS implementations.

---

## 8. Trace Normalization

Different applications naturally produce different execution trace structures.

AgentEval converts these different representations into the canonical `ExecutionTrace`.

Supported inputs include:

- AgentEval-native traces
- AgentOS traces
- ResearchFlow traces
- Generic compatible trace payloads

```text
External Trace
      │
      ▼
┌─────────────────┐
│ Trace Validator │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Trace Normalizer│
└────────┬────────┘
         ▼
  ExecutionTrace
         │
         ▼
     Evaluators
```

The normalization layer ensures that evaluator implementations operate against a consistent data model.

---

## 9. Dataset-Driven Evaluation

AgentEval uses structured evaluation datasets.

An evaluation case can define:

- Input question or task
- Expected answer
- Expected topics
- Expected documents
- Expected tools
- Expected tool arguments
- Expected output format
- Expected task completion state
- Evaluation metrics
- Metric thresholds

Example:

```json
{
  "case_id": "agent_001",
  "system": "agentos",
  "task": "Find blocked projects and summarize their recent issues.",
  "expected_tools": [
    "postgresql",
    "github"
  ],
  "expected_tool_arguments": {
    "postgresql": {
      "status": "blocked"
    }
  }
}
```

Datasets make evaluation repeatable and allow the same evaluation cases to be executed against different versions of a system.

---

## 10. Retrieval Evaluation

Retrieval evaluation is primarily used for RAG and research systems.

AgentEval currently supports:

- Recall@K
- Precision@K
- MRR
- Hit Rate@K
- Expected document recall

### Recall@K

Measures how many of the expected documents appear within the top K retrieved documents.

### Precision@K

Measures how many of the top K retrieved documents belong to the expected relevant set.

### MRR

Measures how highly the first expected document appears in the retrieval ranking.

### Hit Rate@K

Determines whether at least one expected document appears in the top K.

### Expected Document Recall

Measures retrieval coverage across all retrieved documents.

The current implementation uses expected document identifiers defined by the evaluation dataset rather than a separate semantic relevance model.

---

## 11. Agent Evaluation

Agent evaluation focuses on the behavior of tool-using systems.

### Tool Selection Accuracy

Checks whether the agent selected the expected tool capabilities.

```text
Expected:
PostgreSQL + GitHub

Actual:
PostgreSQL + GitHub

Result:
PASS
```

### Tool Argument Correctness

Checks whether important tool arguments match the expected values.

### Tool Success Rate

Measures the proportion of successful tool executions.

```text
successful tool calls
---------------------
total tool calls
```

### Task Completion

Determines whether the agent successfully completed the requested task.

### Tool Efficiency

Checks whether the agent completed the task within an acceptable number of tool calls.

### Trajectory Quality

Provides a simple check for obvious redundant execution behavior.

### Failure Recovery

Checks whether the agent can recover after a failed tool call and still complete the task.

These metrics allow evaluation of the agent's execution behavior in addition to its final response.

---

## 12. Answer Evaluation

AgentEval evaluates the final response generated by the target system.

Current evaluation areas include:

- Answer correctness
- Topic coverage
- Answer relevance
- Groundedness
- Output format compliance

### Answer Correctness

Measures how closely the generated answer matches the expected answer.

### Topic Coverage

Checks whether expected topics are present in the final response.

### Answer Relevance

Measures whether the response addresses the original question or task.

### Groundedness

Checks whether the answer has supporting retrieval or tool activity.

The current implementation uses a deterministic heuristic for groundedness rather than a full semantic LLM judge.

### Output Format

Validates formats such as:

- JSON
- Markdown tables
- Bullet lists

when the evaluation case specifies a required format.

---

## 13. Performance Evaluation

AgentEval also evaluates operational behavior.

Current metrics include:

- Latency
- Total token usage
- Estimated cost
- Cost per successful task

Execution traces also retain:

- LLM call count
- Tool call count

Example:

```text
System Version A
────────────────
Accuracy: 0.91
Latency: 4.2 sec
Cost: $0.012

System Version B
────────────────
Accuracy: 0.94
Latency: 5.8 sec
Cost: $0.019
```

This allows quality improvements to be considered alongside performance and cost.

---

## 14. Evaluation Runner

The evaluation runner coordinates the evaluation process.

For each evaluation case it:

1. Loads the case definition
2. Finds the corresponding execution trace
3. Normalizes the trace
4. Loads the selected metrics
5. Executes each evaluator
6. Produces case-level results
7. Aggregates results across cases
8. Produces an evaluation run

Unknown or unsupported metrics can be reported as skipped rather than terminating the complete evaluation.

Errors are captured at the case level so that one problematic case does not unnecessarily stop the complete evaluation run.

---

## 15. Evaluation Result

Each evaluation case produces metric-level results.

A result can contain:

```text
CaseEvaluationResult
│
├── case_id
├── trace_id
├── metrics
│   ├── metric name
│   ├── score
│   ├── passed
│   └── details
├── overall_score
└── passed
```

The complete evaluation run aggregates results across all cases.

```text
Evaluation Run
│
├── Case 1
│   ├── Retrieval Recall
│   ├── Tool Selection
│   ├── Task Completion
│   └── Answer Correctness
│
├── Case 2
│   └── ...
│
└── Aggregate Metrics
    ├── Mean Score
    ├── Pass Rate
    └── Case Count
```

---

## 16. Regression Evaluation

AgentEval supports comparison between two evaluation runs.

```text
                 ┌─────────────────┐
                 │  Baseline Run   │
                 └────────┬────────┘
                          │
                          │
                    Compare Metrics
                          │
                          ▼
                 ┌─────────────────┐
                 │ Candidate Run   │
                 └─────────────────┘
```

Regression comparison reports:

- Baseline metric score
- Candidate metric score
- Score difference
- Pass-rate difference
- Metric-level changes
- Optional threshold violations

Example:

```text
                 Baseline   Candidate
Retrieval Recall    0.91       0.94
Task Completion     0.88       0.92
Answer Correctness  0.90       0.89
Latency             4.2s       5.8s
```

This makes it possible to identify whether a new system version improved or degraded specific aspects of behavior.

AgentEval reports regression results but does not directly control CI/CD pipelines.

---

## 17. ResearchFlow Integration

ResearchFlow provides an export helper that converts its execution state into an AgentEval-compatible trace.

```python
from researchflow.observability.agenteval_export import to_agenteval_trace

payload = to_agenteval_trace(
    state,
    system_version="0.1.0"
)
```

The resulting trace can then be provided to AgentEval for evaluation.

ResearchFlow retrieval evidence is mapped into AgentEval retrieval records.

Expected document identifiers from the ResearchFlow benchmark can therefore be used by the retrieval evaluators.

ResearchFlow can continue to maintain its local benchmark scoring for development purposes, while AgentEval provides the shared evaluation layer.

---

## 18. AgentOS Integration

AgentOS provides an execution trace export mechanism.

```python
from agentos.trace import build_execution_trace, to_agenteval_trace

trace = build_execution_trace(state)

payload = to_agenteval_trace(
    trace,
    system_version="0.1.0"
)
```

AgentOS also exposes:

```text
GET /agent/runs/{run_id}/trace/agenteval
```

This returns an AgentEval-compatible trace directly from an AgentOS run.

AgentEval can then evaluate:

- Tool selection
- Tool arguments
- Tool success
- Task completion
- Tool efficiency
- Failure recovery
- Answer quality
- Performance

AgentEval does not contain AgentOS execution logic.

---

## 19. Evaluator Architecture

Evaluators operate against two main inputs:

```text
EvaluationCase
+
ExecutionTrace
```

The evaluator layer is source-agnostic.

```text
                 Evaluator Registry
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
   Retrieval          Agent           Answer
   Evaluators       Evaluators       Evaluators
        │               │                │
        └───────────────┼────────────────┘
                        │
                        ▼
                  Performance
                   Evaluators
```

Evaluators should not contain system-specific branches such as:

```python
if system == "agentos":
    ...
elif system == "researchflow":
    ...
```

Instead, source-system-specific logic should be handled during trace export or normalization.

---

## 20. Storage

AgentEval currently uses SQLite as the default persistence layer.

Stored information includes:

- Datasets
- Execution traces
- Evaluation runs

The current storage design intentionally keeps persistence simple and suitable for local or single-node execution.

PostgreSQL support can be introduced later for larger deployment scenarios without changing the evaluation architecture.

---

## 21. API

AgentEval exposes a FastAPI service.

### Health

```text
GET /health
GET /ready
```

### Trace APIs

```text
POST /traces
GET /traces/{run_id}
```

### Evaluation APIs

```text
POST /evaluations/run
GET /evaluations/{evaluation_id}
GET /evaluations/{evaluation_id}/results
```

### Regression API

```text
POST /regression/run
```

The evaluation endpoint can execute evaluation runs asynchronously using FastAPI background execution for the current single-node implementation.

---

## 22. CLI

AgentEval provides a CLI for local evaluation.

Example:

```powershell
.\.venv\Scripts\python.exe -m agenteval run `
  --dataset data/datasets/sample_agent.json `
  --traces data/sample_traces/agentos_ag001.json `
  --output .agenteval/last_run.json
```

The CLI produces a JSON evaluation report that can be inspected or used by other development workflows.

---

## 23. Testing Strategy

AgentEval uses pytest.

### Trace Testing

- Canonical trace validation
- AgentOS trace normalization
- ResearchFlow trace normalization
- Generic trace normalization

### Dataset Testing

- Dataset loading
- Evaluation case validation
- Sample datasets

### Evaluator Testing

- Retrieval metrics
- Agent metrics
- Answer metrics
- Performance metrics

### Runner Testing

- Case execution
- Metric execution
- Aggregation
- Error handling

### API Testing

- Health endpoint
- Trace ingestion
- Evaluation execution
- Result retrieval

External LLM APIs are not required for the standard test suite.

The evaluation framework is therefore deterministic and reproducible.

---

## 24. Project Structure

```text
AgentEval/
│
├── src/
│   └── agenteval/
│       │
│       ├── api/
│       │   ├── app.py
│       │   ├── routes.py
│       │   └── schemas.py
│       │
│       ├── core/
│       │   ├── models.py
│       │   ├── enums.py
│       │   └── exceptions.py
│       │
│       ├── traces/
│       │   ├── schema.py
│       │   ├── validator.py
│       │   └── normalizer.py
│       │
│       ├── datasets/
│       │   ├── models.py
│       │   ├── loader.py
│       │   └── validator.py
│       │
│       ├── evaluators/
│       │   ├── base.py
│       │   ├── registry.py
│       │   ├── retrieval.py
│       │   ├── agent.py
│       │   ├── answer.py
│       │   ├── performance.py
│       │   └── utils.py
│       │
│       ├── judges/
│       │   └── llm_judge.py
│       │
│       ├── evaluation/
│       │   ├── runner.py
│       │   ├── aggregator.py
│       │   ├── regression.py
│       │   └── reports.py
│       │
│       ├── storage/
│       │   ├── store.py
│       │   └── database.py
│       │
│       ├── config.py
│       └── cli.py
│
├── tests/
│   ├── api/
│   ├── datasets/
│   ├── evaluators/
│   ├── traces/
│   └── runs/
│
├── data/
│   ├── researchflow/
│   ├── agentos/
│   ├── datasets/
│   └── sample_traces/
│
├── docker/
├── docker-compose.yml
├── pyproject.toml
├── README.md
├── ARCHITECTURE.md
├── EVALUATORS.md
└── projectoverview.md
```

---

## 25. Configuration

AgentEval supports configuration through environment variables.

Example configuration:

```text
DATABASE_URL
AGENTEVAL_DATA_DIR
ENABLE_LLM_JUDGE
GOOGLE_API_KEY
DEFAULT_JUDGE_MODEL
BENCHMARK_TOPIC_PASS_RECALL
BENCHMARK_ANSWER_PASS_SIMILARITY
MAX_CONCURRENT_CASES
LOG_LEVEL
LOG_JSON
```

Configuration should remain lightweight and should not introduce unnecessary deployment complexity.

---

## 26. LLM-as-a-Judge

AgentEval keeps LLM-as-a-judge as an optional capability.

The current evaluation framework primarily relies on deterministic metrics.

A future LLM judge can be used for metrics where deterministic comparison is insufficient, such as:

- Semantic answer correctness
- Semantic relevance
- Groundedness
- More advanced task completion evaluation

The judge should remain isolated from the core evaluation pipeline.

```text
Evaluation Runner
       │
       ├── Deterministic Evaluators
       │
       └── Optional LLM Judge
```

The evaluation platform should not depend entirely on an LLM judge for its core functionality.

---

## 27. Sample Evaluation Datasets

AgentEval includes sample datasets for both major systems.

### ResearchFlow

Example evaluation areas:

- Retrieval quality
- Expected document retrieval
- Topic coverage
- Answer correctness
- Answer relevance

### AgentOS

Example evaluation areas:

- Tool selection
- Tool arguments
- Tool execution
- Task completion
- Tool efficiency
- Final answer quality

The current project contains approximately 10 evaluation cases for ResearchFlow and 10 for AgentOS.

---

## 28. Engineering Concepts

The project covers several practical engineering concepts.

### LLM and RAG Evaluation

- Recall@K
- Precision@K
- MRR
- Hit Rate
- Groundedness
- Answer correctness
- Topic coverage

### Agent Evaluation

- Tool selection
- Tool argument validation
- Tool success
- Task completion
- Tool efficiency
- Failure recovery
- Execution trajectory

### Evaluation Engineering

- Dataset-driven evaluation
- Deterministic metrics
- Metric aggregation
- Regression testing
- Threshold-based validation

### Backend Engineering

- FastAPI
- Pydantic
- SQLite
- REST APIs
- CLI applications
- Background execution
- Structured validation

### System Design

- Source-agnostic evaluation
- Trace normalization
- Separation of execution and evaluation
- Reusable evaluation components
- Independent system integration

---

## 29. Current Implementation Scope

The current implementation provides:

| Component | Status |
|---|---|
| Execution trace schema | Complete |
| Trace normalization | Complete |
| ResearchFlow integration | Complete |
| AgentOS integration | Complete |
| Retrieval evaluation | Complete |
| Agent evaluation | Complete |
| Answer evaluation | Complete |
| Performance evaluation | Complete |
| Dataset loading | Complete |
| Evaluation runner | Complete |
| Result aggregation | Complete |
| Regression comparison | Complete |
| FastAPI API | Complete |
| CLI | Complete |
| SQLite persistence | Complete |
| Sample datasets | Complete |
| LLM judge | Stub / Future |
| PostgreSQL persistence | Future |
| Semantic document relevance | Future |
| Advanced tool sequence evaluation | Future |

---

## 30. Limitations

Current limitations include:

- Evaluation quality depends on the quality of supplied execution traces.
- Missing retrieval or usage information limits the corresponding metrics.
- Groundedness is currently heuristic.
- Tool capability mapping is intentionally coarse.
- SQLite is intended for lightweight/local persistence.
- Background evaluation currently uses in-process FastAPI background tasks.
- Advanced semantic evaluation is not currently part of the core deterministic pipeline.

These limitations are intentional trade-offs for keeping the evaluation system focused and maintainable.

---

## 31. Future Improvements

Potential future improvements include:

- PostgreSQL-backed persistence
- Basic structured LLM-as-a-judge
- Semantic document relevance
- Dedicated tool sequence evaluation
- Additional performance metrics
- Dataset management APIs
- Markdown/HTML evaluation reports
- More advanced regression thresholds

These improvements can be introduced independently without changing the core architecture.

---

## 32. Quick Start

### Install

```powershell
cd AgentEval

.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

### Run Evaluation

```powershell
.\.venv\Scripts\python.exe -m agenteval run `
  --dataset data/datasets/sample_agent.json `
  --traces data/sample_traces/agentos_ag001.json `
  --output .agenteval/last_run.json
```

### Start API

```powershell
agenteval-api
```

API documentation:

```text
http://127.0.0.1:8010/docs
```

### Run Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

---

## 33. End-to-End Example

A typical evaluation flow looks like:

```text
1. User submits a task
          │
          ▼
2. AgentOS / ResearchFlow executes
          │
          ▼
3. System produces execution trace
          │
          ▼
4. Trace exported to AgentEval
          │
          ▼
5. AgentEval normalizes trace
          │
          ▼
6. Evaluation dataset is loaded
          │
          ▼
7. Metrics are executed
          │
          ├── Retrieval
          ├── Agent
          ├── Answer
          └── Performance
          │
          ▼
8. Results are aggregated
          │
          ▼
9. Evaluation run is persisted
          │
          ▼
10. Optional baseline comparison
          │
          ▼
11. Regression report
```

---

## 34. Project Boundaries

The three projects have clearly separated responsibilities:

```text
┌────────────────────────────────────────────────────┐
│                   ResearchFlow                     │
│                                                    │
│  Research planning                                 │
│  RAG retrieval                                     │
│  Evidence evaluation                               │
│  Research synthesis                                │
└───────────────────────┬────────────────────────────┘
                        │
                        │ Execution
                        ▼
┌────────────────────────────────────────────────────┐
│                     AgentOS                        │
│                                                    │
│  Agent planning                                    │
│  Tool selection                                    │
│  Tool execution                                    │
│  MCP                                               │
│  Memory                                            │
│  Human-in-the-loop                                 │
└───────────────────────┬────────────────────────────┘
                        │
                        │ Execution Trace
                        ▼
┌────────────────────────────────────────────────────┐
│                    AgentEval                       │
│                                                    │
│  Trace normalization                               │
│  Retrieval evaluation                              │
│  Agent evaluation                                  │
│  Answer evaluation                                 │
│  Performance evaluation                             │
│  Regression comparison                             │
└────────────────────────────────────────────────────┘
```

ResearchFlow and AgentOS focus on **executing AI workflows**.

AgentEval focuses on **measuring the quality and performance of those workflows**.

This separation allows AgentEval to be reused for future AI systems without coupling the evaluation platform to a particular agent implementation.


