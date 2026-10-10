from __future__ import annotations


class AgentEvalError(Exception):
    """Base error for AgentEval."""


class TraceValidationError(AgentEvalError):
    """Raw or normalized trace failed validation."""


class DatasetValidationError(AgentEvalError):
    """Dataset or case failed validation."""


class EvaluatorNotFoundError(AgentEvalError):
    """Requested metric has no registered evaluator."""
