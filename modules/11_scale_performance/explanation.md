# M11 — Scale နှင့် Performance: Quantization၊ Sharding၊ Rebuild နှင့် Write Throughput

ဒီ module တွင် vector collection အရွယ်အစား ကြီးလာချိန်၌ search latency နှင့် memory footprint ကို မည်သို့ ထိန်းချုပ်သည်ကို လေ့လာသည်။ Collection ကြီးထွားမှုနှင့်အတူ memory cost နှင့် index maintenance cost နှစ်ခုလုံး scale လိုက်ပါကြီးမားလာသဖြင့် ဒီခေါင်းစဉ်သည် production vector system တိုင်းအတွက် မလွဲမသွေ လိုအပ်သည်။

> ဒီစာစုအုပ်က တရားဝင် open documentation (arxiv, Qdrant docs, FAISS wiki, pgvector GitHub) တွေကနေ ရေးထားတဲ့ original သင်ခန်းစာပါ။ Database ချိတ်ဆက် run မည်မဟုတ်ဘဲ အားလုံးကို Python standard library ဖြင့် offline လုပ်ဆောင်သည်။

## Subtopic 1 — Quantization ဆိုတာ ဘာလဲ

### ဘာကို ဆိုလိုတာလဲ

Quantization ဆိုသည်မှာ vector component တန်ဖိုးများ၏ numerical precision လျှော့ချ၍ memory footprint သက်သာအောင် သိမ်းဆည်းသည့် နည်းလမ်းဖြစ်သည်။ Scalar quantization တွင် float32 (32 bit) အစား int8 (8 bit) သို့မဟုတ် binary (1 bit) ဖြင့် သိမ်းသည်။ Product Quantization (PQ) တွင် dimension များကို subvector အဖြစ် ခွဲခြမ်းပြီး subvector တစ်ခုချင်းစီကို codebook ထဲရှိ centroid id ဖြင့် ကိုယ်စားပြု သိမ်းဆည်းသည်။

### ဘာကြောင့် လဲ

fp32 vector တစ်ခုသည် dimension တစ်ခုအတွက် 4 byte ယူသည်။ Chunk တစ်သန်း၊ dimension 768 ရှိပါက memory footprint သည် ~3 GB ရှိပြီး single-server RAM budget ကို ကျော်လွန်နိုင်သည်။ Quantization မလုပ်ပါက hardware cost မြင့်တက်ပြီး cache efficiency လည်း ကျဆင်းသဖြင့် search throughput ကန့်သတ်ချက် ဖြစ်လာသည်။ Jégou et al. ၏ PQ စာတမ်း (https://arxiv.org/abs/0903.2314) သည် ဤ memory problem ကို အဓိက ဖြေရှင်းချက်အဖြစ် တင်ပြထားသည်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Vector component တန်ဖိုးများကို ကိုယ်စားပြုနိုင်သော discrete level အရေအတွက် ကန့်သတ်ထားသည့် space သို့ map ပြောင်းသည်။
၂။ Scalar quantization တွင် float တန်ဖိုးကို integer level သို့ scale ပြောင်း၍ သိမ်းသည်။
၃။ Binary quantization တွင် component တစ်ခုချင်းစီ၏ လက္ခဏာ (sign) ကိုသာ 1 bit ဖြင့် သိမ်းသည်။
၄။ PQ တွင် dimension များကို subvector အဖြစ် အပိုင်းလိုက် ခွဲခြမ်းသည်။
၅။ Subvector တစ်ခုချင်းစီကို အနီးဆုံး centroid (cluster center) id ဖြင့် ကိုယ်စားပြုသည်။
၆။ Memory reduction နှင့် recall degradation သည် တိုက်ရိုက် trade-off ဖြစ်သည် — oversampling + re-scoring ဖြင့် ပြန်လည်ကောင်းမွန်အောင် လုပ်နိုင်သည်။

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

Qdrant ၏ quantization guide (https://qdrant.tech/documentation/guides/quantization/) တွင် scalar, binary, product quantization သုံးမျိုးလုံးကို တရားဝင် support လုပ်ကြောင်း ဖော်ပြထားသည်။ Memory ၄ ဆ သက်သာခြင်းသည် production scale တွင် hardware cost ကို တိုက်ရိုက် သက်ရောက်မှုရှိသည်။ Compression တိုးလေ၊ approximation error တိုးလေ ဖြစ်သောကြောင့် memory reduction နှင့် recall degradation ၏ trade-off ကို workload အလိုက် ချိန်ညှိရမည်။

## Subtopic 2 — Memory နဲ့ Recall ရဲ့ အပေးအယူ

### ဘာကို ဆိုလိုတာလဲ

Recall နှင့် memory usage သည် သီးခြား ချိန်ညှိရသော axis နှစ်ခုဖြစ်သည်။ Quantization aggressiveness နှင့် recall သည် trade-off ဆက်နွယ်မှုရှိသည် — compression မြင့်တင်လိုက်ပါက approximate distance တွင် ranking error များလာပြီး recall ကျဆင်းနိုင်သည်။ ဤကျဆင်းမှုကို oversampling (လိုအပ်သည်ထက် candidate ပိုဆွဲပြီး original vector ဖြင့် re-scoring ပြန်လုပ်သည့်နည်း) ဖြင့် ပြန်လည်ကောင်းမွန်အောင် လုပ်လေ့ရှိသည်။

### ဘာကြောင့် လဲ

Quantization ပြီးနောက် distance approximation တွင် error ရောဝင်လာသဖြင့် ranking order ပျက်ယွင်းနိုင်ပြီး true nearest neighbor များ top-k အပြင် ရောက်သွားကာ recall ကျဆင်းသည်။ Qdrant docs တွင် quantization သုံးပါက `search` ၌ `oversampling` parameter ဖြင့် candidate ပိုဆွဲ၍ re-scoring လုပ်ရန် အကြံပြုထားသည်။ Memory budget နှင့် recall target နှစ်ခုလုံးကို တစ်ပြိုင်နက် ချိန်ညှိဆုံးဖြတ်ရသည်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Quantized representation ဖြင့် candidate များကို oversampling factor ဖြင့် ပိုမိုဆွဲထုတ်သည်။
၂။ Candidate တစ်ခုချင်းစီ၏ original full-precision (fp32) vector ကို ပြန်ယူသည်။
၃။ Full vector များဖြင့် exact distance ပြန်တွက်သည်။
၄။ Re-score ပြီး candidate များထဲမှ top-k ကို ပြန်ရွေးသည်။
၅။ Oversampling factor မြင့်လေ recall မြင့်လေ၊ တစ်ဖက်တွင် latency နှင့် compute cost မြင့်လေ ဖြစ်သည်။

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

Qdrant docs တွင် quantization အသုံးပြုချိန်၌ original vector များကို re-scoring အတွက် ထားရှိပြီး oversampling ဖြင့် recall ပြန်လည်ကောင်းမွန်စေသည့် pattern ကို တရားဝင် ဖော်ပြထားသည်။ ဒီဥပမာက ထို mechanism ကို offline Python ဖြင့် ပြသထားခြင်းဖြစ်သည်။ Production တွင် recall budget နှင့် memory budget နှစ်ခုလုံးကို တစ်ပြိုင်နက် ချိန်ညှိရသည်။

## Subtopic 3 — Product Quantization (PQ) အခြေခံ

### ဘာကို ဆိုလိုတာလဲ

Product Quantization (PQ) သည် Jégou et al. 2011 စာတမ်း (https://arxiv.org/abs/0903.2314) တွင် မိတ်ဆက်ထားသော compression နည်းလမ်းဖြစ်သည်။ FAISS wiki (https://github.com/facebookresearch/faiss/wiki) တွင် `IndexIVFPQ` စသည့် index အမျိုးအစားများဖြင့် တရားဝင် support လုပ်ထားသည်။

### ဘာကြောင့် လဲ

Scalar quantization သည် fp32 → int8 အတွက် compression ratio ၄ ဆသာ ပေးနိုင်သည်။ PQ သည် subvector တစ်ခုလုံးကို codebook id တစ်ခု (ဥပမာ — 8 bit) ဖြင့် ကိုယ်စားပြုသဖြင့် compression ratio သိသိသာသာ ပိုမြင့်သည်။ ဥပမာ — 768 dim fp32 vector တစ်ခုသည် 3072 byte ယူသော်လည်း subvector 96 ခု၊ id တစ်ခုလျှင် 1 byte ဆိုပါက 96 byte သာ ယူသည် — ၃၂ ဆ သက်သာသည်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Vector ၏ dimension များကို `m` ခု တန်းတူ subvector အဖြစ် ခွဲခြမ်းသည်။
၂။ Subspace တစ်ခုချင်းစီအတွက် centroid 256 ခုပါ codebook တစ်ခု တည်ဆောက်သည်။
၃။ Vector တစ်ခုချင်းစီကို subvector တစ်ခုချင်းစီ၏ အနီးဆုံး centroid id ဖြင့် encode လုပ်သည်။
၄။ Search အချိန်တွင် code များပေါ်၌ approximate distance တွက်ချက်သည်။

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

FAISS wiki တွင် PQ ကို memory သက်သာမှု အမြင့်ဆုံး option အဖြစ် ဖော်ပြထားပြီး compression ပမာဏသည် `m` နှင့် `nbits` ရွေးချယ်မှုအပေါ် မူတည်သည်။ Dataset အလိုက် recall ကျဆင်းမှု မတူညီနိုင်သဖြင့် ကိုယ်ပိုင် dataset ပေါ်တွင် စမ်းသပ်ပြီး codebook configuration ရွေးချယ်ရမည်။

## Subtopic 4 — Dimension ဖြတ်ခြင်း နဲ့ တခြား compression နည်းတွေ

### ဘာကို ဆိုလိုတာလဲ

Dimension reduction သည် memory နှင့် compute နှစ်ခုလုံးကို တစ်ပြိုင်နက် သက်သာစေသည်။ PQ တွင် subvector အရေအတွက် `m` လျှော့ချခြင်းသည်လည်း အလားတူ compression axis တစ်ခုဖြစ်သည်။

### ဘာကြောင့် လဲ

Distance တွက်ချက်မှုသည် dimension တိုင်းအတွက် multiply-accumulate လုပ်ရသဖြင့် dimension လျော့လေ latency လျော့လေ ဖြစ်သည်။ တစ်ဖက်တွင် information ဆုံးရှုံးမှုကြောင့် ranking error ဖြစ်ပေါ်ပြီး recall ကျဆင်းနိုင်သည် — ဤနေရာတွင်လည်း compression နှင့် recall trade-off တည်ရှိသည်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Vector များ၏ အဓိက variance ရှိသော direction များကို ထိန်းသိမ်းသည်။
၂။ Contribution နည်းသော component များကို ဖယ်ရှားသည်။
၃။ ကျန်ရှိသော component များဖြင့်သာ search လုပ်သည်။
၄။ ဖယ်ရှားလိုက်သော information ကြောင့် recall မည်မျှထိခိုက်သည်ကို တိုင်းတာသည်။

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

Qdrant docs တွင် quantization နှင့် indexing level (HNSW graph) ကို ပေါင်းစပ်အသုံးပြုသည့် နည်းလမ်းကို ဖော်ပြထားသည်။ Memory budget တစ်ခုတည်းအတွင်း compression axis များကို မည်သို့ ခွဲဝေမည်ဆိုသည့် ဆုံးဖြတ်ချက်နှင့် အတူတူပင်ဖြစ်သည်။ Embedding model ရွေးချယ်ချိန်တွင် ၎င်း၏ output dimension ကြောင့် ဖြစ်ပေါ်မည့် memory footprint ကို ကြိုတင်တွက်ချက်ထားရမည်။

## Subtopic 5 — Sharding၊ Index Rebuild နဲ့ Write Throughput

### ဘာကို ဆိုလိုတာလဲ

Sharding ဆိုသည်မှာ data ကို node/server အများအပြားအကြား ခွဲဝေသိမ်းဆည်းသည့် နည်းလမ်းဖြစ်သည်။ Index rebuild နှင့် bulk load pattern များသည်လည်း ဤခေါင်းစဉ်အောက်တွင် အကျုံးဝင်သည်။

### ဘာကြောင့် လဲ

Index တစ်ခုကို insert တစ်ခုချင်းစီဖြင့် တည်ဆောက်ပါက insert တိုင်းတွင် index structure ပြန်လည် update လုပ်ရသဖြင့် per-insert cost မြင့်တက်သည်။ Data အားလုံးကို အရင်တင်ပြီးမှ index တည်ဆောက်ခြင်း (build after load) သည် အမြန်ဆုံး လမ်းကြောင်းဖြစ်သည်။ pgvector README (https://github.com/pgvector/pgvector#performance) တွင်လည်း data load ပြီးမှ index create လုပ်ရန် အကြံပြုထားသည်။ Server တစ်လုံးတည်းတွင် data များပြားလာပါက memory capacity ပြတ်လပ်ခြင်းနှင့် QPS (Queries Per Second) ကန့်သတ်ချက် ရောက်ခြင်းတို့ ဖြစ်ပေါ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Data ကို shard key (partition key) အလိုက် ခွဲဝေသည်။
၂။ Query အချိန်တွင် shard တိုင်း၌ search လုပ်ပြီး local result များကို merge လုပ်သည်။
၃။ Bulk load တွင် data အားလုံးကို အရင်တင်သည်။
၄။ Data load ပြီးဆုံးမှသာ index တည်ဆောက်သည်။
၅။ Index ကို ပုံမှန် rebuild လုပ်ပြီး query performance ကို ထိန်းသိမ်းသည်။

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

pgvector README တွင် တရားဝင် performance အကြံပြုချက်များနှင့် benchmark နည်းလမ်းများ ပါဝင်သည်။ ၎င်းအကြံပြုချက်များ၏ အနှစ်ချုပ်မှာ — insert တိုင်း၌ index update လုပ်ခြင်းထက် load အားလုံးပြီးမှ index build လုပ်ခြင်းက write throughput သိသိသာသာ ပိုမြန်သည်။ Sharding သည် system ကြီးထွားလာချိန်တွင် horizontal scaling (server အရေအတွက် တိုး၍ capacity တိုးချဲ့ခြင်း) ၏ အခြေခံဖြစ်သည်။

## အနှစ်ချုပ်

- Quantization (scalar, binary, product) သည် vector memory footprint ကို ၄ ဆ သို့မဟုတ် ထို့ထက်ပို၍ လျှော့ချပေးသည်။
- Memory reduction တိုင်းတွင် recall degradation ၏ trade-off အမြဲ ပါဝင်သည်။
- Oversampling နှင့် re-scoring သည် quantization ကြောင့် ဆုံးရှုံးသော recall ကို ပြန်လည်ကောင်းမွန်စေသည်။
- PQ သည် vector ကို subvector အလိုက် codebook id ဖြင့် encode လုပ်သည့် နည်းလမ်းဖြစ်သည်။
- Dimension reduction သည် compute ကိုပါ သက်သာစေသော်လည်း information ဆုံးရှုံးမှု ရှိသည်။
- Sharding သည် data ကို server အများအပြားအကြား ခွဲဝေ၍ scale တိုးစေသည်။
- Build after load — data အားလုံး တင်ပြီးမှ index တည်ဆောက်ခြင်းသည် write throughput အမြင့်ဆုံး pattern ဖြစ်သည်။
- တရားဝင် sources: https://arxiv.org/abs/0903.2314 , https://qdrant.tech/documentation/guides/quantization/ , https://github.com/facebookresearch/faiss/wiki , https://github.com/pgvector/pgvector#performance တို့ကို ဖတ်ရှုလေ့လာပါ။
