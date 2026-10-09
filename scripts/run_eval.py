from rag_docs.evaluation.evaluator import run_evaluation

print("Running evaluation (15 questions)...\n")
summary = run_evaluation(top_k=4)

print("=" * 70)
print("EVALUATION SUMMARY")
print("=" * 70)
print(f"Questions         : {summary['total_questions']}")
print(f"Retrieval Recall  : {summary['retrieval_recall']:.3f}")
print(f"Keyword Coverage  : {summary['avg_keyword_coverage']:.3f}")
print()

print("Per-question breakdown:")
print("-" * 70)
for i, r in enumerate(summary["details"], start=1):
    if "error" in r:
        print(f"[{i}] ERROR: {r['error']}")
        continue
    hit = "✅" if r["retrieval_hit"] else "❌"
    print(f"[{i}] {hit} coverage={r['keyword_coverage']:.2f} | {r['question']}")
    print(f"     retrieved: {r['retrieved_sources'][0]}")
    print(f"     expected : {r['expected_sources'][0]}")
    print()