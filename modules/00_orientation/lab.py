#!/usr/bin/env python3
"""
Module 00: Orientation — Lab Exercises
Deterministic offline execution using only the Python standard library.
"""

import math
import sys

def exercise_1() -> bool:
    """Exercise 1: Pipeline 8 stages order & architectural reasoning."""
    print("\n--- Exercise 1: Pipeline Stages Order ---")
    pipeline = [
        ("ingest",   "Collect and clean raw source documents first; nothing downstream exists without data."),
        ("chunk",    "Split documents into small passages so each retrievable unit carries one focused idea."),
        ("embed",    "Turn each chunk into a numeric vector that captures semantic meaning."),
        ("index",    "Store vectors in an index (e.g., pgvector) so search is fast, not a full scan."),
        ("retrieve", "At query time, fetch the most similar chunks using the index."),
        ("rerank",   "Reorder the retrieved candidates with a stronger (often cross-encoder) scorer."),
        ("generate", "Feed the top chunks to the LLM (here a scripted stand-in, no real model call) to answer."),
        ("evaluate", "Finally, measure the quality of the answer so the pipeline can be tuned."),
    ]
    for i, (stage, why) in enumerate(pipeline, 1):
        print(f"{i}. {stage}: {why}")
    order_str = " -> ".join(s for s, _ in pipeline)
    print("Full order:", order_str)
    
    assert len(pipeline) == 8
    assert pipeline[0][0] == "ingest"
    assert pipeline[-1][0] == "evaluate"
    return True

def exercise_2() -> bool:
    """Exercise 2: Chunk definition & small vs large chunks comparison."""
    print("\n--- Exercise 2: Chunk Definition & Sizing Trade-Off ---")
    definition = ("A chunk is a small, self-contained piece of a larger document "
                  "(e.g., a paragraph or fixed-length passage) that is the unit "
                  "we embed, index, and retrieve in a RAG pipeline.")
    print(definition)
    
    rows = [
        ("(a) very small chunks",
         "Precise matches; search finds the exact sentence; low memory per chunk",
         "Context is cut off; the retriever returns fragments too short for the LLM to use"),
        ("(b) very large chunks",
         "Rich context; the LLM gets the full surrounding story",
         "Diluted similarity; a vector averages many ideas, so ranking is noisy and costs are high"),
    ]
    print(f"\n{'chunk size':<28} | {'PROS':<52} | {'CONS'}")
    for label, pros, cons in rows:
        print(f"{label:<28} | {pros:<52} | {cons}")
        
    assert len(rows) == 2
    return True

def exercise_3() -> bool:
    """Exercise 3: Cosine similarity calculation."""
    print("\n--- Exercise 3: Cosine Similarity ---")
    def cosine_similarity(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        return dot / (norm_a * norm_b)

    a = [1.0, 0.0]
    b = [0.0, 1.0]
    c = [1.0, 1.0]

    sim_ab = cosine_similarity(a, b)
    sim_ac = cosine_similarity(a, c)
    print(f"cosine(a, b) = {sim_ab:.4f}")
    print(f"cosine(a, c) = {sim_ac:.4f}")
    
    assert math.isclose(sim_ab, 0.0, abs_tol=1e-4)
    assert math.isclose(sim_ac, math.sqrt(2)/2, abs_tol=1e-4)
    return True

def exercise_4() -> bool:
    """Exercise 4: Search modality decision framework."""
    print("\n--- Exercise 4: Search Modality Decision ---")
    decisions = [
        ("error code E-4471",
         "keyword search",
         "Exact codes like E-4471 must match character-for-character."),
        ("ဆီးချိုရောဂါအတွက် အစားအသောက် အကြံပြုချက်",
         "vector search",
         "Semantic paraphrase requires embedding representation."),
        ("မြန်မာနိုင်ငံ ခရီးသွား အကြံပြုချက် ၂၀၂၄",
         "hybrid search",
         "Semantic topic + exact temporal/entity filter requires hybrid fusion."),
    ]
    for query, choice, reason in decisions:
        print(f"query:   {query}\nchoice:  {choice}\nreason:  {reason}\n")
    assert len(decisions) == 3
    return True

def exercise_5() -> bool:
    """Exercise 5: Raw embedding memory calculation."""
    print("\n--- Exercise 5: Embedding Memory Math ---")
    num_chunks = 1_000_000
    dimensions = 768
    bytes_per_float = 4          # fp32 = 4 bytes
    bytes_per_chunk = dimensions * bytes_per_float
    total_bytes = num_chunks * bytes_per_chunk
    gb = 1024 * 1024 * 1024
    total_gb = total_bytes / gb

    print(f"bytes per chunk      = {bytes_per_chunk} B")
    print(f"total bytes          = {total_bytes} B")
    print(f"total GB             = {total_gb:.2f} GB")
    
    assert bytes_per_chunk == 3072
    assert total_bytes == 3_072_000_000
    assert math.isclose(total_gb, 2.861, rel_tol=1e-2)
    return True

def exercise_6() -> bool:
    """Exercise 6: Reciprocal Rank Fusion (RRF) implementation."""
    print("\n--- Exercise 6: Reciprocal Rank Fusion (RRF) ---")
    vector_ranking = ["doc_c", "doc_a", "doc_b"]
    keyword_ranking = ["doc_a", "doc_b", "doc_d"]
    k = 60

    scores = {}
    for ranking in (vector_ranking, keyword_ranking):
        for rank, doc in enumerate(ranking, start=1):
            scores[doc] = scores.get(doc, 0.0) + 1.0 / (k + rank)

    final_ranking = sorted(scores, key=lambda d: scores[d], reverse=True)
    for doc in final_ranking:
        print(f"{doc}: {scores[doc]:.4f}")
    print("Final ranking:", " > ".join(final_ranking))
    
    assert final_ranking == ["doc_a", "doc_b", "doc_c", "doc_d"]
    assert math.isclose(scores["doc_a"], (1/62 + 1/61), rel_tol=1e-3)
    return True

def run_all() -> bool:
    print("=" * 60)
    print("Running Module 00 (Orientation) Lab Exercises")
    print("=" * 60)
    tests = [exercise_1, exercise_2, exercise_3, exercise_4, exercise_5, exercise_6]
    passed = 0
    for t in tests:
        try:
            if t():
                passed += 1
        except Exception as e:
            print(f"[FAIL] {t.__name__}: {e}")
            return False
    print(f"\n[PASS] All {passed}/{len(tests)} exercises passed successfully.")
    return True

if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
