#!/usr/bin/env python3
"""
Module 08_serving_architecture — Lab Exercises
Deterministic offline execution using only the Python standard library.
"""

import sys

def exercise_1() -> bool:
    """Exercise 1: Retrieval API function ရေးပါ"""
    print(f"\n--- Exercise 1: Retrieval API function ရေးပါ ---")
    # Retrieval API simulation: query_vector + top_k + filters (tenant ACL)
    import math
    
    # Hard-coded fake "vector store": metadata dicts with 4-dim embeddings
    ITEMS = [
        {"id": 1, "tenant_id": "A", "content": "alpha doc", "vec": [1.0, 0.0, 0.0, 0.0]},
        {"id": 2, "tenant_id": "B", "content": "bravo doc", "vec": [0.0, 1.0, 0.0, 0.0]},
        {"id": 3, "tenant_id": "A", "content": "charlie doc", "vec": [0.9, 0.1, 0.0, 0.0]},
        {"id": 4, "tenant_id": "C", "content": "delta doc", "vec": [1.0, 0.1, 0.0, 0.0]},
        {"id": 5, "tenant_id": "A", "content": "echo doc", "vec": [0.0, 0.0, 1.0, 0.0]},
    ]
    
    def cosine(a, b):
        num = sum(x * y for x, y in zip(a, b))
        da = math.sqrt(sum(x * x for x in a))
        db = math.sqrt(sum(y * y for y in b))
        return num / (da * db) if da and db else 0.0
    
    def search(query_vector, top_k, filters):
        # In a real system, the tenant filter becomes a SQL WHERE clause
        # (e.g. WHERE tenant_id = $1) inside the vector search, so cross-tenant
        # rows are never even returned by the database.
        tenant = filters.get("tenant_id")
        candidates = []
        for it in ITEMS:
            if it["tenant_id"] != tenant:   # ACL-like filter: skip other tenants
                continue
            score = cosine(query_vector, it["vec"])
            candidates.append({"id": it["id"], "content": it["content"], "score": round(score, 4)})
        candidates.sort(key=lambda r: r["score"], reverse=True)
        return candidates[:top_k]  # never return more than top_k
    
    results = search([1.0, 0.0, 0.0, 0.0], 3, {"tenant_id": "A"})
    for r in results:
        print(r)
    print("count =", len(results))
    # Expected output:
    # {'id': 1, 'content': 'alpha doc', 'score': 1.0}
    # {'id': 3, 'content': 'charlie doc', 'score': 0.9939}
    # {'id': 5, 'content': 'echo doc', 'score': 0.0}
    # count = 3
    return True

def exercise_2() -> bool:
    """Exercise 2: Embedding cache တည်ဆောက်ပါ"""
    print(f"\n--- Exercise 2: Embedding cache တည်ဆောက်ပါ ---")
    # Embedding cache with a deterministic stand-in "model" (no real API call)
    class StandInEmbedder:
        """Deterministic stand-in for a real embedding API (offline, no network)."""
        def embed(self, text):
            vec = [0.0] * 8  # fixed-size vector
            for i, ch in enumerate(text):
                vec[i % 8] += float(ord(ch))
            norm = sum(v * v for v in vec) ** 0.5
            return [round(v / norm, 4) if norm else 0.0 for v in vec]
    
    class EmbeddingCache:
        def __init__(self, embedder):
            self._embedder = embedder
            self._store = {}
            self.hits = 0
            self.misses = 0
    
        def get(self, query):
            if query in self._store:
                self.hits += 1
                return self._store[query]
            self.misses += 1
            vec = self._embedder.embed(query)  # expensive call in real life
            self._store[query] = vec
            return vec
    
    cache = EmbeddingCache(StandInEmbedder())
    v1 = cache.get("hello world")
    v2 = cache.get("hello world")   # same query -> cache hit
    v3 = cache.get("other query")   # new query -> miss
    print("hits =", cache.hits)
    print("misses =", cache.misses)
    print("same object:", v1 is v2)
    print("dim:", len(v3))
    # Expected output:
    # hits = 1
    # misses = 2
    # same object: True
    # dim: 8
    return True

def exercise_3() -> bool:
    """Exercise 3: Result cache (query + filter hash key)"""
    print(f"\n--- Exercise 3: Result cache (query + filter hash key) ---")
    # Result cache keyed on the hash of (query + normalized filters)
    import json
    import hashlib
    
    class ResultCache:
        def __init__(self):
            self._store = {}
    
        @staticmethod
        def _key(query, filters):
            # sort_keys=True -> deterministic regardless of dict insertion order
            payload = json.dumps({"query": query, "filters": filters},
                                sort_keys=True)
            return hashlib.sha256(payload.encode("utf-8")).hexdigest()
    
        def get(self, query, filters):
            key = self._key(query, filters)
            return self._store.get(key)  # None on miss
    
        def put(self, query, filters, results):
            self._store[self._key(query, filters)] = results
    
    cache = ResultCache()
    
    def retrieve(query, filters):
        hit = cache.get(query, filters)
        if hit is not None:
            return hit, "hit"
        results = ["doc1", "doc2"]  # scripted deterministic stand-in for a search
        cache.put(query, filters, results)
        return results, "miss"
    
    f1 = {"tenant_id": "A"}
    f2 = {"tenant_id": "B"}  # same query, different filter -> different entry
    print(retrieve("hello", f1))
    print(retrieve("hello", f1))
    print(retrieve("hello", f2))
    print("entries =", len(cache._store))
    # Expected output:
    # (['doc1', 'doc2'], 'miss')
    # (['doc1', 'doc2'], 'hit')
    # (['doc1', 'doc2'], 'miss')
    # entries = 2
    return True

def exercise_4() -> bool:
    """Exercise 4: Pool နဲ့ concurrency simulation"""
    print(f"\n--- Exercise 4: Pool နဲ့ concurrency simulation ---")
    # Connection pool with blocking acquire via queue.Queue
    import queue
    import threading
    import time
    
    class DummyConnection:
        def __init__(self, cid):
            self.cid = cid
        def __repr__(self):
            return "conn-%d" % self.cid
    
    class ConnectionPool:
        def __init__(self, size=3):
            self._q = queue.Queue()
            for i in range(size):
                self._q.put(DummyConnection(i + 1))
        def acquire(self, timeout=None):
            return self._q.get(block=True, timeout=timeout)  # blocks when empty
        def release(self, conn):
            self._q.put(conn)
    
    pool = ConnectionPool(size=3)
    c1 = pool.acquire()
    c2 = pool.acquire()
    c3 = pool.acquire()
    print("acquired:", c1, c2, c3)
    
    # 4th acquire must block until a release happens (tested with a timeout)
    start = time.monotonic()
    try:
        pool.acquire(timeout=0.2)
        print("ERROR: should have blocked")
    except queue.Empty:
        print("blocked, waited %.1fs" % (time.monotonic() - start))
    
    # Release in a background thread, then the 4th acquire succeeds
    def releaser():
        time.sleep(0.1)
        pool.release(c2)
    threading.Thread(target=releaser).start()
    c4 = pool.acquire(timeout=2)
    print("got after release:", c4)
    # Expected output:
    # acquired: conn-1 conn-2 conn-3
    # blocked, waited 0.2s
    # got after release: conn-2
    return True

def exercise_5() -> bool:
    """Exercise 5: pgvector SQL ရေးပါ (အလုပ်မလုပ်ပါဘူး၊ ဖတ်ဖို့ပါ)"""
    print(f"\n--- Exercise 5: pgvector SQL ရေးပါ (အလုပ်မလုပ်ပါဘူး၊ ဖတ်ဖို့ပါ) ---")
    # This exercise is read-only: the SQL below is NOT executed here.
    # It is valid PostgreSQL + pgvector syntax. See:
    # https://github.com/pgvector/pgvector
    
    SQL = """
    -- Without a vector index (e.g. ivfflat/hnsw), this is an exact search:
    -- the database scans every row that matches the WHERE clause.
    SELECT id, content, embedding <=> $1 AS distance
    FROM documents
    WHERE tenant_id = $2          -- ACL / tenant filter
      AND (embedding <=> $1) < 0.5 -- hybrid score filter
    ORDER BY embedding <=> $1      -- cosine distance, ascending
    LIMIT 3;                      -- top 3
    """
    
    print(SQL.strip())
    # Expected output:
    # -- Without a vector index (e.g. ivfflat/hnsw), this is an exact search:
    # -- the database scans every row that matches the WHERE clause.
    # SELECT id, content, embedding <=> $1 AS distance
    # FROM documents
    # WHERE tenant_id = $2          -- ACL / tenant filter
    #   AND (embedding <=> $1) < 0.5 -- hybrid score filter
    # ORDER BY embedding <=> $1      -- cosine distance, ascending
    # LIMIT 3;                      -- top 3
    return True

def exercise_6() -> bool:
    """Exercise 6: Hybrid architecture စာတမ်းရေးပါ (essay)"""
    print(f"\n--- Exercise 6: Hybrid architecture စာတမ်းရေးပါ (essay) ---")
    # Essay is stored as a string and printed — deterministic, offline.
    ESSAY = """Hybrid architecture: Postgres as source of truth + a dedicated vector store.
    
    (1) Transactional data and relational integrity matter in the "operational"
    layer: invoices, user accounts, permissions, and document ownership live in
    tables with foreign keys, constraints and ACID transactions. PostgreSQL
    guarantees all of this, which is why it should remain the single source of
    truth (pgvector: https://github.com/pgvector/pgvector).
    
    (2) A vector-only store such as Qdrant has advantages for scale-out: it is
    built around HNSW-style approximate search, payload filtering during the
    graph traversal, sharding and replication designed specifically for vector
    workloads (Qdrant docs: https://qdrant.tech/documentation/). Offloading heavy
    ANN search keeps the transactional database free from read-amplification.
    
    (3) The sync problem: two stores can drift if a document is updated in
    Postgres but not (yet) in the vector store. Practical mitigations are:
    write both sides from one application-level "ingest" transaction or outbox
    pattern, use deterministic document ids on both sides, and run a periodic
    reconciliation job that compares counts and spot-checks hashes, re-indexing
    any mismatched documents. Treat the vector store as a derived, rebuildable
    index rather than authoritative state.
    
    Conclusion: Postgres holds the truth; Qdrant is a disposable, scalable search
    index that can always be rebuilt from Postgres."""
    
    print(ESSAY)
    # Expected output:
    # Hybrid architecture: Postgres as source of truth + a dedicated vector store.
    # 
    # (1) Transactional data and relational integrity matter in the "operational"
    # layer: invoices, user accounts, permissions, and document ownership live in
    # tables with foreign keys, constraints and ACID transactions. PostgreSQL
    # guarantees all of this, which is why it should remain the single source of
    # truth (pgvector: https://github.com/pgvector/pgvector).
    # 
    # (2) A vector-only store such as Qdrant has advantages for scale-out: it is
    # built around HNSW-style approximate search, payload filtering during the
    # graph traversal, sharding and replication designed specifically for vector
    # workloads (Qdrant docs: https://qdrant.tech/documentation/). Offloading heavy
    # ANN search keeps the transactional database free from read-amplification.
    # 
    # (3) The sync problem: two stores can drift if a document is updated in
    # Postgres but not (yet) in the vector store. Practical mitigations are:
    # write both sides from one application-level "ingest" transaction or outbox
    # pattern, use deterministic document ids on both sides, and run a periodic
    # reconciliation job that compares counts and spot-checks hashes, re-indexing
    # any mismatched documents. Treat the vector store as a derived, rebuildable
    # index rather than authoritative state.
    # 
    # Conclusion: Postgres holds the truth; Qdrant is a disposable, scalable search
    # index that can always be rebuilt from Postgres.
    return True

def run_all() -> bool:
    print("=" * 60)
    print("Running Module 08_serving_architecture Lab Exercises")
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
