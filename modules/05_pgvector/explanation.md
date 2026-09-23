# Module 05 — pgvector: PostgreSQL ထဲမှာ Vector Search လုပ်ခြင်း

Course: Vector Search & RAG Data Engineering

---

## Subtopic 1 — `vector` column၊ operator class နဲ့ distance operator များ

### ဘာကို ဆိုလိုတာလဲ

pgvector ဆိုတာ PostgreSQL အတွက် extension တစ်ခုပါ။ သူ့ရဲ့ အဓိက အလုပ်ကတော့ embedding vector တွေကို PostgreSQL table column တစ်ခုအနေနဲ့ သိမ်းဆည်းပေးတာပါ။ `vector` type က dimension ကို သတ်မှတ်ပြီး store လုပ်တဲ့ အခါ `vector(1536)` ဆိုပြီး ရေးရပါတယ်။ OpenAI embedding တွေက 1536 dimension ဖြစ်လို့ အဲဒီ number က ဘယ်နေရာက လာတာလဲ ဆိုတာကို OpenAI ရဲ့ embedding model ရှုထောင့်က documentation မှာ ဖော်ပြထားပါတယ်။

Distance operator ဆိုတာကတော့ vector နှစ်ခုကြားမှာ "အနီးစပ်ဆုံး" ဆိုတာကို တွက်ပေးတဲ့ operator တွေပါ။ pgvector မှာ `<->` (L2 distance), `<#>` (negative inner product), `<=>` (cosine distance) ဆိုပြီး သုံးမျိုးရှိပါတယ်။ Query ရေးတဲ့အခါ `ORDER BY embedding <=> '[0.1, 0.2, ...]'` ဆိုတဲ့ပုံစံနဲ့ ရှေ့ဆုံးက document တွေကို ဆွဲထုတ်လို့ရပါတယ်။

### ဘာကြောင့် လဲ

PostgreSQL အပြင် data store သပ်သပ် မထောင်ချင်ဘူးဆိုရင် pgvector က အဆင်ပြေဆုံးပါ။ RAG pipeline မှာ document chunk, metadata, embedding အားလုံးကို database တစ်ခုတည်းထဲ ထားလို့ရလို့ application ကို ရိုးရိုးစင်းစင်း ဖန်တီးနိုင်ပါတယ်။

operator တွေကို သိဖို့ မရှိမဖြစ် လိုအပ်တာက index ဆောက်တဲ့အခါ `vector_cosine_ops` လိုမျိုး operator class ရွေးရပြီး၊ query ရေးတဲ့အခါလည်း အဲဒီ class နဲ့ ကိုက်ညီတဲ့ operator ပဲ သုံးမှ index ကအလုပ်လုပ်မှာ ဖြစ်လို့ပါ။ မတူတဲ့ operator နဲ့ query လုပ်ရင် sequential scan ကျသွားပြီး အရမ်းနှေးသွားမှာပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

1. `CREATE EXTENSION vector;` နဲ့ extension ကို enable လုပ်ပါ။
2. Table ထဲမှာ `embedding vector(1536)` လိုမျိုး column သတ်မှတ်ပါ။ dimension က fixed ဖြစ်လို့ store လုပ်တဲ့ vector ရဲ့ length နဲ့ တူမှ လက်ခံပါမယ်။
3. Data ထည့်တဲ့အခါ vector literal ကို `'[0.1, 0.2, ...]'` string format နဲ့ ရေးပါ၊ pgvector က parse လုပ်ပေးပါမယ်။
4. Distance query က `<->`, `<=>`, `<#>` ထဲက တစ်ခုနဲ့ `ORDER BY ... LIMIT k` ပုံစံသုံးပါ။
5. Index ဆောက်ထားရင် အဲဒီ index ရဲ့ operator class နဲ့ ကိုက်တဲ့ operator ကိုပဲ query မှာ ထည့်ပါ — ဒါမှ planner က Index Scan ကို ရွေးပါလိမ့်မယ်။

### ဥပမာ

Table တစ်ခုနဲ့ cosine distance query ကို ဒီလို ရေးလို့ရပါတယ်။

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE chunks (
  id bigserial PRIMARY KEY,
  content text,
  embedding vector(1536)
);

SELECT id, content, embedding <=> $1::vector AS dist
FROM chunks
ORDER BY embedding <=> $1::vector
LIMIT 5;

*(`$1` ကို ပေးတဲ့ parameter ဖြစ်ပြီး **1536** ခုလုံး ပါရပါမယ် — `vector(1536)` column နဲ့ တူမှ လက်ခံတယ်။ အတိုချုံး `'[0.11, 0.23, ...]'` လို literal ရေးရင် `expected 1536 dimensions` error တက်တယ်။)*
```

Distance operator တွေကို pure Python နဲ့ အသေးစား ပြန်တွက်ကြည့်ရင် ဒီလိုဖြစ်ပါတယ်။

```python
import math

def l2(a, b):
    # Euclidean (L2) distance: sqrt of sum of squared differences
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

def cosine_sim(a, b):
    # Cosine similarity: dot product / (norm(a) * norm(b))
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb)

a, b = [1.0, 2.0, 3.0], [2.0, 3.0, 4.0]
print("l2 =", round(l2(a, b), 4))
print("cosine_sim =", round(cosine_sim(a, b), 4))
print("cosine_dist =", round(1 - cosine_sim(a, b), 4))
# Expected output:
# l2 = 1.7321
# cosine_sim = 0.9926
# cosine_dist = 0.0074
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

RAG pipeline တစ်ခုကို production မှာ တင်မယ်ဆိုရင် embedding သိမ်းတဲ့နေရာ ရွေးချယ်စရာက အရေးကြီးပါတယ်။ pgvector ကို ရွေးရင် metadata filtering, transaction, backup, replication — ဒီအကုန်လုံးကို PostgreSQL ရဲ့ ပုံစံအတိုင်း ရလို့ operation ဘက်က ပိုလွယ်ပါတယ်။

Operator class နဲ့ query operator မကိုက်တာက မကြာခဏ ဖြစ်တတ်တဲ့ လွဲမှားမှုတစ်ခုပါ။ Index ရှိပါလျက်နဲ့ query တွေ ရုတ်တရက် နှေးသွားရင် ပထမဆုံး စစ်ကြည့်စရာက query ထဲမှာသုံးတဲ့ operator နဲ့ index ရဲ့ operator class က ကိုက်လား မကိုက်လားဆိုတာပါ။ ဒါက အဖြစ်များတဲ့ debugging လွဲမှားချက်တစ်ခုပါ။

## အနှစ်ချုပ်

- `vector(n)` type က fixed-dimension embedding ကို table column အနေနဲ့ သိမ်းပေးပါတယ်။
- Distance operator သုံးခုရှိပါတယ် — `<->` L2၊ `<=>` cosine၊ `<#>` inner product (ရှုထောင့်အရ `<=>` က embedding များနဲ့ အဆင်ပြေဆုံး)။
- Index ရဲ့ operator class (ဥပမာ `vector_cosine_ops`) နဲ့ query operator တူမှ Index Scan ရပါမယ်။
- Data, embedding, metadata အားလုံးကို database တစ်ခုတည်းထဲ ထားနိုင်တာက pgvector ရဲ့ အားသာချက်ပါ။
- Operator မကိုက်ရင် sequential scan ကျပြီး query နှေးသွားတတ်ပါတယ် — query ရေးတဲ့အခါ သတိထားပါ။

---

## Subtopic 2 — HNSW နဲ့ IVFFlat ရွေးချယ်မှု၊ `m` / `ef_construction` / `lists` သတ်မှတ်ခြင်း

### ဘာကို ဆိုလိုတာလဲ

pgvector မှာ approximate nearest neighbor (ANN) index နှစ်မျိုးပါဝင်ပါတယ် — HNSW နဲ့ IVFFlat ပါ။ HNSW ဆိုတာ Hierarchical Navigable Small World ပါ၊ multi-layer graph တစ်ခုဆောက်ပြီး အလွှာတစ်ခုစီမှာ "near-neighbor link" တွေနဲ့ အနီးစပ်ဆုံး point ကို မြန်မြန်ဆန်ဆန် လမ်းလျှောက်ရှာပေးပါတယ်။ IVFFlat ကတော့ vector တွေကို cluster တွေအဖြစ် အုပ်စုခွဲပြီး၊ query ရောက်လာရင် နီးစပ်တဲ့ cluster အနည်းငယ်ကိုပဲ ဖြတ်ရှာပေးပါတယ်။

`m` နဲ့ `ef_construction` က HNSW ရဲ့ build-time parameter တွေပါ — `m` က graph တစ်ခုစီမှာ node တစ်ခုက ချိတ်ဆက်ရမယ့် neighbor အရေအတွက်၊ `ef_construction` က build လုပ်နေစဉ် ရှာမယ့် candidate အရေအတွက်ပါ။ `lists` ကတော့ IVFFlat ရဲ့ cluster အရေအတွက်ပါ။

### ဘာကြောင့် လဲ

Exact search က vector အားလုံးနဲ့ တစ်ခုချင်း တွက်ရလို့ data သန်းနီးပါးရှိလာရင် ခံနိုင်ရည် မရှိတော့ပါဘူး။ ANN index က အနည်းငယ် accuracy စွန့်လှူပြီး speed ကို ရယူပေးပါတယ် — ဒါက ဒီ module ရဲ့ နက်နဲတဲ့ အချက်ပါ။

Parameter တွေကို သိထားဖို့ လိုတဲ့ အကြောင်းရင်းက သူတို့က trade-off ကို တိုက်ရိုက်ထိန်းပါလို့ပါ။ `m` ကြီးရင် graph က ပိုချိတ်ဆက်ထူထပ်လာပြီး recall တက်ပေမယ့် build အချိန်နဲ့ memory က တစ်ပြိုင်တည်း တက်သွားပါတယ်။ `lists` ကြီးရင် cluster တွေ သေးသွားပြီး probe တစ်ခုစီက ပိုမြန်ပေမယ့် သင့်တော်တဲ့ cluster ကို မှားနိုင်တဲ့အခွင့်အလမ်း တိုးသွားပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

1. HNSW index ကို `CREATE INDEX ... USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)` ဆိုတဲ့ပုံစံနဲ့ ဆောက်ပါ။
2. pgvector documentation အရ `m` ရဲ့ default က 16 ဖြစ်ပြီး `ef_construction` ရဲ့ default က 64 ပါ။
3. IVFFlat index ကို `CREATE INDEX ... USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)` ဆိုပြီး ဆောက်ပါ — `lists` အတွက် pgvector documentation က row 1M အထိ `rows / 1000`၊ 1M အထက်မှာ `sqrt(rows)` ကို စတင်စရာအဖြစ် ညွှန်ပါတယ်။
4. IVFFlat အတွက် သီးသန့်အချက် — data အနည်းငယ် ဖြည့်ထည့်ပြီးမှ index ဆောက်ပါ၊ ဘာကြောင့်လဲဆိုတော့ cluster center တွေက ရှိပြီးသား data ပေါ်မှာ အခြေခံ တွက်ရလို့ပါ။
5. Query မှာ HNSW အတွက် `SET hnsw.ef_search = 40;` ဆိုတဲ့ runtime knob ရှိပါတယ် — ကြီးရင် recall တက်ပြီး query ပိုနှေးပါတယ်။

### ဥပမာ

HNSW နဲ့ IVFFlat ဆောက်ပုံကို ဒီလို နှိုင်းယှဉ်ကြည့်လို့ရပါတယ်။

```sql
-- HNSW: build slow, query fast, no retrain needed
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 200);

-- IVFFlat: build fast, needs populated data first
CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- IVFFlat query-time tuning (number of clusters scanned)
SET ivfflat.probes = 10;
```

`lists` ကို ယူစား row အရေအတွက်ဆိုပြီး တွက်ကြည့်ရင် ဒီလိုပါ — ဥပမာ row တစ်သန်းရှိရင် square root က 1000 ဖြစ်လို့ `lists = 1000` လောက် ထားကြည့်တာက documentation က suggest တဲ့ အစပြုမှတ်ပါ။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Data အရွယ်အစား အလိုက် အသင့်တော်ဆုံး index က ပြောင်းသွားပါတယ်။ စလောက်လောက် အချက်အလက် များများရှိတဲ့ production system တွေမှာ HNSW က query latency ပိုတည်ငြိမ်လို့ အသုံးများပါတယ်၊ IVFFlat ကတော့ build မြန်ပြီး memory သက်သာလို့ အလုပ်များတဲ့ batch ingestion အတွက် သင့်တော်ပါတယ်။

Parameter တွေကို မျက်စိမှိတ် မသတ်မထားရပါနဲ့ — `m` နဲ့ `ef_construction` ကြီးတိုင်း recall တက်တာ မဟုတ်ပါဘူး၊ build ကုန်ကျစရိတ်ကို အရင်ပေးရပြီး အကျိုးအမြတ်က နောက်မှ ရမှာပါ။ Dataset အစစ်ပေါ်မှာ k-recall တိုင်းပြီး ကိုယ့် SLA နဲ့ ညှိကြည့်တာက တစ်ခုတည်းသော မှန်ကန်တဲ့ လမ်းပါ။

## အနှစ်ချုပ်

- HNSW က graph-based၊ IVFFlat က cluster-based — နှစ်ခုစလုံး ANN index ပါ။
- HNSW က build နှေးပေမယ့် query မြန်ပြီး၊ IVFFlat က build မြန်ပေမယ့် data ထည့်ပြီးမှ ဆောက်သင့်ပါတယ်။
- `m` (neighbor link အရေ) နဲ့ `ef_construction` (build candidate အရေ) က HNSW ရဲ့ quality knob တွေပါ။
- `lists` က IVFFlat ရဲ့ cluster အရေပါ — စမ်းသပ်စမှတ်က row count ရဲ့ square root ပါ။
- Query-time knob `hnsw.ef_search` နဲ့ `ivfflat.probes` က recall နဲ့ latency ကို runtime မှာ ချိန်ပေးပါတယ်။
- Parameter ကို မြှင့်တိုင်း ပိုကောင်းတာ မဟုတ်ပါ — build ချိန်နဲ့ memory က တစ်ပြိုင်တည်း တက်ပါတယ်။

---

## Subtopic 3 — jsonb metadata၊ GIN index နဲ့ SQL-side filtering

### ဘာကို ဆိုလိုတာလဲ

RAG pipeline မှာ embedding တစ်ခုတည်း မလုံလောက်ပါဘူး — chunk တစ်ခုချင်းစီကို ဘယ် document ကလဲ၊ ဘယ် page လဲ၊ ဘယ် department နဲ့ သက်ဆိုင်လဲဆိုတဲ့ metadata တွေ ပါတတ်ပါတယ်။ PostgreSQL မှာ အဲဒါကို `jsonb` column တစ်ခုနဲ့ သိမ်းလို့ရပြီး၊ vector search နဲ့ metadata filter ကို query တစ်ခုတည်းထဲ ပေါင်းရေးလို့ရပါတယ်။

GIN index ဆိုတာ jsonb column ထဲက key/value တွေကို မြန်မြန် ရှာပေးနိုင်အောင် ဆောက်တဲ့ index အမျိုးအစားပါ။ `@>` (contains) လိုမျိုး operator တွေက GIN index ကို အသုံးချပါတယ်။

### ဘာကြောင့် လဲ

Vector database သပ်သပ် သုံးရင် metadata filter အတွက် နောက်ထပ် စနစ်တစ်ခု တပ်ဆင်ရတတ်ပါတယ်။ pgvector ကို သုံးရင်ကတော့ filter တွေက SQL ရဲ့ WHERE clause ထဲကနေ တိုက်ရိုက် လုပ်လို့ရလို့ pipeline ရှုထောင့်က ရိုးသွားပါတယ်။

Post-filter ဖြစ်နိုင်တာကလည်း အရေးကြီးပါ — vector index က top-k ကို ရှာပြီးမှ metadata filter ချက်ရင် ကျန်တဲ့ အရေအတွက်က k ထက် နည်းသွားနိုင်ပါတယ်။ SQL-side filtering က index scan နဲ့ filter ကို တစ်ပြိုင်တည်း ဖြတ်ပေးနိုင်တဲ့ အခွင့်အရေး ရပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

1. Table မှာ `metadata jsonb` column ထည့်ပါ။
2. Metadata ကို `{"source": "hr_manual.pdf", "page": 12, "department": "hr"}` ဆိုတဲ့ပုံစံ သိမ်းပါ။
3. GIN index ကို `CREATE INDEX ON chunks USING gin (metadata jsonb_path_ops);` ဆိုပြီး ဆောက်ပါ — `jsonb_path_ops` က `@>` operator အတွက် သီးသန့် ပိုကျဉ်ပြီး ပိုသေးတဲ့ index ပေးပါတယ်။
4. Query မှာ vector search ရှေ့၊ metadata filter နောက် ချိတ်ပြီး ရေးပါ — planner က operator တွေကို ကြည့်ပြီး scan အစီအစဉ် ရွေးပါလိမ့်မယ်။
5. Filter လုပ်တဲ့ key တွေက အများအားဖြင့် မေးလေ့ရှိရင် partial index နဲ့ expression index တွေကိုလည်း ထည့်စဉ်းစားပါ။

### ဥပမာ

Vector search နဲ့ metadata filter ပေါင်းရေးတဲ့ query က ဒီလိုပါ။

```sql
CREATE INDEX ON chunks USING gin (metadata jsonb_path_ops);

SELECT id, content
FROM chunks
WHERE metadata @> '{"department": "hr"}'
  AND metadata->>'page' IS NOT NULL
ORDER BY embedding <=> $1::vector
LIMIT 5;
```

pgvector documentation မှာ ဒါမျိုး filtering query တွေကို slow ဖြစ်စနေတာကို ဖြေရှင်းဖို့ iterative index scan ဆိုတဲ့ feature လည်း ဖော်ပြထားပါတယ် — filter က strict ဖြစ်လာရင် index က result အရေအတွက် ဖြည့်ပေးပါတယ်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

RAG quality က search ရလာတဲ့ chunk တွေ ဘယ်လောက်သင့်လျော်လဲဆိုတာ အပေါ်မှာ မူတည်ပါတယ်။ "ဒီ question က finance department အတွက်ပဲ" ဆိုတဲ့ filter တစ်ခု ထည့်ရုံနဲ့ မဆီလျော်တဲ့ answer တွေကို အရင်ဆီးပစ်လို့ရပါတယ်။

jsonb က schema-flexible ဖြစ်လို့ metadata structure အမျိုးမျိုး ပြောင်းလဲလို့ရပါတယ် — column အသစ် မထည့်ရဘဲ နောက်ပိုင်း key အသစ်ထည့်လို့ရလို့ data model က လွယ်ကူစွာ ချဲ့ထွင်နိုင်ပါတယ်။ ဒါပေမယ့် query လုပ်တဲ့ key တွေကို GIN index နဲ့ အာရုံစိုက်ပေးဖို့ မမေ့ပါနဲ့။

## အနှစ်ချုပ်

- `jsonb` column က chunk metadata တွေကို schema-flexible သဘောနဲ့ သိမ်းပေးပါတယ်။
- GIN index (`jsonb_path_ops`) က `@>` contains query တွေကို မြန်စေပါတယ်။
- Vector search နဲ့ metadata filter ကို SQL query တစ်ခုတည်းထဲ ရေးနိုင်တာက pgvector ရဲ့ ကြီးမားတဲ့ အားသာချက်ပါ။
- Filter က strict ဖြစ်လာရင် top-k ကြိုက်စရာ မကျန်တတ်လို့ iterative index scan တို့ စဉ်းစားပါ။
- Metadata က RAG answer quality ကို တိုက်ရိုက် မြှင့်ပေးနိုင်တဲ့ လက်နက်ကောင်းပါ။

---

## Subtopic 4 — `maintenance_work_mem`၊ parallel build နဲ့ EXPLAIN ဖတ်ခြင်း

### ဘာကို ဆိုလိုတာလဲ

Index ဆောက်တဲ့အခါ memory နဲ့ CPU နှစ်ခုစလုံး အသုံးပြုပါတယ်။ `maintenance_work_mem` က PostgreSQL ရဲ့ index build, VACUUM လို maintenance အလုပ်တွေအတွက် ခွဲဝေပေးတဲ့ memory size ပါ — default က 64MB ဖြစ်ပြီး ဒါက pgvector HNSW build အတွက် တော်တော် ငယ်ပါတယ်။

Parallel build ဆိုတာက index ဆောက်တဲ့အလုပ်ကို worker process အများကြီးနဲ့ ခွဲဝေလုပ်တာပါ။ `max_parallel_maintenance_workers` parameter က worker အရေအတွက်ကို ထိန်းပါတယ်။ EXPLAIN (နဲ့ `EXPLAIN ANALYZE`) ကတော့ query နဲ့ build plan တွေကို မြင်သာအောင် ပြပေးတဲ့ tool ပါ။

### ဘာကြောင့် လဲ

HNSW build က graph edge တွေကို memory ထဲမှာ ခဏတာ သိမ်းထားရလို့ memory မလုံရင် disk ပေါ် ရောက်သွားပြီး build ချိန်က ကျယ်သွားပါတယ်။ pgvector documentation မှာ build တဲ့အချိန် `maintenance_work_mem` ကို တိုးရင် သိသိသာသာ လျှော့ပါတယ်လို့ မှတ်ချက်ထားပါတယ် — တိကျတဲ့ factor က dataset အပေါ် မူတည်လို့ ကိုယ်တိုင် တိုင်းကြည့်ဖို့ လိုပါတယ်။

EXPLAIN ကို မဖတ်တက်ရင် index က အလုပ်လုပ်မလုပ် မသိရပါဘူး။ Query နှေးတဲ့အခါ ဘာကြောင့်နှေးလဲဆိုတာက plan ထဲမှာ ရေးထားတတ်လို့ ဒီ skill က data engineer တိုင်းရဲ့ လက်စွဲအနေနဲ့ ရှိသင့်တဲ့ အရာပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

1. Build မလုပ်ခင် `SET maintenance_work_mem = '512MB';` လိုမျိုး ခဏတာ တိုးပေးပါ — server restart မလိုပါဘူး၊ session တစ်ခုအတွက်ပဲ အသက်ဝင်ပါတယ်။
2. `SET max_parallel_maintenance_workers = 4;` နဲ့ parallel worker ရေကို ချိန်ပါ — pgvector documentation အရ parallel build က index ဆောက်တဲ့အချိန်ကို လျှော့ပေးပါတယ်။
3. Query ကို `EXPLAIN (ANALYZE, BUFFERS) SELECT ...` နဲ့ run လုပ်ပါ။
4. Plan ထဲမှာ index နာမည်ကိုသာ ပြပါတယ် (ဥပမာ `Index Scan using chunks_embedding_idx`) — operator class နာမည်ကို မပြပါ။ `Index Scan` တွေ့ရင် index ကို အသုံးချနေတာပါ၊ `Seq Scan on chunks` တွေ့ရင် index ကို မသုံးဘဲ table တစ်လျှောက်လုံး ဖြတ်နေတာပါ။
5. Recall တိုင်းချင်ရင် exact search ရလဒ်နဲ့ index search ရလဒ်ကို ယှဉ်ပြီး k ထဲက ဘယ်နှံ့ကျန်တယ်ဆိုတာ တွက်ပါ။

### ဥပမာ

Build ခဏတာ tune လုပ်ပြီး plan စစ်တဲ့ ပုံစံက ဒီလိုပါ။

```sql
SET maintenance_work_mem = '512MB';
SET max_parallel_maintenance_workers = 4;

CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 200);

EXPLAIN (ANALYZE, BUFFERS)
SELECT id FROM chunks
ORDER BY embedding <=> $1::vector
LIMIT 5;
```

Build လုပ်တဲ့ အခြေအနေကို ပုံဆွဲကြည့်တဲ့အခါ worker အရေအတွက်နဲ့ ခန့်မှန်းချိန် ဘယ်လို ဆက်နွယ်လဲဆိုတာကို သင်ခန်းစာသဘောနဲ့ ဒီလို ပြသနိုင်ပါတယ်။

```python
# Toy model: illustrative only, not a benchmark claim.
# Total work is split across W parallel workers, with a fixed
# coordination overhead C. Time per worker unit is 1.
total_units = 100
coordination_overhead = 5

for workers in (1, 2, 4, 8):
    per_worker_units = total_units / workers
    estimated_time = per_worker_units + coordination_overhead
    print(f"workers={workers}, est_time={estimated_time:.1f}")
# Expected output:
# workers=1, est_time=105.0
# workers=2, est_time=55.0
# workers=4, est_time=30.0
# workers=8, est_time=17.5
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Index build က data ingestion pipeline ရဲ့ ဘယ်နေရာမှာမဆို ပိတ်မှတ်ချက် ဖြစ်နေတတ်ပါတယ် — chunk သန်းနီးပါး ထည့်ပြီးမှ HNSW ဆောက်ရင် default memory နဲ့ဆိုရင် အချိန်ကြာလွန်းတတ်ပါတယ်။ `maintenance_work_mem` တိုးပေးရုံနဲ့ pipeline တစ်ခုလုံး ပြန်လည် အရှိန်မြှင့်နိုင်တတ်ပါတယ်။

EXPLAIN ဖတ်တတ်တာက production debugging ရဲ့ အခြေခံပါ။ "Query နှေးနေတယ်" လို့ report လာရင် ပထမတစ်ဆင့်က plan ချရတာပါ — index မသုံးရင် operator class ကိုက်လား၊ data ရှိလား၊ statistic ဟောင်းနေလားဆိုတာတွေကို plan နဲ့ statistics ထဲမှာ အစဉ်လိုက် ဖော်ပြနိုင်ပါတယ်။ Memory တိုးရင် တိုးသလောက် အသုံးမချပါနဲ့ — server မှာ အခြား session တွေလည်း ရှိနေတတ်လို့ ခဏတာ `SET` နဲ့ ချိန်တာက သင့်တော်ဆုံးပါ။

## အနှစ်ချုပ်

- `maintenance_work_mem` က index build ရဲ့ memory budget ပါ — default 64MB က HNSW build အတွက် ငယ်တတ်ပါတယ်။
- `max_parallel_maintenance_workers` က build ကို worker အများနဲ့ ခွဲပေးပါ — coordination overhead ရှိတော့ အရေအတွက် ကြိုက်စား တိုးတိုင်း linear မဖြစ်ပါဘူး။
- `EXPLAIN (ANALYZE, BUFFERS)` က Index Scan ရော Seq Scan ရော ရှင်းပြပါတယ်။
- Plan ထဲမှာ `Seq Scan` တွေ့ရင် operator mismatch, data နည်းနေတာ၊ ဟောင်းနေတဲ့ statistics ဆိုတဲ့ အကြောင်းရင်း သုံးခုကို စဉ်းစားပါ။
- Memory တိုးတာကို session-level `SET` နဲ့ ခဏတာ လုပ်တာက server-wide အကျိုးဆိုးသက်ရောက်မှုကို ရှောင်ပေးပါတယ်။
- Build memory နဲ့ parallelism တိုးတဲ့အချိန် index build pipeline ရဲ့ ချိန်ကို တိုက်ရိုက် လျှော့ပေးနိုင်ပါတယ်။
