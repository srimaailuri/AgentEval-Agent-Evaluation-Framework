from __future__ import annotations

from pydantic import BaseModel, Field

from agenteval.config import get_settings


class JudgeResult(BaseModel):
    score: float = Field(ge=0.0, le=5.0)
    reason: str = ""
    model: str = ""
    prompt_version: str = "v1"


def run_llm_judge(prompt: str, *, task: str = "answer_correctness") -> JudgeResult:
    """Placeholder — wire Gemini when ENABLE_LLM_JUDGE=true and GOOGLE_API_KEY is set."""
    settings = get_settings()
    if not settings.enable_llm_judge:
        raise RuntimeError("LLM judge disabled (set ENABLE_LLM_JUDGE=true)")
    if not settings.google_api_key:
        raise RuntimeError("GOOGLE_API_KEY required for LLM judge")
    raise NotImplementedError("LLM judge integration is planned; use deterministic metrics for now.")
