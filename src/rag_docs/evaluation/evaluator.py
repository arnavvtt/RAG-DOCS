import logging
from typing import Dict, List

from rag_docs.evaluation.dataset import load_eval_dataset
from rag_docs.evaluation.metrics import keyword_coverage, retrieval_hit
from rag_docs.services.qa_service import ask

logger = logging.getLogger(__name__)


def run_evaluation(
    dataset_path: str = "data/eval/qa_pairs.json",
    top_k: int = 4,
) -> Dict:
    """Run the full RAG pipeline over the eval dataset and compute metrics."""
    dataset = load_eval_dataset(dataset_path)

    results = []
    retrieval_hits = 0
    keyword_scores: List[float] = []

    for i, item in enumerate(dataset, start=1):
        question = item["question"]
        logger.info("[%d/%d] %s", i, len(dataset), question)

        try:
            output = ask(question, top_k=top_k)
        except Exception as e:
            logger.error("Failed: %s", e)
            results.append({"question": question, "error": str(e)})
            continue

        retrieved_sources = [s["filename"] for s in output["sources"]]
        hit = retrieval_hit(retrieved_sources, item["expected_sources"])
        coverage = keyword_coverage(output["answer"], item["expected_keywords"])

        retrieval_hits += int(hit)
        keyword_scores.append(coverage)

        results.append({
            "question": question,
            "answer": output["answer"],
            "retrieved_sources": retrieved_sources,
            "expected_sources": item["expected_sources"],
            "retrieval_hit": hit,
            "keyword_coverage": round(coverage, 3),
        })

    total = len(dataset)
    summary = {
        "total_questions": total,
        "retrieval_recall": round(retrieval_hits / total, 3) if total else 0,
        "avg_keyword_coverage": round(
            sum(keyword_scores) / len(keyword_scores), 3
        ) if keyword_scores else 0,
        "details": results,
    }
    return summary