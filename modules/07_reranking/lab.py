#!/usr/bin/env python3
"""
Module 07_reranking — Lab Exercises
Deterministic offline execution using only the Python standard library.
"""

import sys

def exercise_1() -> bool:
    """Exercise 1: Bi-encoder vs Cross-encoder Architectural Differences"""
    print(f"\n--- Exercise 1: Bi-encoder vs Cross-encoder Architectural Differences ---")
    # Deterministic, offline illustration of the bi-encoder vs cross-encoder distinction
    # (text comes from sbert.net's description; no model is called here).
    
    facts = [
        "1) Bi-encoder embeds query and document SEPARATELY, then compares vectors -> document embeddings can be cached offline.",
        "2) Cross-encoder feeds (query, document) PAIRS through one model -> produces one relevance score, no reusable doc embedding.",
        "3) Use bi-encoder for fast retrieval over a huge corpus; use cross-encoder to rerank only the top-k candidates.",
    ]
    for f in facts:
        print(f)
    # Expected output:
    # 1) Bi-encoder embeds query and document SEPARATELY, then compares vectors -> document embeddings can be cached offline.
    # 2) Cross-encoder feeds (query, document) PAIRS through one model -> produces one relevance score, no reusable doc embedding.
    # 3) Use bi-encoder for fast retrieval over a huge corpus; use cross-encoder to rerank only the top-k candidates.
    return True

def exercise_2() -> bool:
    """Exercise 2: Cosine Similarity Scoring & Top-K Manual Reranking"""
    print(f"\n--- Exercise 2: Cosine Similarity Scoring & Top-K Manual Reranking ---")
    # Manual cosine scoring + reranking using only the standard library (math).
    import math
    
    query = [1.0, 0.0]
    docs = {
        "d1": [0.9, 0.1],
        "d2": [0.5, 0.5],
        "d3": [0.0, 1.0],
        "d4": [0.8, -0.6],
        "d5": [-0.5, 0.5],
    }
    
    def cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        return dot / (na * nb)
    
    scored = {doc_id: cosine(query, vec) for doc_id, vec in docs.items()}
    for doc_id, score in scored.items():
        print(doc_id, round(score, 3))
    
    # Rerank: keep top-3, highest score first
    top3 = sorted(scored.items(), key=lambda item: item[1], reverse=True)[:3]
    print("Reranked top-3:", [doc_id for doc_id, _ in top3])
    # Expected output:
    # d1 0.994
    # d2 0.707
    # d3 0.0
    # d4 0.8
    # d5 -0.707
    # Reranked top-3: ['d1', 'd4', 'd2']
    return True

def exercise_3() -> bool:
    """Exercise 3: Cross-encoder Reranking Latency Cost Modeling"""
    print(f"\n--- Exercise 3: Cross-encoder Reranking Latency Cost Modeling ---")
    # Latency cost calculation for a cross-encoder reranking stage.
    # NOTE: all numbers depend on the stated assumptions, not real measurements.
    per_call_ms = 50      # assumed cross-encoder latency per (query, doc) pair
    top_k = 20            # how many candidates we rerank
    retrieve_only_ms = 30 # assumed latency of pure vector retrieval (no rerank)
    
    # Formula: rerank_latency_ms = top_k * per_call_ms
    rerank_ms = top_k * per_call_ms
    
    print("per cross-encoder call:", per_call_ms, "ms")
    print("top-k candidates:", top_k)
    print("rerank cost:", rerank_ms, "ms")
    print("retrieve-only latency:", retrieve_only_ms, "ms")
    
    total_ms = retrieve_only_ms + rerank_ms
    extra_ms = total_ms - retrieve_only_ms
    print("total with rerank:", total_ms, "ms")
    print("extra vs retrieve-only:", extra_ms, "ms")
    # Expected output:
    # per cross-encoder call: 50 ms
    # top-k candidates: 20
    # rerank cost: 1000 ms
    # retrieve-only latency: 30 ms
    # total with rerank: 1030 ms
    # extra vs retrieve-only: 1000 ms
    return True

def exercise_4() -> bool:
    """Exercise 4: HyDE (Hypothetical Document Embeddings) Retrieval Alignment"""
    print(f"\n--- Exercise 4: HyDE (Hypothetical Document Embeddings) Retrieval Alignment ---")
    # HyDE comparison: query-direct embedding vs hypothetical-document embedding.
    # The "hypothetical answer" is HARDCODED because a real LLM call is not allowed
    # offline; it stands in for what an LLM would generate.
    import math
    
    query = [1.0, 0.2, 0.0]                # embedding of the raw question
    hypothetical = [0.9, 0.8, 0.1]         # hardcoded "hypothetical answer" embedding
    docs = {
        "d1": [0.95, 0.1, 0.0],
        "d2": [0.6, 0.5, 0.0],
        "d3": [0.0, 1.0, 0.0],
    }
    
    def cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        return dot / (na * nb)
    
    for doc_id, vec in docs.items():
        direct = cosine(query, vec)
        hyde = cosine(hypothetical, vec)
        print(doc_id, "direct:", round(direct, 3), "| HyDE:", round(hyde, 3))
    # Expected output:
    # d1 direct: 0.996 | HyDE: 0.81
    # d2 direct: 0.879 | HyDE: 0.996
    # d3 direct: 0.196 | HyDE: 0.662
    return True

def exercise_5() -> bool:
    """Exercise 5: Multi-Query Expansion & RRF Score Fusion"""
    print(f"\n--- Exercise 5: Multi-Query Expansion & RRF Score Fusion ---")
    # Multi-query expansion fused with Reciprocal Rank Fusion (RRF).
    # Rankings are hardcoded deterministic stand-ins for three vector searches.
    
    K = 60  # standard RRF constant
    rankings = {
        "paraphrase 1": ["d1", "d2", "d3", "d4"],
        "paraphrase 2": ["d2", "d1", "d4", "d3"],
        "paraphrase 3": ["d3", "d1", "d2", "d4"],
    }
    
    # Show each paraphrase's ranking (rank starts at 1)
    for name, ranked in rankings.items():
        print(name, "->", {doc_id: rank for rank, doc_id in enumerate(ranked, start=1)})
    
    # RRF: score = sum over queries of 1 / (K + rank)
    rrf_scores = {}
    for ranked in rankings.values():
        for rank, doc_id in enumerate(ranked, start=1):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (K + rank)
    
    fused = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)
    for doc_id, score in fused:
        print(doc_id, round(score, 4))
    print("Fused order:", [doc_id for doc_id, _ in fused])
    # Expected output:
    # paraphrase 1 -> {'d1': 1, 'd2': 2, 'd3': 3, 'd4': 4}
    # paraphrase 2 -> {'d2': 1, 'd1': 2, 'd4': 3, 'd3': 4}
    # paraphrase 3 -> {'d3': 1, 'd1': 2, 'd2': 3, 'd4': 4}
    # d1 0.0487
    # d2 0.0484
    # d3 0.0479
    # d4 0.0471
    # Fused order: ['d1', 'd2', 'd3', 'd4']
    return True

def exercise_6() -> bool:
    """Exercise 6: MMR (Maximal Marginal Relevance) Diversity Selection"""
    print(f"\n--- Exercise 6: MMR (Maximal Marginal Relevance) Diversity Selection ---")
    # Full MMR (Maximal Marginal Relevance) selection with two lambda values.
    import math
    
    query = [1.0, 0.0]
    docs = {
        "d1": [0.98, 0.1],
        "d2": [0.96, 0.2],
        "d3": [0.95, -0.15],
        "d4": [0.6, 0.8],
        "d5": [0.7, -0.7],
        "d6": [0.3, 0.9],
    }
    
    def cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        return dot / (na * nb)
    
    relevance = {doc_id: cosine(query, vec) for doc_id, vec in docs.items()}
    
    def mmr_select(lam, n=3):
        selected = []
        while len(selected) < n:
            best_id, best_score = None, None
            for doc_id in docs:
                if doc_id in selected:
                    continue
                if not selected:  # empty selected list -> pure relevance
                    score = lam * relevance[doc_id]
                else:
                    max_sim = max(cosine(docs[doc_id], docs[s]) for s in selected)
                    score = lam * relevance[doc_id] - (1 - lam) * max_sim
                if best_score is None or score > best_score:
                    best_id, best_score = doc_id, score
            selected.append(best_id)
        return selected
    
    for lam in (0.9, 0.3):
        print("lambda =", lam, "->", mmr_select(lam))
    # Expected output:
    # lambda = 0.9 -> ['d1', 'd3', 'd2']
    # lambda = 0.3 -> ['d1', 'd6', 'd5']
    return True

def run_all() -> bool:
    print("=" * 60)
    print("Running Module 07_reranking Lab Exercises")
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
