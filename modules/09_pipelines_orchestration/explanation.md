# 09_pipelines_orchestration

## ၁။ Batch နှင့် Streaming Ingestion

### ဘာကို ဆိုလိုတာလဲ

Batch ingestion ဆိုတာ အချက်အလက်တွေကို အချိန်တစ်ခုအတွင်း စုစည်းပြီးမှ အစုအဝေး (chunk) အတွက် တစ်ခါတည်း ingest လုပ်တာပါ။ ဥပမာ — ညတိုင်း ည ၁၂ နာရီမှာ နောက်ဆုံး ၂၄ နာရီရဲ့ document အသစ်တွေကို စုပြီး chunking → embedding → index ထဲ တင်တဲ့ နည်း။ Streaming ingestion ကတော့ အချက်အလက်ရလိုက်တာနဲ့ ချက်ချင်း (near-real-time) ကိုင်တွယ်တဲ့ နည်းပါ။ Kafka topic တစ်ခုက စာပိုဒ်အသစ်တွေ ရောက်လာရင် consumer က ချက်ချင်း embed လုပ်ပြီး vector store ထဲ ရေးတာမျိုး။ Vector search pipeline မှာ နှစ်မျိုးလုံး အသုံးဝင်ပြီး၊ RAG system တစ်ခုရဲ့ freshness requirement အပေါ် မူတည်ပြီး ရွေးချယ်ကြပါတယ်။

ဒုတိယ အချက်အနေနဲ့ — ingestion ဆိုတာ အလွယ်ပြောရရင် "raw source → cleaned text → chunks → embeddings → vector index" ဆိုတဲ့ အဆင့်ဆင့် လမ်းကြောင်းကို ဆိုလိုတာပါ။ Batch နဲ့ streaming က ဒီလမ်းကြောင်းကို ဘယ်လို အချိန်အတိုင်းအတာနဲ့ ဖြတ်သန်းမလဲဆိုတဲ့ ခြားနားမှုသာ ဖြစ်ပါတယ်။

### ဘာကြောင့် လဲ

RAG application တွေရဲ့ အဖြေအရည်အသွေးက အချက်အလက် အသစ်နဲ့ မက်ချနေမှုပေါ် မူတည်လို့ပါ။ သတင်းစာ ရှာဖွေရေး system တစ်ခုမှာ ၃ နာရီအရင် ထွက်တဲ့ သတင်းကို အဖြေထဲ ထည့်ပြရမယ်ဆိုရင် streaming လိုအပ်ပါတယ်။ တစ်ဖက်မှာ တရားရုံးစာချုပ်စာတမ်း ဟောင်းတွေရဲ့ သမိုင်းဖိုင်တွေကို တစ်ကြိမ်တည်း တင်ရတဲ့ system မှာတော့ batch က ရိုးရှင်းပြီး ထိန်းသိမ်းရလွယ်ပါတယ်။

Cost ကလည်း အကြောင်းရင်းတစ်ခုပါ။ Streaming pipeline တစ်ခုက infrastructure (broker, consumer group, monitoring) ပို၍ ရှုပ်ထွေးစေပြီး ထိန်းသိမ်းစရာ ပိုလိုပါတယ်။ Batch ကတော့ တစ်ညတည်း run ရင် ရှုပ်ထွေးမှုနည်းပါတယ်။ ဒါကြောင့် လိုအပ်ချက်အစစ်အလမ်း မရှိဘဲ streaming ကို ရွေးလိုက်တာက over-engineering ဖြစ်စေနိုင်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

Batch ingestion ရဲ့ အလုပ်လုပ်ပုံ အဆင့်တွေက —

1. Scheduler (ဥပမာ Airflow) က သတ်မှတ်ချိန်မှာ DAG run ကို စတင်စေတယ်။
2. Source ထဲက last watermark နောက်ပိုင်းက အသစ် records တွေကို ရွေးယူတယ်။
3. Records တွေကို သန့်စင်ပြီး chunk အလိုက် ဖြတ်တယ်။
4. Chunk တွေကို embedding model နဲ့ vector အဖြစ်ပြောင်းတယ် (batch API call နဲ့ cost သက်သာစေတယ်)။
5. `pgvector` table ထဲ `INSERT ... ON CONFLICT DO UPDATE` (upsert) နဲ့ ရေးသွင်းတယ်။
6. အောင်မြင်မှုကို checkpoint / watermark အနေနဲ့ သိမ်းတယ်။

Streaming ingestion ကတော့ —

1. Producer က event ကို topic ထဲ တင်တယ် (document id, content, version)။
2. Consumer group က partition တွေကနေ တစ်လှည့်စီ ဖတ်တယ်။
3. တစ် event စီကို clean → chunk → embed လုပ်တယ်။
4. Upsert လုပ်ပြီးမှ offset ကို commit တယ် — commit မလုပ်ခင် crash ဖြစ်ရင် အနည်းဆုံး တစ်ခါ ပြန်ဖတ်ရပြီး idempotency က ကာကွယ်ပေးတယ်။

### ဥပမာ

အောက်က ဥပမာက batch နဲ့ streaming ရဲ့ watermark-based dedupe သဘောကို pure Python နဲ့ ပြထားတာပါ။ တစ်ကြိမ်ထက်ပိုပြီး run လုပ်ပေမယ့် duplicate မဝင်စေတဲ့ သဘောကို တွေ့ရပါမယ်။

```python
from typing import Dict, List, Tuple

# Simulate a batch that was already processed, keyed by watermark id
processed: Dict[str, str] = {"doc_1": "chunk A", "doc_2": "chunk B"}

def run_batch(new_items: List[Tuple[str, str]]) -> List[str]:
    """Insert only items whose id we have never seen. Returns inserted ids."""
    inserted = []
    for doc_id, text in new_items:
        if doc_id not in processed:
            processed[doc_id] = text          # upsert-like guard
            inserted.append(doc_id)
    return inserted

first = run_batch([("doc_1", "old"), ("doc_3", "new text")])
second = run_batch([("doc_3", "replayed"), ("doc_4", "later text")])
print("batch 1 inserted:", first)
print("batch 2 inserted:", second)
print("store size:", len(processed))
# Expected output:
# batch 1 inserted: ['doc_3']
# batch 2 inserted: ['doc_4']
# store size: 4
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

လက်တွေ့ pipeline တစ်ခု run ဖြစ်နိုင်တဲ့ အခြေအနေက — scheduler ပျက်တာ၊ pod restart ဖြစ်တာ၊ network hiccup ဖြစ်တာ — အမြဲရှိနေပါတယ်။ ဒါကြောင့် ingestion ကို ဒီဇိုင်းချတဲ့အခါ "run နှစ်ခါလုပ်ရင် ဘာဖြစ်မလဲ" ဆိုတဲ့ မေးခွန်းကို အရင်ဖြေရပါမယ်။ Batch နဲ့ streaming ကို ရွေးချယ်တာကလည်း စိတ်ကြိုက်မဟုတ်ဘဲ SLA (ဥပမာ "စာရွက်အသစ် ရှာဖွေရမှုမှာ ၅ မိနစ်အတွင်း ပေါ်ရမယ်") ကနေ ပြန်ဆွဲထုတ်သင့်တဲ့ ဆုံးဖြတ်ချက်ပါ။ ဒီ module ရဲ့ နောက်ပိုင်း sections တွေက ဒီလို crash-safe ဖြစ်စေတဲ့ pattern (idempotency, backfill, retry) တွေကို အသေးစိတ် ဖော်ပြပါလိမ့်မယ်။

## အနှစ်ချုပ်

- Batch ingestion က အချိန်အတိုင်းအတာ သတ်မှတ်ပြီး အစုလိုက် ကိုင်တွယ်ပြီး၊ streaming က event ရောက်တဲ့အတိုင်း ချက်ချင်း ကိုင်တွယ်တယ်။
- ရွေးချယ်မှုက freshness SLA နဲ့ cost/freshness tradeoff အပေါ် မူတည်သင့်တယ်။
- နှစ်မျိုးလုံးရဲ့ အသုံးအများဆုံး (အဓိက) pattern က watermark + upsert ဖြစ်တယ်။
- Batch embedding call တွေက per-item call ထက် cost သက်သာစေတယ်။
- Streaming မှာ offset commit ကို upsert အောင်မြင်မှု နောက်မှ လုပ်သင့်တယ်။
- "Run နှစ်ခါလုပ်ရင် ဘာဖြစ်မလဲ" ဆိုတဲ့ မေးခွန်းက ingestion design ရဲ့ ပထမဆုံး စစ်ဆေးချက်ပါ။

## ၂။ Idempotent ပြန်လုပ်နိုင်မှု၊ Backfill နှင့် Rate Limit

### ဘာကို ဆိုလိုတာလဲ

Idempotent ဖြစ်တယ်ဆိုတာ လုပ်ငန်းကို တစ်ခါလုပ်လည်း ဒီထက် ပိုလုပ်လည်း ရလဒ်တစ်ခုတည်း ဖြစ်တယ်ဆိုတဲ့ သဘောတရားပါ။ Vector ingestion မှာ ဒါက document id (သို့) content hash ကို key အဖြစ်သုံးပြီး upsert လုပ်တဲ့ နည်းနဲ့ ရရှိပါတယ်။ Backfill ကတော့ အတိတ်ကာလက (ဟောင်းနွမ်းတဲ့) အချိန်က အချက်အလက်တွေ (ဥပမာ embedding model ပြောင်းလို့ အကုန်လုံး ပြန် embed လုပ်ရမယ့်အခါ) ကို အရင်ကတည်းက ပြန်ဖြည့်တဲ့ လုပ်ငန်းပါ။ Rate limit ကတော့ upstream အချက်အလက် source (ဒါမှမဟုတ် embedding API) ကနေ အလွန်မြန်တဲ့ တောင်းခံမှုကို တားဆီးပေးတဲ့ ကိရိယာပါ။

သုံးခုလုံးက pipeline တစ်ခုရဲ့ "ဘေးအန္တရာယ် ကာကွယ်ရေး" လို့ မြင်နိုင်ပါတယ်။ Idempotency က မတော်တဆ နှစ်ခါ run ဖြစ်တာကို၊ backfill က သမိုင်းဖိုင် ပြန်ဖြည့်ချင်တာကို၊ rate limit က provider quota ကျော်လို့ အမှားဖြစ်တာကို ကာကွယ်ပေးပါတယ်။

### ဘာကြောင့် လဲ

Distributed system တစ်ခုမှာ "တစ်ခါတည်း အတိအကျ တစ်ခါ run ရမယ်" ဆိုတဲ့ အာမခံချက် မရနိုင်ပါ။ Scheduler က job ကို run နှစ်ခါ start လုပ်တတ်သလို၊ worker က အလုပ်အဆင်ပြေပြီးလို့ အဖြေပြန်ပို့ခင်မှာ crash ဖြစ်နိုင်ပါတယ်။ Idempotency မရှိရင် ဒီလို ဖြစ်ရပ်တွေက duplicate chunks တွေ vector table ထဲ ဝင်လာပြီး search result မှာ စာပိုဒ်တူတွေ ထပ်နေစေပါတယ်။

Backfill ကလည်း model upgrade တိုင်း လိုအပ်ပါတယ်။ Embedding model ကောင်းလာတဲ့အခါ အရင် model နဲ့ embed လုပ်ထားတဲ့ vector တွေနဲ့ အသစ်နဲ့ embed လုပ်ထားတဲ့ vector တွေက တစ်ခုနဲ့တစ်ခု ကွာဟတဲ့ space မှာ နေကြလို့ ရှာဖွေရမှု မှားယွင်းစေပါတယ်။ Rate limit ကတော့ OpenAI-style embedding API တွေမှာ requests-per-minute ကန့်သတ်ချက်ရှိလို့၊ ကန့်သတ်ချက်ကို မထိန်းပဲ million chunks တွေကို ပစ်လိုက်ရင် တစ်ဝက်လောက်မှာ HTTP 429 error တွေနဲ့ ရပ်တန့်သွားစေပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

Idempotent ingestion တည်ဆောက်တဲ့ အဆင့်တွေက —

1. Document တစ်ခုစီအတွက် stable key တစ်ခု သတ်မှတ်တယ် — `doc_id + chunk_index + embedding_version` က လုံလောက်တဲ့ composite key ဖြစ်တတ်တယ်။
2. `pgvector` မှာ unique constraint တင်ပြီး `INSERT ... ON CONFLICT (key) DO UPDATE SET embedding = EXCLUDED.embedding` နဲ့ upsert လုပ်တယ်။
3. Run အတွင်း အလုပ်ဖြစ်ခဲ့တဲ့ key တွေကို checkpoint အနေနဲ့ ရေးမှတ်ထားခြင်း (သို့) run ရဲ့ input set ကို pure ဖြစ်စေခြင်းနဲ့ တစ်ခါကိုင်တွယ်တဲ့ သဘော ထိန်းတယ်။

Backfill အတွက် —

1. Backfill လုပ်မယ့် အကွက် (ဥပမာ `created_at < cutoff` ဖြစ်တဲ့ rows) ကို သတ်မှတ်တယ်။
2. Rows တွေကို batch အလိုက် ခွဲပြီး အသစ် model နဲ့ ပြန် embed လုပ်တယ်။
3. အသစ် version ကို အရင် version နဲ့ အတူ dual-write (section 4 မှာ အသေးစိတ်) လုပ်ပြီး ရောက်ရှိမှုကို စစ်ဆေးပြီးမှ ရှေ့ဆက်တယ်။

Rate limit အတွက် —

1. Provider doc ကနေ တရားဝင် quota (ဥပမာ tokens-per-minute) ကို ဖတ်ယူတယ်။
2. Token-bucket (သို့) fixed-window counter နဲ့ sender ကို throttle လုပ်တယ်။
3. Server က `Retry-After` header ပြန်ရင် အဲဒီတန်ဖိုးအတိုင်း စောင့်ပြီး ပြန်ကြိုးစားတယ်။

### ဥပမာ

Token bucket သဘောကို တကယ် runtime နဲ့ စမ်းစရာ မလိုပါဘဲ၊ စိတ်ကူးယဉ် အခြေအနေတွေနဲ့ simulate လုပ်ပြီး တွေ့နိုင်ပါတယ် — capacity 10 token၊ refill rate 2 tokens/unit-time ရှိတဲ့ bucket ကို request ၁၅ ခု ဆက်တိုက် ပို့လိုက်ရင် ပထမ ၁၀ ခု ဖြတ်ပြီး ကျန် ၅ ခုက queue ထဲ စောင့်ရပါတယ်။ Idempotency အတွက်တော့ content hash က `sha256(normalized_text)` ကို သုံးပြီး စာသားတူ စာပိုဒ်နှစ်ခုက အတူတူ hash ထွက်တာကို dedupe အဖြစ် အသုံးချနိုင်ပါတယ်။

```sql
-- Idempotent upsert for a pgvector chunk table (illustrative, never executed)
INSERT INTO chunks (doc_id, chunk_index, embed_version, content_hash, embedding)
VALUES ($1, $2, $3, $4, $5)
ON CONFLICT (doc_id, chunk_index, embed_version)
DO UPDATE SET content_hash = EXCLUDED.content_hash,
              embedding    = EXCLUDED.embedding;
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Production vector pipeline တွေမှာ အဖြစ်အများဆုံး incident က logic မှားတာ မဟုတ်ဘဲ "မလိုလားအပ်ဘဲ နှစ်ခါ run သွားတာ" နဲ့ "quota ကျော်သွားတာ" ပါ။ Idempotent upsert တစ်ခုတည်းနဲ့ ပထမ အမျိုးအစားရဲ့ ဒဏ်ရာ အများစုကို ရှောင်နိုင်ပါတယ်။ Backfill ကတော့ embedding model upgrade လုပ်တိုင်း မဖြစ်မနေ လိုအပ်တဲ့ လုပ်ငန်းဖြစ်ပြီး၊ ကြိုပြင်ဆင်မထားရင် အသစ်-အရင် vector တွေ ရောနေတဲ့ index တစ်ခုကို ဖန်တီးမိပါတယ်။ Rate limit ကတော့ cost spike နဲ့ provider ban နှစ်မျိုးစလုံးကို တားဆီးပေးလို့၊ batch size နဲ့ concurrency ကို quota အတွင်း ကျစေဖို့ အရင်ဆုံး ချိန်ညှိရပါမယ်။

## အနှစ်ချုပ်

- Idempotency က "ဘယ်နှစ်ခါ run လုပ်လည်း ရလဒ်တစ်ခုတည်း" ဆိုတဲ့ အာမခံချက်ပါ။
- `ON CONFLICT DO UPDATE` (upsert) နဲ့ stable composite key က idempotent ingestion ရဲ့ အခြေခံကျောရိုးပါ။
- Backfill က embedding version ပြောင်းလိုက်တဲ့အခါ သမိုင်းဖိုင်တွေကို ပြန်ဖြည့်တဲ့ လုပ်ငန်းပါ။
- Rate limit က provider quota နဲ့ ကိုက်အောင် throttle လုပ်ပေးတဲ့ ကာကွယ်ရေးကိရိယာပါ။
- Quota ကို provider doc ကနေ ဖတ်ယူပြီး bucket ကို အဲဒီတန်ဖိုးအတိုင်း ချိန်ညှိပါ။
- ဒီသုံးခုက pipeline reliability ရဲ့ အခြေခံအဆောက်အအုံ (building blocks) တွေပါ။

## ၃။ Dead-letter နှင့် Retry၊ Change Data Capture အခြေခံ

### ဘာကို ဆိုလိုတာလဲ

Dead-letter queue (DLQ) ဆိုတာ pipeline က အလုပ်မလုပ်နိုင်တဲ့ records (ဥပမာ — corrupt text၊ embedding API က အမြဲ reject လုပ်တဲ့ input) တွေကို ခွဲထုတ်သိမ်းထားတဲ့ နေရာပါ။ Main flow က ဒီ records တွေကြောင့် တစ်လုံးလုံး ရပ်မသွားစေဘဲ၊ နောက်မှာ သီးခြား စစ်ဆေးပြီး ပြင်ဆင်နိုင်ပါတယ်။ Retry က ယာယီ အမှား (transient error) ဖြစ်နိုင်တဲ့ ကြိုးစားမှုကို ထပ်မံ ကြိုးစားတဲ့ (ပြန်လုပ်တဲ့) နည်းလမ်းပါ — ဒါပေမယ့် ရလဒ်တွေက သေချာရမယ်။ Change Data Capture (CDC) ကတော့ source database ရဲ့ ပြောင်းလဲမှု (delete, update) တွေအပါအဝင် အပြောင်းအလဲ အားလုံးကို log အလိုက် ဖမ်းယူတဲ့ နည်းပါ။

သုံးခုလုံးက "အချက်အလက် ပိတ်မိတာနဲ့ ဆုံးရှုံးတာ" ကို ဖြေရှင်းပေးတဲ့ ကိရိယာတွေပါ။ DLQ က ပိတ်မိတာကို ကူးယူဖို့၊ retry က ယာယီပျက်တာကို ပြန်လုပ်ပေးဖို့၊ CDC က delete/update တွေ vector index ထဲ လိုက်မနေစေဖို့ အသုံးဝင်ပါတယ်။

### ဘာကြောင့် လဲ

Streaming ingestion မှာ record တစ်ခုက encoding ပျက်နေတာ (သို့) content က လက်ခံနိုင်တဲ့ input limit ထက် ကြီးနေတာကို တွေ့ရတတ်ပါတယ်။ ဒီ record တစ်ခုကြောင့် consumer က crash လုပ်ပြီး offset ရပ်နေရင်၊ နောက်က အချက်အလက်အသစ် အားလုံးက တန်းစီနေမယ်။ DLQ က ဒီလို "တစ်ခုကြောင့် အားလုံး ရပ်တာ" (poison-pill) ပြဿနာကို ဖြေရှင်းပေးပါတယ်။

CDC က RAG correctness အတွက် သိသိသာသာ အရေးကြီးပါတယ်။ စာရွက်တစ်ခုကို source မှာ ပြင် (သို့) ပယ်ဖျက်လိုက်ရင် vector index ထဲက အဲဒီ chunk တွေက ရောက်နေတုန်းရှိပါတယ်။ ရှာဖွေမှုက ပယ်ဖျက်ပြီး (သို့) ခေတ်မမီတော့တဲ့ (obsolete) ဖြစ်နေတဲ့ အချက်အလက်ကို အဖြေထဲ ထည့်ပေးရင် RAG ရဲ့ ယုံကြည်စိတ်ချရမှု ကျဆင်းသွားပါတယ်။ Polling-based sync က delete တွေကို မမြင်နိုင်လို့၊ CDC (ဥပမာ logical replication slot က `DELETE` event ပေးတာ) က ဒီအခက်အခဲကို ဖြေရှင်းပေးပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

Retry မှာ သတိထားရမယ့် အချက်တွေက —

1. Error က permanent (ဥပမာ 400 Bad Request) လား transient (ဥပမာ 429, 503) လား ခွဲရတယ် — permanent ကို retry လုပ်တာက အချိန်နဲ့ quota ဖြုန်းတာပါ။
2. Transient အတွက် exponential backoff (`delay = base * 2**attempt`) သုံးပြီး ကြိုးစားမှု အရေအတွက် ကန့်သတ်ချက် (ဥပမာ ၅ ခါ) နဲ့ ရပ်တယ်။
3. ကြိုးစားမှု အားလုံး ကုန်သွားရင် record ကို DLQ ထဲ ရွှေ့ပြီး pipeline က ရှေ့ဆက်တယ်။
4. DLQ ထဲက records တွေကို နောက်ထပ် job တစ်ခုက စစ်ဆေးပြီး ပြင်ဆင်ပြီးမှ ပြန် feed လုပ်တယ်။

CDC အတွက် အဆင့်တွေက —

1. Source PostgreSQL မှာ logical replication slot တစ်ခု ဖန်တီးတယ်။
2. Consumer က slot ကနေ `INSERT`/`UPDATE`/`DELETE` events တွေကို ဖတ်တယ် (ဥပမာ Debezium သို့ `pgoutput` plugin)။
3. `INSERT`/`UPDATE` က chunk → embed → upsert path ကို၊ `DELETE` က vector table ထဲက `doc_id` အလိုက် `DELETE` လုပ်တဲ့ path ကို ခေါ်တယ်။
4. Applied position ကို checkpoint လုပ်ပြီး crash ဖြစ်ရင် အဲဒီနေရာကနေ ပြန်စတင်တယ်။

### ဥပမာ

ဥပမာ — စာရွက်တစ်ခု source မှာ အပြီးအပိုင် ဖျက်ပစ်ခြင်း (hard delete) ဖြစ်ပြီးနောက်၊ CDC က `DELETE` event ကို ဖမ်းပြီး vector index ထဲက အဲဒီ document ရဲ့ chunk ၁၂ ခု အားလုံးကို ရှင်းလင်းပေးတယ်။ CDC မရှိရင် အဲဒီ chunk ၁၂ ခုက index ထဲ ကျန်ရှိပြီး ရှာဖွေမှုတွေမှာ "ဖျက်ပြီး စာရွက်" ကနေ အချက်အလက် ယူလာနိုင်ပါတယ်။ Retry ဘက်ကတော့ — embedding API က ၅၀၃ ပြန်ရင် ၂ စက္ကန့်၊ ၄ စက္ကန့်၊ ၈ စက္ကန့် ကြာချိန် နောက်ဆုတ်ပြီး ထပ်ကြိုးစားပြီး၊ နောက်ဆုံး ကြိုးစားမှုအထိ မရရင် DLQ table ထဲ record ထည့်ပြီး run log မှာ warning တင်တာမျိုး ဖြစ်ပါတယ်။

```sql
-- Deleting all chunks of a removed source document (illustrative)
DELETE FROM chunks WHERE doc_id = $1;
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Operation team တစ်ခုက pipeline က ၉၉.၉% record ရောက်တယ်ဆိုတာကို ဘယ်လို သိမလဲဆိုတော့ — ကျန် ၀.၁% က ဘယ်နေရာမှာ ရှိလဲ ဆိုတာကို မြင်နိုင်ရပါမယ်။ DLQ က ဒီမြင်နိုင်စွမ်းကို ပေးတဲ့ ကိရိယာပါ။ Retry policy မရှိတဲ့ pipeline က transient network အမှားတစ်ခုကြောင့်ပဲ လက်တွေ့ ရှုပ်ထွေးနေတတ်ပြီး၊ retry က ရိုးရိုးနဲ့ ပြန်ပေးလိုက်ရုံနဲ့ ရသွားတာမျိုး ရှိပါတယ်။ CDC ကတော့ RAG ရဲ့ "အဖြေကို source နဲ့ လိုက်နေအောင် ထိန်းပေးတဲ့" နောက်ဆုံး ကာကွယ်ရေးလိုင်းပါ — index နဲ့ source ကြား ကွဲလွဲမှုကို နာရီပိုင်း (သို့) မိနစ်ပိုင်းအတွင်း မြင်နိုင်စေပါတယ်။

## အနှစ်ချုပ်

- DLQ က ကိုင်တွဲလို့ မရတဲ့ records တွေကို ခွဲထုတ်သိမ်းပြီး main flow က ရှေ့ဆက်စေပါတယ်။
- Poison-pill record တစ်ခုကြောင့် တစ်လုံးလုံး ရပ်တာကို DLQ က ကာကွယ်ပေးပါတယ်။
- Permanent error နဲ့ transient error ကို ခွဲပြီး၊ transient ကိုပဲ exponential backoff နဲ့ retry လုပ်သင့်ပါတယ်။
- Retry အရေအတွက် ကန့်သတ်ချက် ရှိဖို့ လိုအပ်ပြီး ကုန်သွားရင် DLQ ထဲ ရွှေ့ပါ။
- CDC က `DELETE`/`UPDATE` events တွေအထိ ဖမ်းပြီး vector index ကို source နဲ့ sync ဖြစ်စေပါတယ်။
- Polling က delete ကို မမြင်နိုင်လို့ correctness အတွက် CDC က ပို ယုံကြည်စိတ်ချရပါတယ်။

## ၄။ Embedding Version Migration: Dual-write၊ Shadow Index၊ Cut-over

### ဘာကို ဆိုလိုတာလဲ

Embedding version migration ဆိုတာ embedding model (သို့) model ရဲ့ parameter တွေ ပြောင်းလိုက်တဲ့အခါ vector space တစ်ခုလုံးကို ပြောင်းရတဲ့ လုပ်ငန်းကို ဆိုလိုပါတယ်။ Dual-write က အသစ် document တိုင်းကို version ဟောင်းနဲ့ သစ် နှစ်မျိုးလုံး embed လုပ်ပြီး နှစ်ခုလုံးထဲ ရေးသွင်းတဲ့ အဆင့်ပါ။ Shadow index က version သစ် vector တွေကို production ရှာဖွေမှုက မသုံးရသေးဘဲ နောက်ကွယ်မှာ တည်ဆောက်နေတဲ့ index ပါ။ Cut-over က shadow index ကို အမှန်ခံ (authoritative) အဖြစ် ကူးပြောင်းပြီး version ဟောင်းကို အနီးစပ်ဆုံး ရပ်တဲ့ အဆင့်ပါ။

ဒီသုံးဆင့်လမ်းကြောင်းက "production ကို မရပ်ပဲ model အသစ်ကို လုံခြုံစွာ ကူးပြောင်းတဲ့" pattern ပါ။ တစ်ဆင့်ချင်း ကူးပြီး တစ်ဆင့်ချင်း စစ်ဆေးလို့ရတဲ့ အားသာချက် (advantage) ရှိပါတယ်။

### ဘာကြောင့် လဲ

Embedding တွေက model နဲ့ ချိတ်နေလို့၊ version မတူတဲ့ vector တွေက numeric space မှာ တိုက်ရိုက် နှိုင်းယှဉ်လို့ မရပါ။ `text-embedding-3-small` ရဲ့ vector တစ်ခုနဲ့ `all-MiniLM-L6-v2` ရဲ့ vector တစ်ခုကို cosine similarity နဲ့ နှိုင်းရင် အဓိပ္ပာယ်မရှိတဲ့ တန်ဖိုး ထွက်ပါတယ်။ ဒါကြောင့် model ပြောင်းရင် index တစ်ခုလုံးကို ပြန် embed လုပ်ရပြီး၊ ဒီလုပ်ငန်းက နာရီ (သို့) ရက်ပိုင်း ကြာတတ်ပါတယ်။ ဒီအတွင်း production ရှာဖွေမှုက ရပ်မနေနိုင်လို့၊ တဖြည်းဖြည်း ကူးပြောင်းတဲ့ နည်း လိုအပ်ပါတယ်။

ဒုတိယ အကြောင်းရင်းက risk ပါ။ Model အသစ်က paper အရ ကောင်းတယ်ဆိုပေမယ့် ကိုယ့် data (domain) ပေါ်မှာတော့ ဆိုးသွားနိုင်ပါတယ်။ Shadow index က version သစ်ရဲ့ ရှာဖွေမှု အရည်အသွေးကို production မထိခိုက်စေဘဲ စစ်ဆေးခွင့်ပေးလို့၊ အဆင်မပြေရင် ပြန်ဆုတ်ခွာနိုင်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

1. **ကြေညာချက် (announce)။** Table schema မှာ `embed_version` column ထည့်ပြီး တစ် row စီက version ဘယ်ဟာနဲ့ embed လုပ်ထားလဲ မှတ်တမ်းတင်စေတယ်။
2. **Dual-write စတင်။** အသစ် ingest ဖြစ်တဲ့ document တိုင်းကို version နှစ်ခုလုံးနဲ့ embed လုပ်ပြီး နှစ်ခုလုံးထဲ ရေးသွင်းတယ် — cost က တစ်ဆူနှစ်ဆူ ဖြစ်သွားပေမယ့် ကာလတိုတိုအတွက်သာပါ။
3. **Backfill shadow index။** Section 2 မှာ ဖော်ပြခဲ့တဲ့ backfill နည်းနဲ့ သမိုင်းဖိုင် document တွေကို version သစ်နဲ့ ပြန် embed လုပ်ပြီး shadow index ထဲ ဖြည့်တယ်။
4. **Offline evaluation။** Golden query set တစ်ခု (သိချာတဲ့ မေးခွန်း + မျှော်လင့်တဲ့ document) နဲ့ version သစ် index ကို run ပြီး version ဟောင်းနဲ့ နှိုင်းယှဉ်တယ်။
5. **Cut-over။** Application config မှာ ရှာဖွေမှုကို shadow index (သို့) `embed_version = 'new'` filter ဘက် ပြောင်းလိုက်တယ်။ Feature flag နဲ့ ပြောင်းရင် တစ်နာရီအတွင်း ပြန်ပြောင်းလို့ရပါတယ်။
6. **ရှင်းလင်း။** Version ဟောင်း vector တွေကို ရှာဖွေမှု အားလုံးက new side ကို ရောက်တယ်ဆိုတဲ့ အာမခံချက်ရပြီးမှ၊ ရက်သတ္တပတ်ပိုင်းအတွင်း delete လုပ်ပြီး storage ပြန်ရပါတယ်။

### ဥပမာ

ကိုယ့် pipeline မှာ `embed_version = 'v1'` နဲ့ embed လုပ်ထားတဲ့ chunk ၈ သန်းရှိတယ်ဆိုပါစို့။ Model အသစ် `v2` ကို ကူးပြောင်းချင်ရင် — dual-write စတင်တဲ့နေ့မှစပြီး အသစ် document တိုင်းက `v1` နဲ့ `v2` vector နှစ်ခု ရတယ်။ နောက် ရက်သတ္တပတ်အတွင်း backfill job က သမိုင်းဖိုင် ၈ သန်းကို batch လိုက် ပြန် embed လုပ်တယ် — quota အတွင်း ချိန်ညှိထားတဲ့ batch size အလိုက် ဖြည့်သွားတယ်။ Shadow index ပြည့်ရင် golden query ၃၀၀ နဲ့ offline evaluation လုပ်ပြီး၊ ရလဒ်က ကျေနပ်ဖွယ် ဖြစ်မှ feature flag ကို `v2` ဘက် ဖွင့်ပေးတယ်။ Query log က `v2` ဘက် ကူးသွားတာ သေချာရင် `v1` rows တွေကို batch delete လုပ်ပြီး migration ပြီးပါတယ်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Model upgrade က RAG system တစ်ခုရဲ့ အကြီးမားဆုံး အန္တရာယ်အရှိဆုံး အပြောင်းအရွှေ့ပါ။ တစ်ညတည်း "ရုပ်ပြောင်း" (big-bang) လုပ်ပြီး အားလုံးကို အသစ် model နဲ့ ပြန် embed လုပ်ချင်းက production ရှာဖွေမှုကို နာရီပိုင်း/ရက်ပိုင်း ပျက်စေတတ်ပြီး၊ အသစ် model က မကောင်းဘူးဆိုရင် ပြန်ရမယ့်လမ်း မရှိတော့ပါ။ Dual-write + shadow + cut-over လမ်းကြောင်းက အဆင့်တိုင်းမှာ "မကောင်းရင် ရပ်" ဆိုတဲ့ ရွေးချယ်စရာ ချန်ပေးလို့၊ operation risk ကို သိသိသာသာ လျှော့ချပေးပါတယ်။ Storage cost က migration ကာလအတွင်း နှစ်ဆူတက်တာက သေချာစွာ တွက်နိုင်တဲ့၊ ယာယီ ကုန်ကျစရာပါ။

## အနှစ်ချုပ်

- Model ပြောင်းရင် vector space တစ်ခုလုံး မသင့်တော်တော့လို့ index တစ်ခုလုံး ပြန် embed လုပ်ရပါတယ်။
- `embed_version` column က row တိုင်းရဲ့ model lineage ကို မှတ်တမ်းတင်ပေးပါတယ်။
- Dual-write က migration ကာလအတွင်း အသစ် data နှစ် version လုံးထဲ ရောက်စေပါတယ်။
- Shadow index က version သစ်ကို production မထိခိုက်စေဘဲ offline evaluation လုပ်ခွင့်ပေးပါတယ်။
- Cut-over ကို feature flag နဲ့ လုပ်ရင် လျင်မြန်စွာ ပြန်ဆုတ်ခွာနိုင်ပါတယ်။
- Version ဟောင်း vector တွေကို အာမခံချက် ရပြီးမှ batch delete လုပ်ပါ။

## ၅။ DAG ဒီဇိုင်း (Airflow / Dagster သဘောတရား)

### ဘာကို ဆိုလိုတာလဲ

DAG (Directed Acyclic Graph) ဆိုတာ လုပ်ငန်းတာဝန်များ (task) တွေရဲ့ မှီခိုမှု (dependencies) ကို မကွေးတဲ့ graph အဖြစ် ကြေငြာတဲ့ နည်းပါ — "A ပြီးမှ B စ" ဆိုတဲ့ ချိတ်ဆက်မှုကို code ထဲ ရေးထားတာပါ။ Airflow နဲ့ Dagster က ဒီ DAG တွေကို schedule လုပ်၊ run လုပ်၊ စောင့်ကြည့် (monitor) လုပ်ပေးတဲ့ orchestrator နှစ်ခုပါ။ Vector search pipeline တစ်ခုက သာမန် script (plain script) ထက် DAG အဖြစ် ရေးရင် — extract → clean → chunk → embed → upsert ဆိုတဲ့ အဆင့်တွေရဲ့ ဆက်နွယ်မှု ကို framework က နားလည်ပြီး ပျက်တဲ့နေရာကို ပြန်စဖို့ အလွယ်တကူ ရွေးနိုင်စေပါတယ်။

Dagster ရဲ့ ထူးခြားချက်က "asset" (software-defined asset) ဆိုတဲ့ သဘော — chunk table, embedding table, index တိုင်းကို ရှေ့ဆက်ထုတ်လုပ်ရမယ့် ထုတ်ကုန် (asset) အဖြစ် ကြေငြာစေပြီး၊ lineage ကို first-class အဖြစ် ပြသပါတယ်။ Airflow ကတော့ task-centric အနေနဲ့ စတင်ခဲ့ပြီး ယနေ့ ဗားရှင်းများမှာ Dataset-based scheduling တွေ ထည့်ပေးထားပါတယ်။

### ဘာကြောင့် လဲ

Cron job တွေ အသုံးပြု၍ embedding script ကို ဆက်တိုက် run လိုက်ရင် ဒီစိတ်ပျက်စရာတွေနဲ့ ရင်ဆိုင်ရပါတယ် — run ပျက်ရင် ဘယ်အဆင့်မှာ ပျက်လဲ မသိ၊ ပြန် run မယ်ဆို အစကနေ ပြန်စရာလား (ဒါမှမဟုတ်) ပျက်တဲ့နေရာကနေလား ဆုံးဖြတ်ရ၊ run နှစ်ခု တစ်ပြိုင်တည်း စဖြစ်ရင် duplicate ရေးသွင်းမှု (duplicate writes) ဖြစ်တတ်ပါတယ်။ Orchestrator တစ်ခုက ဒီ ပြဿနာတွေကို — အဆင့်တိုင်းရဲ့ အခြေအနေ (state) ကို database ထဲ မှတ်တမ်းတင်ခြင်း၊ `max_active_runs=1` တို့ concurrency ကန့်သတ်ချက်တို့နဲ့ ဖြေရှင်းပေးပါတယ်။

ဒုတိယ အချက်က observability ပါ။ Vector pipeline တစ်ခုမှာ "ဒီနေ့ embed လုပ်ထားတဲ့ chunk အရေအတွက် ဘယ်လောက်လဲ"၊ "backfill job က ၈၀% ရောက်နေလား" ဆိုတာတွေက operation အတွက် သိသာသာ အရေးကြီးပါတယ်။ Airflow UI နဲ့ Dagster UI က task/asset တိုင်းရဲ့ အခြေအနေ၊ ကြာမြင့်ချိန် (duration)၊ ထပ်ခါထပ်ခါ ကြိုးစားမှု (retry attempts) တွေကို ပြပေးလို့၊ incident စစ်ဆေးဖို့ အချိန် သိသိသာသာ လျှော့ပေးပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

1. Pipeline ကို လုပ်ငန်းတာဝန်များ (task) အဖြစ် ခွဲပါ — တစ်ခုကို တာဝန်တစ်ခု (single responsibility)၊ ဥပမာ `extract_new_docs`, `chunk_texts`, `embed_batch`, `upsert_vectors`။
2. ဆက်နွယ်မှုတွေကို တိကျစွာ graph အဖြစ် ကြေငြာပါ — Airflow မှာ `task_a >> task_b`၊ Dagster မှာ asset ရဲ့ `deps` parameter။
3. အသေးစိတ် ကြိုးစားမှု (retry) နဲ့ ကြားကာလ (delay) ကို task တစ်ခုစီမှာ သတ်မှတ်ပါ — Airflow `retries=3`, `retry_delay=timedelta(minutes=5)` တို့လိုမျိုး။
4. Concurrency ကန့်သတ်ပါ — `max_active_runs=1` နဲ့ တစ်ပြိုင်တည်း run နှစ်ခု မရှိစေဘဲ idempotency အားကိုးရတဲ့ အာမခံချက် ဒီနှစ်ဆင့်စလုံး ရပါတယ်။
5. Parameter တွေကို ခွဲထွက်ဖို့ ပြုလုပ်ပါ (externalize) — embedding model version၊ batch size၊ cutoff date တွေကို code အတွင်း hard-code လုပ်ပြီး မြှုပ်မထားဘဲ config/param အဖြစ် ပြောင်းပေးပါ။
6. Backfill job တွေကို scheduled run ထက် ရှင်းလင်းစွာ ခွဲခြားပါ — Dagster မှာ partition (ဥပမာ တစ်ရက်ချင်း partition) က historical run တွေကို ရိုးရှင်းစေပါတယ်။

### ဥပမာ

```python
from collections import deque

# Tiny topological-order executor: a DAG in ~20 lines, stdlib only.
graph = {
    "extract":   [],
    "clean":     ["extract"],
    "chunk":     ["clean"],
    "embed":     ["chunk"],
    "upsert":    ["embed"],
    "evaluate":  ["upsert"],
}
order, ready = [], deque(sorted(k for k, v in graph.items() if not v))
done = set()
while ready:
    node = ready.popleft()
    order.append(node)
    done.add(node)
    for nxt in sorted(graph):
        if nxt in done or nxt in order:
            continue
        deps = graph[nxt]
        if all(d in done for d in deps):
            ready.append(nxt)
print("run order:", " -> ".join(order))
# Expected output:
# run order: extract -> clean -> chunk -> embed -> upsert -> evaluate
```

အပေါ်က သင်ခန်းစာက — orchestrator တွေက အလုပ်လုပ်တဲ့ နည်းနဲ့ တူတူပါ — task တွေကို dependency အလိုက် အစီအစဉ်ချပြီး အဆင့်အတိအကျ လည်ပတ်စေတယ်။ `extract` မပြီးမချင်း `chunk` ကို ဘယ်တော့မှ စမရဘဲ၊ `evaluate` က နောက်ဆုံးမှ လည်ပတ်ပါတယ်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Vector search pipeline တစ်ခုက ရက်သတ္တပတ်ပိုင်းပြီးမှ ထုတ်လုပ်မှု အဆင့်ရောက်တဲ့ အခြေအနေ (production-grade) အဖြစ် ရောက်တတ်ပြီး၊ အဲဒီကာလအတွင်း လက်တွေ့ဘက်ခြမ်း (operational side) က ပို၍ ပင်ပန်းစေတတ်ပါတယ်။ Task တစ်ခု ပျက်ရင် ဘယ်နေရာကနေ ပြန်စရမလဲ၊ ဘယ် run က ဘယ် data snapshot နဲ့ အလုပ်လုပ်ခဲ့လဲ ဆိုတာတွေက incident အတွက် ဖြေရှင်းနိုင်မှု မရှိပါက အခက်အခဲ ဖြစ်လာစေပါတယ်။ DAG-first design က ဒီမေးခွန်းတွေကို အလိုအလျောက် ဖြေပေးပြီး၊ pipeline ရဲ့ ဖွဲ့စည်းပုံ (structure) ကို code ဖတ်တဲ့သူ တစ်ယောက်က နားလည်နိုင်စေပါတယ်။ Model migration (section 4) လို ရှုပ်ထွေးတဲ့ လုပ်ငန်းတွေကလည်း DAG ရှိမှ အဆင့်တိုင်းကို ခြေရာခံမိပြီး စိတ်ချစွာ တည်ဆောက်နိုင်ပါတယ်။

## အနှစ်ချုပ်

- DAG က လုပ်ငန်းတာဝန်များရဲ့ ဆက်နွယ်မှုကို ကွန်ပျူတာ နားလည်နိုင်တဲ့ graph အဖြစ် ကြေငြာစေပါတယ်။
- Orchestrator က အခြေအနေ မှတ်တမ်းတင်ခြင်း၊ retry၊ concurrency control တွေကို အလိုအလျောက် လုပ်ပေးပါတယ်။
- Task တစ်ခုကို တာဝန်တစ်ခုနဲ့ ခွဲဖို့နဲ့ ဆက်နွယ်မှုကို explicit ရေးဖို့က အခြေခံ စည်းမျဉ်းပါ။
- `max_active_runs=1` နဲ့ idempotent upsert ပေါင်းရင် မတော်တဆ run ထပ်မိမှုက ကာကွယ်နိုင်ပါတယ်။
- Parameter တွေ config ထဲ ထုတ်ထားရင် backfill နဲ့ migration run တွေက ရိုးရှင်းပါတယ်။
- Dagster ရဲ့ asset/partition သဘောက historical data ကို ခြေရာခံမိတဲ့ pipeline တွေ တည်ဆောက်ဖို့ အထူး အဆင်ပြေပါတယ်။
