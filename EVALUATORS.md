# AgentEval evaluators

All metrics listed in [projectoverview.md](projectoverview.md) are registered in `evaluators/registry.py`.

| Module | Metrics |
|--------|---------|
| `retrieval.py` | `recall_at_k`, `precision_at_k`, `mrr`, `hit_rate_at_k`, `expected_document_recall` |
| `agent.py` | `tool_selection_accuracy`, `tool_argument_correctness`, `tool_success_rate`, `task_completion`, `tool_efficiency`, `trajectory_quality`, `failure_recovery` |
| `answer.py` | `answer_correctness`, `topic_recall`, `answer_relevance`, `groundedness`, `output_format` |
| `performance.py` | `latency_ms`, `total_tokens`, `estimated_cost`, `cost_per_successful_task` |

Optional: `judges/llm_judge.py` when `ENABLE_LLM_JUDGE=true`.
