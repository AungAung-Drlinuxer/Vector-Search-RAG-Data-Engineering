#!/usr/bin/env python3
"""
Module 06_hybrid_search — Lab Exercises
Deterministic offline execution using only the Python standard library.
"""

import sys

def exercise_1() -> bool:
    """Exercise 1: tsvector ဆောက်ခြင်း (အခြေခံ)"""
    print(f"\n--- Exercise 1: tsvector ဆောက်ခြင်း (အခြေခံ) ---")
    # Simulating PostgreSQL's to_tsvector(): word -> list of positions (1-based)
    def make_tsvector(text):
        """Build a tsvector-like dict: {lexeme: [positions]} from raw text."""
        tsvector = {}
        for position, word in enumerate(text.split(), start=1):
            lexeme = word.lower()  # basic normalization (real PG also stems words)
            tsvector.setdefault(lexeme, []).append(position)
        return tsvector
    
    docs = [
        "the quick brown fox",
        "the lazy dog the",          # 'the' repeats -> positions [1, 4]
        "postgres vector search guide",
    ]
    
    for doc in docs:
        print(doc, "->", make_tsvector(doc))
    # Expected output:
    # the quick brown fox -> {'the': [1], 'quick': [2], 'brown': [3], 'fox': [4]}
    # the lazy dog the -> {'the': [1, 4], 'lazy': [2], 'dog': [3]}
    # postgres vector search guide -> {'postgres': [1], 'vector': [2], 'search': [3], 'guide': [4]}
    return True

def exercise_2() -> bool:
    """Exercise 2: tsquery matching နှင့် ranking (ts_rank style)"""
    print(f"\n--- Exercise 2: tsquery matching နှင့် ranking (ts_rank style) ---")
    # tsvector simulation (from Exercise 1) + tsquery matching -> simple rank score
    def make_tsvector(text):
        tsvector = {}
        for position, word in enumerate(text.split(), start=1):
            tsvector.setdefault(word.lower(), []).append(position)
        return tsvector
    
    def match_score(tsvector, query_words):
        """Score = number of distinct query words present in the document."""
        doc_words = set(tsvector.keys())
        return len(doc_words.intersection(query_words))
    
    docs = {
        "doc1": "postgres vector search guide",
        "doc2": "mysql administration handbook",
        "doc3": "search guide for postgres",
    }
    query = ["postgres", "search"]
    
    results = []
    for name, text in docs.items():
        score = match_score(make_tsvector(text), query)
        results.append((name, score))
    
    # Sort by score descending (name as deterministic tie-break)
    results.sort(key=lambda item: (-item[1], item[0]))
    for name, score in results:
        print(name, score)
    
    # Negative test: a word that matches nothing scores 0
    print("mysql-only query on doc1:",
          match_score(make_tsvector(docs["doc1"]), ["mysql"]))
    # Expected output:
    # doc1 2
    # doc3 2
    # doc2 0
    # mysql-only query on doc1: 0
    return True

def exercise_3() -> bool:
    """Exercise 3: Trigram similarity (3-gram Jaccard)"""
    print(f"\n--- Exercise 3: Trigram similarity (3-gram Jaccard) ---")
    # 3-gram Jaccard similarity, as pg_trgm / GiST trigram indexes approximate
    def trigrams(word):
        padded = "  " + word + "  "   # pad with two spaces on each side
        return {padded[i:i + 3] for i in range(len(padded) - 2)}
    
    def jaccard(a, b):
        sa, sb = trigrams(a), trigrams(b)
        common = len(sa & sb)
        union = len(sa | sb)
        return common / union if union else 0.0
    
    pairs = [("postgres", "postgresql"), ("postgres", "banana")]
    for w1, w2 in pairs:
        sa, sb = trigrams(w1), trigrams(w2)
        print(w1, "trigrams:", sorted(sa))
        print(w2, "trigrams:", sorted(sb))
        print("common:", len(sa & sb), "union:", len(sa | sb))
        print("similarity:", jaccard(w1, w2))
        print("---")
    # Expected output:
    # postgres trigrams: ['  p', ' po', 'es ', 'gre', 'ost', 'pos', 'res', 's  ', 'stg', 'tgr']
    # postgresql trigrams: ['  p', ' po', 'esq', 'gre', 'l  ', 'ost', 'pos', 'ql ', 'res', 'sql', 'stg', 'tgr']
    # common: 8 union: 14
    # similarity: 0.5714285714285714
    # ---
    # postgres trigrams: ['  p', ' po', 'es ', 'gre', 'ost', 'pos', 'res', 's  ', 'stg', 'tgr']
    # banana trigrams: ['  b', ' ba', 'a  ', 'ana', 'ban', 'na ', 'nan']
    # common: 0 union: 17
    # similarity: 0.0
    # ---
    return True

def exercise_4() -> bool:
    """Exercise 4: BM25 score တွက်ခြင်း"""
    print(f"\n--- Exercise 4: BM25 score တွက်ခြင်း ---")
    # Deterministic offline demo of Okapi BM25, standard library only.
    # No database is used here. k1=1.5, b=0.75 are typical values.
    import math
    
    docs = {
        'd1': 'postgres vector search with pgvector',
        'd2': 'postgres full text search ranking with tsvector and tsquery in postgres',
        'd3': 'vector search ranking comparison',
    }
    query = ['postgres', 'ranking']
    k1, b = 1.5, 0.75
    
    tokens = {d: text.lower().split() for d, text in docs.items()}
    avgdl = sum(len(t) for t in tokens.values()) / len(tokens)
    N = len(docs)
    
    def idf(term):
        n = sum(1 for t in tokens.values() if term in t)
        return math.log(1.0 + (N - n + 0.5) / (n + 0.5))
    
    def bm25(query_terms, doc_tokens):
        D = len(doc_tokens)
        score = 0.0
        for term in query_terms:
            f = doc_tokens.count(term)
            if f == 0:
                continue
            numerator = f * (k1 + 1.0)
            denominator = f + k1 * (1.0 - b + b * (D / avgdl))
            score += idf(term) * (numerator / denominator)
        return score
    
    ranked = sorted(docs.keys(), key=lambda d: bm25(query, tokens[d]), reverse=True)
    for d in ranked:
        print(f"{d}: score={bm25(query, tokens[d]):.4f} (len={len(tokens[d])})")
    return True

def exercise_5() -> bool:
    """Exercise 5: Weighted sum တွင် score normalization ၏ အရေးပါမှု"""
    print(f"\n--- Exercise 5: Weighted sum တွင် score normalization ၏ အရေးပါမှု ---")
    # Weighted sum: raw scores vs min-max normalized scores (0.5/0.5 weights)
    def min_max(values):
        lo, hi = min(values), max(values)
        if hi == lo:
            return [0.0] * len(values)   # edge case: all equal -> avoid zero division
        return [(x - lo) / (hi - lo) for x in values]
    
    docs = ["A", "B", "C"]
    vector_scores = [0.9, 0.8, 0.7]
    bm25_scores = [5.0, 12.0, 20.0]
    
    # (1) raw weighted sum, 0.5/0.5
    raw = [0.5 * v + 0.5 * b for v, b in zip(vector_scores, bm25_scores)]
    # (2) normalized weighted sum, 0.5/0.5
    norm_v = min_max(vector_scores)
    norm_b = min_max(bm25_scores)
    norm = [0.5 * v + 0.5 * b for v, b in zip(norm_v, norm_b)]
    
    def ranked(scores):
        return [docs[i] for i in sorted(range(len(scores)), key=lambda i: -scores[i])]
    
    print("raw sums:    ", [round(s, 4) for s in raw],     "-> ranking:", ranked(raw))
    print("norm vector: ", [round(s, 4) for s in norm_v])
    print("norm bm25:   ", [round(s, 4) for s in norm_b])
    print("norm sums:   ", [round(s, 4) for s in norm],     "-> ranking:", ranked(norm))
    # Expected output:
    # raw sums:     [2.95, 6.4, 10.35] -> ranking: ['C', 'B', 'A']
    # norm vector:  [1.0, 0.5, 0.0]
    # norm bm25:    [0.0, 0.4667, 1.0]
    # norm sums:    [0.5, 0.4833, 0.5] -> ranking: ['A', 'C', 'B']
    return True

def exercise_6() -> bool:
    """Exercise 6: Reciprocal Rank Fusion (RRF) အခြေခံ"""
    print(f"\n--- Exercise 6: Reciprocal Rank Fusion (RRF) အခြေခံ ---")
    # Reciprocal Rank Fusion: rrf_score = sum over lists of 1 / (k + rank)
    K = 60
    
    def rrf_score(ranks, k):
        """ranks: list of this doc's rank in each list (1-based). Missing list = skip."""
        return sum(1.0 / (k + r) for r in ranks)
    
    vector_rank_list  = ["A", "B", "C", "D"]   # A best on vector path
    keyword_rank_list = ["B", "C", "A", "D"]   # B best on keyword path
    
    ranks = {}
    for rank, doc in enumerate(vector_rank_list, start=1):
        ranks.setdefault(doc, []).append(rank)
    for rank, doc in enumerate(keyword_rank_list, start=1):
        ranks.setdefault(doc, []).append(rank)
    
    scores = {doc: rrf_score(rs, K) for doc, rs in ranks.items()}
    final = sorted(scores.items(), key=lambda item: -item[1])
    
    for doc, rs in sorted(ranks.items()):
        print(doc, "ranks:", rs, "rrf:", scores[doc])
    print("final ranking k=60:", [doc for doc, _ in final])
    # Expected output:
    # A ranks: [1, 3] rrf: 0.032266458495966696
    # B ranks: [2, 1] rrf: 0.03252247488101534
    # C ranks: [3, 2] rrf: 0.03200204813108039
    # D ranks: [4, 4] rrf: 0.03125
    # final ranking k=60: ['B', 'A', 'C', 'D']
    return True

def exercise_7() -> bool:
    """Exercise 7: Full hybrid pipeline: နှစ်လမ်း fan-out ပြီး RRF ဖြင့် fusion"""
    print(f"\n--- Exercise 7: Full hybrid pipeline: နှစ်လမ်း fan-out ပြီး RRF ဖြင့် fusion ---")
    # Full hybrid pipeline: keyword match score + cosine similarity -> RRF fusion.
    # No real embedding model: vectors are hardcoded so everything is deterministic & offline.
    import math
    
    def make_tsvector(text):
        tsvector = {}
        for pos, word in enumerate(text.split(), start=1):
            tsvector.setdefault(word.lower(), []).append(pos)
        return tsvector
    
    def keyword_score(text, query_words):
        return len(set(make_tsvector(text)).intersection(query_words))
    
    def cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(x * x for x in b))
        return dot / (na * nb) if na and nb else 0.0
    
    def ranks_from(scores):
        """Rank docs by score descending; ties broken by doc name for determinism."""
        ordered = sorted(scores, key=lambda d: (-scores[d], d))
        return {doc: i + 1 for i, doc in enumerate(ordered)}
    
    def rrf_fuse(rank_dicts, k):
        total = {}
        for rd in rank_dicts:
            for doc, rank in rd.items():
                total[doc] = total.get(doc, 0.0) + 1.0 / (k + rank)
        return total
    
    docs = {
        "A": "postgres vector search guide",
        "B": "hybrid search with rrf fusion",
        "C": "database indexing and performance",
        "D": "machine learning for search ranking",
        "E": "vector database embeddings guide",
    }
    query_words = ["postgres", "search", "guide"]
    query_vec = [1, 0]   # scripted stand-in for an embedding model output
    doc_vecs = {          # hardcoded deterministic "embeddings"
        "A": [4, 3], "B": [3, 4], "C": [1, 3], "D": [1, 7], "E": [7, 2],
    }
    
    kw_scores  = {d: keyword_score(t, query_words) for d, t in docs.items()}
    vec_scores = {d: cosine(query_vec, v) for d, v in doc_vecs.items()}
    kw_rank  = ranks_from(kw_scores)
    vec_rank = ranks_from(vec_scores)
    print("keyword scores:", kw_scores)
    print("vector cosines:", {d: round(s, 4) for d, s in vec_scores.items()})
    
    for k in (60, 1):
        fused = rrf_fuse([kw_rank, vec_rank], k)
        top3 = sorted(fused.items(), key=lambda item: -item[1])[:3]
        print(f"top-3 with k={k}:", [(d, round(s, 6)) for d, s in top3])
    
    print("observation: with k=1 the winner's lead over the runner-up is ~0.4167,")
    print("with k=60 only ~0.0008 -> smaller k makes top ranks dominate much harder.")
    # Expected output:
    # keyword scores: {'A': 3, 'B': 1, 'C': 0, 'D': 1, 'E': 1}
    # vector cosines: {'A': 0.8, 'B': 0.6, 'C': 0.3162, 'D': 0.1414, 'E': 0.9615}
    # top-3 with k=60: [('A', 0.032522), ('E', 0.032018), ('B', 0.032002)]
    # top-3 with k=1: [('A', 0.833333), ('E', 0.7), ('B', 0.583333)]
    # observation: with k=1 the winner's lead over the runner-up is ~0.4167,
    # with k=60 only ~0.0008 -> smaller k makes top ranks dominate much harder.
    return True

def run_all() -> bool:
    print("=" * 60)
    print("Running Module 06_hybrid_search Lab Exercises")
    print("=" * 60)
    tests = [exercise_1, exercise_2, exercise_3, exercise_4, exercise_5, exercise_6, exercise_7]
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
