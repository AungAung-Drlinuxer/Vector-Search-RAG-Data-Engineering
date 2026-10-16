#!/usr/bin/env python3
"""
Module 13_capstone — Lab Exercises
Deterministic offline execution using only the Python standard library.
"""

import sys

def exercise_1() -> bool:
    """Exercise 1: Vector Storage Footprint Capacity Estimation"""
    print(f"\n--- Exercise 1: Vector Storage Footprint Capacity Estimation ---")
    # Storage estimate: chunks * dims * bytes_per_value
    chunks = 1_000_000
    dims = 768
    bytes_per_value = 4  # fp32 = 4 bytes per float
    
    total_bytes = chunks * dims * bytes_per_value
    print("chunks:", chunks)
    print("dims:", dims)
    print("bytes per value (fp32):", bytes_per_value)
    print("total bytes:", total_bytes)
    print("approx GB:", total_bytes / 1e9)
    # Expected output:
    # chunks: 1000000
    # dims: 768
    # bytes per value (fp32): 4
    # total bytes: 3072000000
    # approx GB: 3.072
    return True

def exercise_2() -> bool:
    """Exercise 2: Chunk Size Granularity Trade-Off Analysis"""
    print(f"\n--- Exercise 2: Chunk Size Granularity Trade-Off Analysis ---")
    import math
    
    words = 100_000
    
    for chunk_size in (200, 800):
        num_chunks = math.ceil(words / chunk_size)
        print(f"chunk_size={chunk_size} words -> {num_chunks} chunks")
    
    # Trade-off explanation
    print("200-word chunks: more precise retrieval but 4x more chunks to store/index")
    print("800-word chunks: fewer chunks, richer context, but relevant sentences get diluted")
    # Expected output:
    # chunk_size=200 words -> 500 chunks
    # chunk_size=800 words -> 125 chunks
    # 200-word chunks: more precise retrieval but 4x more chunks to store/index
    # 800-word chunks: fewer chunks, richer context, but relevant sentences get diluted
    return True

def exercise_3() -> bool:
    """Exercise 3: Single-Layer Proximity Graph Construction & Greedy Search"""
    print(f"\n--- Exercise 3: Single-Layer Proximity Graph Construction & Greedy Search ---")
    import random
    
    rng = random.Random(42)
    N = 100
    M = 4
    points = [(rng.random(), rng.random()) for _ in range(N)]
    
    def dist(a, b):
        return (a[0]-b[0])**2 + (a[1]-b[1])**2
    
    # Build graph: each point connects to its M nearest neighbours (bidirectional edges)
    neighbors = {i: set() for i in range(N)}
    for i in range(N):
        ranked = sorted((j for j in range(N) if j != i), key=lambda j: dist(points[i], points[j]))
        for j in ranked[:M]:
            neighbors[i].add(j)
            neighbors[j].add(i)
    
    # Greedy search from entry point 0
    def greedy_search(query, entry=0):
        current = entry
        best_d = dist(points[current], query)
        while True:
            improved = False
            for nb in neighbors[current]:
                d = dist(points[nb], query)
                if d < best_d:
                    best_d = d
                    current = nb
                    improved = True
            if not improved:
                return current, best_d
    
    query = (0.5, 0.5)
    graph_idx, g_d = greedy_search(query)
    exact_idx = min(range(N), key=lambda i: dist(points[i], query))
    print("query:", query)
    print("graph search result idx:", graph_idx, "dist:", round(g_d, 6))
    print("brute-force exact idx:", exact_idx, "dist:", round(dist(points[exact_idx], query), 6))
    print("match:", graph_idx == exact_idx)
    # Expected output:
    # query: (0.5, 0.5)
    # graph search result idx: 7 dist: 0.024485
    # brute-force exact idx: 70 dist: 0.003091
    # match: False
    return True

def exercise_4() -> bool:
    """Exercise 4: Empirical Recall@K Metric Benchmark"""
    print(f"\n--- Exercise 4: Empirical Recall@K Metric Benchmark ---")
    import random
    
    rng = random.Random(42)
    N = 100
    M = 4
    points = [(rng.random(), rng.random()) for _ in range(N)]
    
    def dist(a, b):
        return (a[0]-b[0])**2 + (a[1]-b[1])**2
    
    neighbors = {i: set() for i in range(N)}
    for i in range(N):
        ranked = sorted((j for j in range(N) if j != i), key=lambda j: dist(points[i], points[j]))
        for j in ranked[:M]:
            neighbors[i].add(j)
            neighbors[j].add(i)
    
    def greedy_search(query, entry=0):
        current = entry
        best_d = dist(points[current], query)
        while True:
            improved = False
            for nb in neighbors[current]:
                d = dist(points[nb], query)
                if d < best_d:
                    best_d = d
                    current = nb
                    improved = True
            if not improved:
                return current
    
    def graph_top_k(query, k=5):
        # Greedy stops at a local minimum, so also scan its neighbours for extra candidates
        start = greedy_search(query)
        candidates = {start} | neighbors[start]
        return sorted(candidates, key=lambda i: dist(points[i], query))[:k]
    
    def exact_top_k(query, k=5):
        return sorted(range(N), key=lambda i: dist(points[i], query))[:k]
    
    queries = [(rng.random(), rng.random()) for _ in range(100)]
    total_recall = 0.0
    for q in queries:
        g = graph_top_k(q, 5)
        e = exact_top_k(q, 5)
        total_recall += len(set(g) & set(e)) / 5
    avg_recall = total_recall / len(queries)
    print("avg recall@5 over 100 queries:", round(avg_recall, 4))
    # Expected output:
    # avg recall@5 over 100 queries: 0.748
    return True

def exercise_5() -> bool:
    """Exercise 5: QPS Throughput နှင့် Percentile Latency (p95) Modeling"""
    print(f"\n--- Exercise 5: QPS Throughput နှင့် Percentile Latency (p95) Modeling ---")
    import random
    
    # Greedy graph search with a deterministic step counter and a labelled latency model.
    rng = random.Random(42)
    N, M = 100, 4
    points = [(rng.random(), rng.random()) for _ in range(N)]
    STEP_COST_US = 1.0        # assumption: one distance evaluation costs 1 microsecond
    
    
    def dist(a, b):
        return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
    
    
    neighbors = {i: set() for i in range(N)}
    for i in range(N):
        ranked = sorted((j for j in range(N) if j != i), key=lambda j: dist(points[i], points[j]))
        for j in ranked[:M]:
            neighbors[i].add(j)
            neighbors[j].add(i)
    
    
    def greedy_search(query, entry=0):
        """Return (closest node found, distance evaluations used)."""
        current, best_d, steps = entry, dist(points[entry], query), 1
        while True:
            improved = False
            for nb in neighbors[current]:
                steps += 1
                d = dist(points[nb], query)
                if d < best_d:
                    best_d = d
                    current = nb
                    improved = True
            if not improved:
                return current, steps
    
    
    queries = [(rng.random(), rng.random()) for _ in range(1000)]
    steps = [greedy_search(q)[1] for q in queries]
    total_us = sum(steps) * STEP_COST_US
    print("queries                    :", len(queries))
    print("distance evaluations total :", sum(steps))
    print("mean evaluations per query :", round(sum(steps) / len(queries), 1))
    print("p95 latency (us, model)    :", round(sorted(steps)[int(0.95 * len(steps))] * STEP_COST_US, 1))
    print(f"QPS (model, {STEP_COST_US:.1f} us per eval): {len(queries) / (total_us / 1e6):.0f}")
    # Expected output:
    # queries                    : 1000
    # distance evaluations total : 34153
    # mean evaluations per query : 34.2
    # p95 latency (us, model)    : 57.0
    # QPS (model, 1.0 us per eval): 29280
    return True

def exercise_6() -> bool:
    """Exercise 6: Unified End-to-End Pipeline Consolidation"""
    print(f"\n--- Exercise 6: Unified End-to-End Pipeline Consolidation ---")
    import random
    import math
    
    rng = random.Random(42)
    vocab = ["w%d" % i for i in range(50)]
    corpus = [rng.choice(vocab) for _ in range(1000)]      # deterministic corpus (seed 42)
    
    CHUNK = 100
    chunks = [corpus[i:i + CHUNK] for i in range(0, len(corpus), CHUNK)]
    print("num chunks:", len(chunks))
    
    
    def stable_hash(s):
        h = 2166136261
        for ch in s:
            h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
        return h
    
    
    DIM = 64
    
    
    def embed(words):
        v = [0.0] * DIM
        for w in words:
            v[stable_hash(w) % DIM] += 1.0            # stable hash: identical across runs
        return v
    
    
    vecs = [embed(c) for c in chunks]
    
    
    def dist(a, b):
        return sum((x - y) ** 2 for x, y in zip(a, b))
    
    
    def cosine(a, b):
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(x * x for x in b))
        return 0.0 if na == 0 or nb == 0 else sum(x * y for x, y in zip(a, b)) / (na * nb)
    
    
    M = 4
    N = len(vecs)
    neighbors = {i: set() for i in range(N)}
    for i in range(N):
        ranked = sorted((j for j in range(N) if j != i), key=lambda j: dist(vecs[i], vecs[j]))
        for j in ranked[:M]:
            neighbors[i].add(j)
            neighbors[j].add(i)
    
    
    def greedy_search(query, entry=0):
        current, best_d, steps = entry, dist(vecs[entry], query), 1
        while True:
            improved = False
            for nb in neighbors[current]:
                steps += 1
                d = dist(vecs[nb], query)
                if d < best_d:
                    best_d = d
                    current = nb
                    improved = True
            if not improved:
                return current, steps
    
    
    def retrieve(query, top=20):
        start, steps = greedy_search(query)
        candidates = {start} | neighbors[start]
        return sorted(candidates, key=lambda i: dist(vecs[i], query))[:top], steps
    
    
    def rerank(query, ids, top=5):
        # Rerank with exact cosine similarity (a real system would use a reranker model).
        return sorted(ids, key=lambda i: -cosine(query, vecs[i]))[:top]
    
    
    queries = [embed([rng.choice(vocab) for _ in range(20)]) for _ in range(100)]
    
    
    def exact_top(k, query):
        return sorted(range(N), key=lambda i: -cosine(query, vecs[i]))[:k]
    
    
    total_recall, total_steps = 0.0, 0
    for q in queries:
        cand, steps = retrieve(q, 20)
        top5 = rerank(q, cand, 5)
        total_steps += steps
        total_recall += len(set(top5) & set(exact_top(5, q))) / 5
    
    recall = total_recall / len(queries)
    STEP_COST_US = 1.0                                        # assumption: 1 microsecond per evaluation
    print("recall@5:", round(recall, 4))
    print("distance evaluations total:", total_steps)
    print(f"QPS (model, {STEP_COST_US:.1f} us per eval): {len(queries) / (total_steps * STEP_COST_US / 1e6):.0f}")
    print("recall@5 is identical on every run (seed 42)")
    # Expected output:
    # num chunks: 10
    # recall@5: 0.912
    # distance evaluations total: 1488
    # QPS (model, 1.0 us per eval): 67204
    # recall@5 is identical on every run (seed 42)
    return True

def run_all() -> bool:
    print("=" * 60)
    print("Running Module 13_capstone Lab Exercises")
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
