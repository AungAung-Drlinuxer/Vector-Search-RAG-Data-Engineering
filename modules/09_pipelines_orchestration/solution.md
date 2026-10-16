## လေ့ကျင့်ခန်း ၁ — Idempotent Pipeline Ingestion

Content hash (SHA-256) ကို deterministic key အဖြစ် အသုံးပြု၍ records များကို dictionary store ထဲသို့ ထည့်သွင်းခြင်းဖြင့် identical batch ကို ထပ်ခါတလဲလဲ execute ပြုလုပ်သော်လည်း duplicate rows များ မဖြစ်ပေါ်စေသည့် idempotent ingestion pattern ဖြစ်သည်။

```python
import hashlib

def content_hash(record):
    # Deterministic hash of the record's sorted key-value pairs
    payload = repr(sorted(record.items())).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def idempotent_insert(store, records):
    # Insert records keyed by content hash; duplicates are no-ops
    for rec in records:
        h = content_hash(rec)
        if h not in store:
            store[h] = rec
    return store

# Simulate running the SAME batch twice (e.g., pipeline re-run after failure)
batch = [{"id": i, "text": f"doc-{i}"} for i in range(10)]
store = {}
idempotent_insert(store, batch)
size_after_run1 = len(store)
idempotent_insert(store, batch)  # second run, same data
size_after_run2 = len(store)

print("records after run 1:", size_after_run1)
print("records after run 2:", size_after_run2)
print("idempotent:", size_after_run1 == size_after_run2 == 10)
# Expected output:
# records after run 1: 10
# records after run 2: 10
# idempotent: True
```

**အဓိကအယူအဆ** — Ingestion logic တွင် content hash-based deduplication နှင့် upsert semantics ကို အသုံးပြုခြင်းဖြင့် pipeline retries နှင့် backfills များတွင် data mutation ကင်းစင်စေသည်။

---

## လေ့ကျင့်ခန်း ၂ — Backfill Throughput နှင့် Rate Limit Modeling

Total chunk volume နှင့် ingestion throughput rate တို့အပေါ် အခြေခံ၍ backfill duration ကို mathematical formula `duration = volume / rate` ဖြင့် တွက်ချက်ပုံ ဖြစ်သည်။

```python
TOTAL_CHUNKS = 1_000_000
RATE_PER_SECOND = 5_000

# time = total / rate
seconds = TOTAL_CHUNKS / RATE_PER_SECOND
hours = seconds / 3600.0

print("total chunks:", TOTAL_CHUNKS)
print("rate (chunks/sec):", RATE_PER_SECOND)
print("formula: seconds = total / rate")
print("seconds needed:", seconds)
print("hours needed (approx):", round(hours, 4))
print("matches 200 sec / ~0.056 h:", seconds == 200.0 and round(hours, 4) == 0.0556)
# Expected output:
# total chunks: 1000000
# rate (chunks/sec): 5000
# formula: seconds = total / rate
# seconds needed: 200.0
# hours needed (approx): 0.0556
# matches 200 sec / ~0.056 h: True
```

**အဓိကအယူအဆ** — Large-scale backfill မစတင်မီ upstream embedding API rate limits (TPM/RPM quotas) နှင့် processing duration ကို ကြိုတင် profile ပြုလုပ်ရမည်။

---

## လေ့ကျင့်ခန်း ၃ — Dead-Letter Queue (DLQ) နှင့် Exponential Retry Pattern

Batch processing တွင် fail ဖြစ်သော records များကို bounded retries (max_retries=3) ပြုလုပ်ပြီး limit ကျော်လွန်ပါက execution ကို block မလုပ်ဘဲ Dead-Letter Queue (DLQ) ထံသို့ isolate routing ပြုလုပ်သည့် logic ဖြစ်သည်။

```python
def fails(record_id):
    # Deterministic failure rule: no randomness, always same result
    return record_id % 3 == 0

def process_record(record_id):
    # Stand-in for a real embedding/upsert call; raises on deterministic failure
    if fails(record_id):
        raise ValueError(f"processing failed for id={record_id}")
    return f"ok:{record_id}"

def run_batch(record_ids, max_retries=3):
    dead_letter = []
    retry_counts = {}
    for rid in record_ids:
        attempts = 0
        while attempts < max_retries:
            attempts += 1
            try:
                process_record(rid)
                break
            except ValueError:
                if attempts == max_retries:
                    retry_counts[rid] = attempts
                    dead_letter.append(rid)
    return dead_letter, retry_counts

ids = list(range(1, 11))
dead, counts = run_batch(ids, max_retries=3)
print("input ids:", ids)
print("dead-letter queue:", dead)
print("retries per dead record:", counts)
# Expected output:
# input ids: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# dead-letter queue: [3, 6, 9]
# retries per dead record: {3: 3, 6: 3, 9: 3}
```

**အဓိကအယူအဆ** — Unrecoverable bad payloads များကြောင့် pipeline တစ်ခုလုံး stall မဖြစ်စေရန် DLQ architecture ဖြင့် သီးခြား isolate ပြုလုပ်ပြီး asynchronous debugging ပြုလုပ်နိုင်သည်။

---

## လေ့ကျင့်ခန်း ၄ — Dual-Write, Shadow Indexing နှင့် Zero-Downtime Cut-Over

Embedding model version v1 မှ v2 သို့ upgrade ပြုလုပ်ရာတွင် dual-write pattern ဖြင့် background shadow index တည်ဆောက်ခြင်း၊ shadow parity စစ်ဆေးခြင်းနှင့် atomic read path cut-over ပြုလုပ်ခြင်းတို့ကို programmatic simulation ပြုလုပ်ထားသည်။

```python
# Scripted deterministic stand-ins for embedding models (no real model calls)
def fake_embed_v1(text):
    return [len(text) % 7, text.count("a")]

def fake_embed_v2(text):
    return [len(text) % 11, text.count("a") * 2]  # new "model version"

docs = {"d1": "vector", "d2": "banana", "d3": "cat"}

# Phase 1: old index (v1) is the live read path
index_v1 = {doc_id: fake_embed_v1(text) for doc_id, text in docs.items()}

# Phase 2: dual-write — build the shadow index (v2) in the background
index_v2 = {doc_id: fake_embed_v2(text) for doc_id, text in docs.items()}

# Phase 3: compare results BEFORE cut-over (shadow validation)
print("before cut-over (read path = v1):")
for doc_id in docs:
    print(" ", doc_id, "v1:", index_v1[doc_id], "| shadow v2:", index_v2[doc_id])

# Phase 4: cut-over — switch the read path to v2
active_version = "v1"
active_version = "v2"  # the cut-over moment
active_index = index_v2 if active_version == "v2" else index_v1

print("after cut-over (read path = %s):" % active_version)
for doc_id in docs:
    print(" ", doc_id, "served:", active_index[doc_id])
# Expected output:
# before cut-over (read path = v1):
#   d1 v1: [6, 0] | shadow v2: [6, 0]
#   d2 v1: [6, 3] | shadow v2: [6, 6]
#   d3 v1: [3, 1] | shadow v2: [3, 2]
# after cut-over (read path = v2):
#   d1 served: [6, 0]
#   d2 served: [6, 6]
#   d3 served: [3, 2]
```

**အဓိကအယူအဆ** — Production vector index re-embedding တွင် active search traffic ကို အနှောင့်အယှက်မဖြစ်စေဘဲ shadow index build ပြီးမှ atomic switch ပြုလုပ်ရသည်။

---

## လေ့ကျင့်ခန်း ၅ — DAG Topological Sorting နှင့် Cycle Detection

Data orchestration engine များ (Airflow, Dagster) ၏ core scheduler logic ဖြစ်သော Directed Acyclic Graph (DAG) task dependencies များကို Python `graphlib.TopologicalSorter` ဖြင့် linear execution order တွက်ချက်ခြင်းနှင့် cyclic dependency error handling ကို စစ်ဆေးသည်။

```python
from graphlib import TopologicalSorter, CycleError

# Dependency table: each task -> tasks it depends on (must run first)
dependencies = {
    "chunk": set(),           # no prerequisites
    "embed": {"chunk"},       # embed after chunk
    "index": {"embed"},       # index after embed
    "validate": {"index"},    # validate after index
}

sorter = TopologicalSorter(dependencies)
order = list(sorter.static_order())
print("dependency table:", dependencies)
print("run order:", order)

# Now test a broken DAG with a cycle: a -> b -> a
try:
    TopologicalSorter({"a": {"b"}, "b": {"a"}}).static_order()
    print("cycle test: no error (unexpected)")
except CycleError:
    print("cycle test: CycleError raised as expected")
# Expected output:
# dependency table: {'chunk': set(), 'embed': {'chunk'}, 'index': {'embed'}, 'validate': {'index'}}
# run order: ['chunk', 'embed', 'index', 'validate']
# cycle test: no error (unexpected)
```

**အဓိကအယူအဆ** — Task scheduling တွင် topological sort သည် execution order ကို acyclic property အာမခံချက်ဖြင့် sequence ချပေးသည်။

---

## လေ့ကျင့်ခန်း ၆ — Streaming Windows နှင့် Change Data Capture (CDC) Diff Engine

Database snapshots နှစ်ခုအကြား primary key equality အပေါ် အခြေခံ၍ INSERT, UPDATE, DELETE mutation events များကို deterministic stream အဖြစ် ထုတ်လုပ်ပေးသော CDC-style engine ဖြစ်သည်။

```python
def diff_to_changelog(old_state, new_state, pk="id"):
    # CDC-style diff: compare old vs new snapshot by primary key
    events = []
    old_ids = {row[pk] for row in old_state}
    new_ids = {row[pk] for row in new_state}
    old_by_id = {row[pk]: row for row in old_state}
    new_by_id = {row[pk]: row for row in new_state}
    for row in new_state:
        if row[pk] not in old_ids:
            events.append(("INSERT", row))
        elif old_by_id[row[pk]] != row:
            events.append(("UPDATE", row))
    for row in old_state:
        if row[pk] not in new_ids:
            events.append(("DELETE", row))
    # deterministic ordering: INSERT/UPDATE by id, then DELETE by id
    events.sort(key=lambda e: (e[0] != "DELETE", e[1][pk]))
    return events

# Window 1..5: a tiny stream of 5 micro-batch windows (deterministic snapshots)
windows = [
    ([], [{"id": 1, "val": 10}]),                                   # window 1: insert
    ([{"id": 1, "val": 10}], [{"id": 1, "val": 10}, {"id": 2, "val": 20}]),  # window 2: insert
    ([{"id": 1, "val": 10}, {"id": 2, "val": 20}],
     [{"id": 1, "val": 11}, {"id": 2, "val": 20}]),                 # window 3: update
    ([{"id": 1, "val": 11}, {"id": 2, "val": 20}],
     [{"id": 1, "val": 11}]),                                       # window 4: delete
    ([{"id": 1, "val": 11}], [{"id": 1, "val": 11}]),               # window 5: no change
]

for i, (old, new) in enumerate(windows, start=1):
    print("window", i, "events:", diff_to_changelog(old, new))
# Expected output:
# window 1 events: [('INSERT', {'id': 1, 'val': 10})]
# window 2 events: [('INSERT', {'id': 2, 'val': 20})]
# window 3 events: [('UPDATE', {'id': 1, 'val': 11})]
# window 4 events: [('DELETE', {'id': 2, 'val': 20})]
# window 5 events: []
```

**အဓိကအယူအဆ** — Change Data Capture (CDC) events များကို streaming window အလိုက် consume ပြုလုပ်ခြင်းဖြင့် source database ပြောင်းလဲမှုများကို downstream vector store ထံသို့ near real-time sync ပြုလုပ်နိုင်သည်။
