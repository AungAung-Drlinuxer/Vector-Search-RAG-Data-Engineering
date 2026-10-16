## လေ့ကျင့်ခန်း ၁ — Vector Column Schema ဒီဇိုင်း

pgvector extension ကို enable လုပ်ပြီး `vector(768)` data type ဖြင့် table ဆောက်ကာ cosine distance metric အတွက် `vector_cosine_ops` operator class သုံးစွဲသည့် HNSW index တည်ဆောက်ပုံ ဖြစ်သည်။

```python
# Exercise 1: build the chunks table schema SQL (printed, not executed -- no DB in this exercise).
sql_statements = [
    # Enable pgvector first (run once per database, superuser or appropriate rights).
    "CREATE EXTENSION IF NOT EXISTS vector;",
    # chunks table: 768-dim embedding, cosine distance assumption.
    """
    CREATE TABLE chunks (
        id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        content    text NOT NULL,
        embedding  vector(768) NOT NULL
    );
    """,
    # Cosine assumption -> use vector_cosine_ops operator class.
    # Normalize vectors before insert (e.g., with a Python library) so cosine is meaningful.
    """
    CREATE INDEX ON chunks
        USING hnsw (embedding vector_cosine_ops);
    """,
]
for stmt in sql_statements:
    print(stmt.strip())
    print("---")
# Expected output:
# CREATE EXTENSION IF NOT EXISTS vector;
# ---
# CREATE TABLE chunks (
#         id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
#         content    text NOT NULL,
#         embedding  vector(768) NOT NULL
#     );
# ---
# CREATE INDEX ON chunks
#         USING hnsw (embedding vector_cosine_ops);
# ---
```

**အဓိကအယူအဆ** — 768 dimensions နှင့် cosine similarity လိုအပ်ချက်အတွက် `vector(768)` type နှင့် `vector_cosine_ops` operator class ကို တွဲဖက် အသုံးပြုရသည်။

---

## လေ့ကျင့်ခန်း ၂ — Distance Operators နှိုင်းယှဉ်ချက် (`<->`, `<=>`, `<#>`)

`<->` (L2 distance), `<=>` (Cosine distance) နှင့် `<#>` (Negative inner product) တို့၏ သင်္ချာသဘောတရားကို pure Python ဖြင့် တွက်ချက်ပြထားသည်။ Unit-normalized vectors များတွင် `L2^2 = 2 * cosine_distance` ဖြစ်သဖြင့် relative ranking အစဉ်လိုက်သည် တူညီသည်။

```python
# Exercise 2: show <-> (L2), <=> (cosine), <#> (negative inner product) with plain math.
import math

def l2(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

def cosine_distance(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return 1.0 - dot / (na * nb)

def negative_inner_product(a, b):
    return -sum(x * y for x, y in zip(a, b))

def normalize(v):
    n = math.sqrt(sum(x * x for x in v))
    return [x / n for x in v]

# Deterministic toy vectors (stand-ins for real embeddings).
q = normalize([0.1, 0.2, 0.3, 0.4])
d1 = normalize([0.2, 0.1, 0.4, 0.3])
d2 = normalize([-0.1, 0.3, 0.2, 0.5])

print("L2 (operator <->):", round(l2(q, d1), 6), round(l2(q, d2), 6))
print("Cosine distance (operator <=>):", round(cosine_distance(q, d1), 6),
      round(cosine_distance(q, d2), 6))
print("Negative inner product (operator <#>):", round(negative_inner_product(q, d1), 6),
      round(negative_inner_product(q, d2), 6))
# Normalized vectors: L2^2 == 2 * cosine_distance (monotone, same ranking).
print("Check L2^2 == 2*cosine:",
      round(l2(q, d1) ** 2, 6), "==", round(2 * cosine_distance(q, d1), 6))
# Expected output:
# L2 (operator <->): 0.365148 0.432913
# Cosine distance (operator <=>): 0.066667 0.093707
# Negative inner product (operator <#>): -0.933333 -0.906293
# Check L2^2 == 2*cosine: 0.133333 == 0.133333
```

**အဓိကအယူအဆ** — Normalized vectors များတွင် distance metrics သုံးခုလုံး ranking monotonicity ရှိပြီး unnormalized vectors များအတွက် cosine distance ကို တိုက်ရိုက်လိုချင်ပါက `<=>` နှင့် `vector_cosine_ops` ကို ရွေးချယ်ရသည်။

---

## လေ့ကျင့်ခန်း ၃ — Reciprocal Rank Fusion (RRF) Implementation

Dense vector similarity ranking နှင့် lexical keyword term ranking တို့ကို Reciprocal Rank Fusion (`1 / (60 + rank)`) ဖြင့် deterministic score fusion ပြုလုပ်ပုံ ဖြစ်သည်။

```python
# Exercise 3: Reciprocal Rank Fusion of a cosine ranking and a keyword ranking.
import math

def normalize(v):
    n = math.sqrt(sum(x * x for x in v))
    return [x / n for x in v]

def cosine(a, b):
    return sum(x * y for x, y in zip(a, b))  # vectors already normalized

# Deterministic toy corpus: (id, text, embedding stand-in).
docs = {
    1: ("vector database postgres guide", normalize([0.9, 0.1])),
    2: ("postgres index tuning tips", normalize([0.8, 0.3])),
    3: ("cooking recipes soup", normalize([0.1, 0.9])),
}
query_text = "postgres"
query_vec = normalize([0.85, 0.2])

# Brute-force cosine ranking (ties broken by ascending id -> deterministic).
dense = sorted(docs, key=lambda i: (-cosine(query_vec, docs[i][1]), i))
# Keyword ranking: count of query term occurrences (ties by id).
kwords = sorted(docs, key=lambda i: (-docs[i][0].split().count(query_text), i))

def rrf(rankings, k=60):
    scores = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    # Sort by score desc, then doc id asc for determinism.
    return sorted(scores, key=lambda i: (-scores[i], i))

fused = rrf([dense, kwords])
print("dense ranking:", dense)
print("keyword ranking:", kwords)
print("RRF fused ranking:", fused)
# Expected output:
# dense ranking: [1, 2, 3]
# keyword ranking: [1, 2, 3]
# RRF fused ranking: [1, 2, 3]
```

**အဓိကအယူအဆ** — RRF သည် absolute scores များအပေါ် မှီခိုခြင်းမရှိဘဲ ordinal rank positions များကိုသာ အသုံးပြုသဖြင့် heterogeneous search algorithms များကို ပေါင်းစပ်ရာတွင် hyperparameter tuning overhead အနည်းဆုံးဖြစ်သည်။

---

## လေ့ကျင့်ခန်း ၄ — HNSW vs IVFFlat Index Selection Framework

Scale, latency requirement, recall threshold နှင့် update frequency အပေါ် အခြေခံ၍ HNSW သို့မဟုတ် IVFFlat index အမျိုးအစားနှင့် parameter setting များကို dynamic ဆုံးဖြတ်ပေးသော logic ဖြစ်သည်။

```python
# Exercise 4: deterministic index-choice helper (scripted logic, no real DB).
def choose_index(n_rows, latency_ms_budget, recall_target, frequent_updates):
    advice = []
    # Rule-based stand-in for a real sizing decision.
    hnsw_ok = n_rows <= 50_000_000 and latency_ms_budget < 20
    if recall_target >= 0.95 and hnsw_ok:
        index = "HNSW"
        params = "m=16, ef_construction=200 (raise m to 32 / ef_construction to 400 for higher recall)"
        # ef_search (query time) trades latency for recall.
        advice.append("Set hnsw.ef_search ~= 100, tune upward if recall is short.")
    else:
        index = "IVFFlat"
        lists = max(1, int(math_isqrt(n_rows // 1000)))  # rough rule: sqrt(n/1000)
        params = f"lists={lists}; probes ~= lists // 10 (raise probes for recall, at latency cost)"
        if frequent_updates:
            advice.append("Data drifts -> REINDEX / rebuild clusters periodically.")
    return index, params, advice

def math_isqrt(n):
    import math
    return math.isqrt(max(1, n))

idx, p, tips = choose_index(n_rows=2_000_000, latency_ms_budget=15,
                            recall_target=0.97, frequent_updates=False)
print("Recommended index:", idx)
print("Parameters:", p)
for t in tips:
    print("Tip:", t)
# Expected output:
# Recommended index: HNSW
# Parameters: m=16, ef_construction=200 (raise m to 32 / ef_construction to 400 for higher recall)
# Tip: Set hnsw.ef_search ~= 100, tune upward if recall is short.
```

**အဓိကအယူအဆ** — High-recall, low-latency target များအတွက် HNSW ကို ဦးစားပေးရပြီး memory-constrained သို့မဟုတ် rapid bulk loading အခြေအနေများတွင် IVFFlat ကို ရွေးချယ်ရသည်။

---

## လေ့ကျင့်ခန်း ၅ — JSONB Metadata + GIN Index ဖြင့် Filtered Vector Search

JSONB column အပေါ် GIN index တည်ဆောက်ပြီး selective metadata filter နှင့် vector similarity distance ordering ပေါင်းစပ် query ရေးသားပုံ ဖြစ်သည်။

```python
# Exercise 5: emit valid SQL for jsonb metadata + GIN + filtered vector search.
sql = [
    # 1) Add metadata column (if not already present).
    "ALTER TABLE chunks ADD COLUMN metadata jsonb NOT NULL DEFAULT '{}'::jsonb;",
    # 2) GIN index for the metadata filter (jsonb_path_ops: smaller, faster for containment).
    "CREATE INDEX IF NOT EXISTS chunks_metadata_gin ON chunks USING gin (metadata jsonb_path_ops);",
    # 3) Filtered vector search: exact-filter variant uses the GIN index to pre-filter rows,
    #    then orders the survivors by cosine distance (no post-filter row loss).
    """
    SELECT id, content
    FROM chunks
    WHERE metadata->>'source' = 'product_docs_v2'
    ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
    LIMIT 5;
    """,
]
for stmt in sql:
    print(stmt.strip())
    print("---")
# Expected output:
# ALTER TABLE chunks ADD COLUMN metadata jsonb NOT NULL DEFAULT '{}'::jsonb;
# ---
# CREATE INDEX IF NOT EXISTS chunks_metadata_gin ON chunks USING gin (metadata jsonb_path_ops);
# ---
# SELECT id, content
#     FROM chunks
#     WHERE metadata->>'source' = 'product_docs_v2'
#     ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
#     LIMIT 5;
# ---
```

**အဓိကအယူအဆ** — GIN index သည် JSONB metadata filtering ကို accelerate လုပ်ပေးပြီး filter predicate သည် pre-filter အဖြစ် အလုပ်လုပ်နိုင်မှသာ top-k candidate truncation မဖြစ်ပေါ်စေမည်။

---

## လေ့ကျင့်ခန်း ၆ — Resource Tuning (`maintenance_work_mem`) နှင့် EXPLAIN Analysis

`EXPLAIN` query execution plan ကို programmatic parse ပြုလုပ်၍ vector index scan node နှင့် post-filter placement ကို စစ်ဆေးသည့်အပြင် index build အမြန်နှုန်းအတွက် resource allocation settings များကို ဖော်ပြထားသည်။

```python
# Exercise 6: parse a scripted (deterministic) EXPLAIN output stand-in and read key facts.
explain_lines = [
    "Limit  (cost=0.42..0.68 rows=5) (actual time=0.412..0.431 rows=5 loops=1)",
    "  ->  Index Scan using chunks_embedding_idx on chunks  "
    "(cost=0.42..12345.00 rows=1000) (actual time=0.410..0.425 rows=5 loops=1)",
    "        Order By: embedding <=> '[0.1,0.2,...]'::vector",
    "        Filter: (metadata->>'source' = 'product_docs_v2')",
]

# Read the plan: node type, index name, and where the filter sits.
node_types = [ln.strip().split("  (")[0] for ln in explain_lines if "->" in ln or "Limit" in ln]
index_name = next(ln.split("using ")[1].split(" on")[0].strip()
                 for ln in explain_lines if "Index Scan using" in ln)
has_postfilter = any("Filter:" in ln and "Index" not in ln for ln in explain_lines)

print("Plan nodes:", node_types)
print("Vector index used:", index_name)
print("Metadata filter applied after the index scan (post-filter):", has_postfilter)

# Build-time guidance printed as settings.
print("Suggested build settings:")
print("  SET maintenance_work_mem = '2GB';       -- keeps samples/graph in RAM, avoids disk spill")
print("  SET max_parallel_maintenance_workers = 4; -- parallel HNSW/IVFFlat build")
# Expected output:
# Plan nodes: ['Limit', '->  Index Scan using chunks_embedding_idx on chunks', "Filter: (metadata->>'source' = 'product_docs_v2')"]
# Vector index used: chunks_embedding_idx
# Metadata filter applied after the index scan (post-filter): True
# Suggested build settings:
#   SET maintenance_work_mem = '2GB';       -- keeps samples/graph in RAM, avoids disk spill
#   SET max_parallel_maintenance_workers = 4; -- parallel HNSW/IVFFlat build
```

**အဓိကအယူအဆ** — Index scan နှင့် filter ordering ကို EXPLAIN ဖြင့် verify လုပ်ပြီး `maintenance_work_mem` တိုးမြှင့်ခြင်းဖြင့် in-memory graph construction throughput ကို အမြင့်ဆုံး ရရှိစေသည်။
