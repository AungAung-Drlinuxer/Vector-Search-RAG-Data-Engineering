## Subtopic ၁ — Retrieval API ဒီဇိုင်း (Filter နှင့် ACL ပါဝင်မှု)

### ဘာကို ဆိုလိုတာလဲ

Retrieval API ဆိုတာ RAG system ရဲ့ အပြင်ဘက်က ဝန်ဆောင်မှု တစ်ခုပါ။ Client က search query တစ်ချက်လာလို့ RAG pipeline က context ယူချင်တဲ့အခါ ဒီ API ကို ခေါ်ရတာပါ။ ဒါပေမဲ့ "search" တစ်ခုတည်း မဟုတ်ဘဲ — ဘယ် user က ဘယ် document တွေ ကြည့်ခွင့်ရှိလဲဆိုတဲ့ ACL (Access Control List)၊ metadata filter၊ top-k၊ score threshold စတာတွေ ပါဝင်တဲ့ query interface အပြည့်အစုံကို ဒီဇိုင်းလုပ်ရတယ်။

pgvector နဲ့ဆိုရင် `WHERE` clause နဲ့ vector distance ကို တစ်ပြိုင်တည်း ရောစပ်ပြီး ရှာတာမို့ API layer က filter တွေကို SQL predicate အဖြစ် ဘယ်လို ဘယ်လောက် လုံခြုံစွာ ပြောင်းပေးမလဲ ဆိုတာက အဓိက ပုံစံပေါ့။

### ဘာကြောင့် လဲ

RAG မှာ ဘယ် content ကို ဘယ်သူ ဘယ်ဟာကို ကြည့်ခွင့်ရှိလဲ ဆိုတဲ့ အချက်က အရေးအကြီးဆုံး အချက်တွေထဲ မပါဝင်လို့ မရပါ။ Document တွေကို department, tenant, သို့ project အလိုက် ခွဲထားလို့ document တွေကို user/tenant တစ်ခုတည်းသာ ပြတဲ့ system တစ်ခုမှာ user တစ်ယောက်က သူ့ကို မပိုင်တဲ့ document တွေကို retrieval လမ်းကနေ ဖော်ပေးလိုက်ရင် ဒါက security violation တစ်ခု ဖြစ်ပြီး အလွန်အမင်း ဆိုးရွားပါတယ်။ LLM ကတော့ ပေးထားတဲ့ context အားလုံးကို ယုံကြည်စွာ အသုံးပြုသွားမှာ မို့၊ retrieval layer မှာ အလွန်ခိုင်မာစွာ စစ်ရတယ်။

Filter က performance အတွက်ပါ အရေးကြီးတယ်။ သက်ဆိုင်တဲ့ document တွေပဲ search space ထဲ ပါစေရင် index ရှာတဲ့အချိန် ပိုတိုသွားပြီး result ရဲ့ အရည်အသွေးပါ တက်သွားတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

1. API layer က incoming request ကို လက်ခံပြီး user identity (JWT သို့ session) ကနေ principal ယူတယ်။
2. ACL ကို application မှာ မစစ်ပဲ database query ထဲကို predicate အဖြစ် ထည့်တယ် — ဥပမာ `owner_id = :current_user OR visibility = 'public'`။
3. Metadata filter (date range, tag, doc type) တွေကိုလည်း ဒီ query builder ကနေ ကိုင်တွယ်တယ်။
4. Vector search operator (ဥပမာ pgvector မှာ `<=>`) နဲ့ filter တွေကို တစ်ပြိုင်တည်း ရေးပြီး limit ကို top-k အဖြစ် သတ်မှတ်တယ်။
5. Response မှာ document id, score, snippet သာ ပြန်ပေးပြီး အချက်အလက် အပိုများများ မဖော်ပြပါနဲ့။

SQL ပုံစံက ဒီလို မျိုးဖြစ်နိုင်တယ်:

```sql
SELECT id, content, embedding <=> :query_vec AS distance
FROM documents
WHERE tenant_id = :tenant
  AND (owner_id = :user OR visibility = 'public')
  AND created_at >= :since
ORDER BY embedding <=> :query_vec
LIMIT 10;
```

### ဥပမာ

ဒီ ဥပမာ မှာ filter + ACL စစ်တဲ့ logic အတွေ့အကြုံ အလွန်ခိုင်မာစွာ စစ်ထားတဲ့ သေးငယ်တဲ့ version ကို Python ဖြင့် ပြထားတယ်။ document တစ်ခုစီမှာ tags နှင့် owner ပါဝင်ပြီး၊ request မှာ သက်ဆိုင်တဲ့ document တွေပဲ ရမယ်။

```python
# Simplified retrieval request handler: filter + ACL in one pass
from dataclasses import dataclass

@dataclass
class Doc:
    doc_id: int
    owner: str
    tags: list
    score: float

DOCS = [
    Doc(1, "alice", ["finance"], 0.91),
    Doc(2, "bob", ["finance", "hr"], 0.88),
    Doc(3, "alice", ["hr"], 0.72),
    Doc(4, "public_owner", ["finance"], 0.60),
]

def retrieve(user: str, tag: str, k: int = 2) -> list:
    visible = []
    for d in DOCS:
        allowed = (d.owner == user) or (d.owner == "public_owner")
        if allowed and tag in d.tags:
            visible.append(d)
    visible.sort(key=lambda d: d.score, reverse=True)
    return [(d.doc_id, d.score) for d in visible[:k]]

print("alice, finance:", retrieve("alice", "finance"))
print("bob, finance:", retrieve("bob", "finance"))
# Expected output:
# alice, finance: [(1, 0.91), (4, 0.6)]
# bob, finance: [(2, 0.88), (4, 0.6)]
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

အလုပ်လုပ်ချင်တဲ့ RAG system အများစုက document တွေကို user/tenant အလိုက် ခွဲရတယ်။ SaaS တစ်ခုမှာ tenant တစ်ခုရဲ့ document တွေ အခြား tenant တစ်ခုကို ရောက်သွားတာက စီးပွားရေးအရ အဆင့်အတန်း ကျဆုံးစေတဲ့ အမှားဖြစ်တယ်။ ဒါကို ရှာပြီးမှ ဖယ်နည်း (post-filter) နဲ့ စစ်ပြီးမှ ရှာနည်း (pre-filter) ဆိုပြီး နှစ်မျိုးရှိပေမဲ့၊ post-filter မှာ filter တွေ တင်းကျပ်လာတဲ့အခါ top-k အားလုံး ပျက်သွားနိုင်တယ်။

ဒါကြောင့် ACL ကို "in-filter" အဖြစ် query ထဲ ထည့်ထားတဲ့ ဒီဇိုင်းက အလွန်ခိုင်မာပြီး မှန်ကန်တာမို့ production system တွေအတွက် အကြံပြုထားတဲ့ ပုံစံဖြစ်တယ်။

## အနှစ်ချုပ်

- Retrieval API က "search only" မဟုတ်ဘဲ ACL, metadata filter, top-k, threshold တွေ ပါဝင်တဲ့ interface တစ်ခုဖြစ်တယ်။
- pgvector နဲ့ဆို filter တွေကို SQL `WHERE` predicate အဖြစ် တစ်ပြိုင်တည်း ထည့်နိုင်တယ်။
- ACL စစ်တာက RAG system ရဲ့ လုံခြုံရေး အဓိက အချက်ဖြစ်ပြီး LLM အထိ မရောက်မီ စစ်ပစ်ရတယ်။
- Post-filter နည်းက top-k result တွေ filter နဲ့ ကိုက်လို့ မရတတ်တဲ့ အားနည်းချက်ရှိတယ်။
- In-filter နည်း (query ထဲ predicate ထည့်တာ) က production အတွက် ပိုအဆင့်မြင့်တဲ့ နည်းလမ်းဖြစ်တယ်။
- Response မှာ document id, score, snippet လောက်ပဲ ပြန်တာက data exposure ကို လျှော့ပေးတယ်။

## Subtopic ၂ — Caching အလွှာများ (Embedding Cache နှင့် Result Cache)

### ဘာကို ဆိုလိုတာလဲ

Serving layer မှာ cache နှစ်ခု ထည့်စဉ်းစားလေ့ရှိတယ် — embedding cache နှင့် result cache။ Embedding cache က user query တစ်ခုကို embedding model နဲ့ ပြောင်းတဲ့အဆင့်ကို သိမ်းတာပါ။ Query string တစ်ခု အတွက် vector က deterministic ဖြစ်လို့ တူတဲ့ query လာတိုင်း model နဲ့ ပြန်တွက်စေမနေပဲ cache ကနေ ယူနိုင်တယ်။

Result cache ကတော့ ပြီးမြောက်တဲ့ retrieval result တစ်ခုလုံး (query + filter တွေရဲ့ အဖြေ) ကို သိမ်းတာပါ။ Query နှင့် parameter အားလုံးတူရင် search ကို ပြန်မခေါ်ပဲ အဖြေဟောင်းကို ပြန်ပေးလိုက်ရတယ်။

### ဘာကြောင့် လဲ

Embedding တွက်ခြင်းက CPU/GPU အရင်းအမြစ် အများကြီး စားတယ်။ BERT class model တစ်ခုက query တိုတိုတစ်လုံးကို CPU ပေါ်မှာ millisecond ဆယ်ဂဏန်းအထိ ယူတတ်ပြီး GPU ဖြစ်ဖြစ် batch မရှိရင် စရိတ်ကြီးတယ်။ Chatbot သဖွယ် system တွေမှာ user တွေက "မင်္ဂလာပါ" စတဲ့ greeting တူတာတွေကို အကြိမ်ရာဂဏန်း မေးလေ့ရှိလို့ cache ရရင် ကုန်ကျမှု သိသိသာသာ ကျတယ်။

Result cache က random tail latency ကို ဖယ်ပေးတယ်။ Vector search တစ်ချက်က p99 မှာ ဖြစ်စေ နှေးနေတာကို hit ရတဲ့ request တွေမှာ လုံးဝ မခံစားရစေဘူး။

### ဘယ်လို အလုပ်လုပ်လဲ

1. Embedding cache — key က query text ရဲ့ hash (ဥပမာ SHA-256) နှင့် model version ပူးတွဲပါဝင်တယ်။ Model ပြောင်းလိုက်ရင် cache key ပါ ပြောင်းသွားစေရတယ်။
2. Value က float vector အဖြစ် serialize လုပ်ပြီး (binary သို့ base64) Redis စတဲ့ store မှာ TTL နှင့်အတူ သိမ်းတယ်။
3. Result cache — key က query hash + filter params + index version ဖြစ်ရတယ်။ Index မှာ document အသစ်ထည့်လိုက်ရင် index version တက်သွားပြီး အဖြေဟောင်းတွေ အလိုအလျောက် အသုံးမဝင်တော့ပါစေရ။
4. Read path — cache lookup → miss ဖြစ်ရင် embedding တွက်ပြီး search ပြီး result ကို ပြန်သိမ်း။ Hit ဖြစ်ရင် တန်းပြန်ပေး။
5. Invalidation — document ပြင်ရင် result cache key ထဲပါတဲ့ version ကို တက်စေတယ်။ TTL က backstop အဖြစ် ထားတယ်။

### ဥပမာ

FAQ bot တစ်ခုမှာ user တွေက "ရုံးချိန် ဘယ်လောက်လဲ" လို့ နေ့စဉ် အကြိမ် ၃၀ဝ လောက် မေးတယ်ဆိုပါဆို။ Embedding cache ရှိရင် တစ်ခါပဲ တွက်ရပြီး ကျန်တာက lookup ပဲ၊ result cache ရှိရင်တော့ vector search တောင် မလုပ်ရတော့ဘူး — response က မီလီစက္ကန့်အနည်းငယ် အတွင်း ပြန်ထွက်တယ်။

Document upload လုပ်တဲ့ event ကို ကြားရင် result cache version ကို တစ်ဆင့် တက်စေပြီး သက်ဆိုင်တဲ့ query တွေ အသစ်ရှာစေတဲ့ စနစ် တွေ့ရလေ့ရှိတယ်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Production RAG တစ်ခုရဲ့ serving stack က p50 မှာ မြန်နေတဲ့အခါပဲ cache တွေက အများအားဖြင့် နောက်ကွယ်က အကြောင်းရင်းဖြစ်နေလေ့ရှိတယ်။ Query distribution က long-tail မို့ အကြိမ်များတဲ့ query အနည်းငယ်က traffic အများကြီးကို ကိုင်တာမို့ hit rate က အံ့အားသင့်လောက်အောင် မြင့်တတ်တယ်။

ဒါပေမဲ့ cache က တစ်ဖက်မှာ အလွန်ခက်ခဲဆိုးတဲ့ correctness trap ဖြစ်တယ် — model ပြောင်းလို့ cache မရှင်းရင် ရောနှောတဲ့ embedding တွေနဲ့ search quality တိမ်သွားတယ်။ ဒါကြောင့် cache key မှာ model version နှင့် index version ထည့်တာက သတိရသင့်တဲ့ design discipline တစ်ခုဖြစ်တယ်။

## အနှစ်ချုပ်

- Embedding cache က query text → vector အတွက် ကုန်ကျစရိတ် ဖယ်ပေးတယ်။
- Result cache က query + filter + index version အတွက် ရှာပြီးသား အဖြေကို ပြန်ပေးတယ်။
- Cache key မှာ model version နှင့် index version ပါဝင်ရတယ် — မဟုတ်ရင် stale data ပြဿနာ ဖြစ်တယ်။
- Long-tail query distribution က real systems မှာ hit rate ကို မျှော်ထက် မြင့်စေတတ်တယ်။
- TTL က invalidation ရှုံးရင် အရံအတွက်ထားပြီး အဓိက အားကိုးရတာက version-based invalidation ဖြစ်တယ်။
- Cache hit path က p99 latency ကို သိသိသာသာ လျှော့ပေးတယ်။

## Subtopic ၃ — Concurrency နှင့် Connection Pool

### ဘာကို ဆိုလိုတာလဲ

Concurrency က တစ်ပြိုင်တည်း request အများကြီးကို စနစ်တစ်ခုက ကိုင်နိုင်စွမ်းဆိုတဲ့ အချက်ပါ။ Vector search serving မှာ request တစ်ခုစီက database connection တစ်ခုကို အသုံးပြုရလို့၊ connection pool ဆိုတာ ကြိုတင် ဖွင့်ထားတဲ့ connection တွေကို ပြန်လည် အသုံးပြုခြင်းစနစ်ပါ — ဖွင့်/ပိတ် ကုန်ကျမှုကို ဖယ်ပေးတယ်။

pgvector သုံးတဲ့ case မှာ pool က Postgres connection တွေအတွက် ဖြစ်ပြီး၊ Qdrant/Milvus စတာတွေမှာတော့ HTTP client သို့ gRPC channel တွေကို ပြန်လည်အသုံးပြုတဲ့ pool ဖြစ်တယ်။

### ဘာကြောင့် လဲ

Postgres မှာ process per connection မို့ connection တစ်ခုက memory အနည်းငယ်စီ စားတယ်၊ နှင့် connection အရေအတွက်က `max_connections` နဲ့ ကန့်သတ်ခံရတယ်။ Request တစ်ခုချင်း connection အသစ် ဖွင့်နေရရင် handshake + auth ကျပေါင်းနဲ့ latency တက်ပြီး database ဘက်ကလည်း ဖိအားခံရတယ်။

Pool ရှိရင် connection တွေကို ကြိုဖွင့်ထားပြီး request တွေက queue ကနေ ယူသုံး၊ သုံးပြီးရင် ပြန်ချထားတဲ့ ပုံစံမို့ ကုန်ကျမှု အပိုင်းကြီး ရှင်းသွားတယ်။ Pool က connection အရေအတွက်ကို အနိမ့်ဆုံး/အမြင့်ဆုံး ကန့်သတ်ပေးလို့ database ကို overload မဖြစ်စေဘူး။

### ဘယ်လို အလုပ်လုပ်လဲ

1. Pool ကို min size နှင့် max size သတ်မှတ်ပြီး process တစ်ခုလျှင် pool တစ်ခု ထားတယ် (ဥပမာ `psycopg_pool.ConnectionPool`၊ SQLAlchemy `pool_size` / `max_overflow`)။
2. Request ဝင်လာရင် pool ကနေ connection တစ်ခု ယူတယ် — ကုန်နေရင် max ထိ အသစ်ဖွင့်၊ ပြည့်နေရင် timeout ထိ စောင့်တယ်။
3. Query ပြီးရင် connection ကို မပိတ်ပဲ pool ထဲ ပြန်ချတယ်။ Rollback ကို သေချာ လုပ်ပေးတာကလည်း pool ရဲ့ တာဝန်ဖြစ်တယ်။
4. HNSW index ပေါ်မှာ search တွေက CPU core အများကြီး သုံးလို့ Postgres side မှာ `max_parallel_workers_per_gather` တွေ ထိန်းသင့်တယ်။
5. Queue ကြီးလာတာကို metric ကြည့်ပြီး pool size နှင့် worker အရေအတွက်ကို tune လုပ်တယ်။

### ဥပမာ

Async FastAPI app တစ်ခုမှာ request တွေက event loop ပေါ်မှာ ပြိုင်တည်း လည်ပတ်နေတယ်ဆိုပါစို့။ Pool size 10 ထားရင် vector search တွေက database ဘက်မှာ တစ်ပြိုင်တည်း အများဆုံး 10 ခုပဲ လည်နေမယ်၊ ကျန်တာက pool queue မှာ စောင့်မယ်။ Pool ကို ခဏအသုံးပြုချိန်တစ်ခုလျှင် 50 ms ဆိုရင် request 10 ခုက 50 ms အတွင်း အားလုံး ကိုင်နိုင်တယ် — ဒါက Little's law (throughput = concurrency / latency) အရ တွက်ထားတာပါ၊ တိုင်းထားတဲ့ ဂဏန်းမဟုတ်ဘူး။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

RAG serving မှာ အမှားအများဆုံး production incident တွေက pool setting နဲ့ ဆိုင်တတ်တယ် — pool ကို ကြီးစေလိုက်ရင် Postgres ရဲ့ `max_connections` ကို ကျော်ပြီး "too many connections" error ထွက်တယ်၊ ပြတ်ပြတ်သွားရင် latency က queue ကြောင့် ပေါက်သွားတယ်။ Worker အရေအတွက် နှင့် pool size တွေကို တစ်ပြိုင်တည်း ကြည့်ပြီး ချိန်ရတဲ့ အလုပ်ဖြစ်တယ်။

Serverless / auto-scaling ပတ်ဝန်းကျင်မှာတော့ pool တစ်ခုကို instance အားလုံး ဖွင့်လို့ ဖြစ်လာတဲ့ total connection အရေအတွက်ကို PgBouncer စတဲ့ pooler တစ်ထပ် ကြားထည့်ပြီး ကာကွယ်လေ့ရှိတယ်။

## အနှစ်ချုပ်

- Connection pool က database connection ဖွင့်/ပိတ် ကုန်ကျမှုကို ဖယ်ပေးပြီး database ကို overload ကနေ ကာကွယ်တယ်။
- Postgres က process-per-connection မို့ connection အရေအတွက်က ကန့်သတ်ခံရတဲ့ အရင်းအမြစ်ဖြစ်တယ်။
- Pool က connection အရေအတွက် အနိမ့်ဆုံး/အမြင့်ဆုံး၊ queue timeout၊ rollback စတဲ့ စည်းမျဉ်းတွေနဲ့ ထိန်းရတယ်။
- Throughput ကို Little's law အရ concurrency / latency နဲ့ ချိန်ဆက်ပြီး pool size ခန့်မှန်းလို့ရတယ်။
- အသုံးများတဲ့ incident နှစ်ခုက — pool ကြီးလို့ `max_connections` ကျော်တာ၊ ပြတ်လို့ queue latency ပေါက်တာပါ။
- PgBouncer တို့ ကြားခံ pooler တစ်ခုက အသုံးပြုသူ များတဲ့ system တွေအတွက် လိုအပ်လေ့ရှိတယ်။

## Subtopic ၄ — pgvector vs Qdrant / Milvus / Weaviate / Chroma ရွေးချယ်မှု

### ဘာကို ဆိုလိုတာလဲ

ဒီ subtopic က vector store ရွေးတဲ့ decision framework ပါ — တစ်ဖက်မှာ Postgres extension တစ်ခုဖြစ်တဲ့ pgvector၊ အခြားတဖက်မှာ dedicated vector database တွေဖြစ်တဲ့ Qdrant, Milvus, Weaviate, Chroma တို့ပါ။ တစ်ခုစီက design goal မတူလို့ workload အပေါ် မူတည်ပြီး ရွေးရတယ်။

pgvector က relational data နှင့် vector တွေကို တစ်နေရာတည်း၊ transaction တစ်ခုတည်းနဲ့ စီမံခွင့်ပေးတယ်။ Dedicated vector database တွေကတော့ ANN index engineering၊ distributed scale၊ filter-first search စတာတွေကို အဓိက ထားပြီး တည်ဆောက်ထားတယ်။

### ဘာကြောင့် လဲ

Stack တစ်ခုလုံးကို database နှစ်မျိုး ထိန်းရတာက operational burden ရှိတယ် — backup, monitoring, upgrade, security patch နှစ်ဆ၊ data sync နှစ်ဆ။ Document တွေက မတိမ်းမယိမ်းရှိပြီးသား Postgres ရှိတဲ့ system မှာ pgvector ထည့်လိုက်တာက ရှုပ်ထွေးမှု အလွန်နည်းစေတယ်။

ဒါပေမဲ့ vector အရေအတွက် ကုဋေဂဏန်းအထိ တက်လာရင်၊ သို့ heavy filtering + ANN တွဲပြီး မြန်မြန် လိုအပ်လာရင် dedicated engine တွေက သူတို့ အားသန်ရာမှာ ပိုကောင်းတယ်။ ဒါကြောင့် "ဒီ tool က အကောင်းဆုံးလား" မဟုတ်ဘဲ "ကျွန်တော်တို့ရဲ့ scale နှင့် team အတွက် ဘယ်ဟာ သင့်တော်လဲ" လို့ မေးရတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

1. Data volume စစ်ပါ — million အနည်းငယ်အထိ vector တွေအတွက် pgvector (HNSW index နှင့်) က လုံလောက်တတ်တယ်။ ကုဋာအထိ သွားရင် distributed engine တွေ စဉ်းစားတယ်။
2. Filter behavior စစ်ပါ — pgvector မှာ filter က Postgres execution plan ထဲ ပါပြီး HNSW နှင့် `ef_search` (pgvector မှာ `hnsw.ef_search`) parameter တွေနဲ့ recall/speed ချိန်ရတယ်။ Dedicated engine တွေက filterable HNSW စတဲ့ နည်းပိုင်းရှုပ်ထွေးတဲ့ index တွေ သီးသန့်ပါတယ်။
3. Operational capacity စစ်ပါ — Postgres admin အသုံးပြုနိုင်သူ team ရှိလား၊ Kubernetes ပေါ် stateful service တွေ ထိန်းနိုင်လား။
4. Feature စစ်ပါ — hybrid search (sparse + dense)၊ multi-tenancy၊ built-in embedding integration တွေ လိုအပ်လား။
5. စရိတ်စစ်ပါ — managed service သုံးမယ်လား၊ self-host လား။

### ဥပမာ

Internal knowledge base တစ်ခုအတွက် document တွေ ၃ သိန်း လောက်ရှိပြီး Postgres မှာ အားလုံး ပြီးပြီးသား၊ team က Postgres admin နားလည်တယ်ဆို pgvector က သင့်လျော်တဲ့ ရွေးချယ်စရာ ဖြစ်နိုင်တယ် — backup တစ်လမ်းတည်း၊ transaction တစ်လမ်းတည်း။

ဒါတော့၊ multi-tenant SaaS မှာ tenant သောင်းချီပြီး vector ကုဋာအထိ၊ metadata filter တွေ တင်းကျပ်ပြီး per-tenant isolation လိုအပ်တဲ့ case မှာ Qdrant သို့ Milvus တို့က payload filter နှင့ collection-based multi-tenancy အတွက် ပိုသင့်တော်နိုင်တယ်။ ဒါတွေက design feature အရ ပြောတာဖြစ်ပြီး — benchmark ဂဏန်းတွေက workload ပေါ် မူတည်လို့ သူ့ project schedule အတွက်ပဲ တိုင်းရတယ်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

ရွေးချယ်မှုလွဲရင် နောက်မှ ပြန်ပြောင်းရခက်တဲ့ architectural decision တစ်ခုဖြစ်တယ်။ Database နှစ်ခု ဖြစ်လာရင် "Postgres မှာ source of truth၊ vector store မှာ index" ဆိုတဲ့ sync ပြဿနာ ပေါ်လာပြီး consistency စောင့်ရတဲ့ code တွေ ရှုပ်လာတယ်။

ဒါတော့ over-engineering လည်း ရှိတယ် — million အနည်းငယ်အတွက် distributed vector cluster ထောင်ထားတာက maintenance ကုန်ကျစရိတ်က ရမှုမရှိ စွမ်းဆောင်ရည်အတွက် အမြဲပေးနေရတယ်။ Course ရဲ့ နောက် subtopic မှာ ပြောမယ့် hybrid architecture က ဒီ ရွေးချယ်မှုရဲ့ middle ground ဖြစ်တယ်။

## အနှစ်ချုပ်

- pgvector က relational data နှင့် vector ကို transaction တစ်ခုတည်း စီမံခွင့်ပေးတဲ့ အားသာချက်ရှိတယ်။
- Dedicated vector database (Qdrant/Milvus/Weaviate/Chroma) တွေက ANN scale နှင့် filter-first search အတွက် အဓိက ဆောက်ထားတယ်။
- ရွေးချယ်တဲ့အခါ data volume, filter pattern, operational capacity, feature လိုအပ်ချက်, စရိတ် ကို အစဉ်လိုက် စစ်ရတယ်။
- Stack နှစ်ခု ထိန်းရတဲ့ operational burden က database တစ်ခုတည်း ထိန်းတာထက် ကြီးတယ်။
- Benchmark ဂဏန်းတွေက workload အပေါ် မူတည်လို့ official doc မှ ကိုးကားတာ သာယုံရတယ်။
- Decision လွဲရင် consistency နှင့် sync ကုန်ကျစရိတ် ကြီးမားတဲ့ ပြဿနာတွေ ဖန်တီးတတ်တယ်။

## Subtopic ၅ — Hybrid Architecture (Postgres က source of truth၊ vector store သီးသန့်)

### ဘာကို ဆိုလိုတာလဲ

Hybrid architecture မှာ document တွေရဲ့ master copy အားလုံးကို Postgres မှာ သိမ်းပြီး၊ vector store (ဥပမာ Qdrant) ကိုတော့ search index အဖြစ်သာ အသုံးပြုတယ်။ Postgres က "ဘာက မှန်တယ်" ဆိုတာဆုံးဖြတ်တဲ့ source of truth ဖြစ်ပြီး vector store က rebuild လုပ်လို့ရတဲ့ derived data ဖြစ်တယ်။

အဓိက ကွာခြားချက်က — vector store ထဲမှာ doc content တွေကို duplicate သိမ်းစရာမလိုဘဲ vector နှင့် pointer (doc id) လောက်ပဲ ထားလို့ရတယ်။ Delete ဖြစ်စေ update ဖြစ်စေ Postgres က အရင်ပြောင်း၊ vector store က နောက်ကနေ လိုက်ပြောင်းတယ်။

### ဘာကြောင့် လဲ

Document content တွေက relational data နှင့် တွဲပြီး update/delete ခံရလေ့ရှိတယ် — user တွေ ဖျက်တာ၊ edit လုပ်တာ၊ permission ပြောင်းတာ။ Vector store မှာ content ကိုပါ မသိမ်းထားရင် update လုပ်ရင် embedding ပြန်တွက်ရတဲ့ အလုပ်ပဲ ရှိတယ်။

ဒုတိယအချက်က durability ပါ — Qdrant စတဲ့ store တွေကလည်း persistence ပေးပေမဲ့ Postgres လောက် ရင့်ကျက်တဲ့ transactional, backup, tooling ecosystem မရှိတတ်ဘူး။ Source of truth ကို Postgres မှာ ထားခြင်းက company ရဲ့ ရှိပြီးသား backup/audit infrastructure ကို ပြန်အသုံးပြုခွင့်ပေးတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

1. Write path — Postgres မှာ document နှင့် metadata ကို transaction ထဲ သိမ်းတယ်။ Commit ဖြစ်ပြီးရင် event (ဥပမာ outbox row သို့ queue message) ထွက်တယ်။
2. Worker က event ကို ကြားပြီး embedding တွက်၊ vector store ထဲ upsert လုပ်တယ် — payload မှာ vector နှင့် Postgres doc id ပါတယ်။
3. Delete path — Postgres မှာ ဖျက်ပြီးရင် vector store ထဲ သက်ဆိုင်တဲ့ point id ကို delete လုပ်တယ်။ Out-of-order event တွေကို version သို့ timestamp နဲ့ ကာကွယ်ရတယ်။
4. Read path — Retrieval API က query vector ကို ရှာပြီး doc id တွေ ရရင် Postgres ကနေ content, ACL စစ်ပြီး အချက်အလက် ဖြည့်ပေးတယ် ( ACL ကို vector store payload မှာ ထည့်ပြီး filter နဲ့ တွဲနိုင်တယ် )။
5. Rebuild path — vector store တစ်ခုလုံး ပျက်ရင် Postgres ကနေ document အားလုံးကို ပြန်ထုတ်ပြီး reindex လုပ်နိုင်တယ် — ဒါက architecture ဖြစ်တာမို့ လွန်းလွန်း စိတ်မပျက်ရဘူး။

```sql
-- Outbox pattern: write doc and event in one transaction
BEGIN;
INSERT INTO documents (id, content, owner_id, updated_at)
VALUES (42, '...', 'alice', now());
INSERT INTO outbox (doc_id, op, emitted_at)
VALUES (42, 'UPSERT', now());
COMMIT;
```

### ဥပမာ

ဒီ ဥပမာ က hybrid write path ရဲ့ event ordering စစ်တဲ့ logic ကို Python ဖြင့် ပြထားတယ် — worker က event တွေကို version စစ်ပြီး vector store (mock) ထဲ အသစ်ဆုံးပဲ ထည့်တယ်။

```python
# Hybrid sync worker: apply only events newer than stored version
VECTOR_STORE = {}  # doc_id -> (version, vector)

EVENTS = [
    {"doc_id": 7, "version": 1, "vector": [0.1, 0.2]},
    {"doc_id": 7, "version": 3, "vector": [0.5, 0.6]},
    {"doc_id": 7, "version": 2, "vector": [0.3, 0.4]},  # stale, must be skipped
]

for ev in EVENTS:
    stored = VECTOR_STORE.get(ev["doc_id"])
    if stored is None or ev["version"] > stored[0]:
        VECTOR_STORE[ev["doc_id"]] = (ev["version"], ev["vector"])
        print("applied doc", ev["doc_id"], "version", ev["version"])
    else:
        print("skipped stale doc", ev["doc_id"], "version", ev["version"])

print("final:", {k: v[0] for k, v in VECTOR_STORE.items()})
# Expected output:
# applied doc 7 version 1
# applied doc 7 version 3
# skipped stale doc 7 version 2
# final: {7: 3}
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Scale ကို million ကနေ ကုဋာတင်တက်သွားတဲ့အခါ pgvector တစ်ခုတည်းနဲ့ မလုံလောက်တော့ပေမဲ့၊ Postgres ကို ဖျက်ပြီး ကူးပြောင်းဖို့ကလည်း မဖြစ်နိုင်တော့ဘူး။ ဒီအချိန်မှာ hybrid model က migration ကို အဆင့်ဆင့် ခံနိုင်တဲ့ လမ်းဖြစ်လာတယ် — Postgres အားလုံး အတိုင်းထားပြီး vector search အပိုင်းကိုပဲ dedicated engine ကို ရွှေ့တယ်။

အဓိက စိန်ခေါ်မှုက consistency ပါ — event တွေက အစီအစဉ်မတည့် ရောက်တတ်လို့ version စစ်ခြင်း၊ failed upsert တွေ retry ခြင်း၊ vector store ထဲ "Postgres မှာ မရှိတော့တဲ့" doc ကျန်နေခြင်း စတာတွေကို operational discipline နဲ့ ကိုင်ရတယ်။ Course ရဲ့ နောက် module တွေမှာ ဒီ sync pipeline ကို ဖန်တီးပြီး streaming ingestion နဲ့ တွဲပြပါမယ်။

## အနှစ်ချုပ်

- Hybrid architecture မှာ Postgres က source of truth ဖြစ်ပြီး vector store က derived index သာ ဖြစ်တယ်။
- Vector store ထဲ content မထည့်ပဲ vector နှင့် doc pointer လောက်ပဲ ထားလို့ရတယ်။
- Outbox pattern က document write နှင့် sync event ကို transaction တစ်ခုတည်းထဲ ပေါင်းပေးတယ်။
- Event ordering ကို version နဲ့ ကာကွယ်ပြီး stale event တွေကို skip ရတယ်။
- Vector store တစ်ခုလုံး ပျက်သွားလည်း Postgres ကနေ အလုံးအမြစ် rebuild လုပ်နိုင်တယ်။
- pgvector ကနေ dedicated store ကို migration လုပ်ရင် ဒီ model က incremental ဖြစ်တဲ့ ခံနိုင်တဲ့ လမ်းဖြစ်တယ်။
