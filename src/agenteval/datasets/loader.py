from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agenteval.datasets.models import EvaluationCase, EvaluationDataset, ExpectedOutcome, EvaluationConfig
from agenteval.datasets.validator import validate_dataset


def _case_from_flat(item: dict[str, Any]) -> EvaluationCase:
    """Overview section 12 flat case rows."""
    case_id = str(item.get("case_id") or item.get("id"))
    expected = ExpectedOutcome(
        answer=item.get("expected_answer") or item.get("expected_outcome"),
        documents=list(item.get("expected_documents") or []),
        tools=list(item.get("expected_tools") or []),
        topics=list(item.get("expected_topics") or []),
        tool_arguments=dict(item.get("expected_tool_arguments") or item.get("tool_arguments") or {}),
        output_format=item.get("expected_output_format") or item.get("output_format"),
    )
    question = item.get("question") or item.get("task") or ""
    metrics = list(item.get("metrics") or [])
    if not metrics:
        system = str(item.get("system") or "")
        metrics = (
            ["tool_selection_accuracy", "tool_success_rate", "task_completion", "answer_correctness"]
            if system == "agentos"
            else ["expected_document_recall", "recall_at_k", "answer_correctness", "topic_recall"]
        )
    return EvaluationCase(
        id=case_id,
        input={"question": question, "query": question},
        expected=expected,
        evaluation=EvaluationConfig(metrics=metrics),
        metadata={"system": item.get("system")},
    )


def _case_from_legacy(item: dict[str, Any]) -> EvaluationCase:
    """ResearchFlow benchmark JSON entries (question + expected_* fields)."""
    expected = ExpectedOutcome(
        answer=item.get("expected_answer"),
        topics=list(item.get("expected_topics") or []),
        documents=list(item.get("source_documents") or item.get("expected_documents") or []),
    )
    metrics = list(
        item.get("evaluation", {}).get("metrics")
        or [
            "expected_document_recall",
            "topic_recall",
            "answer_correctness",
        ]
    )
    return EvaluationCase(
        id=str(item["id"]),
        name=item.get("name"),
        input={"question": item.get("question", ""), "query": item.get("question", "")},
        expected=expected,
        evaluation=EvaluationConfig(metrics=metrics),
        metadata={"type": item.get("type"), "legacy_format": "researchflow_benchmark"},
    )


def load_cases_from_json(path: Path) -> list[EvaluationCase]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "cases" in data:
        dataset = EvaluationDataset.model_validate(data)
        validate_dataset(dataset)
        return dataset.cases
    if isinstance(data, list):
        cases: list[EvaluationCase] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            if "case_id" in item and ("task" in item or "question" in item):
                cases.append(_case_from_flat(item))
            elif "expected" in item and "input" in item:
                cases.append(EvaluationCase.model_validate(item))
            elif "question" in item and "id" in item:
                cases.append(_case_from_legacy(item))
        return cases
    raise ValueError(f"Unsupported dataset format in {path}")


def load_dataset(path: Path, dataset_id: str | None = None) -> EvaluationDataset:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "cases" in data:
        dataset = EvaluationDataset.model_validate(data)
    elif isinstance(data, list):
        cases = load_cases_from_json(path)
        dataset = EvaluationDataset(
            dataset_id=dataset_id or path.stem,
            cases=cases,
            metadata={"source_path": str(path)},
        )
    else:
        raise ValueError(f"Unsupported dataset format in {path}")
    if dataset_id:
        dataset = dataset.model_copy(update={"dataset_id": dataset_id})
    validate_dataset(dataset)
    return dataset
