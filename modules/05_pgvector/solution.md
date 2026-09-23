## လေ့ကျင့်ခန်း ၁ — vector column ဆောက်တာ

`CREATE EXTENSION` နဲ့ extension အရင်ဖွင့်ပြီးမှ `vector(768)` type နဲ့ embedding column ဆောက်ရမယ်၊ cosine သုံးမယ့်အတွက် value တွေကို normalize လုပ်ထားဖို့လည်း လိုအပ်ပါတယ်နော်။ အောက်မှာ schema နဲ့ HNSW index ကို တွဲရေးပြထားပါတယ်။

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

**အဓိကအယူဆ** — 768 dimension, cosine ယူဆချက်အတွက် `vector(768)` column နဲ့ `vector_cosine_ops` operator class ကိုတွဲသုံးရပါတယ်။

## လေ့ကျင့်ခန်း ၂ — distance operator သုံးခွဲခြားခြင်း

`<->` က L2, `<=>` က cosine, `<#>` က negative inner product ဖြစ်ပြီး၊ normalize လုပ်ထားရင် L2 နဲ့ cosine က `L2 = sqrt(2 * cosine)` ဆိုတဲ့ ဆက်စပ်မှုနဲ့ တစ်ပြိုင်တည်း order တူသွားတယ်၊ inner product သုံးမယ်ဆို `vector_ip_ops` class လိုပါတယ်နော်။ ဒီ code က ဒါကို pure Python နဲ့ သက်သေပြပါတယ်။

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

**အဓိကအယူဆ** — normalize လုပ်ထားရင် L2, cosine, inner product ranking သုံးခုလုံး အစဉ်လိုက်တူပြီး၊ unnormalized ဖြစ်ရင် cosine အတွက် `<=>` + `vector_cosine_ops` ကို ခွဲခြားသုံးသင့်ပါတယ်။

## လေ့ကျင့်ခန်း ၃ — စာပိုဒ်ရှေ့ပိုင်းအတွက် RRF fusion (Python)

RRF က `1 / (60 + rank)` formula နဲ့ rank နှစ်ခုကို ပေါင်းပြီး brute-force cosine နဲ့ keyword ranking နှစ်ခုလုံးရဲ့ အားသာချက် ရောနေတဲ့ fused ranking ထုတ်ပေးပါတယ်၊ deterministic ဖြစ်အောင် tie ကို ID နဲ့ ဖြေရှင်းထားပါတယ်။

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

**အဓိကအယူဆ** — RRF က score တန်ဖိုးမသုံးပါဘူး၊ rank position ပေါ်အခြေခံထားလို့ scale မတူတဲ့ ranking နှစ်ခုကို လွယ်လွယ်ပေါင်းလို့ရပါတယ်။

## လေ့ကျင့်ခန်း ၄ — HNSW နဲ့ IVFFlat ရွေးချယ်တာ

million-level data အတွက် HNSW က build ကြာပေမယ့် query latency နဲ့ recall ကို ပိုသာပြီး၊ IVFFlat က build မြန်ပေမယ့် recall က `probes` အပေါ်မူတည်ပြီး data အသစ်ထည့်ရင် cluster ပျက်လို့ retrain လိုနိုင်ပါတယ်နော်။ အောက် code က dataset size, latency budget, recall target အပေါ် အခြေခံပြီး အကြံပေးတဲ့ decision helper ပါ။

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

**အဓိကအယူဆ** — recall မြင့်မြင့်နဲ့ latency နည်းနည်း လိုချင်ရင် HNSW၊ build မြန်မြန်နဲ့ memory သက်သာချင်ရင် probes တင်ပေးရတဲ့ IVFFlat ကို ရွေးသင့်ပါတယ်။

## လေ့ကျင့်ခန်း ၅ — jsonb metadata နဲ့ GIN index + filtered search

`metadata->>'source'` condition နဲ့ distance ordering နှစ်ခုလုံး query ထဲမှာ ပါလာပြီး၊ pre-filter မဖြစ်ရင် vector index က row တွေ ဖြတ်သွားပြီး post-filter ကြောင့် ရလဒ် လျော့နိုင်တာကို သတိထားရပါတယ်။ index build တွေအတွက် SQL ကို string အနေနဲ့ ထုတ်ပြပါတယ်။

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

**အဓိကအယူဆ** — GIN က metadata filter ကို မြန်စေပြီး၊ filter condition က vector index scan မတိုင်ခင် အလုပ်လုပ်နေမှ ရလဒ် လျော့သလို post-filter ပြဿနာ မဖြစ်ပါဘူး။

## လေ့ကျင့်ခန်း ၆ — maintenance_work_mem, parallel build, EXPLAIN ဖတ်တာ

`maintenance_work_mem` တန်ဖိုးက IVFFlat sample data တွေနဲ့ HNSW graph ကို memory ထဲ ဆောက်ပေးပြီး၊ `max_parallel_maintenance_workers` က build ကို CPU များများနဲ့ အလုပ်ခွဲပေးပါတယ်၊ memory မလုံရင် disk ပေါ် spill လုပ်ပြီး build နှေးသွားတယ်နော်။ အောက်မှာ sample EXPLAIN output ကို ဖတ်ပြပါတယ်။

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

**အဓိကအယူဆ** — EXPLAIN မှာ `Index Scan` နဲ့ index name ကို မြင်ရပြီး၊ maintenance memory နဲ့ parallel workers တိုးလိုက်ရင် build ရဲ့ sampling/graph-building အပိုင်းတွေ မြန်လာပါတယ်။
