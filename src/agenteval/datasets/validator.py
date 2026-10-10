from __future__ import annotations

from agenteval.core.exceptions import DatasetValidationError
from agenteval.datasets.models import EvaluationCase, EvaluationDataset


def validate_case(case: EvaluationCase) -> None:
    if not case.id.strip():
        raise DatasetValidationError("case id is required")
    if not case.input:
        raise DatasetValidationError(f"case {case.id}: input is required")


def validate_dataset(dataset: EvaluationDataset) -> None:
    if not dataset.dataset_id.strip():
        raise DatasetValidationError("dataset_id is required")
    seen: set[str] = set()
    for case in dataset.cases:
        validate_case(case)
        if case.id in seen:
            raise DatasetValidationError(f"duplicate case id: {case.id}")
        seen.add(case.id)
