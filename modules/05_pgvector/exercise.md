## လေ့ကျင့်ခန်း ၁ — vector column ဆောက်တာ

ရောင်းစာအဖြစ် `chunks` table မှာ id, content, embedding column သုံးခုပါအောင် SQL ရေးပါ။ embedding က 768 dimension, cosine distance နဲ့ တွက်မယ်လို့ ယူဆပါ (assume)။

**Hints:** dimension က 123-2000 ထိပဲ pgvector က ထောက်ပံ့ပါတယ်။ cosine သုံးမယ်ဆိုရင် vector value တွေကို normalize လုပ်ဖို့ လိုပါတယ်။ extension ကို `CREATE EXTENSION vector;` နဲ့ အရင် enable လုပ်ပါ။

**Expected behavior:** SQL က PostgreSQL မှာ run လို့ရတဲ့ valid statement ဖြစ်ပြီး, embedding column က `vector(768)` type နဲ့ `vector_cosine_ops` operator class ကို သုံးထားပါမယ်။

## လေ့ကျင့်ခန်း ၂ — distance operator သုံးခွဲခြားခြင်း

အောက်က query သုံးခုမှာ `<->`, `<=>`, `<#>` သုံးပြီး ဘယ်အချိန် ဘယ် operator ကို သုံးသင့်လဲဆိုတာ ရှင်းပါ။

```sql
SELECT content FROM chunks
ORDER BY embedding <=> '[0.1,0.2,0.3]'::vector
LIMIT 5;
```

**Hints:** `<->` က L2 distance, `<=>` က cosine distance, `<#>` က negative inner product ပါ။ inner product အတွက် သီးသန့် operator class တစ်ခု ရှိပါတယ်။

**Expected behavior:** ဘယ် operator ကဘယ် distance နဲ့ တူညီကြောင်း, normalize လုပ်ထားတဲ့ vector တွေမှာ L2 နဲ့ cosine ရလဒ်တွေ ဆက်စပ်ကြောင်း ရှင်းပြနိုင်ရပါမယ်။

## လေ့ကျင့်ခန်း ၃ — စာပိုဒ်ရှေ့ပိုင်းအတွက် RRF fusion (Python)

ကိုယ်တိုင်ရေးတဲ့ brute-force cosine ranking တစ်ခုနဲ့ စာသား keyword ranking တစ်ခုကို Reciprocal Rank Fusion (RRF) နဲ့ ပေါင်းပါ။ rank တွေက deterministic ဖြစ်ရပါမယ်။

**Hints:** RRF formula က `1 / (k + rank)` ပါ, k=60 ယူဆပါ။ ranking နှစ်ခုလုံးကို standard-library Python (`math`, `statistics` စတာတွေ) နဲ့ပဲ ရေးပါ။ runtime မှာ database ချိတ်စရာ မလိုပါ။

**Expected behavior:** fusion ရလဒ်က input ranking နှစ်ခုလုံးရဲ့ အားသာချက်တွေ ရောနေပြီး, ရလဒ်က ထပ်ခါထပ်ခါ run ရင် တစ်နေရာတည်း ရပါမယ်။

## လေ့ကျင့်ခန်း ၄ — HNSW နဲ့ IVFFlat ရွေးချယ်တာ

million-level chunk တွေအတွက် ဘယ် index ကို ရွေးမလဲ, `m` နဲ့ `ef_construction` တန်ဖိုးတွေကဘယ်လို သက်ရောက်မလဲဆိုတာ ရှင်းပါ။ IVFFlat မှာဆိုရင် `lists` တန်ဖိုးနဲ့ `probes` တန်ဖိုးကိုလည်း ဖော်ပြပါ။

**Hints:** IVFFlat က cluster တွေ ခွဲပြီး search တယ်, HNSW က graph layer တွေ ဆောက်တယ်။ IVFFlat က build ကြာတာနည်းပေမယ့် recall က probes ပေးထားမှုအပေါ် မူတည်ပါတယ်။ HNSW က build ကြာပေမယ့် query performance က ပိုသာပါတယ်။ IVFFlat မှာ data အသစ်ထည့်နေရင် cluster တွေ ပျက်နိုင်လို့ retrain လုပ်ဖို့ လိုနိုင်ပါတယ်။

**Expected behavior:** dataset size, query latency tolerance, recall requirement တွေအပေါ် မူတည်ပြီး trade-off တွေကို အကြောင်းပြချက်နဲ့ ရွေးချယ်နိုင်ရပါမယ်။

## လေ့ကျင့်ခန်း ၅ — jsonb metadata နဲ့ GIN index + filtered search

`metadata` jsonb column တစ်ခုထည့်ပြီး, `source` field အပေါ် filter လုပ်တဲ့ vector search query ကို ရေးပါ။ metadata filter အတွက် GIN index တစ်ခုပါ ထည့်ပေးပါ။

```sql
CREATE INDEX ON chunks USING gin (metadata jsonb_path_ops);
```

**Hints:** filter condition က query execution ထဲ ဘယ်နေရာမှာ ပေါ်လာမလဲ စဉ်းစားပါ — pre-filter မဟုတ်ရင် vector index က row တွေ ကျော်ရင်း ဖြတ်သွားနိုင်ပါတယ်။ PostFilter ခံရတဲ့ row တွေများရင် ရလဒ်အရေအတွက် လျော့နိုင်ပါတယ်။

**Expected behavior:** SQL က PostgreSQL + pgvector မှာ valid ဖြစ်ပြီး, filter နဲ့ distance ordering နှစ်ခုလုံး တွဲဆောင်ရွက်နေတာ မြင်ရပါမယ်။

## လေ့ကျင့်ခန်း ၆ — maintenance_work_mem, parallel build, EXPLAIN ဖတ်တာ

Index build တွေမှာ `maintenance_work_mem` တန်ဖိုးနဲ့ `max_parallel_maintenance_workers` တန်ဖိုးတွေကဘယ်လို သက်ရောက်လဲဆိုတာ ရှင်းပြပြီး, vector index scan တစ်ခုရဲ့ `EXPLAIN` output ကို ဖတ်ပါ။

**Hints:** memory ကနောက်မှ တစ်နေရာရာသို့ သွားစောင့်ချင်ပါတယ်။ IVFFlat build မှာ `maintenance_work_mem` က sample data တွေကို memory ထဲ တင်ပါတယ်, HNSW build မှာက graph ကို memory ထဲ ဆောက်ပါတယ်။

**Expected behavior:** HNSW scan မှာ `Index Scan` နဲ့ index name ကို, IVFFlat scan မှာ probe အရေအတွက်ကို plan ထဲ မြင်နိုင်ရပါမယ်။ memory setting တွေ တိုးလိုက်ရင် build ဖြစ်စဉ်က ဘယ်အပိုင်း တက်လာနိုင်လဲဆိုတာ ခန့်မှန်းပြနိုင်ရပါမယ်။
