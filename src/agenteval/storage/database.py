from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from agenteval.config import get_settings


def get_engine() -> Engine:
    """SQLAlchemy engine from DATABASE_URL (sqlite or postgresql)."""
    settings = get_settings()
    url = settings.database_url
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args)
