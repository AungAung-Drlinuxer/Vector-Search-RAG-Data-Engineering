# Module 05 — pgvector: PostgreSQL ထဲမှာ Vector Search လုပ်ခြင်း

Course: Vector Search & RAG Data Engineering

---

## Subtopic 1 — `vector` column၊ operator class နဲ့ distance operator များ

### ဘာကို ဆိုလိုတာလဲ

pgvector သည် PostgreSQL အတွက် extension တစ်ခု ဖြစ်ပြီး embedding vector များကို PostgreSQL table column အဖြစ် သိမ်းဆည်းပေးသည်။ `vector` type တွင် dimension ကို သတ်မှတ်၍ `vector(1536)` ပုံစံဖြင့် ရေးသားသည်။ OpenAI embedding များသည် 1536 dimension ဖြစ်ပြီး၊ ဤကိန်းဂဏန်းသည် OpenAI ၏ embedding model documentation တွင် သတ်မှတ်ထားခြင်း ဖြစ်သည်။

Distance operator များသည် vector နှစ်ခုကြား အနီးစပ်ဆုံးဖြစ်မှုကို တွက်ချက်ပေးသော operator များ ဖြစ်သည်။ pgvector တွင် `<->` (L2 distance), `<#>` (negative inner product), `<=>` (cosine distance) သုံးမျိုး ရှိသည်။ Query တွင် `ORDER BY embedding <=> '[0.1, 0.2, ...]'` ပုံစံဖြင့် အနီးဆုံး document များကို ဆွဲထုတ်နိုင်သည်။

### ဘာကြောင့် လဲ

PostgreSQL အပြင် သီးသန့် data store မတည်ဆောက်လိုပါက pgvector သည် သင့်တော်သော ရွေးချယ်မှု ဖြစ်သည်။ RAG pipeline တွင် document chunk, metadata, embedding အားလုံးကို database တစ်ခုတည်း၌ သိမ်းဆည်းနိုင်သဖြင့် application architecture ရိုးရှင်းသည်။

Operator အသိသည် မရှိမဖြစ် လိုအပ်သည် — index ဆောက်ရာတွင် `vector_cosine_ops` ကဲ့သို့ operator class ရွေးရပြီး၊ query တွင်လည်း ထို class နှင့် ကိုက်ညီသော operator ကိုသာ သုံးမှ index အလုပ်လုပ်သည်။ မကိုက်ညီသော operator ဖြင့် query လုပ်ပါက sequential scan ကျပြီး latency သိသိသာသာ မြင့်တက်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

1. `CREATE EXTENSION vector;` ဖြင့် extension ကို enable လုပ်ပါ။
2. Table တွင် `embedding vector(1536)` ကဲ့သို့ column သတ်မှတ်ပါ။ Dimension သည် fixed ဖြစ်သဖြင့် သိမ်းဆည်းသော vector ၏ length တူညီမှသာ လက်ခံသည်။
3. Data ထည့်ရာတွင် vector literal ကို `'[0.1, 0.2, ...]'` string format ဖြင့် ရေးပါ — pgvector က parse လုပ်သည်။
4. Distance query ကို `<->`, `<=>`, `<#>` တစ်ခုနှင့် `ORDER BY ... LIMIT k` ပုံစံဖြင့် ရေးပါ။
5. Index ရှိပါက ထို index ၏ operator class နှင့် ကိုက်ညီသော operator ကိုသာ query တွင် သုံးပါ — planner က Index Scan ရွေးချယ်ရန် ဤအချက်က ဆုံးဖြတ်သည်။

### ဥပမာ

Table တစ်ခုနှင့် cosine distance query ကို အောက်ပါပုံစံဖြင့် ရေးသားနိုင်သည်။

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

Distance operator များကို pure Python ဖြင့် အသေးစား ပြန်လည်တွက်ချက်ကြည့်ပါက အောက်ပါအတိုင်း ဖြစ်သည်။

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

RAG pipeline တစ်ခု production တင်ရာတွင် embedding storage ရွေးချယ်မှုသည် အရေးကြီးသည်။ pgvector ကို ရွေးချယ်ပါက metadata filtering, transaction, backup, replication အားလုံးကို PostgreSQL ၏ စံလုပ်ထုံးလုပ်နည်းအတိုင်း ရရှိသဖြင့် operations ဘက်တွင် လွယ်ကူသည်။

Operator class နှင့် query operator မကိုက်ညီမှုသည် အဖြစ်များသော အမှားတစ်မျိုး ဖြစ်သည်။ Index ရှိပါလျက် query latency ရုတ်တရက် မြင့်တက်ပါက ပထမဆုံး စစ်ဆေးရမည့်အချက်မှာ query ၏ operator နှင့် index ၏ operator class ကိုက်ညီမှု ရှိ/မရှိ ဖြစ်သည်။ ဤအချက်သည် အဖြစ်များသော debugging လွဲမှားမှုတစ်ခု ဖြစ်သည်။

## အနှစ်ချုပ်

- `vector(n)` type သည် fixed-dimension embedding ကို table column အဖြစ် သိမ်းဆည်းသည်။
- Distance operator သုံးမျိုး ရှိသည် — `<->` L2၊ `<=>` cosine၊ `<#>` inner product (embedding အများစုအတွက် `<=>` ကို သုံးသည်)။
- Index ၏ operator class (ဥပမာ `vector_cosine_ops`) နှင့် query operator တူညီမှသာ Index Scan ရရှိသည်။
- Data, embedding, metadata အားလုံးကို database တစ်ခုတည်း၌ သိမ်းဆည်းနိုင်ခြင်းသည် pgvector ၏ အဓိက အားသာချက် ဖြစ်သည်။
- Operator မကိုက်ညီပါက sequential scan ကျပြီး latency မြင့်တက်သည် — query ရေးသားရာတွင် စစ်ဆေးရမည့် အချက်ဖြစ်သည်။

---

## Subtopic 2 — HNSW နဲ့ IVFFlat ရွေးချယ်မှု၊ `m` / `ef_construction` / `lists` သတ်မှတ်ခြင်း

### ဘာကို ဆိုလိုတာလဲ

pgvector တွင် ANN index နှစ်မျိုး ပါဝင်သည် — HNSW နှင့် IVFFlat။ HNSW (Hierarchical Navigable Small World) သည် multi-layer graph တည်ဆောက်ပြီး layer တစ်ခုစီရှိ near-neighbor link များဖြင့် အနီးဆုံး point ကို ရှာဖွေသည်။ IVFFlat သည် vector များကို cluster အဖြစ် ခွဲခြမ်းပြီး query ရောက်ရှိလာပါက အနီးဆုံး cluster အနည်းငယ်ကိုသာ scan လုပ်သည်။

`m` နှင့် `ef_construction` သည် HNSW ၏ build-time parameter များ ဖြစ်သည် — `m` သည် node တစ်ခု၏ neighbor အရေအတွက်၊ `ef_construction` သည် build အတွင်း ထိန်းထားသော candidate အရေအတွက် ဖြစ်သည်။ `lists` သည် IVFFlat ၏ cluster အရေအတွက် ဖြစ်သည်။

### ဘာကြောင့် လဲ

Exact search သည် vector အားလုံးကို တစ်ခုချင်း တွက်ချက်ရသဖြင့် data သန်းချီ ရှိလာပါက scalability မရှိတော့ပေ။ ANN index သည် recall အနည်းငယ် စွန့်လှူ၍ speed ရယူသည် — ဤသည်မှာ ဤ module ၏ အခြေခံ trade-off ဖြစ်သည်။

Parameter များကို သိရှိရန် လိုအပ်သည့် အကြောင်းရင်းမှာ ၎င်းတို့က trade-off ကို တိုက်ရိုက် ထိန်းချုပ်သောကြောင့် ဖြစ်သည်။ `m` ကြီးပါက graph connectivity ထူထပ်ပြီး recall တက်သော်လည်း build time နှင့် memory တစ်ပြိုင်နက် တက်သည်။ `lists` ကြီးပါက cluster များ သေးငယ်ပြီး probe တစ်ခုစီ မြန်ဆန်သော်လည်း သက်ဆိုင်ရာ cluster ကို လွဲချော်နိုင်ခြေ တိုးသည်။

### ဘယ်လို အလုပ်လုပ်လဲ

1. HNSW index ကို `CREATE INDEX ... USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)` ပုံစံဖြင့် ဆောက်ပါ။
2. pgvector documentation အရ `m` default သည် 16၊ `ef_construction` default သည် 64 ဖြစ်သည်။
3. IVFFlat index ကို `CREATE INDEX ... USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)` ဖြင့် ဆောက်ပါ — `lists` အတွက် pgvector documentation က row 1M အထိ `rows / 1000`၊ 1M အထက်တွင် `sqrt(rows)` ကို ကနဦးတန်ဖိုးအဖြစ် ညွှန်းဆိုသည်။
4. IVFFlat အတွက် သီးသန့်အချက် — data အနည်းငယ် ထည့်သွင်းပြီးမှ index ဆောက်ပါ။ Cluster center များကို ရှိပြီးသား data ပေါ် အခြေခံ၍ တွက်ချက်သောကြောင့် ဖြစ်သည်။
5. HNSW query အတွက် runtime knob `SET hnsw.ef_search = 40;` ရှိသည် — တန်ဖိုးကြီးပါက recall တက်ပြီး query latency တက်သည်။

### ဥပမာ

HNSW နှင့် IVFFlat ဆောက်ပုံကို အောက်ပါအတိုင်း နှိုင်းယှဉ်နိုင်သည်။

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

`lists` ကို row အရေအတွက်မှ တွက်ချက်ပါက — row တစ်သန်းအတွက် square root သည် 1000 ဖြစ်သဖြင့် `lists = 1000` သည် documentation ၏ suggested starting point ဖြစ်သည်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Data အရွယ်အစားအလိုက် အသင့်တော်ဆုံး index ပြောင်းလဲသည်။ Data ပမာဏ များသော production system များတွင် HNSW သည် query latency ပိုတည်ငြိမ်သဖြင့် အသုံးများပြီး၊ IVFFlat သည် build မြန်ပြီး memory သက်သာသဖြင့် batch ingestion များသော workload အတွက် သင့်တော်သည်။

Parameter များကို စမ်းသပ်ခြင်း မပြုဘဲ မသတ်မှတ်သင့်ပါ — `m` နှင့် `ef_construction` ကြီးတိုင်း recall တက်သည်မဟုတ်ဘဲ build ကုန်ကျစရိတ်ကို အရင် ပေးဆောင်ရသည်။ Dataset အစစ်ပေါ်တွင် k-recall တိုင်းတာပြီး SLA နှင့် ညှိနှိုင်းခြင်းသာ မှန်ကန်သော နည်းလမ်း ဖြစ်သည်။

## အနှစ်ချုပ်

- HNSW သည် graph-based၊ IVFFlat သည် cluster-based — နှစ်ခုစလုံး ANN index ဖြစ်သည်။
- HNSW သည် build နှေးသော်လည်း query မြန်ပြီး၊ IVFFlat သည် build မြန်သော်လည်း data ထည့်သွင်းပြီးမှ ဆောက်သင့်သည်။
- `m` (neighbor link အရေအတွက်) နှင့် `ef_construction` (build candidate အရေအတွက်) သည် HNSW ၏ quality knob များ ဖြစ်သည်။
- `lists` သည် IVFFlat ၏ cluster အရေအတွက် ဖြစ်ပြီး၊ စတင်စမ်းသပ်ရန် တန်ဖိုးမှာ row count ၏ square root ဖြစ်သည်။
- Query-time knob `hnsw.ef_search` နှင့် `ivfflat.probes` သည် recall နှင့် latency ကို runtime တွင် ချိန်ညှိပေးသည်။
- Parameter မြှင့်တိုင်း ပိုကောင်းသည်မဟုတ် — build time နှင့် memory တစ်ပြိုင်နက် တက်သည်။

---

## Subtopic 3 — jsonb metadata၊ GIN index နဲ့ SQL-side filtering

### ဘာကို ဆိုလိုတာလဲ

RAG pipeline တွင် embedding တစ်ခုတည်း မလုံလောက်ပါ — chunk တစ်ခုချင်းစီတွင် မည်သည့် document၊ မည်သည့် page၊ မည်သည့် department နှင့် သက်ဆိုင်သည်ဆိုသော metadata ပါဝင်လေ့ရှိသည်။ PostgreSQL တွင် ထိုအချက်အလက်များကို `jsonb` column ဖြင့် သိမ်းဆည်းနိုင်ပြီး၊ vector search နှင့် metadata filter ကို query တစ်ခုတည်းတွင် ပေါင်းစပ်ရေးသားနိုင်သည်။

GIN index သည် jsonb column အတွင်းရှိ key/value များကို မြန်ဆန်စွာ ရှာဖွေနိုင်စေရန် တည်ဆောက်သော index အမျိုးအစား ဖြစ်သည်။ `@>` (contains) ကဲ့သို့ operator များက GIN index ကို အသုံးပြုသည်။

### ဘာကြောင့် လဲ

Vector database သီးသန့် သုံးပါက metadata filter အတွက် system အပို တစ်ခု ထပ်တပ်ဆင်ရလေ့ရှိသည်။ pgvector တွင် filter များကို SQL ၏ WHERE clause မှ တိုက်ရိုက် လုပ်ဆောင်နိုင်သဖြင့် pipeline ရိုးရှင်းသည်။

Post-filter ပြဿနာသည်လည်း အရေးကြီးသည် — vector index က top-k ကို ရှာပြီးမှ metadata filter ကျေသောအခါ ကျန်ရှိသော result အရေအတွက်သည် k ထက် နည်းသွားနိုင်သည်။ SQL-side filtering သည် index scan နှင့် filter ကို တစ်ပြိုင်နက် လုပ်ဆောင်နိုင်စေသည်။

### ဘယ်လို အလုပ်လုပ်လဲ

1. Table တွင် `metadata jsonb` column ထည့်ပါ။
2. Metadata ကို `{"source": "hr_manual.pdf", "page": 12, "department": "hr"}` ပုံစံဖြင့် သိမ်းပါ။
3. GIN index ကို `CREATE INDEX ON chunks USING gin (metadata jsonb_path_ops);` ဖြင့် ဆောက်ပါ — `jsonb_path_ops` သည် `@>` operator အတွက် သီးသန့် ပိုကျဉ်းပြီး ပိုသေးသော index ပေးသည်။
4. Query တွင် vector search နှင့် metadata filter ကို တွဲဖက်ရေးပါ — planner သည် operator များကို ကြည့်၍ scan အစီအစဉ် ရွေးချယ်သည်။
5. Filter ပြုလုပ်သော key များကို မေးမြန်းမှု များပါက partial index နှင့် expression index များကိုလည်း စဉ်းစားပါ။

### ဥပမာ

Vector search နှင့် metadata filter ပေါင်းစပ်ထားသော query မှာ အောက်ပါအတိုင်း ဖြစ်သည်။

```sql
CREATE INDEX ON chunks USING gin (metadata jsonb_path_ops);

SELECT id, content
FROM chunks
WHERE metadata @> '{"department": "hr"}'
  AND metadata->>'page' IS NOT NULL
ORDER BY embedding <=> $1::vector
LIMIT 5;
```

pgvector documentation တွင် ဤကဲ့သို့ filtering query များ နှေးကွေးမှုကို ဖြေရှင်းရန် iterative index scan feature ကို ဖော်ပြထားသည် — filter selectivity မြင့်လာပါက index က result အရေအတွက် ပြည့်မီအောင် ထပ်မံ ဖြည့်ဆည်းပေးသည်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

RAG quality သည် search မှ ရရှိသော chunk များ၏ သင့်လျော်မှုအပေါ် မူတည်သည်။ "ဤ question သည် finance department အတွက်သာ" ကဲ့သို့ filter တစ်ခုဖြင့် မသက်ဆိုင်သော answer များကို ကြိုတင် တားဆီးနိုင်သည်။

jsonb သည် schema-flexible ဖြစ်သဖြင့် metadata structure ပြောင်းလဲမှုကို လွယ်ကူစွာ လက်ခံသည် — column အသစ် မထည့်ဘဲ key အသစ် ထည့်နိုင်သဖြင့် data model ချဲ့ထွင်ရန် လွယ်ကူသည်။ Query ပြုလုပ်သော key များကို GIN index ဖြင့် ကာမိစေရန် စစ်ဆေးရန် လိုအပ်သည်။

## အနှစ်ချုပ်

- `jsonb` column သည် chunk metadata များကို schema-flexible အဖြစ် သိမ်းဆည်းသည်။
- GIN index (`jsonb_path_ops`) သည် `@>` contains query များကို မြန်ဆန်စေသည်။
- Vector search နှင့် metadata filter ကို SQL query တစ်ခုတည်းတွင် ရေးသားနိုင်ခြင်းသည် pgvector ၏ ထင်ရှားသော အားသာချက် ဖြစ်သည်။
- Filter selectivity မြင့်ပါက top-k မပြည့်နိုင်သဖြင့် iterative index scan ကဲ့သို့ feature များကို စဉ်းစားရမည်။
- Metadata သည် RAG answer quality ကို တိုက်ရိုက် မြှင့်တင်နိုင်သော ကိရိယာ ဖြစ်သည်။

---

## Subtopic 4 — `maintenance_work_mem`၊ parallel build နဲ့ EXPLAIN ဖတ်ခြင်း

### ဘာကို ဆိုလိုတာလဲ

Index ဆောက်ရာတွင် memory နှင့် CPU နှစ်ခုလုံး အသုံးပြုသည်။ `maintenance_work_mem` သည် PostgreSQL ၏ index build, VACUUM စသည့် maintenance အလုပ်များအတွက် ခွဲဝေပေးသော memory size ဖြစ်သည် — default သည် 64MB ဖြစ်ပြီး pgvector HNSW build အတွက် မလုံလောက်နိုင်သည်။

Parallel build သည် index build အလုပ်ကို worker process အများအပြားဖြင့် ခွဲဝေလုပ်ဆောင်ခြင်း ဖြစ်သည်။ `max_parallel_maintenance_workers` parameter က worker အရေအတွက်ကို ထိန်းချုပ်သည်။ EXPLAIN (နှင့် `EXPLAIN ANALYZE`) သည် query plan များကို ဖတ်ရှုနိုင်စေသော tool ဖြစ်သည်။

### ဘာကြောင့် လဲ

HNSW build သည် graph edge များကို memory အတွင်း တည်ဆောက်ရသဖြင့် memory မလုံလောက်ပါက disk ပေါ် spill ဖြစ်ပြီး build time သိသိသာသာ တိုးသည်။ pgvector documentation တွင် build အချိန်၌ `maintenance_work_mem` တိုးပါက build time သိသိသာသာ လျော့ကျကြောင်း မှတ်ချက်ပြုထားသည် — တိကျသော factor သည် dataset အပေါ် မူတည်သဖြင့် ကိုယ်တိုင် တိုင်းတာရန် လိုအပ်သည်။

EXPLAIN မဖတ်တတ်ပါက index အလုပ်လုပ်/မလုပ် မသိနိုင်ပေ။ Query နှေးကွေးမှု၏ အကြောင်းရင်းသည် plan အတွင်း ဖော်ပြထားလေ့ရှိသဖြင့် ဤ skill သည် data engineer တိုင်း၏ အခြေခံ လက်စွမ်း ဖြစ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

1. Build မလုပ်မီ `SET maintenance_work_mem = '512MB';` ဖြင့် ယာယီ တိုးမြှင့်ပါ — server restart မလိုဘဲ session အတွင်းသာ သက်ရောက်သည်။
2. `SET max_parallel_maintenance_workers = 4;` ဖြင့် parallel worker အရေအတွက် ချိန်ညှိပါ — pgvector documentation အရ parallel build သည် index build time ကို လျှော့ချပေးသည်။
3. Query ကို `EXPLAIN (ANALYZE, BUFFERS) SELECT ...` ဖြင့် run ပါ။
4. Plan တွင် index အမည်သာ ပြသသည် (ဥပမာ `Index Scan using chunks_embedding_idx`) — operator class အမည် မပြသပါ။ `Index Scan` တွေ့ပါက index အသုံးပြုနေပြီး၊ `Seq Scan on chunks` တွေ့ပါက index မသုံးဘဲ table တစ်လျှောက် scan ဖြစ်နေသည်။
5. Recall တိုင်းတာလိုပါက exact search ရလဒ်နှင့် index search ရလဒ်ကို နှိုင်းယှဉ်၍ top-k အတွင်း ပါဝင်မှု အချိုး တွက်ချက်ပါ။

### ဥပမာ

Build ချိန်ညှိပြီး plan စစ်ဆေးသော ပုံစံမှာ အောက်ပါအတိုင်း ဖြစ်သည်။

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

Build အခြေအနေကို ပုံဖော်ကြည့်ရာတွင် worker အရေအတွက်နှင့် ခန့်မှန်းချိန် ဆက်နွယ်မှုကို သင်ခန်းစာသဘောဖြင့် အောက်ပါအတိုင်း ပြသနိုင်သည်။

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

Index build သည် data ingestion pipeline ၏ မည်သည့်နေရာတွင်မဆို bottleneck ဖြစ်နိုင်သည် — chunk သန်းချီ ထည့်ပြီးမှ HNSW ဆောက်ပါက default memory ဖြင့် build time အလွန် ကြာနိုင်သည်။ `maintenance_work_mem` တိုးမြှင့်ခြင်းဖြင့် pipeline တစ်ခုလုံး ပြန်လည် အရှိန်မြှင့်နိုင်သည်။

EXPLAIN ဖတ်တတ်ခြင်းသည် production debugging ၏ အခြေခံ ဖြစ်သည်။ "Query နှေးနေသည်" report ရောက်လာပါက ပထမဆုံး အဆင့်မှာ plan ချခြင်း ဖြစ်သည် — index မသုံးပါက operator class ကိုက်ညီမှု၊ data ပမာဏ၊ statistics သက်တမ်း စသည်တို့ကို plan နှင့် statistics မှ အစဉ်လိုက် ခွဲခြမ်းနိုင်သည်။ Memory တိုးရာတွင် server-wide setting မပြုလုပ်ဘဲ — အခြား session များလည်း ရှိနေနိုင်သဖြင့် ယာယီ `SET` ဖြင့် ချိန်ညှိခြင်းက သင့်တော်သည်။

## အနှစ်ချုပ်

- `maintenance_work_mem` သည် index build ၏ memory budget ဖြစ်သည် — default 64MB သည် HNSW build အတွက် မလုံလောက်နိုင်သည်။
- `max_parallel_maintenance_workers` သည် build ကို worker အများဖြင့် ခွဲဝေသည် — coordination overhead ရှိသဖြင့် worker အရေအတွက်နှင့် အချိန် linear အချိုး မကျပါ။
- `EXPLAIN (ANALYZE, BUFFERS)` သည် Index Scan နှင့် Seq Scan နှစ်ခုလုံးကို ခွဲခြား ပြသသည်။
- Plan တွင် `Seq Scan` တွေ့ပါက operator mismatch, data နည်းခြင်း, statistics ဟောင်းနေခြင်း — အကြောင်းရင်း သုံးမျိုးကို စဉ်းစားရမည်။
- Memory တိုးမြှင့်မှုကို session-level `SET` ဖြင့် ယာယီ ပြုလုပ်ခြင်းက server-wide အကျိုးဆက်ကို ရှောင်ရှားပေးသည်။
- Build memory နှင့် parallelism တိုးမြှင့်ခြင်းသည် index build pipeline ၏ ကြာချိန်ကို တိုက်ရိုက် လျှော့ချနိုင်သည်။