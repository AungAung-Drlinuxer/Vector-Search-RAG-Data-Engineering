# M4 — HNSW Index အတွင်းပိုင်း: Parameter၊ Recall နှင့် Memory

ဤ module တွင် HNSW (Hierarchical Navigable Small World) index ၏ အတွင်းပိုင်း mechanics ကို လေ့လာသည်။ အခြေခံ အချက်အလက်များကို [Malkov & Yashunin, 2016](https://arxiv.org/abs/1603.09320)၊ [pgvector](https://github.com/pgvector/pgvector) နှင့် [Faiss wiki](https://github.com/facebookresearch/faiss/wiki) တို့မှ ယူထားပြီး၊ official documentation များအပေါ် အခြေခံသည့် original လေ့လာစာ ဖြစ်သည်။ Database ကို runtime တွင် ချိတ်ဆက်ခြင်း မပြုဘဲ Python standard library ဖြင့် mechanics များကို ပြန်လည် တည်ဆောက်ပြသည်။

## Subtopic ၁ — Multi-layer Graph သဘောတရား

### ဘာကို ဆိုလိုတာလဲ

HNSW သည် layer ပေါင်းများစွာ ဆင့်ထားသော graph တစ်ခု ဖြစ်သည်။ Upper layer များတွင် node အနည်းငယ်သာ ပါဝင်ပြီး bottom layer တွင် node အားလုံး ပါဝင်သည်။ Query တစ်ခုကို uppermost layer မှ စတင်၍ layer တစ်ဆင့်ချင်း ဆင်း၍ ရှာဖွေသည်။

### ဘာကြောင့် လဲ

Node သန်းချီ ပါဝင်သော flat graph တစ်ခုတွင် greedy search တစ်ဆင့်ချင်း လျှောက်ရပါက hop အရေအတွက် များပြီး latency မြင့်သည်။ Layer ခွဲထားခြင်းဖြင့် sparse ဖြစ်သော upper layer တွင် အကွာအဝေး ခုန်ကျော်မှု ကြီးမားပြီး၊ dense ဖြစ်သော lower layer တွင် local refinement သာ လုပ်ရသဖြင့် စုစုပေါင်း hop အရေအတွက် လျော့ကျသည်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Node တိုင်းကို bottom layer (layer 0) တွင် ထည့်သည်။
၂။ Node တစ်ခု၏ အမြင့်ဆုံး layer ကို exponential decay probability ဖြင့် ကျပန်း သတ်မှတ်သည် (paper ၏ layer assignment distribution)။
၃။ Search ကို အမြင့်ဆုံး layer ၏ entry point မှ စတင်သည်။
၄။ Layer တစ်ခုတွင် ရှာဖွေတွေ့ရှိသော အနီးဆုံး node ကို နောက် layer ၏ entry point အဖြစ် လွှဲပြောင်းသည်။
၅။ Bottom layer တွင် candidate အသေးစိတ် ရှာဖွေမှု ပြုလုပ်သည်။

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

pgvector တွင် `m` parameter နှင့် layer ဖွဲ့စည်းပုံက index ၏ graph topology ကို သတ်မှတ်ပြီး၊ upper layer များက search speed ကို အဓိက ထိန်းချုပ်သည်။ ဤ mechanics ကို နားလည်မှသာ parameter ကို မှန်ကန်စွာ ရွေးချယ်နိုင်သည်။

## Subtopic ၂ — M နှင့် ef_construction (Build Parameter)

### ဘာကို ဆိုလိုတာလဲ

`M` (Faiss တွင် `M`၊ pgvector တွင် `m`) သည် node တစ်ခု၏ neighbor connection အရေအတွက် upper bound ဖြစ်သည်။ `ef_construction` သည် build လုပ်စဉ် insertion တစ်ခုအတွက် ထားရှိမည့် candidate list ၏ အရွယ်အစား ဖြစ်သည်။

### ဘာကြောင့် လဲ

`M` နည်းပါက graph connectivity ကျဆင်းပြီး recall ကျသည်။ `M` များပါက memory footprint နှင့် build time တက်သည်။ `ef_construction` နည်းပါက neighbor ရွေးချယ်မှု မတိကျဘဲ graph quality ကျသည်။ များပါက build time တက်သည်။ ဤ parameter များသည် build quality နှင့် build cost ကြား ချိန်ညှိမှု ဖြစ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Node အသစ်တစ်ခု ထည့်သွင်းသည်။
၂။ အမြင့်ဆုံး layer မှ စ၍ greedy search ဖြင့် အနီးဆုံး node ကို ရှာသည်။
၃။ `ef_construction` အရွယ်အစားအထိ candidate စုဆောင်းသည်။
၄။ အနီးဆုံး `M` ခုကို neighbor edge အဖြစ် ယူသည်။
၅။ Neighbor အရေအတွက် upper bound ကျော်လွန်ပါက edge များကို ပြန်လည် ဖြတ်တောက်သည်။

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

pgvector documentation အရ `m` default သည် 16၊ `ef_construction` default သည် 64 ဖြစ်သည်။ `m` တိုးပါက index size တက်ပြီး recall တက်နိုင်သည်။ Dataset size နှင့် latency requirement အပေါ် အခြေခံ၍ ရွေးချယ်ရသည်။

## Subtopic ၃ — ef_search၊ Recall နှင့် Latency

### ဘာကို ဆိုလိုတာလဲ

`ef_search` (Faiss တွင် `efSearch`၊ pgvector တွင် `hnsw.ef_search`) သည် query-time search တွင် ထားရှိမည့် candidate list ၏ အရွယ်အစား ဖြစ်သည်။ Recall@k (top-k ရလဒ်တွင် ground truth ပါဝင်မှု အချိုး) သည် ef_search တိုးသည်နှင့်အမျှ တက်သည်။

### ဘာကြောင့် လဲ

ef_search နည်းပါက evaluate လုပ်သော node အရေအတွက် နည်းပြီး latency နိမ့်သော်လည်း true neighbor များ လွတ်သွားနိုင်သည်။ ef_search များပါက recall တက်သော်လည်း query latency တက်သည်။ ဤသည်မှာ accuracy နှင့် speed ကြား trade-off ဖြစ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Query vector ကို ယူသည်။
၂။ Search တွင် ef_search အရွယ်အစားရှိ candidate list ထိန်းထားသည်။
၃။ Candidate list ထဲမှ top-k ကို ထုတ်ပြန်သည်။
၄။ Ground truth နှင့် နှိုင်းယှဉ်၍ recall@k တွက်ချက်သည်။

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

Faiss wiki အရ `efSearch` တိုးပါက recall တက်ပြီး search time လည်း တက်သည်။ Production တွင် target recall အတွက် ef_search ကို တိုင်းတာ၍ သတ်မှတ်ရသည်။ pgvector တွင် `SET hnsw.ef_search = 100;` ဖြင့် session-level ချိန်ညှိနိုင်သည်။

## Subtopic ၄ — Index Memory တွက်နည်း

### ဘာကို ဆိုလိုတာလဲ

Index memory ဆိုသည်မှာ HNSW graph အတွင်း vector data နှင့် link data သိမ်းဆည်းရန် လိုအပ်သော byte ပမာဏ ဖြစ်ပြီး အကြမ်းဖျင်း ခန့်မှန်း တွက်ချက်နိုင်သည်။

### ဘာကြောင့် လဲ

maintenance_work_mem မလုံလောက်ပါက index build သည် disk spill ဖြစ်ပြီး build time သိသိသာသာ တိုးမည်။ ကြိုတင် တွက်ချက်နိုင်ပါက hardware sizing တိကျပြီး ကုန်ကျစရိတ် သက်သာသည်။ Faiss wiki အရ graph structure တွင် link များကို integer အဖြစ် သိမ်းဆည်းသည်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Vector data memory = N × dim × bytes-per-value။
၂။ Link memory = N × M × 2 (bidirectional edge၊ integer တစ်ခုစီ) ဟု ခန့်မှန်းသည်။
၃။ နှစ်ခု ပေါင်း၍ စုစုပေါင်း အရွယ်အစား ခန့်မှန်းသည်။

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

pgvector တွင် vector များကို table column တစ်ခုတည်း၌ သိမ်းဆည်းသဖြင့် storage estimation သည် table data နှင့် index structure နှစ်ခုလုံးကို ထည့်သွင်းတွက်ချက်ရသည်။ fp32 အစား half-precision သုံးခြင်း သို့မဟုတ် dimension လျှော့ချခြင်းဖြင့် memory footprint လျှော့ချနိုင်သည်။

## Subtopic ၅ — Delete/Update နှင့် Filtered Search ရဲ့ သက်ရောက်မှု

### ဘာကို ဆိုလိုတာလဲ

HNSW index တွင် insert ထက် delete က ပိုမို ရှုပ်ထွေးပြီး overhead များသည်။ Faiss သည် dead node များကို filter list ဖြင့် search မှ ချန်လှပ်ထားသည်။ Filtered search ဆိုသည်မှာ query ၏ condition (ဥပမာ `WHERE category = 'news'`) အပေါ် မူတည်၍ candidate စုကို ကန့်သတ်ခြင်း ဖြစ်သည်။

### ဘာကြောင့် လဲ

Graph node တစ်ခုကို ဖျက်လိုက်ပါက ၎င်း၏ edge များ ပျက်ပြီး search path connectivity ထိခိုက်နိုင်သည်။ ထို့ကြောင့် node များကို ချက်ချင်း မဖျက်ဘဲ dead mark လုပ်၍ နောက်ပိုင်းတွင် rebuild လုပ်သည့် နည်းလမ်းက ပိုများသည်။ Filter selectivity မြင့်ပါက ကျန်ရှိသော candidate နည်းသွားပြီး recall ကျဆင်းနိုင်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Delete လုပ်မည့် node ကို dead list ထဲ ထည့်သည်။
၂။ Search အတွင်း dead list ပါဝင်သော node ကို skip လုပ်သည်။
၃။ Dead node အချိုးအစား မြင့်လာပါက index ကို rebuild လုပ်သည်။
၄။ Filtered search တွင် filter condition ကို ကျော်သော candidate များကိုသာ ထည့်သွင်းသည်။

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

pgvector တွင် update လုပ်ရန် လက်တွေ့ကျသော နည်းလမ်းမှာ row အသစ် insert ပြီး အဟောင်းကို delete လုပ်ခြင်း ဖြစ်သည်။ RAG pipeline တွင် document များ မကြာခဏ ပြောင်းလဲပါက index rebuild plan လိုအပ်သည်။ Filter များသော use case အတွက် `hnsw.iterative_scan` ကဲ့သို့သော feature များကို pgvector documentation တွင် ဖတ်ရှုသင့်သည်။

## အနှစ်ချုပ်

- HNSW သည် multi-layer graph ဖြစ်သည် — upper layer တွင် အကွာအဝေး ခုန်ကျော်၊ lower layer တွင် local search ပြုလုပ်သည်။
- `m` သည် connection upper bound၊ `ef_construction` သည် build quality parameter — တိုးပါက build time နှင့် memory တက်သည်။
- `ef_search` သည် query-time တွင် recall နှင့် latency ကို ချိန်ညှိသည်။
- Memory ကို vector data (N × dim × bytes) နှင့် link data (bidirectional) ပေါင်း၍ ခန့်မှန်းနိုင်သည်။
- Delete/update သည် graph connectivity ကို ထိခိုက်စေသဖြင့် dead-marking နှင့် rebuild နည်းလမ်းများ သုံးသည်။
- Filtered search တွင် candidate နည်းသွားပါက recall ကျဆင်းနိုင်သည်။

**Official sources:** [HNSW paper](https://arxiv.org/abs/1603.09320) · [pgvector](https://github.com/pgvector/pgvector) · [Faiss wiki](https://github.com/facebookresearch/faiss/wiki)