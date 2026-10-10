# AgentEval

Lightweight evaluation platform for **ResearchFlow**, **AgentOS**, and other systems that emit a simple **execution trace** JSON.

Design reference: [projectoverview.md](projectoverview.md) (aligned with the simplified portfolio scope).

## Setup

```powershell
cd AgentEval
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
copy .env.example .env
```

Use `.\.venv\Scripts\python.exe` — not bare `python` if LibreOffice is on PATH.

## Trace format (normalized)

```json
{
  "run_id": "run_123",
  "system": "agentos",
  "input": "User task text",
  "steps": [{"step": 1, "tool": "query_database", "arguments": {}, "status": "success"}],
  "retrievals": [{"source": "doc.pdf", "rank": 1}],
  "final_answer": "...",
  "usage": {"latency_ms": 5400, "total_tokens": 0},
  "status": "completed"
}
```

AgentOS and ResearchFlow exports are **normalized** automatically (`traces/normalizer.py`).

## CLI

```powershell
.\.venv\Scripts\python.exe -m agenteval run `
  --dataset data/datasets/sample_agent.json `
  --traces data/sample_traces/agentos_ag001.json `
  --output .agenteval/last_run.json
```

Flat dataset rows: `data/researchflow/`, `data/agentos/`.

## API

```powershell
agenteval-api
```

| Method | Path |
|--------|------|
| GET | `/health`, `/ready` |
| POST | `/traces` |
| GET | `/traces/{run_id}` |
| POST | `/evaluations/run` |
| GET | `/evaluations/{evaluation_id}` |
| GET | `/evaluations/{evaluation_id}/results` |
| POST | `/regression/run` |

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

## Project layout

Matches overview section 19: `evaluators/{retrieval,agent,answer,performance}.py`, `evaluation/runner.py`, `judges/llm_judge.py`, `storage/`, `api/routes.py`.

See [ARCHITECTURE.md](ARCHITECTURE.md) and [EVALUATORS.md](EVALUATORS.md).
