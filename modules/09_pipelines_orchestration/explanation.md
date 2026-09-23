# M9 — Data Pipeline နှင့် Orchestration: Batch၊ Streaming၊ Backfill၊ Migration

> ဒီ module ရဲ့ အချက်အလက်တွေက https://airflow.apache.org/docs/ , https://docs.dagster.io/ , https://github.com/pgvector/pgvector ဆိုတဲ့ official documentation တွေကနေ ရေးထားတဲ့ မူလဆည်းလည်းမှု material ပါ။ မည်သည့် commercial course ကိုမှ ကူးယူ ဖော်ပြထားတာမဟုတ်ပါဘူး။ သင်ခန်းစာတွေက runtime မှာ database ချိတ်ဆက်ပြီး မလုပ်ပါဘူး — Python standard library နဲ့ပဲ mechanics တွေကို ပြန်လုပ်ပြထားပြီး၊ real system ကိုတော့ prose နဲ့ ရှင်းပြပါမယ်။

## ၁။ Batch နှင့် Streaming Ingestion

### ဘာကို ဆိုလိုတာလဲ
- **Batch ingestion** (အစုံအလင် တစ်ခါတည်း ထည့်သွင်းခြင်း) ဆိုတာ ဒေတာတွေကို အချိန်အနည်းငယ် စုပြီးမှ တစ်ပြိုင်တည်း process လုပ်တာပါ။
- **Streaming ingestion** (ဒေတာ ရလာသလိုလို ထည့်သွင်းခြင်း) ဆိုတာ ဒေတာ အသစ် ရလာတာနဲ့ ချက်ချင်း ခနည်းနည်းစီ process လုပ်တာပါ။

### ဘာကြောင့် လဲ
Batch ချည်းနဲပဲဆိုရင် ဒေတာအသစ်ကို နာရီပိုင်း စောင့်ရတယ်။ RAG system (AI က document တွေထဲကနေ အဖြေရှာပေးတဲ့စနစ်) မှာ အဖြေဟောင်းပဲ ပြနိုင်တယ်။ Streaming ချည်းနဲပဲဆိုရင် ဒေတာတစ်ခုချင်းစီကို overhead (အလုပ်ပို) များတယ်။ ဒါကြောင့် နှစ်မျိုး ရောစပ်သုံးတာ အသင့်တော်ဆုံးပါ။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ Batch pipeline က document တွေကို ညအိပ်ချိန်မှာ အစုံအလင် စုစည်းပြီး embedding (စာသားကို နံပါတ် vector ဖြစ်ပြောင်းတဲ့ပုံစံ) ထုတ်ပါတယ်။
၂။ Streaming pipeline က document အသစ် တစ်ခု ရင် ချက်ချင်း ယူပြီး embedding ထုတ်ပါတယ်။
၃။ နှစ်လမ်းကြားမှာ idempotency (တစ်ခါထက်ပို လုပ်လို့ရတဲ့၊ ရလဒ် မပြောင်းတဲ့ သွားသွားမှု) ကို စစ်ပြီး ဒေတာထပ်မိမှု ကာကွယ်ပါတယ်။

### ဥပမာ

```python
import hashlib

# Deterministic offline stand-in for an embedding model (no network, no LLM).
def fake_embed(text):
    h = hashlib.sha256(text.encode("utf-8")).digest()
    return [b / 255.0 for b in h[:4]]

# Batch ingestion: process accumulated documents at once.
batch = ["doc_a", "doc_b", "doc_c"]
batch_embeddings = {d: fake_embed(d) for d in batch}
print("batch size:", len(batch_embeddings))

# Streaming ingestion: process one document at a time as it arrives.
stream = ["doc_d", "doc_e"]
for i, doc in enumerate(stream):
    print("stream event", i, "->", doc, "embedded:", len(fake_embed(doc)), "dims")
# Expected output:
# batch size: 3
# stream event 0 -> doc_d embedded: 4 dims
# stream event 1 -> doc_e embedded: 4 dims
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
Airflow ရော Dagster ရော နှစ်ခုစလုံးက scheduled pipeline ကို support လုပ်ပါတယ်။ Airflow doc အရ schedule နဲ့ trigger rule တွေက batch လုပ်ငန်းတွေကို အချိန်မှန် လုပ်ပေးပါတယ်။ Real project မှာ document အသစ် များရင် batch၊ အရေးပါ ချက်ချင်းခန့်မှတ်ချင်တာများရင် streaming ကို ရွေးပါ။

## ၂။ Idempotent ပြန်လုပ်နိုင်မှု၊ Backfill နှင့် Rate Limit

### ဘာကို ဆိုလိုတာလဲ
- **Idempotent** ဆိုတာ လုပ်ငန်းတစ်ခုကို နှစ်ခါ၊ သုံးခါ ထပ်လုပ်ခဲ့ရင်တောင် ရလဒ်က အတူတူပဲ ဖြစ်နေတာပါ။
- **Backfill** (ဒေတာဟောင်းတွေကို နောက်မှ ပြန်ဖြည့်ခြင်း) ဆိုတာ pipeline အသစ်ကို ဒေတာဟောင်းတွေအပေါ် ပြန် လုပ်ပေးတာပါ။
- **Rate limit** (တစ်စက္ကန့်ကို လုပ်နိုင်တဲ့ အရေအတွက် ကန့်သတ်ချက်) ဆိုတာ embedding API စတာတွေရဲ့ ခွင့်ပြု limit ပါ။

### ဘာကြောင့် လဲ
Pipeline က တစ်ဝက်လောက်မှာ ပျက်သွားရင် ပြန် run ရတယ်။ Idempotent မဟုတ်ရင် ဒေတာထပ်သွင်းမိပြီး duplicate (ပုံတူပွါး) တွေ ဖြစ်တယ်။ Backfill လုပ်ရင် ဒေတာဟောင်း အားလုံးအပေါ် ပြန်လုပ်ရလို့ idempotency က ပိုသေချာ လိုအပ်တယ်။ Rate limit ကို မစီမံရင် API က request တွေ ငြင်းပယ်တယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ Document တစ်ခုစီကို stable ID (document ID + embedding version ပေါင်းထားတဲ့ ID) နဲ့ မှတ်ပါတယ်။
၂။ Insert မလုပ်ခင် ဒီ ID ရှိပြီလားဆိုပြီး စစ်ပါတယ် — ရှိရင် ကျော်ပါတယ်။
၃။ Rate limit အတွက် အချိန်အကန့်သတ်ပြီး တစ်ကန့်ကို request အရေအတွက် ကန့်သတ်ပါတယ်။

### ဥပမာ

```python
import time, hashlib

def fake_embed(text):
    h = hashlib.sha256(text.encode("utf-8")).digest()
    return [b / 255.0 for b in h[:4]]

store = {}          # stands for a pgvector table (never executed here)
EMBED_VERSION = "v1"

def doc_id(text, version):
    # Stable id: content hash + embedding version -> idempotent across re-runs.
    return hashlib.sha1(f"{text}:{version}".encode()).hexdigest()[:8]

def ingest(documents, rate_limit=2):
    """Idempotent ingest with a simple rate limit (docs per second)."""
    ingested, skipped = 0, 0
    batch_start = time.time()
    for doc in documents:
        did = doc_id(doc, EMBED_VERSION)
        if did in store:              # already ingested -> skip (idempotent)
            skipped += 1
            continue
        if ingested and ingested % rate_limit == 0:
            elapsed = time.time() - batch_start
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)   # wait to respect the rate limit
            batch_start = time.time()
        store[did] = fake_embed(doc)  # a real system would INSERT into pgvector
        ingested += 1
    return ingested, skipped

docs = ["doc_a", "doc_b", "doc_c"]
print("run 1:", ingest(docs))
print("run 2 (same docs, re-run):", ingest(docs))   # proves idempotency
# Expected output:
# run 1: (3, 0)
# run 2 (same docs, re-run): (0, 3)
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
pgvector က table တွေမှာ unique index နဲ့ `ON CONFLICT` ပါ support လုပ်ပါတယ်။ ဒါက PostgreSQL level မှာ idempotent ingest လုပ်တာကို အလွယ်ပေးပါတယ်။ Airflow doc အရ backfill က past interval တွေကို ပြန် run လုပ်တဲ့ feature ပါ — idempotent task မှ ဒီလို ဘေးကင်းစွာ လုပ်နိုင်ပါတယ်။

## ၃။ Dead-letter နှင့် Retry၊ Change Data Capture အခြေခံ

### ဘာကို ဆိုလိုတာလဲ
- **Retry** (ပျက်တဲ့အလုပ်ကို ပြန်ကြိုးစားခြင်း) ဆိုတာ လုပ်ငန်းတစ်ခု ပျက်ရင် နောက်မှ ထပ်စမ်းကြည့်တာပါ။
- **Dead-letter queue** (ပြန်လုပ်ရမလို့ ဖယ်ထားတဲ့ ဒေတာအစု) ဆိုတာ retry အများကြီး လုပ်လည်း မအောင်မြင်တဲ့ ဒေတာတွေကို သီးသန့် ဖမ်းထားတဲ် နေရာပါ။
- **Change Data Capture — CDC** (ဒေတာပြောင်းလဲမှုကို ဖမ်းယူခြင်း) ဆိုတာ source database မှာ ပြောင်းလဲတာတွေကို ချက်ချင်း ဖမ်းယူပြီး အခြား system ဆီ ပို့တဲ့ နည်းပါ။

### ဘာကြောင့် လဲ
Pipeline ရှည်တာမှာ ဒေတာတစ်ခုချင်း ပျက်တာ သာမန်ပါ။ Retry မရှိရင် တစ်ချက်ပျက်ရင် တစ်ချုပ်လုံး ရပ်တယ်။ Dead-letter မရှိရင် ပျက်တဲ့ဒေတာက အခြား ဒေတာကောင်းတွေကိုပါ တာဆီးတယ်။ CDC မရှိရင် source ကို အချိန်ပိုင်း ပြန်စစ်ရတဲ့ polling (အချိန်စနစ် စစ်ဆေးခြင်း) ပိုလေးလေး ဖြစ်တယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ Task တစ်ခု ပျက်ရင် နားရက် တဖြည်းဖြည်း ကြာလာစေပြီး retry လုပ်ပါတယ် (exponential backoff — စောင့်ချိန် နှစ်ဆာတွေးတိုးတာ)။
၂။ Retry အရေအတွက် ကျော်ရင် ဒေတာကို dead-letter list ထဲ ထည့်ပါတယ်။
၃။ CDC မှာ insert/update/delete event တွေကို အစဉ်လိုက် ဖမ်းပြီး pipeline ဆီ တန်းစီပို့ပါတယ်။

### ဥပမာ

```python
import time

dead_letters = []          # stands for a real dead-letter queue
MAX_RETRIES = 3

def process(doc):
    """Deterministic stand-in: docs named 'bad_*' always fail."""
    if doc.startswith("bad_"):
        raise ValueError("embedding service rejected: " + doc)
    return "ok:" + doc

def run_with_retry(doc):
    wait = 0.1
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return process(doc)
        except ValueError:
            if attempt == MAX_RETRIES:
                dead_letters.append(doc)      # give up -> dead-letter
                return None
            time.sleep(wait)                  # exponential backoff
            wait *= 2
    return None

for d in ["good_1", "bad_x", "good_2"]:
    result = run_with_retry(d)
    print(d, "->", result)

print("dead_letters:", dead_letters)
# Expected output:
# good_1 -> ok:good_1
# bad_x -> None
# good_2 -> ok:good_2
# dead_letters: ['bad_x']
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
Airflow doc အရ task တွေမှာ `retries` parameter ရှိပြီး ပျက်ရင် အလိုအလျောက် ပြန် run ပါတယ်။ Dagster မှာတော့ failure handling နဲ့ retry policy concept တွေရှိပါတယ်။ CDC အတွက် PostgreSQL က logical replication feature ကို သုံးလို့ရပြီး၊ pgvector နဲ့တွဲပြီး insert/update event တွေကို vector table ဆီ တစိမ့်စိမ့် ပို့လို့ရပါတယ်။

## ၄။ Embedding Version Migration: Dual-write၊ Shadow Index၊ Cut-over

### ဘာကို ဆိုလိုတာလဲ
- **Embedding version** ဆိုတာ embedding model တစ်မျိုးစီရဲ့ အမှတ်အသားပါ (ဥပမာ v1, v2)။
- **Dual-write** (နေရာနှစ်ခု တပြိုင်တည်း ရေးခြင်း) ဆိုတာ vector အသစ်ကို အနှစ်ဟောင်း table နဲ့ အသစ် table နှစ်ခုလုံးမှာ ရေးတာပါ။
- **Shadow index** (အရိပ် index — စမ်းသပ်ဖို့ ကိုယ်ပွား) ဆိုတာ production (အမှန်အသုံးပြုနေတဲ့) မဟုတ်တဲ့ လျှို့ဝှက် index ပါ။
- **Cut-over** (အသစ်ကို အလုံးစုံ ပြောင်းကြည့်ခြင်း) ဆိုတာ ရက်သတ္တပတ် စစ်ပြီးမှ query traffic အားလုံးကို အသစ်ဆီ ရွှေ့တာပါ။

### ဘာကြောင့် လဲ
Embedding model ပြောင်းရင် vector space (နံပါတ်တွေရဲ့ အကွာအပြား အဓိပ္ပာယ်) တစ်ခုလုံး ပြောင်းသွားတယ်။ ဒါကြောင့် ဒေတာအားလုံးကို ပြန် embed လုပ်ရတယ်။ တစ်ခါတည်း ဖျက်ပြီး အသစ်ထည့်ရင် system တစ်ခုလုံး ခေတ္တရပ်တယ်၊ ပျက်ရင် ပြန်ရနိုင်လမ်းလည်း မရှိတော့ဘူး။ ဒါကြောင့် အဆင့်ဆင့် ပြောင်းတဲ့ နည်းလိုအပ်တယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ Shadow index အသစ်ကို တည်ဆောက်ပါတယ် (production query က မသုံးသေးဘူး)။
၂။ Dual-write နဲ့ ဒေတာအသစ်တွေကို index နှစ်ခုလုံးမှာ ရေးပါတယ်။
၃။ ဒေတာဟောင်းတွေကို backfill လုပ်ပြီး အသစ် model နဲ့ ပြန် embed လုပ်ပါတယ်။
၄။ Shadow index အပေါ် quality စစ်ပါတယ်။ အဆင့်သင့်ဖြစ်ရင် cut-over လုပ်ပါတယ်။
၅။ အရင် index ကို ထားရှိချင်ရင် ထားပါ၊ မလိုရင် ဖျက်ပါတယ်။

### ဥပမာ

```python
import hashlib

def fake_embed(text, version):
    h = hashlib.sha256(f"{version}:{text}".encode()).digest()
    return [b / 255.0 for b in h[:4]]

old_index = {}     # stands for a pgvector table with v1 vectors
new_index = {}     # stands for the shadow pgvector table with v2 vectors

docs = ["doc_a", "doc_b", "doc_c"]

# Step 1-3: backfill old docs into the shadow index with the new version.
for d in docs:
    old_index[d] = fake_embed(d, "v1")   # legacy vectors (already existed)
    new_index[d] = fake_embed(d, "v2")   # shadow index, dual-write

# Step 4: simple sanity check on the shadow index before cut-over.
assert len(new_index) == len(old_index)
print("shadow index size:", len(new_index))

# Step 5: cut-over -> queries now use the new index.
active_index = new_index
print("cut-over done, active index has", len(active_index), "docs")
# Expected output:
# shadow index size: 3
# cut-over done, active index has 3 docs
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
pgvector repo အရ vector column တွေမှာ data type တွေ (`vector` စတာ) ကိုသုံးပြီး index (ANN — ခန့်မှန်း အနီးစပ်ဆုံး ရှာဖွေမှု) တည်ဆောက်ရတယ်။ Version နှစ်ခုက vector dimension တွေ ကွာနိုင်လို့ table သပ်သပ် ခွဲထားတာ အလွယ်ဆုံးပါ။ Cut-over မလုပ်ခင် လက်တွေ့ query တွေနဲ့ စမ်းတာက production risk ကို သိသိသိသိ လျှော့ပေးပါတယ်။

## ၅။ DAG ဒီဇိုင်း (Airflow / Dagster သဘောတရား)

### ဘာကို ဆိုလိုတာလဲ
- **DAG — Directed Acyclic Graph** (ဦးတည်ချက်ရှိပြီး ပြန်လှည့်လမ်းမရှိတဲ့ အဆင့်ကြီးမားပုံသဏ္ဌာန်) ဆိုတာ task တွေရဲ် မှီခိုမှု ကွန်ရက်ပါ — task တချို့က တချို့ ပြီးမှ လုပ်ရတယ်။

### ဘာကြောင့် လဲ
RAG pipeline မှာ "document ရယူ → ရှင်းလင်း → chunk (အပိုင်းခွဲ) လုပ် → embed → index ထည့်" ဆိုတဲ့ အဆင့်တွေ ရှိတယ်။ လက်ဖြင့် run ရင် အဆင့်ချိတ်ဆက်မှု မှားလွယ်တယ်။ Scheduler (အလုပ်တွေကို အချိန်မှန် ဖြန့်ချိတ် system) က ဒီ အဆင့်တွေကို အလိုအလျောက် စီမံပေးပါတယ်။

###
