## လေ့ကျင့်ခန်း ၁ — Retrieval API function ရေးပါ

`/search` endpoint ကို simulate လုပ်တဲ့ function ကို ဒီမှာ ရေးပြထားပါတယ်။ tenant_id မတူတဲ့ items တွေကို ဘယ်တော့မှ မပြပါနဲ့ — real system မှာဆို ဒါက SQL `WHERE tenant_id = $1` clause နဲ့ လုပ်တာပါ။

```python
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
```

**အဓိကအယူဆ** — ACL filter က Python မှာ မဟုတ်ဘဲ database query ထဲမှာ တည်နေရာချထားဖို့က လုံခြုံမှုအတွက် အရေးကြီးဆုံးပါ။

## လေ့ကျင့်ခန်း ၂ — Embedding cache တည်ဆောက်ပါ

query string တူလျှင် cache hit ဖြစ်ပြီး embedding နောက်တစ်ခါ မထုတ်ပါနော်။ real system မှာ embedding API call က ကုန်ကျစရိတ်ရှိလို့ cache က ကယ်တင်ပေးပါတယ်။

```python
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
```

**အဓိကအယူဆ** — cache key က query string တစ်ခုတည်းနဲ့ ရိုးရိုးရှင်းရှင်း အလုပ်လုပ်ပြီး hit/miss counts က cache အလုပ်လုပ်မှုကို ပြောပြပေးပါတယ်။

## လေ့ကျင့်ခန်း ၃ — Result cache (query + filter hash key)

query တူပေမယ့် filter မတူရင် cache hit မဖြစ်ရပါဘူး — ဒါကြောင့် key မှာ (query, filters) နှစ်ခုလုံး ပါဝင်ရမယ်။ dict order က အရေးကြီးလို့ `sort_keys=True` နဲ့ JSON serialize လုပ်ပါတယ်။

```python
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
```

**အဓိကအယူဆ** — cache key မှာ query နဲ့ filter နှစ်ခုလုံး ပါဝင်မှ cross-tenant ဒါမှမဟုတ် မမှန်တဲ့ result တွေ ပြန်မပေးမှာပါ။

## လေ့ကျင့်ခန်း ၄ — Pool နဲ့ concurrency simulation

pool size 3 နဲ့ acquire ၃ ခါ အရင် အောင်မြင်ပြီး စတုတ္ထအကြိမ်က release မလုပ်မချင်း စောင့်ရမယ်နော်။ connection တွေက dummy object တွေပါ — real system မှာ Postgres connection တွေပါ။

```python
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
```

**အဓိကအယူဆ** — pool က connection ပြန်လည်အသုံးပြုခြင်းနဲ့ အလွန်အကျွံ ဖွင့်မခံရစေတာကြောင့် bounded resource တွေကို စနစ်တကျ ထိန်းပေးပါတယ်။

## လေ့ကျင့်ခန်း ၅ — pgvector SQL ရေးပါ (အလုပ်မလုပ်ပါဘူး၊ ဖတ်ဖို့ပါ)

ဒါက ဖတ်ဖို့ပါ — pgvector ရဲ့ `<=>` operator က cosine distance အတွက်ပါ။ tenant_id filter က WHERE clause ထဲ ပါရမယ်၊ နဲ့ index မတပ်ရသေးရင် exact search ပါလို့ comment မှာ ဖော်ပြထားပါတယ်။

```python
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
```

**အဓိကအယူဆ** — pgvector မှာ vector search နဲ့ SQL filter တွေက တူညီတဲ့ query တစ်ခုထဲ ပေါင်းလုပ်လို့ရတာက hybrid filtering ရဲ့ အားသာချက်ပါ။

## လေ့ကျင့်ခန်း ၆ — Hybrid architecture စာတမ်းရေးပါ (essay)

Essay ကို python block ထဲမှာ string အဖြစ် ထည့်ပြီး print ထုတ်ပါမယ် — မေးခွန်းသုံးခုလုံးကို ဖြေရှင်းထားပြီး official docs နှစ်ခု ကိုးကားထားပါတယ်။ ဂဏန်းတွေကို အထောက်အထားမရှိဘဲ မထည့်ပါနော်။

```python
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
```

**အဓိကအယူဆ** — vector store က rebuild လုပ်လို့ရတဲ့ derived index တစ်ခုပါ — source of truth ကတော့ Postgres မှာသာ နေရမယ်။
