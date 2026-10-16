# M13 — Capstone: End-to-End System Design & Capacity Sizing Engine

Data engineering architecture တွင် individual components (ingestion, chunking, indexing, retrieval, reranking, evaluation) တစ်ခုချင်းစီကို သီးခြားနားလည်ရုံသာမက ၎င်းတို့အားလုံး အပြန်အလှန် ချိတ်ဆက်လည်ပတ်နေသော holistic system တစ်ခုအဖြစ် ပေါင်းစပ်ဒီဇိုင်းဆွဲနိုင်ရန် လိုအပ်သည်။ ဤ module တွင် end-to-end pipeline consolidation၊ storage calculations၊ HNSW index memory profiling၊ QPS throughput modeling နှင့် empirical evaluation metrics များကို စနစ်တကျ လေ့လာမည်။

---

## Subtopic 1 — End-to-End Pipeline Architecture Consolidation

### Overview

RAG data pipeline တစ်ခုသည် stage ၈ ခုဖြင့် အစဉ်လိုက် ချိတ်ဆက်လည်ပတ်သည်:
`Ingest` → `Chunk` → `Embed` → `Index` → `Retrieve` → `Rerank` → `Generate` → `Evaluate`
အဆင့်တစ်ခုချင်းစီ၏ parameter configuration သည် downstream stages များအားလုံးအပေါ် cascading effect ဖြစ်ပေါ်စေသည်။ ဥပမာ - Chunk size သေးငယ်ပါက vector index row count မြင့်တက်ပြီး HNSW memory overhead များပြားစေကာ retrieval recall@k တိကျမှုနှင့် reranker latency budget ကို ပြောင်းလဲစေသည်။

### End-to-End Flow Emulation

```python
import math

# A tiny "corpus": real ingest/chunk/embed steps are replaced by fixed vectors
# so the lesson runs fully offline and deterministically.
docs = ["PostgreSQL stores data", "pgvector adds vector search",
        "RAG retrieves documents", "HNSW is a graph index"]
vecs = [[1.0, 0.0, 1.0, 0.0], [0.0, 1.0, 0.0, 1.0],
        [1.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 1.0]]
query = [1.0, 0.0, 1.0, 0.0]

def cosine(a, b):
    # cosine similarity: dot(a,b) / (||a|| * ||b||)
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb)

# This is the "retrieve" step; pgvector's operator would do this inside SQL.
scores = sorted(((cosine(query, v), i) for i, v in enumerate(vecs)), reverse=True)
top3 = [i for _, i in scores[:3]]
# Ground truth: doc ids the evaluator (e.g. a Ragas-style checker,
# https://docs.ragas.io/) marked as relevant. Here it is a fixed list.
ground_truth = [0, 2, 3]
recall3 = len(set(top3) & set(ground_truth)) / 3

print("Retrieved top-3 doc ids:", top3)
print("recall@3 vs ground truth: {:.2f}".format(recall3))
# Expected output:
# Retrieved top-3 doc ids: [0, 3, 2]
# recall@3 vs ground truth: 1.00
```

---

## Subtopic 2 — Vector Storage Calculation (Chunks × Dimensions × Bytes)

### Mathematical Formulation

Raw embedding storage footprint ကို အောက်ပါ deterministic formula ဖြင့် တွက်ချက်သည်:
```
Vector_Storage_Bytes = Chunk_Count * Dimensions * Bytes_Per_Value
```
- **FP32 Precision**: 4 bytes per dimension (Standard precision)
- **FP16 / Halfvec Precision**: 2 bytes per dimension (50% storage reduction)

### Python Derivation

```python
GIB = 1024 ** 3  # bytes in one GiB, derived here so the number is traceable

chunks = 1_000_000      # assumption: one million chunks
dim = 768               # assumption: 768-dimensional embeddings
bytes_per_value = 4     # fp32 = 4 bytes per number

vector_bytes = chunks * dim * bytes_per_value
print("fp32 vector storage: {} bytes = {:.2f} GiB".format(vector_bytes, vector_bytes / GIB))

bytes_per_value = 2     # fp16 / halfvec = 2 bytes per number
vector_bytes = chunks * dim * bytes_per_value
print("fp16 vector storage: {} bytes = {:.2f} GiB".format(vector_bytes, vector_bytes / GIB))
# Expected output:
# fp32 vector storage: 3072000000 bytes = 2.86 GiB
# fp16 vector storage: 1536000000 bytes = 1.43 GiB
```

---

## Subtopic 3 — HNSW Multi-Layer Graph Index Memory Footprint

### Architectural Breakdown

HNSW (Hierarchical Navigable Small World, Malkov & Yashunin, 2016, https://arxiv.org/abs/1603.09320) index memory သည် vector coordinates သာမက graph connectivity edge lists များအတွက်ပါ RAM allocation လိုအပ်သည်:
1. **Raw Vector Buffer**: `Chunk_Count * Dimensions * 4 bytes` (fp32)
2. **Layer 0 Edge List Buffer**: `Chunk_Count * (2 * M) * 4 bytes` (int32 node identifiers)
3. **Upper Layers Overhead**: Node density သည် geometric progression အတိုင်း ကိန်းဂဏန်း လျင်မြန်စွာ ကျဆင်းသဖြင့် Layer 0 က memory အများစုကို dominant ယူဆသည်။

### Python Derivation

```python
GIB = 1024 ** 3

chunks = 1_000_000
dim = 768
vector_bytes_per_chunk = dim * 4        # fp32
M = 16
layer0_links = 2 * M                    # HNSW paper: layer 0 allows up to 2M links
link_bytes = 4                          # assumption: int32 link ids

vector_bytes = chunks * vector_bytes_per_chunk
graph_bytes = chunks * layer0_links * link_bytes
total = vector_bytes + graph_bytes

print("Vector data : {} bytes = {:.2f} GiB".format(vector_bytes, vector_bytes / GIB))
print("Graph links : {} bytes = {:.2f} GiB".format(graph_bytes, graph_bytes / GIB))
print("Index total : {} bytes = {:.2f} GiB".format(total, total / GIB))
# Expected output:
# Vector data : 3072000000 bytes = 2.86 GiB
# Graph links : 128000000 bytes = 0.12 GiB
# Index total : 3200000000 bytes = 2.98 GiB
```

---

## Subtopic 4 — Throughput (QPS) & Percentile Latency Modeling

### Capacity Principles

Vector database cluster sizing တွင် QPS (Queries Per Second) throughput နှင့် p95/p99 query latencies များကို အောက်ပါ parameters များဖြင့် model လုပ်ရသည်:
- `ef_search`: Query traversal candidate list size (higher `ef_search` increases recall at the cost of distance evaluations and latency)
- Concurrency & CPU Core Allocation: Single replica ၏ throughput saturation limit
- Cache Hit Ratio: Frequent queries များအတွက် embedding cache နှင့် vector result cache အကျိုးသက်ရောက်မှု

## Summary Checklist

- Vector table storage = `Chunks * Dimensions * Bytes_Per_Value` (+ relational metadata overhead)။
- HNSW index total RAM footprint = `Vector Buffer + Layer 0 Adjacency List (2*M*4B)`။
- Chunk size သတ်မှတ်ရာတွင် granular precision နှင့် context window trade-offs ကို ချိန်ဆပါ။
- End-to-end latency budget တွင် first-stage retrieval, reranking model inference နှင့် network roundtrip များကို ပေါင်းစပ်ထည့်သွင်းပါ။
- System sizing document (RFC) တိုင်းတွင် assumptions, mathematical formulas နှင့် empirical benchmarks များကို explicit ဖော်ပြပါ။
