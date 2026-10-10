# AgentEval architecture (simplified)

```text
Dataset case  +  raw execution trace (any supported shape)
        │
        ▼
  traces/normalizer.py  →  ExecutionTrace (simple contract)
        │
        ▼
  evaluation/runner.py  →  evaluators/*  →  MetricResult[]
        │
        ▼
  evaluation/aggregator.py  →  EvaluationRun + optional regression
```

No imports from ResearchFlow or AgentOS. Portfolio separation is documented in [projectoverview.md](projectoverview.md) section 23.
