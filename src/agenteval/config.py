from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(default="sqlite:///./.agenteval/agenteval.db", alias="DATABASE_URL")
    data_dir: Path = Field(default=Path(".agenteval"), alias="AGENTEVAL_DATA_DIR")

    default_judge_model: str = Field(default="gemini-3.8-flash", alias="DEFAULT_JUDGE_MODEL")
    enable_llm_judge: bool = Field(default=False, alias="ENABLE_LLM_JUDGE")
    google_api_key: str | None = Field(default=None, alias="GOOGLE_API_KEY")

    max_concurrent_cases: int = Field(default=4, alias="MAX_CONCURRENT_CASES")
    max_concurrent_judges: int = Field(default=2, alias="MAX_CONCURRENT_JUDGES")
    default_timeout_seconds: int = Field(default=300, alias="DEFAULT_TIMEOUT_SECONDS")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_json: bool = Field(default=True, alias="LOG_JSON")

    topic_pass_recall: float = Field(default=0.5, alias="BENCHMARK_TOPIC_PASS_RECALL")
    answer_pass_similarity: float = Field(default=0.35, alias="BENCHMARK_ANSWER_PASS_SIMILARITY")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return settings
