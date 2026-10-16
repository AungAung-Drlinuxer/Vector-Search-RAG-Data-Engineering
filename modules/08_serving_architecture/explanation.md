## Subtopic ၁ — Retrieval API ဒီဇိုင်း (Filter နှင့် ACL ပါဝင်မှု)

### ဘာကို ဆိုလိုတာလဲ

Retrieval API သည် RAG system ၏ external interface ဖြစ်သည်။ Client မှ context ရယူလိုသောအခါ ဤ API ကို ခေါ်ယူသည်။ "search" တစ်ခုတည်းမဟုတ်ဘဲ — ACL (Access Control List)၊ metadata filter၊ top-k၊ score threshold တို့ ပါဝင်သော query interface တစ်ခုလုံးကို ဒီဇိုင်းဆွဲရသည်။

pgvector တွင် `WHERE` clause နှင့် vector distance operator ကို query တစ်ခုတည်း၌ ပေါင်းစပ်ထားသဖြင့် API layer သည် filter များကို SQL predicate အဖြစ် မည်သို့ လုံခြုံစွာ ပြောင်းလဲပေးမည်ဆိုသည့် အချက်က အဓိက ဒီဇိုင်း ဆုံးဖြတ်ချက် ဖြစ်သည်။

### ဘာကြောင့် လဲ

Retrieval system တွင် document-level access control သည် security requirement အဖြစ် မဖြစ်မနေ ပါဝင်ရသည်။ Document များကို department, tenant သို့ project အလိုက် ခွဲခြားထားသော system တွင် retrieval path က မြင်ခွင့်မရှိသော document များကို ဖော်ထုတ်ပေးလိုက်ပါက security violation ဖြစ်ပြီး အလွန်ဆိုးရွားသည်။ LLM သည် ပေးထားသော context အားလုံးကို ယုံကြည်စွာ အသုံးပြုသဖြင့် retrieval layer တွင် access control ကို တင်းကျပ်စွာ စစ်ဆေးရသည်။

Filter သည် performance အတွက်လည်း အရေးပါသည်။ သက်ဆိုင်ရာ document များသာ search space ထဲ ပါဝင်ပါက index traversal အချိန် တိုတောင်းသွားပြီး result အရည်အသွေးလည်း မြင့်တက်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

1. API layer သည် incoming request ကို လက်ခံပြီး user identity (JWT သို့ session) မှ principal ကို ဆွဲထုတ်သည်။
2. ACL ကို application layer တွင် စစ်ဆေးခြင်းမပြုဘဲ database query ထဲ predicate အဖြစ် ထည့်သွင်းသည် — ဥပမာ `owner_id = :current_user OR visibility = 'public'`။
3. Metadata filter (date range, tag, doc type) များကိုလည်း query builder တစ်ခုတည်းက ကိုင်တွယ်သည်။
4. Vector search operator (pgvector တွင် `<=>`) နှင့် filter များကို query တစ်ခုတည်းတွင် ပေါင်းရေးပြီး limit ကို top-k အဖြစ် သတ်မှတ်သည်။
5. Response တွင် document id, score, snippet သာ ပြန်လည်ပေးပြီး မလိုအပ်သော field များ ဖော်ပြခြင်း မပြုရပါ။

SQL ပုံစံမှာ အောက်ပါအတိုင်း ဖြစ်နိုင်သည်:

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

အောက်ပါ ဥပမာတွင် filter + ACL logic ကို Python ဖြင့် compact version အဖြစ် ပြထားသည်။ Document တစ်ခုစီ၌ tags နှင့် owner ပါဝင်ပြီး request သည် သက်ဆိုင်ရာ document များကိုသာ ရရှိသည်။

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

Production RAG system အများစုသည် document များကို user/tenant အလိုက် ခွဲခြားပေးရသည်။ SaaS တွင် tenant တစ်ခု၏ document များ အခြား tenant ထံ ရောက်ရှိသွားခြင်းသည် စီးပွားရေးအရ အလွန်ဆိုးရွားသော failure mode ဖြစ်သည်။ Filter နည်းလမ်းနှစ်မျိုးရှိသည် — search အပြီး စစ်သည့် post-filter နှင့် search မတိုင်မီ ကန့်သတ်သည့် pre-filter။ Post-filter တွင် filter တင်းကျပ်လာပါက top-k result များ filter နှင့် မကိုက်ညီဘဲ ကျန်ရစ်နိုင်သည်။

ထို့ကြောင့် ACL ကို "in-filter" အဖြစ် query ထဲ ထည့်သွင်းသော ဒီဇိုင်းသည် correctness အရ ပိုခိုင်မာပြီး production system များအတွက် အကြံပြုထားသော ပုံစံဖြစ်သည်။

## အနှစ်ချုပ်

- Retrieval API သည် "search only" မဟုတ်ဘဲ ACL, metadata filter, top-k, threshold ပါဝင်သော interface ဖြစ်သည်။
- pgvector တွင် filter များကို SQL `WHERE` predicate အဖြစ် query တစ်ခုတည်း၌ ပေါင်းစပ်နိုင်သည်။
- ACL စစ်ဆေးခြင်းသည် RAG system ၏ အဓိက security control ဖြစ်ပြီး LLM ထံ မရောက်မီ retrieval layer တွင် စစ်ဆေးရသည်။
- Post-filter နည်း၌ top-k result များ filter condition နှင့် မကိုက်ညီနိုင်သော အားနည်းချက်ရှိသည်။
- In-filter နည်း (query ထဲ predicate ထည့်ခြင်း) သည် production အတွက် ပိုမိုခိုင်မာသော နည်းလမ်းဖြစ်သည်။
- Response တွင် document id, score, snippet သာ ပြန်လည်ပေးခြင်းက data exposure ကို လျှော့ချပေးသည်။

## Subtopic ၂ — Caching အလွှာများ (Embedding Cache နှင့် Result Cache)

### ဘာကို ဆိုလိုတာလဲ

Serving layer တွင် cache နှစ်မျိုး ထည့်သွင်းစဉ်းစားလေ့ရှိသည် — embedding cache နှင့် result cache။ Embedding cache သည် user query ကို embedding model ဖြင့် vector အဖြစ် ပြောင်းလဲသည့် အဆင့်၏ ရလဒ်ကို သိမ်းဆည်းသည်။ Query string တစ်ခုအတွက် vector သည် deterministic ဖြစ်သဖြင့် တူညီသော query တိုင်းအတွက် model ကို ပြန်မခေါ်ဘဲ cache မှ ယူနိုင်သည်။

Result cache သည် ပြီးမြောက်ပြီးသော retrieval result တစ်ခုလုံး (query + filter combination ၏ အဖြေ) ကို သိမ်းဆည်းသည်။ Query နှင့် parameter အားလုံး တူညီပါက search ကို ပြန်မခေါ်ဘဲ အဖြေဟောင်းကို ပြန်ပေးသည်။

### ဘာကြောင့် လဲ

Embedding တွက်ချက်ခြင်းသည် CPU/GPU resource များစွာ သုံးစွဲသည်။ BERT class model သည် query တိုတစ်ခုကို CPU ပေါ်တွင် millisecond ဆယ်ဂဏန်းအထိ ယူနိုင်ပြီး GPU ပေါ်တွင်လည်း batch မရှိပါက စရိတ်ကြီးသည်။ Chatbot ပုံစံ system များတွင် user များသည် greeting ကဲ့သို့ တူညီသော query များကို အကြိမ်ရာချီ ပို့လေ့ရှိသဖြင့် cache သည် ကုန်ကျစရိတ်ကို သိသာစွာ လျှော့ချပေးသည်။

Result cache သည် tail latency ကို ဖယ်ရှားပေးသည်။ Vector search သည် p99 တွင် နှေးကွေးနိုင်သော်လည်း hit ဖြစ်သော request များတွင် ထို latency ကို လုံးဝ မခံစားရစေပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

1. Embedding cache — key သည် query text ၏ hash (ဥပမာ SHA-256) နှင့် model version ပေါင်းစပ်ဖြစ်ရသည်။ Model ပြောင်းလဲပါက cache key ပါ ပြောင်းလဲသွားစေရန် ရည်ရွယ်သည်။
2. Value ကို float vector အဖြစ် serialize လုပ်ပြီး (binary သို့ base64) Redis ကဲ့သို့ store တွင် TTL နှင့်အတူ သိမ်းဆည်းသည်။
3. Result cache — key သည် query hash + filter params + index version ဖြစ်ရသည်။ Index ထဲ document အသစ်ထည့်ပါက index version မြင့်တက်သွားပြီး အဖြေဟောင်းများ အလိုအလျောက် invalid ဖြစ်သွားသည်။
4. Read path — cache lookup → miss ဖြစ်ပါက embedding တွက်ချက်ပြီး search ခေါ်ကာ result ကို ပြန်သိမ်းသည်။ Hit ဖြစ်ပါက တန်းပြန်ပေးသည်။
5. Invalidation — document ပြင်ဆင်ပါက result cache key ထဲပါ version ကို မြှင့်တင်သည်။ TTL ကို backstop အဖြစ် ထားရှိသည်။

### ဥပမာ

FAQ bot တစ်ခုတွင် user များက "ရုံးချိန် ဘယ်လောက်လဲ" ကို နေ့စဉ် အကြိမ် ၃၀၀ ခန့် မေးသည်ဟု ဆိုပါစို့။ Embedding cache ရှိပါက embedding ကို တစ်ကြိမ်သာ တွက်ချက်ရပြီး ကျန်အကြိမ်များသည် lookup သာဖြစ်သည်။ Result cache ရှိပါက vector search ပင် မလိုတော့ဘဲ response သည် မီလီစက္ကန့်အနည်းငယ်အတွင်း ပြန်ထွက်သည်။

Document upload event ကို လက်ခံရရှိပါက result cache version ကို တစ်ဆင့်မြှင့်တင်ပြီး သက်ဆိုင်ရာ query များကို အသစ်ရှာစေသည့် invalidation ပုံစံကို လက်တွေ့တွင် တွေ့ရလေ့ရှိသည်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Production RAG ၏ serving stack တွင် p50 latency နိမ့်နေခြင်း၏ နောက်ကွယ်အကြောင်းရင်းမှာ cache ဖြစ်လေ့ရှိသည်။ Query distribution သည် long-tail ဖြစ်ပြီး အကြိမ်ရေများသော query အနည်းငယ်က traffic အများစုကို ကိုင်တွယ်သဖြင့် hit rate သည် မျှော်လင့်သည်ထက် မြင့်တတ်သည်။

တစ်ဖက်တွင် cache သည် correctness trap လည်း ဖြစ်သည် — model ပြောင်းပြီး cache မရှင်းလင်းပါက ရောနှောနေသော embedding များဖြင့် search quality ကျဆင်းသွားသည်။ ထို့ကြောင့် cache key ထဲတွင် model version နှင့် index version ထည့်သွင်းခြင်းသည် မဖြစ်မနေ လိုက်နာရမည့် design discipline ဖြစ်သည်။

## အနှစ်ချုပ်

- Embedding cache သည် query text → vector တွက်ချက်မှု ကုန်ကျစရိတ်ကို ဖယ်ရှားပေးသည်။
- Result cache သည် query + filter + index version အတွက် ရှာဖွေပြီးသား အဖြေကို ပြန်ပေးသည်။
- Cache key တွင် model version နှင့် index version ပါဝင်ရသည် — မပါပါက stale data ပြဿနာ ဖြစ်ပေါ်သည်။
- Long-tail query distribution ကြောင့် real system များတွင် hit rate မျှော်လင့်သည်ထက် မြင့်တတ်သည်။
- TTL သည် invalidation ပျက်ကွက်မှုအတွက် backstop သာဖြစ်ပြီး အဓိက အားကိုးရသည်မှာ version-based invalidation ဖြစ်သည်။
- Cache hit path သည် p99 latency ကို သိသာစွာ လျှော့ချပေးသည်။

## Subtopic ၃ — Concurrency နှင့် Connection Pool

### ဘာကို ဆိုလိုတာလဲ

Concurrency ဆိုသည်မှာ request အများအပြားကို တစ်ပြိုင်တည်း ကိုင်တွယ်နိုင်စွမ်း ဖြစ်သည်။ Vector search serving တွင် request တစ်ခုစီသည် database connection တစ်ခု သုံးရသဖြင့် connection pool ဆိုသည်မှာ ကြိုတင်ဖွင့်ထားသော connection များကို ပြန်လည်အသုံးပြုသည့် စနစ်ဖြစ်သည် — connection ဖွင့်/ပိတ် ကုန်ကျစရိတ်ကို ဖယ်ရှားပေးသည်။

pgvector case တွင် pool သည် Postgres connection များအတွက် ဖြစ်ပြီး Qdrant/Milvus ကဲ့သို့ store များတွင် HTTP client သို့ gRPC channel များကို ပြန်လည်အသုံးပြုသော pool ဖြစ်သည်။

### ဘာကြောင့် လဲ

Postgres သည် process-per-connection model ဖြစ်သဖြင့် connection တစ်ခုစီက memory အနည်းငယ်စီ သုံးပြီး connection အရေအတွက်ကို `max_connections` ဖြင့် ကန့်သတ်ထားသည်။ Request တစ်ခုချင်း connection အသစ်ဖွင့်ပါက handshake + auth latency ပေါင်းစပ် တက်လာပြီး database ဘက်တွင်လည်း ဖိအား ဖြစ်ပေါ်သည်။

Pool ရှိပါက connection များကို ကြိုတင်ဖွင့်ထားပြီး request များက pool မှ ယူသုံးကာ အသုံးပြုပြီးနောက် ပြန်ချထားသော ပုံစံဖြစ်သဖြင့် ကုန်ကျစရိတ် အများစု ရှင်းလင်းသွားသည်။ Pool က connection အရေအတွက်ကို min/max ဖြင့် ကန့်သတ်ပေးသဖြင့် database overload မဖြစ်စေပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

1. Pool ကို min size နှင့် max size သတ်မှတ်ပြီး process တစ်ခုလျှင် pool တစ်ခု ထားရှိသည် (ဥပမာ `psycopg_pool.ConnectionPool`၊ SQLAlchemy `pool_size` / `max_overflow`)။
2. Request ဝင်လာပါက pool မှ connection တစ်ခု ယူသည် — pool ဗလာဖြစ်နေပါက max အထိ အသစ်ဖွင့်ပြီး ပြည့်နေပါက timeout အထိ စောင့်ဆိုင်းသည်။
3. Query ပြီးပါက connection ကို မပိတ်ဘဲ pool ထဲ ပြန်ချသည်။ Rollback ကို သေချာဆောင်ရွက်ပေးခြင်းသည်လည်း pool ၏ တာဝန်ဖြစ်သည်။
4. HNSW index ပေါ်ရှိ search များသည် CPU core များစွာ သုံးသဖြင့် Postgres ဘက်တွင် `max_parallel_workers_per_gather` ကဲ့သို့ parameter များကို ထိန်းချုပ်သင့်သည်။
5. Queue depth ကို metric ဖြင့် စောင့်ကြည့်ပြီး pool size နှင့် worker အရေအတွက်ကို tune လုပ်သည်။

### ဥပမာ

Async FastAPI app တစ်ခုတွင် request များသည် event loop ပေါ်၌ တပြိုင်တည်း လည်ပတ်နေသည်ဟု ဆိုပါစို့။ Pool size 10 ဖြစ်ပါက vector search များသည် database ဘက်တွင် တစ်ပြိုင်တည်း အများဆုံး 10 ခုသာ လည်ပတ်နိုင်ပြီး ကျန် request များသည် pool queue တွင် စောင့်ဆိုင်းရမည်။ Connection တစ်ခုလျှင် အသုံးပြုချိန် 50 ms ဖြစ်ပါက request 10 ခုကို 50 ms အတွင်း ကိုင်တွယ်နိုင်သည် — ဤတွက်ချက်မှုသည် Little's law (throughput = concurrency / latency) အခြေခံ ခန့်မှန်းချက်ဖြစ်ပြီး တိုင်းတာထားသော ဂဏန်း မဟုတ်ပါ။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

RAG serving တွင် production incident အများစုသည် pool configuration နှင့် ဆက်စပ်သည် — pool ကြီးလွန်းပါက Postgres ၏ `max_connections` ကို ကျော်လွန်ပြီး "too many connections" error ထွက်ပေါ်သည်။ Pool သေးလွန်းပါက queue latency ကြောင့် request latency ပေါက်ကွဲသွားသည်။ Worker အရေအတွက်နှင့် pool size ကို တစ်ပြိုင်တည်း စောင့်ကြည့်ပြီး ချိန်ညှိရသည်။

Serverless / auto-scaling environment တွင် instance တစ်ခုစီက pool တစ်ခုစီ ဖွင့်သဖြင့် စုစုပေါင်း connection အရေအတွက် ပေါက်ကွဲနိုင်ပြီး PgBouncer ကဲ့သို့ pooler တစ်ထပ် ကြားထည့်ကာ ကာကွယ်လေ့ရှိသည်။

## အနှစ်ချုပ်

- Connection pool သည် connection ဖွင့်/ပိတ် ကုန်ကျစရိတ်ကို ဖယ်ရှားပြီး database ကို overload မှ ကာကွယ်ပေးသည်။
- Postgres သည် process-per-connection model ဖြစ်သဖြင့် connection အရေအတွက်သည် ကန့်သတ်ခံရသော resource ဖြစ်သည်။
- Pool ကို connection min/max အရေအတွက်၊ queue timeout၊ rollback ကဲ့သို့ စည်းမျဉ်းများဖြင့် ထိန်းချုပ်ရသည်။
- Throughput ကို Little's law (concurrency / latency) အရ ချိန်ဆပြီး pool size ခန့်မှန်းနိုင်သည်။
- အဖြစ်များသော incident နှစ်ခုမှာ — pool ကြီးလွန်း၍ `max_connections` ကျော်လွန်ခြင်းနှင့် pool သေးလွန်း၍ queue latency မြင့်တက်ခြင်းတို့ ဖြစ်သည်။
- PgBouncer ကဲ့သို့ ကြားခံ pooler သည် instance အရေအတွက်များသော system များအတွက် လိုအပ်လေ့ရှိသည်။

## Subtopic ၄ — pgvector vs Qdrant / Milvus / Weaviate / Chroma ရွေးချယ်မှု

### ဘာကို ဆိုလိုတာလဲ

ဤ subtopic သည် vector store ရွေးချယ်မှု decision framework ဖြစ်သည် — တစ်ဖက်တွင် Postgres extension ဖြစ်သော pgvector၊ အခြားတစ်ဖက်တွင် dedicated vector database များဖြစ်သော Qdrant, Milvus, Weaviate, Chroma တို့ ရှိသည်။ တစ်ခုစီ၏ design goal မတူညီသဖြင့် workload အပေါ် မူတည်၍ ရွေးချယ်ရသည်။

pgvector သည် relational data နှင့် vector များကို storage တစ်ခုတည်း၊ transaction တစ်ခုတည်းဖြင့် စီမံခွင့်ပေးသည်။ Dedicated vector database များကမူ ANN index engineering၊ distributed scale၊ filter-first search တို့ကို အဓိကထား တည်ဆောက်ထားသည်။

### ဘာကြောင့် လဲ

Stack တစ်ခုလုံးတွင် database နှစ်မျိုး ထိန်းချုပ်ရခြင်းသည် operational burden ဖြစ်စေသည် — backup, monitoring, upgrade, security patch နှစ်ဆ၊ data sync နှစ်ဆ။ Document များ Postgres ထဲ ရှိပြီးသား system တွင် pgvector ထည့်သွင်းခြင်းက ရှုပ်ထွေးမှုကို သိသာစွာ လျှော့ချပေးသည်။

သို့သော် vector အရေအတွက် သန်းချီအထိ တက်လာပါက သို့မဟုတ် heavy filtering + ANN ပေါင်းစပ် performance လိုအပ်လာပါက dedicated engine များက ၎င်းတို့ အားသန်ရာတွင် ပိုကောင်းသည်။ ထို့ကြောင့် "မည်သည့် tool အကောင်းဆုံးလဲ" ဟုမမေးဘဲ "ကျွန်ုပ်တို့၏ scale နှင့် team အတွက် မည်သည်က သင့်တော်သလဲ" ဟု မေးရမည်။

### ဘယ်လို အလုပ်လုပ်လဲ

1. Data volume စစ်ဆေးပါ — million အနည်းငယ်အထိ vector များအတွက် pgvector (HNSW index ဖြင့်) လုံလောက်လေ့ရှိသည်။ သန်းချီအထိ ရောက်ပါက distributed engine များ စဉ်းစားပါ။
2. Filter behavior စစ်ဆေးပါ — pgvector တွင် filter သည် Postgres execution plan ထဲ ပါဝင်ပြီး HNSW ၏ `ef_search` (`hnsw.ef_search`) parameter ဖြင့် recall/speed ချိန်ညှိရသည်။ Dedicated engine များတွင် filterable HNSW ကဲ့သို့ ရှုပ်ထွေးသော index structure များ သီးသန့်ပါရှိသည်။
3. Operational capacity စစ်ဆေးပါ — Postgres admin ကျွမ်းကျင်သော team ရှိသလား၊ Kubernetes ပေါ်တွင် stateful service များ ထိန်းချုပ်နိုင်သလား။
4. Feature စစ်ဆေးပါ — hybrid search (sparse + dense)၊ multi-tenancy၊ built-in embedding integration များ လိုအပ်သလား။
5. ကုန်ကျစရိတ် စစ်ဆေးပါ — managed service သုံးမည်လား၊ self-host လုပ်မည်လား။

### ဥပမာ

Internal knowledge base တစ်ခုအတွက် document သုံးသိန်းခန့် ရှိပြီး data အားလုံး Postgres ထဲ ရှိပြီးသားဖြစ်ကာ team က Postgres admin နားလည်ပါက pgvector သည် သင့်လျော်သော ရွေးချယ်မှု ဖြစ်နိုင်သည် — backup path တစ်ခုတည်း၊ transaction path တစ်ခုတည်း။

တစ်ဖက်တွင် multi-tenant SaaS၌ tenant သောင်းချီ၊ vector သန်းချီ၊ တင်းကျပ်သော metadata filter နှင့် per-tenant isolation လိုအပ်သော case အတွက် Qdrant သို့ Milvus တို့သည် payload filter နှင့် collection-based multi-tenancy အတွက် ပိုသင့်လျော်နိုင်သည်။ ဤအချက်များသည် design feature အခြေခံ ဆုံးဖြတ်ချက်များဖြစ်ပြီး — benchmark ဂဏန်းများသည် workload ပေါ် မူတည်သဖြင့် သက်ဆိုင်ရာ project အတွက်သာ ကိုယ်တိုင် တိုင်းတာသင့်သည်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

ရွေးချယ်မှု မှားယွင်းပါက နောက်ပိုင်းတွင် ပြန်လည်ပြောင်းလဲရန် ခက်ခဲသော architectural decision ဖြစ်သည်။ Database နှစ်ခု ဖြစ်လာပါက "Postgres မှာ source of truth၊ vector store မှာ index" ဆိုသည့် sync ပြဿနာ ပေါ်လာပြီး consistency စောင့်ကြည့်ရသော code များ ရှုပ်ထွေးလာသည်။

ထို့ပြင် over-engineering အန္တရာယ်လည်း ရှိသည် — million အနည်းငယ်အတွက် distributed vector cluster ထောင်ခြင်းသည် maintenance ကုန်ကျစရိတ်ကို အမြတ်မရဘဲ ဆက်လက်ပေးဆောင်ရစေသည်။ နောက် subtopic တွင် ဖော်ပြမည့် hybrid architecture သည် ဤရွေးချယ်မှု၏ middle ground ဖြစ်သည်။

## အနှစ်ချုပ်

- pgvector သည် relational data နှင့် vector ကို transaction တစ်ခုတည်းဖြင့် စီမံခွင့်ပေးသည့် အားသာချက်ရှိသည်။
- Dedicated vector database (Qdrant/Milvus/Weaviate/Chroma) များသည် ANN scale နှင့် filter-first search အတွက် အဓိက တည်ဆောက်ထားသည်။
- ရွေးချယ်ရာတွင် data volume, filter pattern, operational capacity, feature လိုအပ်ချက်, ကုန်ကျစရိတ် တို့ကို အစဉ်လိုက် စစ်ဆေးရသည်။
- Stack နှစ်ခု ထိန်းချုပ်ရသည့် operational burden သည် database တစ်ခုတည်းထက် ကြီးမားသည်။
- Benchmark ဂဏန်းများသည် workload အပေါ် မူတည်သဖြင့် official doc ကိုးကားချက်များကိုသာ အားကိုးသင့်သည်။
- Decision မှားယွင်းပါက consistency နှင့် sync ကုန်ကျစရိတ် ကြီးမားသော ပြဿနာများ ဖြစ်ပေါ်စေသည်။

## Subtopic ၅ — Hybrid Architecture (Postgres က source of truth၊ vector store သီးသန့်)

### ဘာကို ဆိုလိုတာလဲ

Hybrid architecture တွင် document များ၏ master copy အားလုံးကို Postgres တွင် သိမ်းပြီး vector store (ဥပမာ Qdrant) ကို search index အဖြစ်သာ အသုံးပြုသည်။ Postgres သည် authoritative state (source of truth) ဖြစ်ပြီး vector store သည် rebuild လုပ်၍ရသော derived data ဖြစ်သည်။

အဓိက ကွာခြားချက်မှာ — vector store ထဲတွင် doc content ကို duplicate သိမ်းစရာမလိုဘဲ vector နှင့် pointer (doc id) သာ ထားရှိနိုင်ခြင်း ဖြစ်သည်။ Delete သို့ update ဖြစ်ပါက Postgres က အရင်ပြောင်းပြီး vector store က နောက်မှ လိုက်ပြောင်းသည်။

### ဘာကြောင့် လဲ

Document content များသည် relational data နှင့် တွဲလျက် update/delete ခံရလေ့ရှိသည် — user ဖျက်ခြင်း၊ edit လုပ်ခြင်း၊ permission ပြောင်းခြင်း။ Vector store တွင် content မသိမ်းထားပါက update လုပ်ရာ၌ embedding ပြန်တွက်ချက်ရသည့် အလုပ်သာ ကျန်ရှိသည်။

ဒုတိယအချက်မှာ durability ဖြစ်သည် — Qdrant ကဲ့သို့ store များက persistence ပေးသော်လည်း Postgres လောက် ရင့်ကျက်သော transactional, backup, tooling ecosystem မရှိတတ်ပါ။ Source of truth ကို Postgres တွင် ထားခြင်းက ရှိပြီးသား backup/audit infrastructure ကို ပြန်လည်အသုံးပြုခွင့် ပေးသည်။

### ဘယ်လို အလုပ်လုပ်လဲ

1. Write path — Postgres တွင် document နှင့် metadata ကို transaction တစ်ခုတည်း၌ သိမ်းသည်။ Commit ဖြစ်ပြီးနောက် event (ဥပမာ outbox row သို့ queue message) ထွက်ရှိသည်။
2. Worker က event ကို လက်ခံရရှိပြီး embedding တွက်ချက်ကာ vector store ထဲ upsert လုပ်သည် — payload တွင် vector နှင့် Postgres doc id ပါဝင်သည်။
3. Delete path — Postgres တွင် ဖျက်ပြီးနောက် vector store ထဲရှိ သက်ဆိုင်ရာ point id ကို delete လုပ်သည်။ Out-of-order event များကို version သို့ timestamp ဖြင့် ကာကွယ်ရသည်။
4. Read path — Retrieval API က query vector ဖြင့် ရှာဖွေပြီး doc id များ ရရှိပါက Postgres မှ content, ACL စစ်ဆေးကာ အချက်အလက် ဖြည့်စွက်ပေးသည် (ACL ကို vector store payload ထဲ ထည့်ပြီး filter နှင့် တွဲဖက်အသုံးပြုခြင်းလည်း ပြုလုပ်နိုင်သည်)။
5. Rebuild path — vector store တစ်ခုလုံး ပျက်စီးပါက Postgres မှ document အားလုံးကို ပြန်ထုတ်ပြီး reindex လုပ်နိုင်သည် — ဤ architecture ၏ အဓိက အားသာချက်ဖြစ်သည်။

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

အောက်ပါ ဥပမာသည် hybrid write path ၏ event ordering logic ကို Python ဖြင့် ပြထားသည် — worker သည် event version များကို စစ်ဆေးပြီး vector store (mock) ထဲသို့ အသစ်ဆုံး version သာ ထည့်သွင်းသည်။

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

Scale သည် million မှ ကုဋေချီအထိ တက်လာသောအခါ pgvector တစ်ခုတည်းဖြင့် မလုံလောက်တော့သော်လည်း Postgres ကို ဖယ်ရှားပြီး အပြည့်အဝ migrate လုပ်ခြင်းမှာလည်း လက်တွေ့မကျတော့ပါ။ ထိုအခြေအနေတွင် hybrid model သည် migration ကို အဆင့်ဆင့် ဆောင်ရွက်နိုင်သော လမ်းကြောင်း ဖြစ်လာသည် — Postgres ကို မူလအတိုင်းထားပြီး vector search အပိုင်းကိုသာ dedicated engine သို့ ရွှေ့ပြောင်းသည်။

အဓိက စိန်ခေါ်မှုမှာ consistency ဖြစ်သည် — event များသည် အစီအစဉ်မညီဘဲ ရောက်ရှိနိုင်သဖြင့် version စစ်ဆေးခြင်း၊ failed upsert များ retry ပြုလုပ်ခြင်း၊ vector store ထဲ၌ Postgres တွင် မရှိတော့သော doc ကျန်ရစ်ခြင်း စသည်တို့ကို operational discipline ဖြင့် ကိုင်တွယ်ရသည်။ နောက် module များတွင် ဤ sync pipeline ကို streaming ingestion နှင့် တွဲဖက် တည်ဆောက်ပြမည်။

## အနှစ်ချုပ်

- Hybrid architecture တွင် Postgres သည် source of truth ဖြစ်ပြီး vector store သည် derived index သာဖြစ်သည်။
- Vector store ထဲတွင် content မထည့်ဘဲ vector နှင့် doc pointer သာ ထားရှိနိုင်သည်။
- Outbox pattern သည် document write နှင့် sync event ကို transaction တစ်ခုတည်းအတွင်း ပေါင်းစည်းပေးသည်။
- Event ordering ကို version ဖြင့် ကာကွယ်ပြီး stale event များကို skip လုပ်ရသည်။
- Vector store တစ်ခုလုံး ပျက်စီးသွားသော်လည်း Postgres မှ အစအဆုံး rebuild လုပ်နိုင်သည်။
- pgvector မှ dedicated store သို့ migration လုပ်ရာတွင် ဤ model သည် incremental လမ်းကြောင်း ဖြစ်သည်။
