from typing import List, Dict


def retrieval_hit(
    retrieved_sources: List[str],
    expected_sources: List[str],
) -> bool:
    """True if at least one retrieved source is in expected sources."""
    return any(src in expected_sources for src in retrieved_sources)


def keyword_coverage(
    answer: str,
    expected_keywords: List[str],
) -> float:
    """Fraction of expected keywords present in the answer (case-insensitive)."""
    if not expected_keywords:
        return 1.0
    answer_lower = answer.lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
    return hits / len(expected_keywords)