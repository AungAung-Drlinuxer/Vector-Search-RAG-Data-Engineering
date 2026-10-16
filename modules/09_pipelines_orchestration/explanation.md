# 09_pipelines_orchestration: Data Pipelines, Orchestration & Lifecycle

Production RAG architecture တွင် ingestion pipeline သည် static data load တစ်ခုတည်း မဟုတ်ဘဲ dynamic corpus synchronization၊ embedding version lifecycle management၊ rate limiting နှင့် failure recovery များကို စဉ်ဆက်မပြတ် ကိုင်တွယ်ဖြေရှင်းရသော distributed data system တစ်ခုဖြစ်သည်။ ဤ module တွင် batch vs streaming trade-offs၊ idempotency၊ DLQ/retry patterns၊ embedding migration strategies နှင့် DAG orchestration mechanics များကို programmatic perspective ဖြင့် လေ့လာမည်။

---

## ၁။ Batch နှင့် Streaming Ingestion Architecture

### Overview

Batch ingestion သည် documents များကို fixed time intervals (ဥပမာ scheduled nightly runs) ဖြင့် စုစည်း၍ chunking, embedding, indexing အဆင့်ဆင့်ကို bulk throughput ဖြင့် execute လုပ်သည့် architecture ဖြစ်သည်။ Streaming ingestion သည် source change events (ဥပမာ Kafka topic မှ document updates) ရောက်ရှိလာသည်နှင့် micro-batch သို့မဟုတ် event-by-event near real-time (NRT) ingestion ပြုလုပ်သည့် architecture ဖြစ်သည်။

### Engineering Rationale

Architecture ရွေးချယ်မှုသည် data freshness SLA နှင့် operational complexity အကြား trade-off အပေါ်တွင် မူတည်သည်။
- **Batch Processing**: Resource allocation ကို optimize လုပ်နိုင်ပြီး embedding provider API များတွင် batch endpoint calls ဖြင့် network roundtrip latency နှင့် cost ကို လျှော့ချနိုင်သည်။ Static archives သို့မဟုတ် daily SLA သတ်မှတ်ထားသော datasets များအတွက် standard ရွေးချယ်မှုဖြစ်သည်။
- **Streaming Processing**: Immediate visibility လိုအပ်သော dynamic documents များ (ဥပမာ customer support tickets, breaking news) အတွက် latency ကို minutes သို့မဟုတ် seconds အဆင့်သို့ လျှော့ချပေးသည်။ သို့သော် message broker infrastructure, partition rebalancing နှင့် backpressure monitoring overhead များ တိုးပွားစေသည်။

### Watermark & Checkpointing Logic

Batch နှင့် streaming architectures နှစ်ခုလုံးတွင် duplicate processing ကို တားဆီးရန် high watermark (timestamp သို့မဟုတ် log offset) နှင့် state checkpointing ကို မဖြစ်မနေ အသုံးပြုရသည်။

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

---

## ၂။ Idempotency, Historical Backfill နှင့် Rate Limiting

### Overview

Distributed systems များတွင် at-least-once message delivery semantics ကြောင့် pipeline retries သို့မဟုတ် duplicate task triggers များ မကြာခဏ ဖြစ်ပေါ်နိုင်သည်။ Idempotent ingestion ဆိုသည်မှာ 동일 input payload အား ထပ်ခါတလဲလဲ execute ပြုလုပ်သော်လည်း database state သည် mutation မရှိဘဲ တစ်ကြိမ်သာ execute လုပ်သကဲ့သို့ တည်ငြိမ်နေစေခြင်း ဖြစ်သည်။

### Engineering Mechanics

1. **Deterministic Composite Key**: Chunk identifier အား random UUID မသုံးဘဲ `doc_id + chunk_index + embedding_model_version` ဖြင့် deterministic key သတ်မှတ်ပါ။
2. **Database-Level Upsert**: Unique constraints များ သတ်မှတ်၍ atomic `ON CONFLICT DO UPDATE` semantics ဖြင့် write ပြုလုပ်ပါ။
3. **Leaky Bucket / Token Bucket Throttling**: Upstream embedding providers (ဥပမာ OpenAI, Cohere) ၏ rate limit quotas (TPM/RPM) ကျော်လွန်၍ HTTP 429 Too Many Requests မဖြစ်စေရန် client-side rate limiter ဖြင့် request traffic ကို smooth ဖြစ်အောင် ထိန်းညှိပါ။

```sql
-- Idempotent upsert for a pgvector chunk table (illustrative, never executed)
INSERT INTO chunks (doc_id, chunk_index, embed_version, content_hash, embedding)
VALUES ($1, $2, $3, $4, $5)
ON CONFLICT (doc_id, chunk_index, embed_version)
DO UPDATE SET content_hash = EXCLUDED.content_hash,
              embedding    = EXCLUDED.embedding;
```

---

## ၃။ Dead-Letter Queue (DLQ), Retry Policies နှင့် Change Data Capture (CDC)

### Overview

Corpus ingestion တွင် unparseable documents, encoding corruption သို့မဟုတ် transient API rate limits စသည့် failure classes အမျိုးမျိုးနှင့် ရင်ဆိုင်ရသည်။ Robust pipeline သည် transient errors များကို exponential backoff ဖြင့် retry ပြုလုပ်ပြီး persistent errors များကို Dead-Letter Queue (DLQ) ထံသို့ route ပြုလုပ်၍ main pipeline blockage (poison-pill phenomenon) ကို ကာကွယ်ပေးသည်။

### CDC Architecture for Deletion Integrity

Source database တွင် document တစ်ခု hard delete သို့မဟုတ် soft delete ဖြစ်သွားချိန်တွင် vector index အတွင်း၌ အဆိုပါ document ၏ chunk vectors များ ကျန်ရှိနေပါက (orphan vectors) retrieval hallucination ဖြစ်ပေါ်စေသည်။
- **CDC Mechanism**: PostgreSQL logical decoding (`pgoutput`, Debezium) မှ streaming WAL events (`INSERT`, `UPDATE`, `DELETE`) များကို capture ပြုလုပ်သည်။
- **Cascade Deletion**: Source table တွင် `DELETE` event ဖြစ်ပေါ်သည်နှင့် vector store ထံသို့ purge command ပို့ဆောင်သည်။

```sql
-- Deleting all chunks of a removed source document (illustrative)
DELETE FROM chunks WHERE doc_id = $1;
```

---

## ၄။ Embedding Version Migration: Dual-Write, Shadow Indexing & Cut-Over

### Overview

Embedding model အသစ် (ဥပမာ v1 မှ v2) သို့ upgrade ပြုလုပ်ခြင်းသည် vector coordinates များ၏ geometric space တစ်ခုလုံး ပြောင်းလဲသွားခြင်း ဖြစ်သည်။ Model အဟောင်းနှင့် အသစ်မှ ထွက်ပေါ်လာသော vectors များသည် cosine similarity အားဖြင့် တိုက်ရိုက် နှိုင်းယှဉ်၍ မရနိုင်ပါ။ ဤပြဿနာကို zero-downtime ဖြင့် ဖြေရှင်းရန် Dual-Write and Shadow Index pattern ကို အသုံးပြုရသည်။

### Migration Phases

1. **Schema Versioning**: Table တွင် `embed_version` column ထည့်သွင်းပြီး vectors များကို version tag တပ်ပါ။
2. **Dual-Write State**: Incoming documents အသစ်များကို v1 နှင့် v2 embedding models နှစ်မျိုးလုံးဖြင့် embed လုပ်၍ parallel write ပြုလုပ်ပါ။
3. **Historical Backfill (Shadow Index)**: Background batch worker များဖြင့် existing corpus ကို v2 model ဖြင့် re-embed ပြုလုပ်ကာ shadow table/index သို့ populate လုပ်ပါ။
4. **Offline Evaluation Parity Check**: Golden evaluation dataset ဖြင့် v1 နှင့် v2 retrieval quality metrics (Recall@K, MRR) ကို နှိုင်းယှဉ် အတည်ပြုပါ။
5. **Atomic Cut-Over**: Application retrieval layer ၏ configuration/feature flag ကို v2 သို့ switch လုပ်ပါ။
6. **Deprecation & Cleanup**: Retention buffer ကာလ ကျော်လွန်ပြီးနောက် v1 vectors များကို drop/purge ပြုလုပ်ပါ။

---

## ၅။ Directed Acyclic Graph (DAG) Workflow Orchestration

### Overview

Complex ingestion pipelines များတွင် tasks များ (extract → clean → chunk → embed → upsert → evaluate) ၏ dependency hierarchy ကို Directed Acyclic Graph (DAG) အဖြစ် declare လုပ်၍ orchestrator (Airflow, Dagster) ဖြင့် execute ပြုလုပ်သည်။

### Core Orchestration Principles

- **Single Responsibility Principle**: Task တစ်ခုစီကို atomic boundary ဖြင့် သတ်မှတ်ပါ။
- **Acyclic Enforcement**: Task dependencies များတွင် cycle မရှိစေရန် topological sorting algorithm ဖြင့် validation ပြုလုပ်ပါ။
- **Stateful Observability**: Execution runs များ၏ state progression, retry counts နှင့် execution timing များကို centralized metadata database တွင် track လုပ်ပါ။

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

## Summary Checklist

- Freshness SLA အပေါ် မူတည်၍ Batch (low cost, high throughput) သို့မဟုတ် Streaming (near real-time) ကို ရွေးချယ်ပါ။
- Deterministic chunk composite keys နှင့် database `ON CONFLICT` upsert ဖြင့် idempotency ကို အာမခံပါ။
- Upstream embedding API quota limits များကို token bucket rate limiter ဖြင့် ထိန်းချုပ်ပါ။
- Poison-pill errors များကြောင့် pipeline stall မဖြစ်စေရန် exponential backoff retries နှင့် Dead-Letter Queue (DLQ) ကို တပ်ဆင်ပါ။
- Deletion synchronization အတွက် Change Data Capture (CDC) replication ကို အသုံးပြုပါ။
- Zero-downtime embedding model upgrade အတွက် Dual-Write → Shadow Index → Evaluation → Cut-over sequence ကို လိုက်နာပါ။
- Data pipeline tasks များကို explicit acyclic dependencies ပါဝင်သော DAGs အဖြစ် orchestrate လုပ်ပါ။
