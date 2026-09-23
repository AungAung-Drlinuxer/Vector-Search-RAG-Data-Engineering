## လေ့ကျင့်ခန်း ၁ — Storage အရွယ် တွက်ပါ

chunks × dims × bytes ဆိုတဲ့ formula နဲ့ တိုက်ရိုက်တွက်လို့ ရပါတယ်။ ဒီဂဏန်းကတော့ vector database အတွက် memory ဘယ်လောက် ပြင်ဆင်ရမလဲဆိုတာ ခန့်မှန်းပေးပါတယ်နော်။

```python
# Storage estimate: chunks * dims * bytes_per_value
chunks = 1_000_000
dims = 768
bytes_per_value = 4  # fp32 = 4 bytes per float

total_bytes = chunks * dims * bytes_per_value
print("chunks:", chunks)
print("dims:", dims)
print("bytes per value (fp32):", bytes_per_value)
print("total bytes:", total_bytes)
print("approx GB:", total_bytes / 1e9)
# Expected output:
# chunks: 1000000
# dims: 768
# bytes per value (fp32): 4
# total bytes: 3072000000
# approx GB: 3.072
```

**အဓိကအယူဆ** — fp32 vector တစ်ခုချင်းစီက 768 × 4 = 3,072 bytes ယူလို့ သုံးဘီလီယံခုထဲမှာ ၃ GB ကျော် လိုအပ်ပါတယ်။

## လေ့ကျင့်ခန်း ၂ — Chunk size ရွေးမှုရဲ့ အကျိုးသက်ရောက်မှု

chunk ငယ်ရင် အရေအတွက် များပြီး precision ကောင်းပေမယ့် storage နဲ့ index အလုပ် ပိုများပါတယ်။ chunk ကြီးရင်တော့ context များပေမယ့် စာကြောင်းအလွန် ပျောက်လွယ်သွားပါတယ်နော်။

```python
import math

words = 100_000

for chunk_size in (200, 800):
    num_chunks = math.ceil(words / chunk_size)
    print(f"chunk_size={chunk_size} words -> {num_chunks} chunks")

# Trade-off explanation
print("200-word chunks: more precise retrieval but 4x more chunks to store/index")
print("800-word chunks: fewer chunks, richer context, but relevant sentences get diluted")
# Expected output:
# chunk_size=200 words -> 500 chunks
# chunk_size=800 words -> 125 chunks
# 200-word chunks: more precise retrieval but 4x more chunks to store/index
# 800-word chunks: fewer chunks, richer context, but relevant sentences get diluted
```

**အဓိကအယူဆ** — chunk size က recall နဲ့ precision နှစ်ခုလုံးကို ထိခိုက်လို့ corpus နဲ့ query အမျိုးအစားအပေါ် မူတည်ပြီး မျှတတဲ့ အရွယ် ရွေးရပါတယ်။

## လေ့ကျင့်ခန်း ၃ — HNSW-style graph ဆောက်ပြီး search လုပ်ပါ

level 0 တစ်ထပ်ပဲ ပါတဲ့ ရိုးရိုး graph ကို အနီးဆုံး M=4 ချက်နဲ့ ချိတ်ပြီး entry point ကနေ greedy သွားပါတယ်။ real HNSW က multi-layer ဖြစ်ပေမယ့် ဒီမှာတော့ အတွေးကို အလွယ်ပြထားတာပါနော်။

```python
import random

rng = random.Random(42)
N = 100
M = 4
points = [(rng.random(), rng.random()) for _ in range(N)]

def dist(a, b):
    return (a[0]-b[0])**2 + (a[1]-b[1])**2

# Build graph: each point connects to its M nearest neighbours (bidirectional edges)
neighbors = {i: set() for i in range(N)}
for i in range(N):
    ranked = sorted((j for j in range(N) if j != i), key=lambda j: dist(points[i], points[j]))
    for j in ranked[:M]:
        neighbors[i].add(j)
        neighbors[j].add(i)

# Greedy search from entry point 0
def greedy_search(query, entry=0):
    current = entry
    best_d = dist(points[current], query)
    while True:
        improved = False
        for nb in neighbors[current]:
            d = dist(points[nb], query)
            if d < best_d:
                best_d = d
                current = nb
                improved = True
        if not improved:
            return current, best_d

query = (0.5, 0.5)
graph_idx, g_d = greedy_search(query)
exact_idx = min(range(N), key=lambda i: dist(points[i], query))
print("query:", query)
print("graph search result idx:", graph_idx, "dist:", round(g_d, 6))
print("brute-force exact idx:", exact_idx, "dist:", round(dist(points[exact_idx], query), 6))
print("match:", graph_idx == exact_idx)
# Expected output:
# query: (0.5, 0.5)
# graph search result idx: 7 dist: 0.024485
# brute-force exact idx: 70 dist: 0.003091
# match: False
```

**အဓိကအယူဆ** — greedy graph search က အမြဲတမ်း အနီးဆုံးကို မရဘူးဆိုတာက graph ရဲ့ သဘာဝပါ၊ ဒါပေမယ့် ဒေတာနည်းရင်တော့ များသောအားဖြင့် brute-force နဲ့ တူပါတယ်။

## လေ့ကျင့်ခန်း ၄ — Recall@k တိုင်းပါ

graph search နဲ့ brute-force နှစ်ခုလုံးကို query ၁၀၀ ခုမှာ run ပြီး top-5 ထဲ ဘယ်နှစ်ခု ထပ်တယ်ဆိုတာ ပျမ်းမျှတိုင်းပါတယ်။ seed 42 သုံးထားလို့ run တိုင်း တူတဲ့ တန်ဖိုး ပြန်ရပါတယ်နော်။

```python
import random

rng = random.Random(42)
N = 100
M = 4
points = [(rng.random(), rng.random()) for _ in range(N)]

def dist(a, b):
    return (a[0]-b[0])**2 + (a[1]-b[1])**2

neighbors = {i: set() for i in range(N)}
for i in range(N):
    ranked = sorted((j for j in range(N) if j != i), key=lambda j: dist(points[i], points[j]))
    for j in ranked[:M]:
        neighbors[i].add(j)
        neighbors[j].add(i)

def greedy_search(query, entry=0):
    current = entry
    best_d = dist(points[current], query)
    while True:
        improved = False
        for nb in neighbors[current]:
            d = dist(points[nb], query)
            if d < best_d:
                best_d = d
                current = nb
                improved = True
        if not improved:
            return current

def graph_top_k(query, k=5):
    # Greedy stops at a local minimum, so also scan its neighbours for extra candidates
    start = greedy_search(query)
    candidates = {start} | neighbors[start]
    return sorted(candidates, key=lambda i: dist(points[i], query))[:k]

def exact_top_k(query, k=5):
    return sorted(range(N), key=lambda i: dist(points[i], query))[:k]

queries = [(rng.random(), rng.random()) for _ in range(100)]
total_recall = 0.0
for q in queries:
    g = graph_top_k(q, 5)
    e = exact_top_k(q, 5)
    total_recall += len(set(g) & set(e)) / 5
avg_recall = total_recall / len(queries)
print("avg recall@5 over 100 queries:", round(avg_recall, 4))
# Expected output:
# avg recall@5 over 100 queries: 0.748
```

**အဓိကအယူဆ** — recall@k က graph ရဲ့ အရည်အသွေးကို တိုင်းတာပြတဲ့ metric ဖြစ်ပြီး M တိုးရင် သို့မဟုတ် multi-layer သုံးရင် ပိုကောင်းလာပါတယ်။

## လေ့ကျင့်ခန်း ၅ — QPS တွက်ပါ

query ၁,၀၀၀ ခုကို `time.perf_counter` နဲ့ ချိန်တာတိုင်းပြီး QPS = 1000 / total_seconds နဲ့ တွက်ပါတယ်။ p95 latency က sorted latencies ထဲက 95% index ထုတ်တာပါ — ဒီဂဏန်းတွေက စက်ပေါ်မူတည်လို့ run တိုင်း နည်းနည်း ကွာနိုင်ပါတယ်နော်။

```python
import random

# Greedy graph search with a deterministic step counter and a labelled latency model.
rng = random.Random(42)
N, M = 100, 4
points = [(rng.random(), rng.random()) for _ in range(N)]
STEP_COST_US = 1.0        # assumption: one distance evaluation costs 1 microsecond


def dist(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


neighbors = {i: set() for i in range(N)}
for i in range(N):
    ranked = sorted((j for j in range(N) if j != i), key=lambda j: dist(points[i], points[j]))
    for j in ranked[:M]:
        neighbors[i].add(j)
        neighbors[j].add(i)


def greedy_search(query, entry=0):
    """Return (closest node found, distance evaluations used)."""
    current, best_d, steps = entry, dist(points[entry], query), 1
    while True:
        improved = False
        for nb in neighbors[current]:
            steps += 1
            d = dist(points[nb], query)
            if d < best_d:
                best_d, current, improved = d, nb, True
        if not improved:
            return current, steps


queries = [(rng.random(), rng.random()) for _ in range(1000)]
steps = [greedy_search(q)[1] for q in queries]
total_us = sum(steps) * STEP_COST_US
print("queries                    :", len(queries))
print("distance evaluations total :", sum(steps))
print("mean evaluations per query :", round(sum(steps) / len(queries), 1))
print("p95 latency (us, model)    :", round(sorted(steps)[int(0.95 * len(steps))] * STEP_COST_US, 1))
print(f"QPS (model, {STEP_COST_US:.1f} us per eval): {len(queries) / (total_us / 1e6):.0f}")
# Expected output:
# queries                    : 1000
# distance evaluations total : 34153
# mean evaluations per query : 34.2
# p95 latency (us, model)    : 57.0
# QPS (model, 1.0 us per eval): 29280
```

**အဓိကအယူဆ** — QPS နဲ့ p95 latency က index ဒီဇိုင်းရဲ့ speed/recall trade-off ကို ပြပြီး production မှာ SLA ချမှတ်ဖို့ အသုံးဝင်ပါတယ်။

## လေ့ကျင့်ခန်း ၆ — End-to-end pipeline ဒီဇိုင်းပါ

ingest ကနေ evaluate အထိ တစ်ခုတည်း script ထဲ စုထားပါတယ်။ embedding model အစား hash-based deterministic vector ကို scripted stand-in အဖြစ် သုံးထားတာပါ — real system မှာတော့ embedding model သုံးရပါတယ်နော်။

```python
import random
import math

rng = random.Random(42)
vocab = ["w%d" % i for i in range(50)]
corpus = [rng.choice(vocab) for _ in range(1000)]      # deterministic corpus (seed 42)

CHUNK = 100
chunks = [corpus[i:i + CHUNK] for i in range(0, len(corpus), CHUNK)]
print("num chunks:", len(chunks))


def stable_hash(s):
    h = 2166136261
    for ch in s:
        h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    return h


DIM = 64


def embed(words):
    v = [0.0] * DIM
    for w in words:
        v[stable_hash(w) % DIM] += 1.0            # stable hash: identical across runs
    return v


vecs = [embed(c) for c in chunks]


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def cosine(a, b):
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return 0.0 if na == 0 or nb == 0 else sum(x * y for x, y in zip(a, b)) / (na * nb)


M = 4
N = len(vecs)
neighbors = {i: set() for i in range(N)}
for i in range(N):
    ranked = sorted((j for j in range(N) if j != i), key=lambda j: dist(vecs[i], vecs[j]))
    for j in ranked[:M]:
        neighbors[i].add(j)
        neighbors[j].add(i)


def greedy_search(query, entry=0):
    current, best_d, steps = entry, dist(vecs[entry], query), 1
    while True:
        improved = False
        for nb in neighbors[current]:
            steps += 1
            d = dist(vecs[nb], query)
            if d < best_d:
                best_d, current, improved = d, nb, True
        if not improved:
            return current, steps


def retrieve(query, top=20):
    start, steps = greedy_search(query)
    candidates = {start} | neighbors[start]
    return sorted(candidates, key=lambda i: dist(vecs[i], query))[:top], steps


def rerank(query, ids, top=5):
    # Rerank with exact cosine similarity (a real system would use a reranker model).
    return sorted(ids, key=lambda i: -cosine(query, vecs[i]))[:top]


queries = [embed([rng.choice(vocab) for _ in range(20)]) for _ in range(100)]


def exact_top(k, query):
    return sorted(range(N), key=lambda i: -cosine(query, vecs[i]))[:k]


total_recall, total_steps = 0.0, 0
for q in queries:
    cand, steps = retrieve(q, 20)
    top5 = rerank(q, cand, 5)
    total_steps += steps
    total_recall += len(set(top5) & set(exact_top(5, q))) / 5

recall = total_recall / len(queries)
STEP_COST_US = 1.0                                        # assumption: 1 microsecond per evaluation
print("recall@5:", round(recall, 4))
print("distance evaluations total:", total_steps)
print(f"QPS (model, {STEP_COST_US:.1f} us per eval): {len(queries) / (total_steps * STEP_COST_US / 1e6):.0f}")
print("recall@5 is identical on every run (seed 42)")
# Expected output:
# num chunks: 10
# recall@5: 0.912
# distance evaluations total: 1488
# QPS (model, 1.0 us per eval): 67204
# recall@5 is identical on every run (seed 42)
```

**အဓိကအယူဆ** — pipeline တစ်ခုလုံးကို deterministic stand-in တွေနဲ့ စုပြီး run ကြည့်တာက storage, chunking, indexing, reranking, evaluation တွေ အတူတကွ ဘယ်လို ဆက်စပ်လဲဆိုတာကို အလွယ်မြင်အောင် ပြပေးပါတယ်။
