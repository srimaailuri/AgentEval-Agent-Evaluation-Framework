from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agenteval.traces.schema import ExecutionTrace

_TOPIC_STOPWORDS = frozenset({"the", "and", "for", "with", "from", "that", "this"})


def normalize_text(text: str) -> str:
    cleaned = text.lower()
    cleaned = re.sub(r"[^\w\s-]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def normalize_document_stem(name: str) -> str:
    stem = name.strip().lower()
    for suffix in (".pdf", ".txt", ".md"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
    return stem


def topic_is_present(corpus: str, topic: str) -> bool:
    corpus_norm = normalize_text(corpus.replace("-", " "))
    topic_norm = normalize_text(topic.replace("-", " "))
    if not topic_norm:
        return False
    if topic_norm in corpus_norm:
        return True
    tokens = [t for t in topic_norm.split() if len(t) > 2 and t not in _TOPIC_STOPWORDS]
    if len(tokens) >= 2:
        return all(token in corpus_norm for token in tokens)
    return topic_norm in corpus_norm


def answer_similarity(expected_answer: str, generated_text: str) -> float:
    if not expected_answer.strip():
        return 1.0
    if not generated_text.strip():
        return 0.0
    expected = normalize_text(expected_answer)
    generated = normalize_text(generated_text)
    sequence_ratio = SequenceMatcher(None, expected, generated).ratio()
    expected_tokens = {t for t in expected.split() if len(t) > 2}
    generated_tokens = {t for t in generated.split() if len(t) > 2}
    if not expected_tokens:
        return round(sequence_ratio, 4)
    token_recall = len(expected_tokens & generated_tokens) / len(expected_tokens)
    return round(0.45 * sequence_ratio + 0.55 * token_recall, 4)


def retrieval_document_ids(trace: ExecutionTrace) -> list[str]:
    ids: list[str] = []
    meta_ids = trace.metadata.get("rag_document_ids") or []
    ids.extend(str(x) for x in meta_ids if x)
    for item in trace.retrievals:
        if not isinstance(item, dict):
            continue
        doc = item.get("source") or item.get("document_id")
        if doc:
            ids.append(str(doc))
    return ids


def tool_capabilities(trace: ExecutionTrace) -> set[str]:
    caps: set[str] = set()
    for step in trace.steps:
        caps.add(_capability_from_tool_name(step.tool.lower()))
    return caps


def _capability_from_tool_name(name: str) -> str:
    if "github" in name or name.startswith("mcp."):
        return "github"
    if name in {"query_database", "postgres", "postgresql"} or "postgres" in name:
        return "postgresql"
    if "document" in name or name == "document_search":
        return "rag"
    if "web" in name:
        return "web"
    if name.endswith("_search"):
        return name.replace("_search", "")
    return name.split(".")[-1] if "." in name else name
