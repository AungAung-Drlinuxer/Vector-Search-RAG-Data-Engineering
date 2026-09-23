# M4 — HNSW Index အတွင်းပိုင်း: Parameter၊ Recall နှင့် Memory

ဒီ module မှာ HNSW index (Hierarchy of Navigable Small World — vector တွေကို graph ပေါ်မှာ ရှာတဲ့ data structure) ရဲ့ အတွင်းပိုင်းကို လေ့လာပါမယ်။ အခြေခံအားဖြင့် paper ဖြစ်တဲ့ [Malkov & Yashunin, 2016](https://arxiv.org/abs/1603.09320)၊ [pgvector](https://github.com/pgvector/pgvector) နဲ့ [Faiss wiki](https://github.com/facebookresearch/faiss/wiki) တွေကနေ ယူထားတာပါ။ ဒါက original လေ့လာသင်ယူမှု material ဖြစ်ပြီး official documentation တွေကနေ ရေးထားတာပါ။ အချိန်ပြည့် runtime မှာ database ချိတ်မှာ မဟုတ်ပါ — Python standard library နဲ့ပဲ mechanics တွေကို ပြန်ဆောက်ပြပါမယ်။

## Subtopic ၁ — Multi-layer Graph သဘောတရား

### ဘာကို ဆိုလိုတာလဲ

HNSW ဆိုတာ layer အများကြီးဆင့်ထားတဲ့ graph ပါ။ အပေါ် layer တွေမှာ point အနည်းငယ်ပဲ ရှိပြီး၊ အောက်ဆုံး layer မှာ point အားလုံး ရှိပါတယ်။ Query တစ်ခကို အပေါ်ကနေ အောက်ကို ဆင်းရှာတာပါ။

### ဘာကြောင့် လဲ

Graph ထဲမှာ point သန်းနဲ့ချီရှိရင် တစ်ခြမ်းဖြတ်ရှာတာ တစ်ချက်ချင်းသွားရင် နှေးပါတယ်။ Layer တွေခွဲထားရင် အပေါ် layer မှာ အဝေးဝေးကို ကြီးကြီးခုန်ပြီး ရောက်နိုင်ပါတယ်။ အောက် layer မှာ အနီးကို အနည်းငယ်သာ ရှာရတော့ လမ်းတိုသွားပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Point တိုင်းကို အောက် layer အားလုံးမှာ ထည့်ပါတယ်။
၂။ ဘယ် layer အထိတက်မလဲဆိုတာ တစ်ချက်ချင်း ဖြတ်သတာက ဆုံးဖြတ်ပါတယ် (paper မှာ "exponential decay" လို့ ခေါ်ပါတယ်)။
၃။ အပေါ် layer မှာ အစပြု point ကနေ ရှာပါတယ်။
၄။ ရှာတွေ့တဲ့ အကောင်းဆုံး point ကို အောက် layer ရဲ့ အစပြု point အဖြစ် ယူပါတယ်။
၅။ အောက်ဆုံး layer မှာ အနီးနားကို အသေးစိတ် ရှာပါတယ်။

### ဥပမာ

```python
# A tiny multi-layer structure in pure Python (standard library only).
# Real systems like pgvector build this with real distance functions.

import random
random.seed(42)

def assign_layer(max_layers):
    # Paper: layer assignment decays exponentially, so upper layers are sparse.
    level = 0
    while random.random() < 0.5 and level < max_layers - 1:
        level += 1
    return level

points = list(range(20))
layers = {0: points, 1: [], 2: []}
for p in points:
    lvl = assign_layer(3)
    for l in range(lvl + 1):
        if p not in layers[l]:
            layers[l].append(p)

for l in sorted(layers):
    print("layer", l, "has", len(layers[l]), "points")
# Expected output:
# layer 0 has 20 points
# layer 1 has 8 points
# layer 2 has 5 points
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

pgvector မှာ `m` parameter နဲ့ layer အရေအတွက်က index ရဲ့ ပုံသဏ္ဌာန်ကို ဆုံးဖြတ်ပါတယ်။ အပေါ် layer တွေက ရှာဖွေမှုရဲ့ speed ကို ချုပ်ကိုင်ပါတယ်။ နားလည်မှ ကောင်းရွေးနိုင်ပါမယ်။

## Subtopic ၂ — M နှင့် ef_construction (Build Parameter)

### ဘာကို ဆိုလိုတာလဲ

`M` (Faiss မှာ `M`) က point တစ်ခုချင်းရဲ့ connection အရေအတွက်ရဲ့ အမြင့်ဆုံး နယ်နိမိတ်ပါ။ `ef_construction` (pgvector မှာ `ef_construction`) က build လုပ်စဉ် တစ်ဆင့်မှာ စစ်ဆေးမယ့် ကန့်သတ်ချက်ပါ။

### ဘာကြောင့် လဲ

`M` နည်းရင် graph က တစ်ဖက်စီ ချိုင်ဆက်မှု နည်းပြီး recall ကျပါတယ်။ `M` များရင် memory နဲ့ build time တက်ပါတယ်။ `ef_construction` နည်းရင် အိမ်နီးချင်း ရွေးတဲ့အခါ မှားနိုင်ပါတယ်။ အများရင် build နှေးပါတယ်။ ဒါတွေက build အရည်အသွေးရဲ့ ချိန်ညှိမှု ဖြစ်တယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Point အသစ်တစ်ခု ဝင်လာပါတယ်။
၂။ အပေါ် layer ကနေ greedy search နဲ့ အနီးဆုံး point ကို ရှာပါတယ်။
၃။ `ef_construction` အတိုင်း candidate အရေအတွက် စုပါတယ်။
၄။ အနီးဆုံး `M` ခုကို ချိုင်ဆက်ချင်း အဖြစ် ယူပါတယ်။
၅။ Graph မှာ ချိတ်ဆက်ချက်တွေကို ပြန်စစ်ပြီး ကျော်လွန်ရင် ဖြတ်ပါတယ်။

### ဥပမာ

```python
# Pure-Python demo of how ef_constriction controls candidate width.
# ef_construction = size of the candidate set kept during insertion.

import heapq, random
random.seed(7)

def build_connections(new_point, all_points, m, ef_construction):
    # Distances to existing points (1-D toy vectors for clarity).
    dists = [(abs(new_point - p), p) for p in all_points]
    # Keep the best ef_construction candidates while searching.
    candidates = heapq.nsmallest(ef_construction, dists)
    # Then finally keep only the m nearest as neighbors.
    return [p for _, p in heapq.nsmallest(m, candidates)]

existing = [random.randrange(0, 100) for _ in range(50)]
neighbors = build_connections(50, existing, m=5, ef_construction=20)
print("neighbors:", sorted(neighbors))
# Expected output:
# neighbors: [46, 50, 50, 53, 53]
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

pgvector documentation မှာ `m` default 16 ဖြစ်ပြီး၊ `ef_construction` default 64 ဖြစ်တယ်လို့ ဖော်ပြထားပါတယ်။ `m` တက်ရင် index ကြီးပြီး recall တက်နိုင်ပါတယ်။ Data အရွယ်အစားနဲ့ ချိန်ပြီး ရွေးရပါမယ်။

## Subtopic ၃ — ef_search၊ Recall နှင့် Latency

### ဘာကို ဆိုလိုတာလဲ

`ef_search` (Faiss မှာ `efSearch`၊ pgvector မှာ `hnsw.ef_search`) က query ရှာစဉ် ထားရမယ့် candidate list အရွယ်အစားပါ။ Recall@k (top-k ထဲ အမှန်ဘယ်နှးရှိလဲဆိုတဲ့ အချိုး) က ef_search တက်တာနဲ့ တက်ပါတယ်။

### ဘာကြောင့် လဲ

ef_search နည်းရင် စစ်တဲ့ node နည်းပြီး မြန်ပေမယ့် အမှန်ရလဒ် လွတ်သွားနိုင်ပါတယ်။ ef_search များရင် ပိုတိတိကျကျ ရသော်လည်း query နှေးလာပါတယ်။ ဒါက accuracy နဲ့ speed ကြားရဲ့ အပေးအယူ ဖြစ်တယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Query vector ကို ယူပါတယ်။
၂။ ရှာဖွေတဲ့ အခါ ef_search အရွယ်အတိုင်း candidate အုပ်စု ထားပါတယ်။
၃။ Candidate စုထဲကနေ top-k ကို ထုတ်ပြပါတယ်။
၄။ Ground truth နဲ့ တိုက်ဆိုင်ပြီး recall@k တွက်ပါတယ်။

### ဥပမာ

```python
# Recall@k measurement with brute-force ground truth (standard library only).
# In pgvector you would compare HNSW results against a seq-scan of the table.

import heapq, random
random.seed(1)

def cosine(a, b):
    num = sum(x * y for x, y in zip(a, b))
    da = sum(x * x for x in a) ** 0.5
    db = sum(x * x for x in b) ** 0.5
    return num / (da * db)

data = [[random.random() for _ in range(8)] for _ in range(200)]
query = [random.random() for _ in range(8)]
k = 5

truth = sorted(data, key=lambda v: -cosine(query, v))[:k]  # brute force
approx = sorted(data[:120], key=lambda v: -cosine(query, v))[:k]  # partial scan as stand-in

hits = len([v for v in approx if any(v is t for t in truth)])
print("recall@%d =" % k, hits / k)
# Expected output:
# recall@5 = 0.4
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Faiss wiki မှာ `efSearch` တက်ရင် recall တက်ပြီး search time လည်း တက်တယ်လို့ ရှင်းပြထားပါတယ်။ Production မှာ target recall အတွက် အပေါင်းဆုံး ef_search ကို ရှာပြီး သတ်မှတ်တာ အရေးကြီးပါတယ်။ pgvector မှာတော့ `SET hnsw.ef_search = 100;` လိုမျိုး ချိန်နိုင်ပါတယ်။

## Subtopic ၄ — Index Memory တွက်နည်း

### ဘာကို ဆိုလိုတာလဲ

Index memory က HNSW graph ထဲမှာ vector တွေနဲ့ link တွေကို သိမ်းဖို့ လိုတဲ့ byte အရေအတွက်ပါ။ ကြမ်းတမ်းတွက်လို့ ရပါတယ်။

### ဘာကြောင့် လဲ

RAM မလုံလောက်ရင် index မတည်ဆောက်နိုင်ပါ။ ကြိုတွက်နိုင်ရင် hardware စီမံကိန်း တိကျမှ စရိတ်သက်သာပါတယ်။ Faiss wiki မှာ graph structure တစ်ခုမှာ link တွေကို integer တွေနဲ့ သိမ်းတယ်လို့ ဖော်ပြထားပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Vector data memory = N × dim × bytes-per-value နဲ့ တွက်ပါတယ်။
၂။ Link memory = N × M × 2 (လမ်းနှစ်ဖက်၊ integer တစ်ခုစီ) နဲ့ ခန့်မှန်းပါတယ်။
၃။ နှစ်ခုပေါင်းပြီး ကြမ်းတမ်းအရွယ်အစား ထုတ်ပါတယ်။

### ဥပမာ

```python
# Assumption (clearly labelled): 1,000,000 vectors, 768 dims, fp32 (4 bytes),
# m = 16, link stored as 4-byte integers, bidirectional (x2).

n = 1_000_000
dim = 768
bytes_per_float = 4
m = 16
bytes_per_int = 4

vector_bytes = n * dim * bytes_per_float
link_bytes = n * m * 2 * bytes_per_int
total = vector_bytes + link_bytes

print("vectors:", vector_bytes / 1e9, "GB")
print("links:  ", link_bytes / 1e9, "GB")
print("total: ", total / 1e9, "GB (approximate, before OS overhead)")
# Expected output:
# vectors: 3.072 GB
# links:   0.128 GB
# total:  3.2 GB (approximate, before OS overhead)
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

pgvector မှာ vector ကတစ်ခါတည်း column ထဲ သိမ်းတဲ့အတွက် index နဲ့ table နှစ်ခုလုံးရဲ့ အရွယ်ကို တွက်ရပါမယ်။ fp32 အစား half-precision ဒါမှမဟုတ် dimension လျှော့တာတွေက memory သက်သာစေနိုင်ပါတယ်။

## Subtopic ၅ — Delete/Update နဲ့ Filtered Search ရဲ့ သက်ရောက်မှု

### ဘာကို ဆိုလိုတာလဲ

HNSW က append လုပ်တာ အားနာပြီး၊ point ဖျက်တာက အားနာပါတယ်။ Faiss မှာ dead node တွေကို filter list နဲ့ ချန်ထားတတ်ပါတယ်။ Filtered search က query မှာ condition (ဥပမာ `WHERE category = 'news'`) ပေါ် မူတည်ပြီး candidate လျှော့တာပါ။

### ဘာကြောင့် လဲ

Graph node တစ်ခု ဖျက်လိုက်ရင် ချိတ်ဆက်ချက်တွေ ပျက်ပြီး ရှာဖွေလမ်းကြောင်း ရှုပ်နိုင်ပါတယ်။ ဒါကြောင့် point တွေကို တကယ်ဖျက်ထုတ်ဖို့အစား mark လုပ်ပြီး နောက်မှ rebuild လုပ်တာ ပိုများပါတယ်။ Filter ကများရင်လည်း ကျန် candidate နည်းသွားပြီး recall ကျတတ်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Delete လုပ်ချင်တဲ့ point ကို dead list ထဲ ထည့်ပါတယ်။
၂။ Search လုပ်တဲ့အခါ dead list ထဲပါရင် ခဏ skip လုပ်ပါတယ်။
၃။ Dead များလာရင် index အသစ် rebuild လုပ်ပါတယ်။
၄။ Filtered search မှာ filter ကို ကျော်လွန်တဲ့ candidate တွေကို ထည့်တွက်ပါတယ်။

### ဥပမာ

```python
# Simplified dead-marker + filtered search demo (standard library only).
# pgvector does deletion via standard DELETE + VACUUM; this is the concept.

data = [("chunk1", 0.9), ("chunk2", 0.8), ("chunk3", 0.7), ("chunk4", 0.6)]
dead = {"chunk2"}          # marked deleted, not removed from graph
category = {"chunk1": "news", "chunk2": "news", "chunk3": "blog", "chunk4": "news"}

def search(k, want):
    results = []
    for name, score in data:          # walk order = our stand-in "graph path"
        if name in dead:
            continue                  # skip dead node
        if category[name] != want:
            continue                  # filter applied during search
        results.append((score, name))
        if len(results) == k:
            break
    return results

print(search(2, "news"))
# Expected output:
# [(0.9, 'chunk1'), (0.6, 'chunk4')]
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

pgvector မှာ update လုပ်ဖို့ အလွယ်ဆုံးလမ်းက row အသစ် insert ပြီး အဟောင်း delete တာပါ။ RAG pipeline မှာ document တွေ မကြာခဏ ပြောင်းလဲရင် index rebuild plan လိုပါတယ်။ Filter များတဲ့ use case မှာ `hnsw.iterative_scan` စတာတွေကို pgvector documentation မှာ ဖတ်ကြည့်ပါ။

## အနှစ်ချုပ်

- HNSW က multi-layer graph ပါ — အပေါ် layer က အဝေးခုန်၊ အောက် layer က အနီးရှာပါ။
- `m` က connection နယ်နိမိတ်၊ `ef_construction` က build အရည်အသွေးပါ — များရင် build နှေးပြီး memory တက်ပါတယ်။
- `ef_search` က query အချိန်မှာ recall နဲ့ latency ကို ချိန်ပါတယ်။
- Memory က vector data (N × dim × bytes) နဲ့ link တွေ နှစ်ခါ ပေါင်းပြီး ခန့်မှန်းလို့ ရပါတယ်။
- Delete/update က graph ကို ပျက်စေနိုင်တာကြောင့် dead-marking နဲ့ rebuild နည်းတွေ သုံးပါတယ်။
- Filtered search မှာ candidate နည်းသွားရင် recall ကျတတ်တာကို သတိထားပါ။

**Official sources:** [HNSW paper](https://arxiv.org/abs/1603.09320) · [pgvector](https://github.com/pgvector/pgvector) · [Faiss wiki](https://github.com/facebookresearch/faiss/wiki)
