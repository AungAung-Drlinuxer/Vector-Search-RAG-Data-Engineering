# M8 — Retrieval Serving Architecture: API၊ Cache နှင့် pgvector vs Vector DB

> ဒီ module ရဲ့ အချက်အလက်တွေက https://github.com/pgvector/pgvector , https://qdrant.tech/documentation/ , https://weaviate.io/developers/weaviate , https://docs.trychroma.com/ , https://github.com/milvus-io/milvus ဆိုတဲ့ official documentation တွေကနေ ယူထားတာ ဖြစ်ပါတယ်။ ဒီ course က original study material ပါ။

---

## Subtopic ၁ — Retrieval API ဒီဇိုင်း (Filter နှင့် ACL ပါဝင်မှု)

### ဘာကို ဆိုလိုတာလဲ

Retrieval API ဆိုတာ vector search ကို အခြား service တွေက ခေါ်သုံးလို့ရအောင် ဖွင့်ပေးထားတဲ့ interface ကို ဆိုလိုတယ်။ Filter က query နဲ့တွဲပြီး metadata အခြေအနေနဲ့ စစ်တာပါ။ ACL (Access Control List — ဘယ် user က ဘယ် data ကို မြင်ရလဲဆိုတာ သတ်မှတ်တဲ့စာရင်း) က user အခွင့်အရေးနဲ့ စစ်တာပါ။

### ဘာကြောင့် လဲ

ACL မပါဘဲ search ဖွင့်ရင် အလုပ်ရှင့်တဲ့ စာရွက်တွေ အားလုံး ရလာပါလိမ့်မယ်။ RAG က အဲဒီစာရွက်တွေကို LLM ဆီ ပို့ပါလိမ့်မယ်။ ဒါဆို မခွင့်ပြုထားတဲ့ data ပေါ်ထွက်တဲ့ answer ရလာပါတယ်။ ဒါက production system အတွက် အလွန် အန္တရာယ်ကြီးတဲ့ အမှားပါ။ Filter လည်း မရှိရင် ရလဒ်တွေက ကွာပါတယ် — ဥပမာ "၂၀၂၄ ခုနှစ် report တွေပဲ ရှေ့တွင် ခေါ်ချင်တာ" ဆိုတာမျိုး မလုပ်နိုင်ဘူး။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Request ၀င်လာရင် အရင်ဆုံး user identity ကို စစ်ပါတယ်။
၂။ user ရဲ့ ACL ကနေ allowed document set ကို ယူပါတယ်။
၃။ query text ကနေ embedding ထုတ်ပါတယ် (ဒီမှာ deterministic stand-in သုံးပါမယ်)။
၄။ filter ကို metadata အပေါ် အရင်လည်ပတ်ပါတယ် (Postgres မှာ WHERE clause နဲ့ တူတယ်)။
၅။ filter ပြီးတဲ့ subset ထဲမှာပဲ similarity search လုပ်ပါတယ်။
၆။ ရလဒ်ကို score နဲ့တွဲပြီး response ပြန်ပါတယ်။

### ဥပမာ

```python
# Retrieval API sketch: ACL filter first, then similarity search.
# No real database is used; logic mirrors what pgvector does with WHERE + ORDER BY.

docs = [
    {"id": 1, "vec": [1.0, 0.0], "meta": {"year": 2024, "team": "eng"}},
    {"id": 2, "vec": [0.9, 0.1], "meta": {"year": 2023, "team": "eng"}},
    {"id": 3, "vec": [0.0, 1.0], "meta": {"year": 2024, "team": "sales"}},
]

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    return dot / (na * nb)

def search(user_teams, query_vec, filters, top_k):
    # Step 1-2: ACL restricts the candidate set before any math happens.
    candidates = [d for d in docs if d["meta"]["team"] in user_teams]
    # Step 3: metadata filters narrow it further.
    for key, value in filters.items():
        candidates = [d for d in candidates if d["meta"].get(key) == value]
    # Step 4: similarity only inside the allowed subset.
    scored = [(d["id"], cosine(query_vec, d["vec"])) for d in candidates]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:top_k]

result = search(user_teams={"eng"}, query_vec=[1.0, 0.1],
                filters={"year": 2024}, top_k=5)
print(result)
# Expected output:
# [(1, 0.9950371902099893)]
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

pgvector က Postgres ရဲ့ WHERE clause ကို vector search နဲ့ တွဲပေးတယ်။ ဒါက ACL ကို SQL level မှာပဲ စစ်လို့ရတယ်ဆိုတာ သက်သေပါ။ Qdrant documentation (https://qdrant.tech/documentation/) ကလည်း payload filter နဲ့ vector search တွဲလို့ရတယ်လို့ ပြောပါတယ်။ Production မှာ filter မပါတဲ့ API က security bug ပါ။

---

## Subtopic ၂ — Caching အလွှာများ (Embedding Cache နှင့် Result Cache)

### ဘာကို ဆိုလိုတာလဲ

Embedding cache က query text → vector ကို သိမ်းထားတဲ့ cache ပါ။ Result cache က (query + filter + user) → ရလဒ်စာရင်း ကို သိမ်းတဲ့ cache ပါ။ Cache ဆိုတာ တွက်ချက်ပြီးသားအဖြေကို ပြန်သုံးရအောင် သိမ်းတဲ့နေရာ ဖြစ်ပါတယ်။

### ဘာကြောင့် လဲ

တူတဲ့ query တွေ ထပ်ရောက်ရင် embedding model ထပ်ခေါ်ရတယ်။ Model ခေါ်တာက ကုန်ကျစရာ အများဆုံးအဆင့်ပါ။ Result cache ကိုလည်း မရှိရင် search တွေ အကြိမ်ကြိမ် ထပ်တွက်ရတယ်။ Cache နှစ်မျိုးနဲ့ တူတဲ့ query ကို ကုန်ကျစရိတ်နည်းအောင် လျှော့နိုင်တယ်။ ဒါပေမယ့် data အသစ်ဝင်လာရင် result cache ဟာ ဟောင်းသွားနိုင်တယ် — ဒါကို invalidation လို့ ခေါ်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Query ၀င်လာရင် cache key ဆောက်ပါတယ် (user + filter ပါတဲ့ hash)။
၂။ Result cache မှာရှိရင် တန်းပြန်ပါတယ် (cache hit)။
၃။ မရှိရင် embedding cache ကို စစ်ပါတယ်။
၄။ Vector မရှိရင် embedding model ခေါ်ပြီး cache ထဲ ထည့်ပါတယ်။
၅။ Search တွက်ပြီး ရလဒ်ကို result cache ထဲ ထည့်ပါတယ်။
၆။ Data update ဖြစ်တိုင်း သက်ဆိုင်တဲ့ cache key တွေကို ဖျက်ပါတယ်။

### ဥပမာ

```python
# Two-layer cache: embedding cache and result cache (LRU-style dicts).
# Where a real embedding model would run, we use a deterministic stand-in.

embedding_cache = {}   # query text -> vector
result_cache = {}      # cache key -> results
MODEL_CALLS = 0        # count how often the "model" actually runs

def fake_embed(text):
    # Deterministic stand-in: hash-based vector, no real model call.
    h = hash(text)
    return [((h >> i) % 1000) / 1000.0 for i in range(8)]

def embed(text):
    global MODEL_CALLS
    if text not in embedding_cache:
        MODEL_CALLS += 1
        embedding_cache[text] = fake_embed(text)
    return embedding_cache[text]

def retrieve(user, filters, text):
    key = (user, tuple(sorted(filters.items())), text)
    if key in result_cache:
        return result_cache[key], "result-cache-hit"
    vec = embed(text)  # may hit the embedding cache instead of the model
    results = ["doc%d" % i for i in range(3)]  # stand-in search results
    result_cache[key] = results
    return results, "computed"

print(retrieve("alice", {"year": 2024}, "_vector search_"))
print(retrieve("alice", {"year": 2024}, "vector search"))
print(retrieve("alice", {"year": 2024}, "vector search"))
print("model calls:", MODEL_CALLS)
# Expected output:
# (['doc0', 'doc1', 'doc2'], 'computed')
# (['doc0', 'doc1', 'doc2'], 'computed')
# (['doc0', 'doc1', 'doc2'], 'result-cache-hit')
# model calls: 2
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Cache layer တွေက serving cost ကို တိုက်ရိုက်လျှော့ပေးတယ်။ ဒါပေမယ့် user မတူတဲ့ cache key ခွဲရင် cache hit ကျသွားပါတယ်။ ဒါက filter နဲ့ ACL ကို key ထဲ မထည့်ရင် မှားတဲ့ user ကို အခြားသူရဲ့ cached ရလဒ် ပြနိုင်တယ်။ Security နဲ့ performance နှစ်ခုလုံးအတွက် key design က အရေးကြီးတယ်။

---

## Subtopic ၃ — Concurrency နှင့် Connection Pool

### ဘာကို ဆိုလိုတာလဲ

Concurrency ဆိုတာ request များများကို တစ်ပြိုင်တည်း ဆက်တွက်ပေးနိုင်တဲ့ စွမ်းရည်ပါ။ Connection pool က database connection တွေကို ကြိုဖွင့်ထားပြီး ပြန်သုံးတဲ့ ကိုင်တွယ်မှုပါ။ Pool ဆိုတာ ကြိုပြင်ထားတဲ့ connection စုပါ။

### ဘာကြောင့် လဲ

Request တိုင်းအတွက် database connection အသစ်ဖွင့်ရင် နှောင့်နှေးပါတယ်။ Postgres connection တစ်ခုက process တစ်ခုနဲ့ ချိတ်တာပါ။ Connection များလွန်းရင် database ကလည်း ပြင်းပြင်းထိုး လုပ်ရတယ်။ Pool နဲ့ ကြိုဖွင့်ထားတဲ့ connection အနည်းငယ်ကို လှည့်သုံးလို့ request များတာကို ခံနိုင်တယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Service စတဲ့အခါ pool ထဲမှာ connection N ခု ကြိုဖွင့်ထားပါတယ်။
၂။ Request ၀င်လာရင် pool ထဲက connection တစ်ခု ယူပါတယ်။
၃။ ရှာတာ လုပ်ပြီးရင် connection ကို pool ထဲ ပြန်ထည့်ပါတယ်။
၄။ Pool ဗလာဆို အခြား request က စောင့်ပါတယ်။
၅။ Timeout ကျော်ရင် error ပြန်ပါတယ်။

### ဥပမာ

```python
# A toy connection pool with a work queue, using only the standard library.
# Where Postgres + pgvector would connect, we hold "slots" instead.

import queue

class Pool:
    def __init__(self, size):
        # size pre-opened "connections" ready for reuse.
        self.slots = queue.Queue()
        for _ in range(size):
            self.slots.put_nowait("conn")

    def checkout(self, timeout):
        try:
            return self.slots.get(timeout=timeout)
        except queue.Empty:
            return None

    def checkin(self, conn):
        self.slots.put_nowait(conn)

pool = Pool(size=2)
c1 = pool.checkout(timeout=1.0)
c2 = pool.checkout(timeout=1.0)
c3 = pool.checkout(timeout=1.0)  # pool is empty, must wait or fail
print("c1:", c1, "c2:", c2, "c3:", c3)
pool.checkin(c1)
print("after checkin:", pool.checkout(timeout=1.0))
# Expected output:
# c1: conn c2: conn c3: None
# after checkin: conn
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Postgres မှာ max_connections က ကန့်သတ်ထားရတယ်။ App instance တိုင်းက connection များများ ဖွင့်ရင် ကျော်သွားတယ်။ ဒါကြောင့် PgBouncer လို pooler တွေ ရှိတာပါ။ Vector store တွေမှာလည်း တစ်ပြိုင်တည်း request များတဲ့အခါ search performance က ကွာခြားတယ်။ Pool size ကို စမ်းတာက production capacity planning ရဲ့ အခြေခံပါ။

---

## Subtopic ၄ — pgvector vs Qdrant / Milvus / Weaviate / Chroma ရွေးချယ်မှု

### ဘာကို ဆိုလိုတာလဲ

pgvector က Postgres ထဲမှာ vector search လုပ်စေတဲ့ extension ပါ။ Qdrant (https://qdrant.tech/documentation/)၊ Milvus (https://github.com/milvus-io/milvus)၊ Weaviate (https://weaviate.io/developers/weaviate)၊ Chroma (https://docs.trychroma.com/) တွေက vector store သီးသန့် ဖြစ်ပါတယ်။ ရွေးချယ်မှုက ဒီ tool တွေထဲက ဘယ်ဟာက ကိုယ့် system နဲ့ ကိုက်လဲ ဆုံးဖြတ်တာပါ။

### ဘာကြောင့် လဲ

Project တိုင်းမှာ "အကြီးဆုံး" tool မလိုပါ။ Postgres ကို ကိုယ်တိုင်တောင်းနေရင် pgvector က operations ရိုးရိုးရှင်းရှင်းပေးတယ် — database တစ်ခုတည်းနဲ့ ရတယ်။ Data volume ကြီးလာပြီး search latency က အဓိကဖြစ်လာရင် vector store သီးသန့်က ပိုသင့်တော်တတ်တယ်။ Operational cost ကို ကြိုတွက်ရင် မှားရင် project က နှောင့်နှေးတယ်။ ဒါကြောင့် ရွေးချယ်မှု criteria တွေကို ကြိုသိထားရတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ လက်ရှိ data ကို ဘယ်နေရာမှာ သိမ်းနေလဲ သတ်မှတ်ပါတယ်။
၂။ Vector data အရွယ်ကို ခန့်မှန်းပါတယ် (worked example အောက်မှာ ကြည့်ပါ)။
၃။ Search latency နဲ့ QPS လိုအပ်ချက်ကို သတ်မှတ်ပါတယ်။
၄။ Operations team ရဲ့ skill ကို စစ်ပါတယ် — Postgres ကို ရင်းနှီးရင် pgvector က သင့်တော်တယ်။
၅။ Backup, security, filter, update pattern တွေကို တိုက်စစ်ပါတယ်။
၆။ ရလဒ်အရ decision မှတ်ပြီး revisit date သတ်မှတ်ပါတယ်။

### ဥပမာ

```python
# Worked example: vector memory footprint, derived with shown arithmetic.
# Assumptions: 1,000,000 chunks, 768 dimensions, fp32 (4 bytes per float).

chunks = 1_000_000
dims = 768
bytes_per_float = 4

raw_bytes = chunks * dims * bytes_per_float
print("bytes:", raw_bytes)
print("gibibytes: %.2f" % (raw_bytes / (1024 ** 3)))

# Index overhead: HNSW graphs add extra edges per node.
# Assumption: HNSW stores ~2x the raw vector bytes (links + parameters).
print("with ~2x index overhead (GiB): %.2f" % (raw_bytes * 2 / (1024 ** 3)))
# Expected output:
# bytes: 3072000000
# gibibytes: 2.86
# with ~2x index overhead (GiB): 5.72
```

pgvector မှာ ဒီလောက်ကို Postgres table ထဲမှာ index တွဲသိမ်းရတယ်။ Vector store သီးသန့်တွေကလည်း အတူတူ memory planning လိုအပ်တယ်။ ကိန်းဂဏန်းတွေက ကိုယ်တိုင် တွက်ထားတာ ဖြစ်ပြီး official benchmark number တွေ မဟုတ်ပါ။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

pgvector (https://github.com/pgvector/pgvector) က HNSW, IVFFlat index တွေကို support ပါတယ်။ Qdrant documentation (https://qdrant.tech/documentation/) က filterable HNSW အကြောင်း ရှင်းပြပါတယ်။ Milvus (https://github.com/milvus-io/milvus) က distributed scale ကို ရည်ရွယ်ပါတယ်။ Weaviate (https://weaviate.io/developers/weaviate) က modules နဲ့ hybrid search support ပါတယ်။ Chroma (https://docs.trychroma.com/) က developer experience ရိုးရှင်းမှုကို ရည်ရွယ်ပါတယ်။ Tool တိုင်းရဲ့ design goal ကို သိရင် ရွေးချယ်မှုက အခြေအတင် ဖြစ်လာတယ်။

---

## Subtopic ၅ — Hybrid Architecture (Postgres က source of truth၊ vector store သီးသန့်)

### ဘာကို ဆိုလိုတာလဲ

Source of truth ဆိုတာ data ရဲ့ တစ်စုံတစ်ခုတည်းသော မှန်ကန်တဲ့မူကြမ်း သိမ်းနေရာပါ။ Hybrid architecture မှာ Postgres က အဓိက data ပါ၊ vector store က copy တစ်ခုပြီး ရှာဖွေရေးအတွက်ပဲ သုံးတယ်။

### ဘာကြောင့် လဲ

Vector store တစ်ခုတည်းကို data အားလုံးသိမ်းရင် transaction, backup, relation တွေ လျှော့သွားတယ်။ Postgres က ACID transaction (လုပ်ဆောင်မှုတစ်ခုက အလုံးလုံး အောင်မြင်မှု ဒါမှမဟုတ် အလုံးလုံး ပြန်ဖျက်မှု) ကို သေချာပေးတယ်။ ဒါပေမယ့် vector search latency အတွက် vector store သီးသန့်က ပိုသင့်တတ်တယ်။ ဒုတိယနည်းက — data နှစ်နေရာ ထားရမှုက sync (တူညီအောင် ထိန်းချင်း) ပြဿနာ တင်လာတယ်။ ဒါကြောင့် sync pattern ကို နားလည်ရတယ်။

### ဘယ်လို အလုပ်လ
