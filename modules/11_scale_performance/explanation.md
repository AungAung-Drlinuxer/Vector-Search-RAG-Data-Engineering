# M11 — Scale နှင့် Performance: Quantization၊ Sharding၊ Rebuild နှင့် Write Throughput

ဒီ module မှာ vector search ကို data အရမ်းများလာတဲ့အခါ ဘယ်လို မြန်အောင်၊ memory သက်သက်သာအောင် လုပ်နိုင်တယ် ဆိုတာကို လေ့လာရမယ်ပါ။ အရင်ဆုံး ဘာကြောင့် ဒီနေရာကို မလေ့လာပဲ မဖြစ်နိုင်တဲ့ အခြေအနေတွေ ရှိနေလို့ပါပဲ။

> ဒီစာစုအုပ်က တရားဝင် open documentation (arxiv, Qdrant docs, FAISS wiki, pgvector GitHub) တွေကနေ ရေးထားတဲ့ original သင်ခန်းစာပါ။ လမ်းညွှန်အားဖြင့် database ချိတ်ဆက်ပြီး run မှာ မဟုတ်ဘူးနော်။ အားလုံးကို Python standard library နဲ့ offline သာ လုပ်ပါမယ်။

## Subtopic 1 — Quantization ဆိုတာ ဘာလဲ

### ဘာကို ဆိုလိုတာလဲ

Quantization (quantization — vector ထဲက ကိန်းတွေကို ပိုသေးတဲ့ ပုံစံနဲ့ သိမ်းတဲ့နည်း) က vector memory အရွယ်ကို လျှော့ပေးတဲ့ နည်းပါတယ်။ Scalar quantization က float32 (32 bit) အစား int8 (8 bit) သို့မဟုတ် binary (1 bit) နဲ့ သိမ်းတာပါ။ Product Quantization (PQ) က dimension တွေကို အပိုင်းခွဲပြီး အပိုင်းတိုင်းကို codebook (codebook — ကိန်းအစုကို ကိုယ်စားပြတဲ့ စာရင်း) နဲ့ သိမ်းတာပါ။

### ဘာကြောင့် လဲ

Vector တစ်ခုက fp32 မှာ dimension တစ်ခုကို 4 byte ယူပါတယ်။ Chunk တစ်သန်း၊ dimension 768 ရှိရင် memory က ကြီးလွန်းသွားပြီး server တစ်လုံးထဲ မဆံ့တော့ပါဘူး။ Quantization မလုပ်ဘူးဆိုရင် hardware ဈေးကြီးလို့ စရိတ်တက်သွားပြီး search ရဲ့ အရေအတွက်ကိုလည်း ကန့်သတ်ရတယ်ပါ။ Jégou et al. ရဲ့ PQ စာတမ်း (https://arxiv.org/abs/0903.2314) မှာ ဒီ memory problem ကို အဓိက ဖြေရှင်းခဲ့တာပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Vector ရဲ့ တန်ဖိုးတွေကို ပြောင်းလို့ရတဲ့ ပုံစံနည်းနည်းထဲ ရောက်အောင် လုပ်ပါတယ်။
၂။ Scalar quantization မှာ float တန်ဖိုးကို int အဆင့်ထဲ မြှောက်ပြီး သိမ်းပါတယ်။
၃။ Binary quantization မှာ ပုစ္ဆာသင်္ချာသဘောနဲ့ အနှုတ်/အပေါင်း သာ သိမ်းပါတယ်။
၄။ PQ မှာ dimension တွေကို subvector အပိုင်းလိုက် ခွဲပါတယ်။
၅။ Subvector တိုင်းကို အနီးဆုံး centroid (centroid — အလယ်က ကိုယ်စားကိန်း) တစ်ခုနဲ့ ရည်ညွှန်းပါတယ်။
၆။ Memory သက်သာပေမယ့် recall နည်းနိုင်တဲ့ အပေးအယူ ရှိတယ်ဆိုတာကို လက်ခံရပါမယ်။

### ဥပမာ

```python
# Scalar quantization: pack a float32 vector into int8 levels.
# Assumption: all values lie in [-1.0, 1.0] (cosine-normalized vectors).
import math

vec = [0.31, -0.92, 0.05, -0.44, 0.77]  # float32 values, 5 dims

levels = 127  # int8 range is -128..127; we use -127..127 symmetric
def quantize(x):
    return max(-levels, min(levels, round(x * levels)))

q = [quantize(x) for x in vec]
# Dequantize back (approximate reconstruction)
dq = [v / levels for v in q]
err = sum(abs(a - b) for a, b in zip(vec, dq)) / len(vec)

bytes_before = 4 * len(vec)   # fp32: 4 bytes per dim
bytes_after  = 1 * len(vec)    # int8: 1 byte per dim
print("quantized:", q)
print("mean abs error: %.4f" % err)
print("memory: %d bytes -> %d bytes (x%.1f smaller)" %
      (bytes_before, bytes_after, bytes_before / bytes_after))
# Expected output:
# quantized: [39, -117, 6, -56, 98]
# mean abs error: 0.0019
# memory: 20 bytes -> 5 bytes (x4.0 smaller)
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Qdrant ရဲ့ quantization guide (https://qdrant.tech/documentation/guides/quantization/) မှာ scalar, binary, product quantization သုံးမျိုးလုံးကို တရားဝင် support လုပ်တယ်လို့ ပြောထားပါတယ်။ Memory ၄ ဆ သက်သာရင် တကယ့် production မှာ hardware စရိတ် သိသိသာသာ ကျသွားနိုင်ပါတယ်။ ဒါပေမယ့် တိကျမှု နည်းနည်းလေ စျေးသက်သာမှု များများ ဆိုတဲ့ အပေးအယူကို နားလည်ဖို့ အရေးကြီးပါတယ်နော်။

## Subtopic 2 — Memory နဲ့ Recall ရဲ့ အပေးအယူ

### ဘာကို ဆိုလိုတာလဲ

Recall (recall — မှန်တဲ့အဖြေတွေကို ဘယ်နှုန်းထက်ထက် ပြန်တွေ့တယ် ဆိုတဲ့ အညွှန်း) နဲ့ memory usage က တစ်ခုတည်း မဟုတ်ပါ။ Quantization ပြင်းရင် memory ကျပေမယ့် အချို့အဖြေတွေ ပျောက်သွားနိုင်ပါတယ်။ ဒါကြောင့် oversampling (oversampling — လိုအပ်တဲ့ထက် ပိုရှာပြီး နောက်မှ ပြန်စစ်တဲ့နည်း) သုံးတတ်ပါတယ်။

### ဘာကြောင့် လဲ

Quantize လုပ်ပြီးတဲ့နောက် ကိန်းတွေ ပြောင်းသွားလို့ ရှေ့မှာတုံးတူမတူတော့ပါဘူး။ ဒါကြောင့် ပျောက်တဲ့အဖြေတွေ ရှိလာပြီး recall ကျနိုင်ပါတယ်။ Qdrant docs က quantization သုံးရင် `search` မှာ `oversampling` parameter နဲ့ ပိုရှာပြီး re-scoring လုပ်ဖို့ အကြံပေးထားပါတယ်။ Memory ကို တစ်ဖက်တစ်ချက်ကြည့်ပြီး မှန်တဲ့အဖြေ ဘယ်လောက်ရမလဲ ဆုံးဖြတ်ရတာ အရေးကြီးပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Quantized representation နဲ့ ရှေ့ဆုံး candidate တွေကို များများ ဆွဲထုတ်ပါတယ်။
၂။ Candidate တိုင်းရဲ့ original full vector (fp32) ကို ပြန်ထုတ်ပါတယ်။
၃။ Full vector တွေနဲ့ exact score ပြန်တွက်ပါတယ်။
၄။ Top-k ကို ပြန်ရွေးပါတယ်။
၅။ Oversampling များရင် recall တက်ပေမယ့် latency တက်ပါတယ်နော်။

### ဥပမာ

```python
# Show recall drop from quantization, then recover it with oversampling.
import random

random.seed(42)  # deterministic
D = 8
vecs = [[random.uniform(-1, 1) for _ in range(D)] for _ in range(200)]
query = [random.uniform(-1, 1) for _ in range(D)]

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def topk_indices(vectors, q, k):
    scores = sorted(range(len(vectors)), key=lambda i: -dot(vectors[i], q))
    return scores[:k]

# Baseline: exact top-5 on fp32 vectors
exact = topk_indices(vecs, query, 5)

# Binary quantization: keep only the sign of each dim
def bquant(v):
    return [1 if x >= 0 else -1 for x in v]

bvecs = [bquant(v) for v in vecs]
bquery = bquant(query)

def recall_at_k(found, truth):
    return len(set(found) & set(truth)) / len(truth)

for over in (1, 2, 4):  # oversampling factor: fetch k*over then re-score
    cand = topk_indices(bvecs, bquery, 5 * over)          # rough ranking
    resc = sorted(cand, key=lambda i: -dot(vecs[i], query))  # re-score fp32
    print("oversampling=%d  recall@5 = %.2f" % (over, recall_at_k(resc[:5], exact)))
# Expected output:
# oversampling=1  recall@5 = 0.20
# oversampling=2  recall@5 = 0.40
# oversampling=4  recall@5 = 0.60
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Qdrant docs မှာ quantization သုံးတဲ့အခါ re-scoring အတွက် original vectors ထားပြီး oversampling ဆိုတဲ့ နည်းလမ်းကို တရားဝင် ဖော်ပြထားပါတယ်။ ဒီဥပမာက အဲဒီသဘောကို offline Python နဲ့ ပြထားတာပါ။ Production မှာ recall budget နဲ့ memory budget နှစ်ခုလုံးကို တစ်ပြိုင်တည်း ညှိရပါတယ်။

## Subtopic 3 — Product Quantization (PQ) အခြေခံ

### ဘာကို ဆိုလိုတာလဲ

PQ (Product Quantization — vector တစ်ခုကို အပိုင်းခွဲပြီး အပိုင်းတိုင်းကို codebook နဲ့ သိမ်းတဲ့နည်း) က Jégou et al. 2011 စာတမ်း (https://arxiv.org/abs/0903.2314) က မိတ်ဆက်ခဲ့တဲ့ နည်းပါတယ်။ FAISS wiki (https://github.com/facebookresearch/faiss/wiki) မှာလည်း `IndexIVFPQ` လိုမျိုးတွေနဲ့ တရားဝင် support လုပ်ပါတယ်။

### ဘာကြောင့် လဲ

Scalar quantization က တစ်ချည်းချည်း ၄ ဆပဲ သက်သာပါတယ်။ PQ က codebook id (ဥပမာ — 8 bit) တစ်ခုနဲ့ subvector တစ်ခုလုံးကို ကိုယ်စားပြလို့ compression ratio က ပိုကြီးပါတယ်။ ဥပမာ — 768 dim, fp32 vector တစ်ခုက 3072 byte ယူပေမယ့် PQ မှာ subvector 96 ခု၊ id တစ်ခုကို 1 byte ဆိုရင် 96 byte ပဲ ယူပါတယ်။ ဒါက ၃၂ ဆ သက်သာတာပါပဲ။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Vector ရဲ့ dimension တွေကို `m` ခု တန်းတူအပိုင်းလိုက် ခွဲပါတယ်။
၂။ အပိုင်းတိုင်းအတွက် centroid 256 ခု နဲ့ codebook တစ်ခု တည်ဆောက်ပါတယ်။
၃။ Vector တစ်ခုချင်းစီကို subvector တိုင်းရဲ့ အနီးဆုံး centroid id တွေနဲ့ encode လုပ်ပါတယ်။
၄။ Search မှာ encode ထားတဲ့ ကိန်းတွေနဲ့ approximate distance တွက်ပါတယ်။

### ဥပမာ

```python
# Tiny PQ demo: split dims into 2 subvectors, use 4 centroids each.
import random, math

random.seed(7)
D, M = 6, 2          # 6 dims, 2 subvectors of 3 dims each
sub = D // M
vecs = [[random.uniform(-1, 1) for _ in range(D)] for _ in range(60)]

def kmeans(points, k=4, iters=10):
    cents = points[:k]
    for _ in range(iters):
        assign = []
        for p in points:
            d = [sum((a - b) ** 2 for a, b in zip(p, c)) for c in cents]
            assign.append(d.index(min(d)))
        new = []
        for j in range(k):
            grp = [p for p, a in zip(points, assign) if a == j]
            if grp:
                new.append([sum(col) / len(grp) for col in zip(*grp)])
            else:
                new.append(cents[j])
        cents = new
    return cents

codebooks = []
for s in range(M):
    subpts = [v[s * sub:(s + 1) * sub] for v in vecs]
    codebooks.append(kmeans(subpts))

def encode(v):
    ids = []
    for s in range(M):
        sv = v[s * sub:(s + 1) * sub]
        d = [sum((a - b) ** 2 for a, b in zip(sv, c)) for c in codebooks[s]]
        ids.append(d.index(min(d)))
    return ids

sample = vecs[0]
code = encode(sample)
# memory per vector: fp32 = D*4 bytes; PQ = M*1 byte here
print("PQ code for vec[0]:", code)
print("memory: %d bytes -> %d bytes (x%.1f smaller)" % (D * 4, M, (D * 4) / M))
# Expected output:
# PQ code for vec[0]: [0, 0]
# memory: 24 bytes -> 2 bytes (x12.0 smaller)
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

FAISS wiki မှာ PQ က memory အများဆုံးသက်သာတဲ့ option အဖြစ် ဖော်ပြထားပြီး `m` နဲ့ `nbits` ရွေးချယ်မှုအပေါ် မူတည်ပါတယ်။ Recall က အခြေအနေပေါ် ကျနိုင်တာကြောင့် ကိုယ့် dataset နဲ့ စမ်းကြည့်ပြီး codebook အရွယ် ရွေးရပါတယ်။

## Subtopic 4 — Dimension ဖြတ်ခြင်း နဲ့ တခြား compression နည်းတွေ

### ဘာကို ဆိုလိုတာလဲ

Dimension reduction (dimension reduction — vector ရဲ့ dimension အရေအတွက်ကို လျှော့တဲ့နည်း) က memory နဲ့ compute နှစ်ခုလုံး သက်သာစေပါတယ်။ PQ မှာ subvector အပိုင်းရေ `m` ကို လျှော့တာဟာလည်း ဒီနည်းနဲ့ တူတူ ဆင်တာပါပဲ။

### ဘာကြောင့် လဲ

Distance တွက်တဲ့အခါ dimension တိုင်းကို မြှောက်ပေါင်းရပါတယ်။ Dimension တိုလျှင် latency တိုပါတယ်။ ဒါပေမယ့် အချက်အလက် ဆုံးရှုံးမှု ရှိလာပြီး recall ကျနိုင်ပါတယ်။ ဒီနေရာမှာလည်း အပေးအယူ ရှိတယ်ဆိုတာ မမေ့ပါနော်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Vector တွေရဲ့ အရေးကြီးတဲ့ direction တွေကို ဖော်ပြပါတယ်။
၂။ အရေးမကြီးတဲ့ component တွေကို ချန်ပစ်ပါတယ်။
၃။ ကျန်တဲ့ component တွေနဲ့ပဲ ရှာပါတယ်။
၄။ ကျန်ခဲ့တဲ့အချက်အလက်ကြောင့် recall ဘယ်လောက်ထိခိုက်လဲ တိုင်းပါတယ်။

### ဥပမာ

```python
# Simple dimension truncation: keep only the first half of dims.
import random

random.seed(3)
D = 8
vecs = [[random.uniform(-1, 1) for _ in range(D)] for _ in range(50)]
query = [random.uniform(-1, 1) for _ in range(D)]

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def topk(vs, q, k):
    return sorted(range(len(vs)), key=lambda i: -dot(vs[i], q))[:k]

exact = topk(vecs, query, 5)
half = D // 2
trunc_vecs = [v[:half] for v in vecs]
trunc_query = query[:half]
approx = topk(trunc_vecs, trunc_query, 5)
r = len(set(exact) & set(approx)) / 5
print("exact top5 :", exact)
print("trunc top5 :", approx)
print("recall@5 = %.2f" % r)
# Expected output:
# exact top5 : [30, 37, 24, 27, 7]
# trunc top5 : [7, 9, 27, 24, 40]
# recall@5 = 0.60
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Qdrant docs မှာ တစ်ဖက်က quantization နဲ့ တစ်ဖက်က indexing level (HNSW graph) တွေ ပေါင်းစပ်သုံးတဲ့ နည်းကို ပြောထားပါတယ်။ Memory budget တစ်ခုထဲ အပိုင်းတွေကို ဘယ်လိုခွဲမလဲ ဆိုတာ ဒီမှာလည်း အတူတူပါပဲ။ Model ကိုရွေးတဲ့အခါ သူ့ embedding ရဲ့ dimension အရွယ် ကြိုတွက်ထားဖို့ အရေးကြီးပါတယ်။

## Subtopic 5 — Sharding၊ Index Rebuild နဲ့ Write Throughput

### ဘာကို ဆိုလိုတာလဲ

Sharding (sharding — data တွေကို server အများအပြားထဲ ကျဲထည့်တဲ့နည်း) က data တစ်ခုတည်း မဆံ့တော့တဲ့အခါ အလုပ်ခွဲယူဖို့ သုံးပါတယ်။ Index rebuild (rebuild — ဒေတာအားလုံးပြန်စုပြီး index အသစ်တည်ဆောက်တဲ့အလုပ်) နဲ့ bulk load ရဲ့ နည်းလမ်းတွေကလည်း ဒီဇိုးရီမှာ ထိုင်ပါတယ်။

### ဘာကြောင့် လဲ

Index တစ်ခုကို insert တစ်ခုချင်းနဲ့ တည်ဆောက်ရင် တစ်ခုနဲ့တစ်ခု ကြားမှာ လမ်းကြောင်းတွေ ထပ်တိုးရလို့ အလုပ်များပါတယ်။ Data အားလုံးကို အရင်တင်ပြီးမှ index ဆောက်ရင် (build after load) အမြန်ဆုံး ဖြစ်ပါတယ်။ pgvector README (https://github.com/pgvector/pgvector#performance) မှာလည်း data load ပြီးမှ index create လုပ်ဖို့ အကြံပေးထားပါတယ်။ Server တစ်လုံးကို data တစ်ခုတည်း များလာရင် memory နဲ့ QPS (QPS — စက္ကန့်တစ်ခါမှာ မေးခွန်း ဘယ်နှစ်ခု အဖြေပေးနိုင်လဲ) ကို မတက်နိုင်တော့ပါဘူး။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Data တွေကို shard key (shard key — ဒေတာတစ်ခု ဘယ် server ထဲ သွားမလဲ ဆုံးဖြတ်ပေးတဲ့ သော့) နဲ့ ခွဲပါတယ်။
၂။ ရှာတဲ့အခါ shard တိုင်းကို ဝင်ရှာပြီး အဖြေတွေ ပြန်ပေါင်းပါတယ်။
၃။ Bulk load မှာ ဒေတာအားလုံးကို အရင်တင်ပါတယ်။
၄။ Index ကို ဒေတာအားလုံး ပြီးမှ တည်ဆောက်ပါတယ်။
၅။ ရံဖန်ရံခါ index ကို rebuild လုပ်ပြီး အင်မြင်ခံကောင်းအောင် ထိန်းပါတယ်။

### ဥပမာ

```python
# Shard vectors across 3 "servers" (simulated with lists) and merge results.
import random

random.seed(11)
D = 6
all_vecs = [[random.uniform(-1, 1) for _ in range(D)] for _ in range(30)]

N_SHARDS = 3
shards = [[] for _ in range(N_SHARDS)]
for i, v in enumerate(all_vecs):
    shards[i % N_SHARDS].append((i, v))  # simple round-robin sharding

query = [random.uniform(-1, 1) for _ in range(D)]
def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

# Search each shard, take local top-5, merge, take global top-5.
merged = []
for s in shards:
    local = sorted(s, key=lambda t: -dot(t[1], query))[:5]
    merged.extend(local)
global_top = sorted(merged, key=lambda t: -dot(t[1], query))[:5]
exact = sorted(range(len(all_vecs)), key=lambda i: -dot(all_vecs[i], query))[:5]
r = len(set(i for i, _ in global_top) & set(exact)) / 5
print("merged top5 ids:", [i for i, _ in global_top])
print("exact   top5 ids:", exact)
print("recall@5 = %.2f" % r)
# Expected output:
# merged top5 ids: [14, 13, 25, 17, 21]
# exact   top5 ids: [14, 13, 25, 17, 21]
# recall@5 = 1.00
```

```sql
-- pgvector: bulk load first, then build the index (build after load).
-- Valid PostgreSQL + pgvector; never executed by this lesson.
CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(768));
-- COPY is much faster than row-by-row INSERT for bulk loading.
-- COPY items (embedding) FROM '/path/to/vectors.csv' WITH (FORMAT csv);
-- Only after all data is loaded, create the index:
CREATE INDEX ON items USING hnsw (embedding vector_cosine_ops);
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

pgvector README မှာ တရားဝင် performance အကြံပေးချက်တွေနဲ့ benchmark နည်းလမ်းတွေ ထည့်ပေးထားပါတယ်။ ဒီအကြံပေးချက်တွေက "insert ပြီးသလို index update လုပ်" ထက် "load အားလုံးပြီးမှ index build" က မြန်တယ် ဆိုတဲ့သဘောပါ။ Sharding က system ကြီးလာတဲ့အခါ horizontal scaling (server ထပ်ထည့်ပြီး ခံနိုင်ရည်တက်အောင် လုပ်တဲ့နည်း) ရဲ့ အခြေခံ ဖြစ်ပါတယ်နော်။

## အနှစ်ချုပ်

- Quantization (scalar, binary, product) က vector memory ကို ၄ ဆ သို့မဟုတ် ၄ ဆထက်ပို သက်သာစေပါတယ်။
- Memory သက်သာလာရင် recall ကျနိုင်တဲ့ အပေးအယူ အမြဲရှိပါတယ်။
- Oversampling နဲ့ re-scoring က quantization ရဲ့ recall ပျောက်ဆုံးမှုကို ပြန်ဖြည့်ပေးပါတယ်။
- PQ က vector ကို subvector အပိုင်းလိုက် ကုဒ်နံပါတ်နဲ့ သိမ်းတဲ့နည်း ဖြစ်ပါတယ်။
- Dimension ဖြတ်ခြင်းက compute ပါ သက်သာစေပေမယ့် အချက်အလက် ဆုံးရှုံးမှု ရှိပါတယ်။
- Sharding က data ကို server အများထဲ ခွဲပြီး scale တက်စေပါတယ်။
- Build after load — ဒေတာအားလုံး အရင်တင်ပြီးမှ index တည်ဆောက်တာက write throughput အကောင်းဆုံး နည်းပါတယ်။
- တရားဝင် sources: https://arxiv.org/abs/0903.2314 , https://qdrant.tech/documentation/guides/quantization/ , https://github.com/facebookresearch/faiss/wiki , https://github.com/pgvector/pgvector#performance တို့ကို ဖတ်ကြည့်ဖို
