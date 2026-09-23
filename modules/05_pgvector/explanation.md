# M5 — PostgreSQL + pgvector: Schema၊ Operator၊ Index နှင့် Tuning

ဒီ module မှာ pgvector extension ကို PostgreSQL ထဲမှာ ဘယ်လို သုံးမလဲဆိုတာ လေ့လာပါမယ်။
အရင်ဆုံး သတိပြုရမှာက ဒီသငခန်း များက SQL ကို run မိုက်တာမှု မလုပ်ပါဘူးနော်။
အားလုံးက standard-library Python နဲ့ offline သာ လုပ်ပါတယ်။
Source ကတော့ official pgvector repo နဲ့ PostgreSQL docs တွေပဲ ဖြစ်ပါတယ်။

---

## Subtopic 1 — `vector` column၊ operator class နဲ့ distance operator များ

### ဘာကို ဆိုလိုတာလဲ

pgvector ဆိုတာ PostgreSQL အတွက် vector data သိမ်းတဲ့ extension တစ်ခုပါ။
ဒါက AI embedding (စာသားကနေ ထုတ်ယူထားတဲ့ နံပါတ်စု) တွေကို DB ထဲ မှာတိုက်ရိုက် သိမ်းခွင့်ပေးပါတယ်။
`vector(768)` ဆိုရင် dimension ၇၆၈ ပါတဲ့ vector ဆိုပါတယ်။
Operator class ကတော့ index က ဘယ် distance ပုံစံနဲ့ ရှာမလဲ သတ်မှတ်တဲ့ setting ပါ။

### ဘာကြောင့် လဲ

vector ကို plain array အနေနဲ့ သိမ်းရင် ဘယ်လိုမှ မကိုက်နိုင်ပါဘူး။
"အနီးဆုံး" ဆိုတဲ့ သဘောကို SQL က နားလည်ဖို့ distance operator လိုပါတယ်။
pgvector မှာ operator သုံးမျိုးရှိပါတယ် — `<->` (L2 distance)၊ `<=>` (cosine distance)၊ `<#>` (inner product) တို့ပါ။
ဒီ operator တွေကို `ORDER BY` ထဲမှာ သုံးရင် "အနီးဆုံး အစီအစဉ်နဲ့" ပြန်ပေးပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ `CREATE EXTENSION vector;` နဲ့ extension တင်ပါတယ်။
၂။ table ထဲမှာ `embedding vector(768)` လို့ column သတ်မှတ်ပါတယ်။
၃။ ရှာချင်တဲ့ distance အမျိုးအစားအရ operator ရွေးပါတယ်။
၄။ index ဆောက်တဲ့အခါ `vector_cosine_ops` လိုမျိုး operator class ပေးရပါတယ်။
၅။ query မှာ သုံးတဲ့ operator နဲ့ index ရဲ့ operator class တူရပါမယ်။ မတူရင် index က အသုံးမဝင်ပါဘူး။

### ဥပမာ

```python
# This lesson does NOT connect to any database.
# We re-implement the three pgvector distance operators in pure Python
# so the math behind <->, <=> and <#> is visible.

import math

def l2_distance(a, b):
    # pgvector <-> operator: squared Euclidean distance
    return sum((x - y) ** 2 for x, y in zip(a, b))

def cosine_distance(a, b):
    # pgvector <=> operator: 1 - cosine similarity
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return 1 - dot / (na * nb)

def negative_inner_product(a, b):
    # pgvector <#> operator: negative inner product (smaller = closer)
    return -sum(x * y for x, y in zip(a, b))

q = [1.0, 0.0]
a = [1.0, 1.0]
b = [0.5, 0.0]

print("l2:", l2_distance(q, a), l2_distance(q, b))
print("cosine:", round(cosine_distance(q, a), 4), cosine_distance(q, b))
print("nip:", negative_inner_product(q, a), negative_inner_product(q, b))
# Expected output:
# l2: 1.0 0.25
# cosine: 0.2929 0.0
# nip: -1.0 -0.5
```

အဲဒီ logic အတွက် SQL က ဒီလို ဖြစ်ပါမယ် (run မလုပ်ပါနော်၊ ဖတ်ရုံပါ)။

```sql
CREATE EXTENSION vector;

CREATE TABLE chunks (
  id bigserial PRIMARY KEY,
  content text,
  embedding vector(768)
);

-- operator class must match the operator used in queries
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);

SELECT content FROM chunks
ORDER BY embedding <=> $1::vector   -- dimension must match the column: 768 numbers
LIMIT 5;                            -- a short '[...]' literal raises "expected 768 dimensions"
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

operator နဲ့ operator class မကိုက်ရင် query က slow scan ဖြစ်သွားပါတယ်။
production မှာ ဒါဟာ "index ရှိပါလျက် မသုံးဘူး" ဆိုတဲ့ အမှားအနှေးရဲ့ အကြီးဆုံး အကြောင်းရင်းပါပါတယ်။
cosine သုံးမယ်ဆိုရင် `vector_cosine_ops` ပေးဖို့ မမှတ်သားသင့်ပါဘူး။

---

## Subtopic 2 — HNSW နဲ့ IVFFlat ရွေးချယ်မှု၊ `m` / `ef_construction` / `lists` သတ်မှတ်ခြင်

### ဘာကို ဆိုလိုတာလဲ

HNSW ဆိုတာ graph ပုံစံနဲ့ အနီးဆုံး vector တွေကို ရှာပေးတဲ့ index algorithm ပါ။
IVFFlat ကတော့ data ကို cluster အချင်းချင်း ခွဲပြီး ရှာတဲ့ algorithm ပါ။
`m` က graph node တစ်ခုရဲ့ ဆက်သွယ်မှု အရေအတွက်ပါ။
`ef_construction` က index ဆောက်ချိန်မှာ စစ်ဆေးတဲ့ node အရေအတွက်ပါ။
`lists` က IVFFlat မှာ ခွဲထားတဲ့ cluster အရေအတွက်ပါ။

### ဘာကြောင့် လဲ

table အလုံးကို တစ်ခုချင်း နှိုင်းရင် row သန်းနဲ့ချီရင် အလွန်နှေးပါတယ်။
Approximate index က အတိအကျ မဟုတ်ပေမယ့် မြန်အောင် လုပ်ပေးပါတယ်။
HNSW က query လျင်ပြီး index build ကြားပါတယ်၊ data ထည့်ပြီးသားမှ build လည်း ရပါတယ်။
IVFFlat က build မြန်ပေမယ့် data နည်းရင် အလုပ်မကောင်းပါဘူး — pgvector docs က row ၁၀,၀၀၀ ထက် နည်းရင် index မဆောက်သင့်တယ်လို့ ပြောပါတယ်။
pgvector docs မှာ IVFFlat အတွက် `lists ≈ rows / 1000` နဲ့ စဖို့ အကြံပေးထားပါတယ်။
row ၁,၀၀၀,၀၀၀ အထက်ဆို `sqrt(rows)` လို့ အကြံပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ row အရေအတွက် ခန့်မှန်းပါတယ်။
၂။ နည်းရင် (၁၀၀၀၀ အောက်) index မဆောက်ဘူး၊ plain scan က ပိုမြန်ပါတယ်။
၃။ အလယ်အလတ်/ကြီးရင် HNSW က ပိုမှီခိုလို့ ကောင်းပါတယ်။
၄။ build အမြန်ကို ပိုအရေးပါရင် IVFFlat ရွေးပါတယ်။
၅။ recall (ရှာမိမှုနှုန်း) မလုံရင် `m` ဒါမှမဟုတ် `ef_construction` တိုးပါတယ် — pgvector မှာ `m` default ၁၆၊ `ef_construction` default ၆၄ ပါ။

### ဥပမာ

```python
# Deterministic "small HNSW-style" graph search, offline, stdlib only.
# A real system would run this inside pgvector's HNSW index.

import math, heapq

def l2(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

def build_graph(points, m=2):
    # m = max connections per node (pgvector's m parameter)
    graph = {}
    ids = list(points)
    for i in ids:
        # connect each node to its m nearest earlier neighbors
        dists = [(l2(points[i], points[j]), j) for j in ids if j != i]
        graph[i] = [j for _, j in heapq.nsmallest(m, dists)]
    return graph

def greedy_search(graph, points, q, start):
    # greedy walk: move to the closest neighbor until no improvement
    best, best_d = start, l2(points[start], q)
    while True:
        improved = False
        for n in graph[best]:
            d = l2(points[n], q)
            if d < best_d:
                best, best_d, improved = n, d, True
        if not improved:
            return best, round(best_d, 4)

pts = {0: [0.0, 0.0], 1: [1.0, 0.0], 2: [0.0, 1.0], 3: [5.0, 5.0]}
g = build_graph(pts, m=2)
print("graph:", g)
node, dist = greedy_search(g, pts, [0.1, 0.1], start=3)
print("greedy nearest:", node, "dist:", dist)
# Expected output:
# graph: {0: [1, 2], 1: [0, 2], 2: [0, 1], 3: [1, 2]}
# greedy nearest: 0 dist: 0.1414
```

SQL အနေနဲ့ကတော့ —

```sql
-- HNSW with pgvector defaults shown explicitly
CREATE INDEX ON chunks USING hnsw (
  embedding vector_cosine_ops
) WITH (m = 16, ef_construction = 64);

-- IVFFlat: lists ~ rows/1000 as a starting point per pgvector docs
CREATE INDEX ON chunks USING ivfflat (
  embedding vector_cosine_ops
) WITH (lists = 100);
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

index ရွေးချယ်မှုက latency နဲ့ recall နှစ်ခုလုံးကို သက်ရောက်ပါတယ်။
data နည်းနည်းနဲ့ IVFFlat သုံးလိုက်ရင် cluster တွေ လုံးဝ မကိုက်ပါဘူး။
ဒါကြောင့် pgvector docs ရဲ့ အကြံအစဉ်အတိုင်း စမ်းပြီး ကိုယ့် data နဲ့ တိုင်းတာဖို့ အရေးကြီးပါတယ်။

---

## Subtopic 3 — jsonb metadata၊ GIN index နဲ့ SQL-side filtering

### ဘာကို ဆိုလိုတာလဲ

`jsonb` က PostgreSQL ရဲ့ JSON data သိမ်းတဲ့ binary column type ပါ။
GIN (Generalized Inverted Index) က jsonb ထဲက key/value တွေကို ဖြစ်စေ၊ array တွေကို ဖြစ်စေ မြန်မြန် ရှာပေးတဲ့ index ပါ။
SQL-side filtering ဆိုတာ vector ရှာတုန်းမှာ metadata condition ကို SQL `WHERE` နဲ့ တွဲစစ်တာပါ။

### ဘာကြောင့် လဲ

vector နဲ့ကျူးပါပါတယ်ဆိုပေမယ့် source ဒါမှမဟုတ် ရက်စွဲ မှန်ရမယ်လို့ အမြဲလိုအပ်ပါတယ်။
ဥပမာ — "ဒီ PDF ထဲက အခန်းငယ်တွေပဲ ပြောင်းပြန်ပြောပေးပါ" လိုမျိုးပါ။
vector index က condition မစစ်နိုင်လို့ metadata ကို WHERE နဲ့ တွဲစစ်ရပါတယ်။
WHERE မှာ GIN index မရှိရင် rows အားလုံးကို scan ပြီးမှ filter လုပ်ရပါတယ်။ ဒါက နှေးပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ `metadata jsonb` column ထည့်ပါတယ်။
၂။ မကြာခဏ စစ်တဲ့ key တွေအတွက် GIN index ဆောက်ပါတယ်။
၃။ vector query နဲ့ `WHERE metadata @> '{"source": "manual"}'` လို containment စစ်ပါတယ်။
၄။ filter မြန်အောင် Postgres က query plan ကို ကြည့်ပါတယ်။

### ဥပမာ

```python
# Offline stand-in for "vector search + metadata filter".
# Postgres would do this with an HNSW index scan plus a WHERE clause.

def l2(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))

rows = [
    {"id": 1, "vec": [0.1, 0.1], "meta": {"source": "manual"}},
    {"id": 2, "vec": [0.2, 0.0], "meta": {"source": "web"}},
    {"id": 3, "vec": [0.15, 0.05], "meta": {"source": "manual"}},
]
q = [0.1, 0.0]

# WHERE metadata @> '{"source":"manual"}' equivalent
filtered = [r for r in rows if r["meta"].get("source") == "manual"]
ranked = sorted(filtered, key=lambda r: l2(r["vec"], q))
print([(r["id"], round(l2(r["vec"], q), 4)) for r in ranked])
# Expected output:
# [(3, 0.005), (1, 0.01)]
```

SQL ပုံကတော့ —

```sql
CREATE TABLE chunks (
  id bigserial PRIMARY KEY,
  content text,
  embedding vector(768),
  metadata jsonb
);

CREATE INDEX ON chunks USING gin (metadata);

CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);

SELECT content
FROM chunks
WHERE metadata @> '{"source": "manual"}'
ORDER BY embedding <=> $1::vector   -- 768 numbers, matching the column
LIMIT 5;
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

RAG pipeline မှာ metadata filter က မပါလို့မရတဲ့ အပိုင်းပါ။
GIN မရှိရင် filter က တစ်ချိန်ကြာ ကြောင့် index အလုပ်လုပ်သလို ထင်ရပေမယ့် တကယ်က နှေးနေတတ်ပါတယ်။
ဒါက troubleshooting လုပ်ရခက်တဲ့ bug တွေထဲ ထိပ်ဆုံးကပါပါတယ်။

---

## Subtopic 4 — `maintenance_work_mem`၊ parallel build နဲ့ EXPLAIN ဖတ်ခြင်

### ဘာကို ဆိုလိုတာလဲ

`maintenance_work_mem` က index ဆောက်တဲ့ အချိန်မှာ သုံးတဲ့ memory အတွက် setting ပါ။
Parallel build က index ဆောက်တဲ့ အလုပ်ကို worker process တွေနဲ့ ခွဲလုပ်တာပါ။
`EXPLAIN ANALYZE` က query ကို ဘယ်လို အဆင့်ဆင့် လုပ်သလဲ ပြတဲ့ command ပါ။

### ဘာကြောင့် လဲ

HNSW index ကြီးတစ်ခုကို memory အနည်းငယ်နဲ့ ဆောက်ရင် အလွန်ကြာပါတယ်။
PostgreSQL docs အရ `maintenance_work_mem` က index ဆောက်တဲ့ အချိန်မှာတစ်ကြိမ်ချင်း သုံးပါတယ်။
ဒါကြောင့် build တစ်ခုကြီးတဲ့အချိန်မှာ ပိုတက်တဲ့ setting တင်လို့ရပါတယ်။
EXPLAIN မဖတ်နိုင်ရင် index အလုပ်လုပ်မလုပ် မသိပါဘူး။ ဒါက blind debugging ဖြစ်စေပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ build မစခင် `SET maintenance_work_mem = '512MB';` လို့ တစ် session အတွက် တင်ပါတယ်။
၂။ build ပြီးရင် ပုံမှန် setting ပြန်ချပါတယ် — memory ကြီးနေရင် အခြား operation တွေကို ထိခိုက်ပါတယ်။
၃။ query ရဲ့ plan ကို `EXPLAIN ANALYZE` နဲ့ ကြည့်ပါတယ်။
၄။ plan ထဲမှာ `Index Scan ... using chunks_embedding_idx` ဆိုရင် index သုံးနေတာပါ။
၅။ `Seq Scan` ပေါ်လာရင် operator class ဒါမှမဟုတ် query ပုံစံ မကိုက်နေတာပါ။

### ဥပမာ

```python
# Deterministic offline stand-in for recall@k: how often does an
# approximate plan find the same top-k as an exact scan?
# pgvector would compute this over real table data.

def exact_topk(points, q, k):
    return sorted(points, key=lambda p: sum((a - b) ** 2 for a, b in zip(p, q)))[:k]

def approx_topk(points, q, k, sample_step=2):
    # stand-in for an index that inspects only a subset of points
    subset = points[::sample_step]
    return sorted(subset, key=lambda p: sum((a - b) ** 2 for a, b in zip(p, q)))[:k]

pts = [[float(i), 0.0] for i in range(100)]
q = [10.0, 0.0]

exact = [tuple(p) for p in exact_topk(pts, q, 5)]
approx = [tuple(p) for p in approx_topk(pts, q, 5)]
hits = len(set(exact) & set(approx))
print("exact:", exact)
print("approx:", approx)
print("recall@5 =", hits / 5)
# Expected output:
# exact: [(10.0, 0.0), (9.0, 0.0), (11.0, 0.0), (8.0, 0.0), (12.0, 0.0)]
# approx: [(10.0, 0.0), (8.0, 0.0), (12.0, 0.0), (6.0, 0.0), (14.0, 0.0)]
# recall@5 = 0.6
```

PostgreSQL ဘက်မှာ စစ်တဲ့ ပုံစံကတော့ —

```sql
-- raise memory for the index build only, in this session
SET maintenance_work_mem = '512MB';

CREATE INDEX ON chunks USING hnsw (
  embedding vector_cosine_ops
);

-- check that the index is actually used
EXPLAIN ANALYZE
SELECT content FROM chunks
ORDER BY embedding <=> $1::vector   -- 768 numbers, matching the column
LIMIT 5;
```

PostgreSQL docs အရ parallel build က B-tree လို index တချို့အတွက် အလိုအလျောက် ဝင်ပါတယ်။
pgvector index တွေအတွက်ကတော့ pgvector ရဲ့ version အလိုက် အထောက်အပံ့ ကွာပါတယ် — official repo ကို အတည်ပြုကြည့်ပါ။

### လ
