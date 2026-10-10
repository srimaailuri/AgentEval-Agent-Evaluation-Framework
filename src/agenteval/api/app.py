from __future__ import annotations

from fastapi import FastAPI

from agenteval.api.routes import router
from agenteval.api.schemas import HealthResponse, ReadyResponse
from agenteval.evaluators.registry import build_default_registry
from agenteval.storage.store import EvaluationStore

app = FastAPI(title="AgentEval", version="0.1.0")
app.include_router(router)

_store: EvaluationStore | None = None


def get_store() -> EvaluationStore:
    global _store
    if _store is None:
        _store = EvaluationStore()
    return _store


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.get("/ready", response_model=ReadyResponse)
def ready() -> ReadyResponse:
    return ReadyResponse(ready=True, evaluators_loaded=len(build_default_registry()))


def main() -> None:
    import uvicorn

    uvicorn.run("agenteval.api.app:app", host="127.0.0.1", port=8010, reload=False)


if __name__ == "__main__":
    main()
