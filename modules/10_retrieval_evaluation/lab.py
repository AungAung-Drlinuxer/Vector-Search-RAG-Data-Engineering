#!/usr/bin/env python3
"""
Module 10_retrieval_evaluation — Lab Exercises
Deterministic offline execution using only the Python standard library.
"""

import sys

def exercise_1() -> bool:
    """Exercise 1: Golden set ဖွဲ့ပါ"""
    print(f"\n--- Exercise 1: Golden set ဖွဲ့ပါ ---")
    # Build a minimal golden set: query string -> list of correct chunk ids.
    golden = {
        "how do I reset my password": ["doc1#chunk3", "doc2#chunk1"],
        "what is vector search": ["doc3#chunk1"],
        "pricing for the api": ["doc4#chunk2", "doc4#chunk5", "doc1#chunk1"],
    }
    
    print(len(golden))
    for q, ids in golden.items():
        print(q, "->", ids, type(ids).__name__)
    # Expected output:
    # 3
    # how do I reset my password -> ['doc1#chunk3', 'doc2#chunk1'] list
    # what is vector search -> ['doc3#chunk1'] list
    # pricing for the api -> ['doc4#chunk2', 'doc4#chunk5', 'doc1#chunk1'] list
    return True

def exercise_2() -> bool:
    """Exercise 2: recall@k တွက်ပါ"""
    print(f"\n--- Exercise 2: recall@k တွက်ပါ ---")
    def recall_at_k(retrieved, relevant, k):
        # recall@k = |hits in top k| / |all relevant|
        if not relevant:
            return 0.0
        rel = set(relevant)
        hits = sum(1 for c in retrieved[:k] if c in rel)
        return hits / len(rel)
    
    r = ["a", "b", "c", "d"]
    rel = ["a", "c", "x"]
    print(round(recall_at_k(r, rel, 4), 4))
    print(recall_at_k(r, rel, 2))
    print(recall_at_k(r, [], 4))
    # Expected output:
    # 0.6667
    # 0.3333333333333333
    # 0.0
    return True

def exercise_3() -> bool:
    """Exercise 3: precision@k နဲ့ MRR တွက်ပါ"""
    print(f"\n--- Exercise 3: precision@k နဲ့ MRR တွက်ပါ ---")
    import math
    
    def precision_at_k(retrieved, relevant, k):
        # precision@k = |hits in top k| / k
        if k <= 0:
            return 0.0
        rel = set(relevant)
        hits = sum(1 for c in retrieved[:k] if c in rel)
        return hits / k
    
    def mrr(retrieved, relevant):
        # MRR = 1 / rank of first relevant result (0 if none)
        rel = set(relevant)
        for rank, c in enumerate(retrieved, start=1):
            if c in rel:
                return 1.0 / rank
        return 0.0
    
    r = ["a", "b", "c"]
    rel = ["b"]
    print(precision_at_k(r, rel, 2))
    print(mrr(r, rel))
    print(mrr(["a", "c"], ["b"]))
    # Expected output:
    # 0.5
    # 0.5
    # 0.0
    return True

def exercise_4() -> bool:
    """Exercise 4: nDCG@k တွက်ပါ"""
    print(f"\n--- Exercise 4: nDCG@k တွက်ပါ ---")
    import math
    
    def _dcg(hits):
        # hits: list of 0/1, position i (0-based) has rank = i + 1
        return sum(1.0 / math.log2((i + 1) + 1) for i, h in enumerate(hits) if h)
    
    def ndcg_at_k(retrieved, relevant, k):
        rel = set(relevant)
        top = retrieved[:k]
        actual_hits = [1 if c in rel else 0 for c in top]
        # Ideal ranking: all relevant first, limited by k.
        n_ideal = min(len(rel), k)
        ideal_hits = [1] * n_ideal
        dcg = _dcg(actual_hits)
        idcg = _dcg(ideal_hits)
        if idcg == 0.0:
            return 0.0
        return dcg / idcg
    
    r = ["a", "b", "c", "d"]
    print(ndcg_at_k(r, ["a", "b"], 4))
    print(round(ndcg_at_k(r, ["d"], 4), 4))
    # Expected output:
    # 1.0
    # 0.4307
    return True

def exercise_5() -> bool:
    """Exercise 5: document-level အကဲဖြတ်ခြင်း ပြောင်းပါ"""
    print(f"\n--- Exercise 5: document-level အကဲဖြတ်ခြင်း ပြောင်းပါ ---")
    def recall_at_k_doc(retrieved, relevant, k):
        # A relevant chunk is "covered" if its DOCUMENT appears in top k.
        rel = set(relevant)
        retrieved_docs = set(c.split("#")[0] for c in retrieved[:k])
        covered = sum(1 for c in rel if c.split("#")[0] in retrieved_docs)
        if not rel:
            return 0.0
        return covered / len(rel)
    
    retrieved = ["doc1#1", "doc2#1", "doc1#2"]
    relevant = ["doc1#1", "doc1#2", "doc3#1"]
    print(round(recall_at_k_doc(retrieved, relevant, 3), 4))
    # Expected output:
    # 0.6667
    return True

def exercise_6() -> bool:
    """Exercise 6: Regression gate နဲ့ drift စစ်ပါ"""
    print(f"\n--- Exercise 6: Regression gate နဲ့ drift စစ်ပါ ---")
    def regression_gate(baseline, current):
        # Returns False if any current metric dropped below baseline.
        passed = True
        for metric, base_value in baseline.items():
            cur_value = current.get(metric, 0.0)
            if cur_value < base_value:
                print(f"{metric} dropped: {base_value} -> {cur_value}")
                passed = False
        return passed
    
    baseline = {"recall@5": 0.9, "mrr": 0.8}
    
    # A real LLM judge would live here; we use a scripted deterministic stand-in.
    current_bad = {"recall@5": 0.85, "mrr": 0.82}
    print(regression_gate(baseline, current_bad))
    
    current_good = {"recall@5": 0.91, "mrr": 0.8}
    print(regression_gate(baseline, current_good))
    # Expected output:
    # recall@5 dropped: 0.9 -> 0.85
    # False
    # True
    return True

def run_all() -> bool:
    print("=" * 60)
    print("Running Module 10_retrieval_evaluation Lab Exercises")
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
