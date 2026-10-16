## လေ့ကျင့်ခန်း ၁ — Vector Column Schema ဒီဇိုင်း

`chunks` table တွင် `id`, `content`, `embedding` column များ ပါဝင်သော DDL statement ကို ရေးသားပါ။ Embedding dimension ကို 768 အဖြစ် သတ်မှတ်ပြီး cosine distance metric အတွက် index သတ်မှတ်ချက်ကို ထည့်သွင်းပါ။

**Hints:** pgvector extension ကို `CREATE EXTENSION IF NOT EXISTS vector;` ဖြင့် ဦးစွာ enable လုပ်ပါ။ Cosine distance အတွက် `vector_cosine_ops` operator class ကို အသုံးပြုပြီး vector representation များကို insert မပြုမီ L2 normalization ပြုလုပ်ထားရန် လိုအပ်သည်။

**Expected behavior:** PostgreSQL + pgvector standard syntax နှင့် ကိုက်ညီသော DDL statement ဖြစ်ရမည်ဖြစ်ပြီး `vector(768)` data type နှင့် HNSW index definition ပါဝင်ရမည်။

---

## လေ့ကျင့်ခန်း ၂ — Distance Operators နှိုင်းယှဉ်ချက် (`<->`, `<=>`, `<#>`)

အောက်ပါ query တွင် အသုံးပြုထားသော `<=>` အပါအဝင် pgvector distance operators သုံးမျိုး (`<->`, `<=>`, `<#>`) ၏ mathematical properties နှင့် သင့်လျော်သော use case များကို ရှင်းပြပါ။

```sql
SELECT content FROM chunks
ORDER BY embedding <=> '[0.1,0.2,0.3]'::vector
LIMIT 5;
```

**Hints:** `<->` သည် Euclidean (L2) distance, `<=>` သည် Cosine distance, `<#>` သည် Negative Inner Product ဖြစ်သည်။ Unit-normalized vectors များတွင် L2 distance နှင့် Cosine distance တို့သည် monotonic relationship (`L2^2 = 2 * cosine_distance`) ရှိသည်။

**Expected behavior:** Operator တစ်ခုချင်းစီ၏ mathematical formulation၊ operator class mapping (`vector_l2_ops`, `vector_cosine_ops`, `vector_ip_ops`) နှင့် normalization အခြေအနေအလိုက် ranking equivalence ကို ရှင်းပြနိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၃ — Reciprocal Rank Fusion (RRF) Implementation

Deterministic cosine similarity ranking နှင့် lexical keyword ranking နှစ်ခုကို Python standard library အသုံးပြု၍ Reciprocal Rank Fusion (RRF, k=60) ဖြင့် ပေါင်းစပ်သည့် algorithm ကို implement လုပ်ပါ။

**Hints:** RRF formula သည် `RRF_score(d) = Σ [1 / (k + rank(d))]` ဖြစ်သည်။ External database မလိုအပ်ဘဲ pure Python ဖြင့် tie-breaking logic (ID-based determinism) ပါဝင်စွာ ရေးသားပါ။

**Expected behavior:** Dense search နှင့် keyword search ranking နှစ်ခုမှ candidate များကို score calibration မလိုအပ်ဘဲ rank-based ပေါင်းစပ်နိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၄ — HNSW vs IVFFlat Index Selection Framework

Production dataset (million-scale vectors) အတွက် HNSW နှင့် IVFFlat index types များအကြား trade-offs များကို build-time memory, query latency, recall targets (`ef_search`, `probes`) နှင့် data volatility အပေါ် အခြေခံ၍ ဆန်းစစ်ပါ။

**Hints:** IVFFlat သည် inverted file clustering အပေါ် အခြေခံပြီး build time မြန်ဆန်ကာ memory နည်းပါးသော်လည်း recall သည် `probes` setting ပေါ်တွင် မူတည်ပြီး data drift ဖြစ်ပါက periodic reindexing လိုအပ်သည်။ HNSW သည် multi-layer proximity graph ဖြစ်ပြီး high recall နှင့် low latency ပေးနိုင်သော်လည်း memory footprint နှင့် build time ပိုမိုမြင့်မားသည်။

**Expected behavior:** Dataset size, QPS budget, update frequency တို့အလိုက် index type နှင့် hyperparameter recommendation ထုတ်ပေးနိုင်သော logic ကို ဖော်ပြနိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၅ — JSONB Metadata + GIN Index ဖြင့် Filtered Vector Search

`metadata` jsonb column တစ်ခု ထည့်သွင်းပြီး structural attribute အပေါ် pre-filter ပြုလုပ်သည့် vector query ကို ရေးသားပါ။ Attribute filtering အတွက် GIN index ကို design လုပ်ပါ။

```sql
CREATE INDEX ON chunks USING gin (metadata jsonb_path_ops);
```

**Hints:** Filter predicate သည် execution plan တွင် pre-filter သို့မဟုတ် post-filter အနေဖြင့် အလုပ်လုပ်ပုံကို သုံးသပ်ပါ။ Selective filter များတွင် post-filtering သည် top-k candidate starvation ဖြစ်ပေါ်စေနိုင်သည်။

**Expected behavior:** Valid PostgreSQL + pgvector query ဖြစ်ရမည်ဖြစ်ပြီး containment operator သို့မဟုတ် json extraction filter နှင့် vector distance ordering ပေါင်းစပ်ပါဝင်ရမည်။

---

## လေ့ကျင့်ခန်း ၆ — Resource Tuning (`maintenance_work_mem`) နှင့် EXPLAIN Analysis

Vector index build throughput အတွက် `maintenance_work_mem` နှင့် `max_parallel_maintenance_workers` settings များ၏ သက်ရောက်မှုကို သုံးသပ်ပြီး vector query ၏ `EXPLAIN (ANALYZE)` execution plan ကို parse လုပ်ပါ။

**Hints:** Memory allocation မလုံလောက်ပါက index build သည် disk-spill ဖြစ်ပေါ်ပြီး performance သိသိသာသာ ကျဆင်းသည်။ Execution plan တွင် Index Scan node type နှင့် filter placement ကို စစ်ဆေးပါ။

**Expected behavior:** Execution plan မှ vector index အသုံးပြုမှုနှင့် post-filter overhead ကို ဖော်ထုတ်နိုင်ပြီး build performance အတွက် memory/parallelism recommendations ပေးနိုင်ရမည်။
