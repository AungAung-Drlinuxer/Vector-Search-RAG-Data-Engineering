## လေ့ကျင့်ခန်း ၁ — Memory size တွက်ခြင်း

Vector တစ်သန်း ၇၆၈ dimension ကို fp32 နဲ့သိမ်းရင် dimension တစ်ခုကို 4 bytes ယူလို့ ၃ ဘီလီယံနီးပါး ဖြစ်ပါတယ်။ int8 လျှော့လိုက်ရင်တော့ ၄ ပုံ ၁ ပုံ အထိ ကျသွားပါတယ်နော်။

```python
# Memory size calculation for vector collections (standard library only, deterministic)
n_vectors = 1_000_000
dim = 768

# fp32: 4 bytes per dimension
fp32_bytes = n_vectors * dim * 4
fp32_gb = fp32_bytes / (1024 ** 3)  # binary GB

# int8 quantization: 1 byte per dimension (32-bit -> 8-bit)
int8_bytes = n_vectors * dim * 1
int8_gb = int8_bytes / (1024 ** 3)

print(f"fp32 bytes : {fp32_bytes:,}")
print(f"fp32 GB    : {fp32_gb:.2f}")
print(f"int8 bytes : {int8_bytes:,}")
print(f"int8 GB    : {int8_gb:.2f}")
print(f"reduction  : {fp32_bytes / int8_bytes:.0f}x")
# Expected output:
# fp32 bytes : 3,072,000,000
# fp32 GB    : 2.86
# int8 bytes : 768,000,000
# int8 GB    : 0.72
# reduction  : 4x
```

**အဓိကအယူဆ** — Quantization က memory ကို ၄ ဆ သက်သာစေပေမယ့် တိကျမှု အနည်းငယ် ဆုံးရှုံးစေတယ်ဆိုတဲ့ အပေးအယူကို ကိန်းဂဏန်းနဲ့ မြင်ရပါတယ်။

## လေ့ကျင့်ခန်း ၂ — Binary quantization နဲ့ cosine

Cosine အပြည့်အစုံ တွက်တာနဲ့ binary quantization လုပ်ပြီး dot product တွက်တာ နှစ်မျိုး နှိုင်းကြည့်ရုံပါ။ Binary မှာတော့ အပေါင်းကို 1၊ အနှုတ်ကို 0 ပြောင်းပြီး overlap အရေအတွက်ပဲ ကျန်ပါတယ်နော်။

```python
# Binary quantization vs full cosine similarity (standard library only)
import math

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb)

def to_binary(v):
    # positive -> 1, negative/zero -> 0
    return [1 if x > 0 else 0 for x in v]

v1 = [0.2, -0.5, 0.8, 0.1, -0.3, 0.7]
v2 = [0.3, -0.4, 0.6, -0.2, -0.1, 0.5]

full_cos = cosine(v1, v2)
b1 = to_binary(v1)
b2 = to_binary(v2)
# binary dot product = number of positions where both are 1
bin_dot = sum(x & y for x, y in zip(b1, b2))
# normalize by Hamming-like measure: overlap / sqrt(popcount*popcount)
bin_approx = bin_dot / math.sqrt(sum(b1) * sum(b2))

print(f"v1 binary: {b1}")
print(f"v2 binary: {b2}")
print(f"full cosine       : {full_cos:.4f}")
print(f"binary dot        : {bin_dot}")
print(f"binary approx cos : {bin_approx:.4f}")
# Expected output:
# v1 binary: [1, 0, 1, 1, 0, 1]
# v2 binary: [1, 0, 1, 0, 0, 1]
# full cosine       : 0.9353
# binary dot        : 3
# binary approx cos : 0.8660
```

**အဓိကအယူဆ** — Binary quantization က memory ကို ၃၂ ဆအထိ သက်သာစေပေမယ့် approximate ဖြစ်လို့ recall ချမ်းသွားနိုင်ပါတယ်။

## လေ့ကျင့်ခန်း ၃ — Product Quantization (PQ) အခြေခံ

PQ က vector ကြီးကို subvector ခွဲပြီး တစ်ခုစီကို သူ့နဲ့ အနီးဆုံး centroid နဲ့ အစားထိုးတာပါ။ Jégou et al. ရဲ့ စာတမ်းအတိုင်း တိကျမှု အနည်းငယ် စွန့်ပြီး memory အများကြီး သက်သာစေတယ်နော်။

```python
# Basic Product Quantization (Jegou et al., arXiv:0903.2314) — stdlib only, deterministic stand-in centroids
import math

def sq_euclid(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))

def nearest_centroid(sub, centroids):
    # return code index and the centroid vector itself
    best_i, best_d = 0, float("inf")
    for i, c in enumerate(centroids):
        d = sq_euclid(sub, c)
        if d < best_d:
            best_i, best_d = i, d
    return best_i, centroids[best_i]

# ---- Part 1: 4-dim vector split into 2 subvectors of 2 dims ----
v = [1.2, 0.3, -0.8, 1.5]
sub1, sub2 = v[:2], v[2:]
# fixed (scripted) codebook of 4 centroids per subspace (deterministic stand-in, no training)
codebook1 = [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
codebook2 = [[0.0, 0.0], [1.0, 0.0], [0.0, -1.0], [1.0, 1.0]]
c1, r1 = nearest_centroid(sub1, codebook1)
c2, r2 = nearest_centroid(sub2, codebook2)
recon = r1 + r2
print(f"original  : {v}")
print(f"codes     : ({c1}, {c2})  -> 2 bytes instead of 16")
print(f"reconstruct: {[round(x, 2) for x in recon]}")

# ---- Part 2: 8-dim -> 4 subvectors, approximate distance ----
import random
rng = random.Random(7)
query = [rng.uniform(-1, 1) for _ in range(8)]
vec = [rng.uniform(-1, 1) for _ in range(8)]

def pq_approx_distance(q, x, dsub, codebook):
    # sum of squared error per subspace after replacing each subvector by its centroid
    total = 0.0
    for s in range(0, len(q), dsub):
        qs, xs = q[s:s+dsub], x[s:s+dsub]
        _, qc = nearest_centroid(qs, codebook)
        _, xc = nearest_centroid(xs, codebook)
        total += sq_euclid(qc, xc)
    return total

cb = [[0.0, 0.0], [1.0, 0.0], [0.0, -1.0], [-1.0, 1.0]]
orig_d = sq_euclid(query, vec)
approx_d = pq_approx_distance(query, vec, 2, cb)
print(f"exact squared distance    : {orig_d:.4f}")
print(f"PQ approx squared distance: {approx_d:.4f}")
# Expected output:
# original  : [1.2, 0.3, -0.8, 1.5]
# codes     : (1, 0)  -> 2 bytes instead of 16
# reconstruct: [1.0, 0.0, 0.0, 0.0]
# exact squared distance    : 3.2405
# PQ approx squared distance: 2.0000
```

**အဓိကအယူဆ** — PQ က vector တစ်ခုကို code နည်းနည်းနဲ့ ကိုယ်စားပြုလို့ memory အများကြီး ချွေတာပေမယ့် distance က ခန့်မှန်း ဖြစ်သွားပါတယ်။

## လေ့ကျင့်ခန်း ၄ — Recall@k တိုင်းတာခြင်း

Seed 42 နဲ့ vector ၁၂၈ ခု ဖန်တီးပြီး brute-force top-5 ကို ground truth အဖြစ် ထားပါမယ်။ int8 quantization လုပ်ပြီးမှ Recall@5 တွက်တဲ့အခါ ၁.၀ ထက် နည်းနေတာကို မြင်ရပါလိမ့်မယ်နော်။

```python
# Recall@5 measurement: exact vs int8-quantized search (stdlib only, seed 42)
import random
import math

rng = random.Random(42)
d = 16
vectors = [[rng.uniform(-1, 1) for _ in range(d)] for _ in range(128)]
query = [rng.uniform(-1, 1) for _ in range(d)]

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb)

def top_k(q, data, k=5):
    scored = sorted(range(len(data)), key=lambda i: -cosine(q, data[i]))
    return set(scored[:k])

# ground truth: brute force on fp32
truth = top_k(query, vectors, 5)

# int8 quantization: min/max scaling over ALL vectors (approximate formula from the exercise)
all_vals = [x for vec in vectors for x in vec] + query
mn, mx = min(all_vals), max(all_vals)

def to_int8(v):
    return [round((x - mn) / (mx - mn) * 127 - 128) for x in v]

q_int8 = to_int8(query)
vecs_int8 = [to_int8(v) for v in vectors]
quant_results = top_k(q_int8, vecs_int8, 5)

recall5 = len(truth & quant_results) / 5
print(f"ground truth top-5 ids : {sorted(truth)}")
print(f"int8 search top-5 ids : {sorted(quant_results)}")
print(f"overlap               : {len(truth & quant_results)} / 5")
print(f"Recall@5              : {recall5:.2f}")
# Expected output:
# ground truth top-5 ids : [13, 18, 92, 105, 107]
# int8 search top-5 ids : [18, 24, 64, 92, 107]
# overlap               : 3 / 5
# Recall@5              : 0.60
```

**အဓိကအယူဆ** — int8 quantization လုပ်လိုက်ရင် Recall@k က ၁.၀ နဲ့ ၁.၀ အောက် ကြား ကျသွားနိုင်ပြီး quantization ရဲ့ တိကျမှု ဆုံးရှုံးမှုကို recall ကိန်းနဲ့ တိုင်းတာလို့ရပါတယ်။

## လေ့ကျင့်ခန်း ၅ — Sharding နဲ့ distributed search

Vector ၂၀၀ ကို shard ၄ ပိုင်း hash-based နဲ့ dimension-based နှစ်နည်း ခွဲကြည့်မယ်။ Shard တိုးလိုက်တာနဲ့ shard တစ်ခုရဲ့ memory က လျှော့သွားပြီး query ကတော့ shards အားလုံးကို ပျံ့သွားရပါမယ်နော်။

```python
# Hash-based vs dimension-based sharding with merged top-k search (stdlib only, deterministic)
import math

rng = None  # placeholder; we use a simple deterministic LCG below so results are fully reproducible
seed = 42
def lcg():
    # deterministic stand-in for random generation (no random module dependency surprises)
    global seed
    seed = (seed * 1103515245 + 12345) % (2 ** 31)
    return seed / (2 ** 31) * 2 - 1  # uniform in [-1, 1)

n, d, n_shards = 200, 8, 4
ids = list(range(n))
vectors = {i: [lcg() for _ in range(d)] for i in ids}
query = [lcg() for _ in range(d)]

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

# --- strategy 1: hash-based sharding (like Qdrant) ---
hash_shards = {s: {} for s in range(n_shards)}
for i in ids:
    hash_shards[i % n_shards][i] = vectors[i]

# --- strategy 2: dimension-based (one dim-slice per shard, partial dot products summed) ---
def search_dimension_sharded(query, data, k):
    # shard s holds dimensions [2s : 2s+2] of every vector; scores are summed across shards
    partial = {i: 0.0 for i in ids}
    for s in range(n_shards):
        lo, hi = s * 2, s * 2 + 2
        for i in ids:
            partial[i] += dot(query[lo:hi], data[i][lo:hi])
    return sorted(partial, key=lambda i: -partial[i])[:k], partial

def search_hash_sharded(query, shards, k):
    merged = []
    for s in range(n_shards):
        for i, v in shards[s].items():
            merged.append((dot(query, v), i))
    merged.sort(key=lambda t: -t[0])
    return [i for _, i in merged[:k]], merged

top_hash, all_hash = search_hash_sharded(query, hash_shards, 5)
top_dim, full_scores = search_dimension_sharded(query, vectors, 5)
top_full = [i for i in sorted(ids, key=lambda i: -dot(query, vectors[i]))[:5]]

per_shard = len(vectors) // n_shards
print(f"hash-based top-5      : {top_hash}")
print(f"dimension-based top-5: {top_dim}")
print(f"single-node top-5    : {top_full}")
print(f"results identical    : {top_hash == top_full == top_dim}")
print(f"vectors per shard    : {per_shard} (total {n} / {n_shards} shards)")
# Expected output:
# hash-based top-5      : [90, 104, 5, 165, 192]
# dimension-based top-5: [90, 104, 5, 165, 192]
# single-node top-5    : [90, 104, 5, 165, 192]
# results identical    : True
# vectors per shard    : 50 (total 200 / 4 shards)
```

**အဓိကအယူဆ** — Sharding နည်းနှစ်မျိုးလုံး merge လုပ်ပြီး top-k ထပ်စစ်ရင် single-node ရလဒ်နဲ့ တူညီပြီး shard တိုးတိုင်း shard တစ်ခုစီရဲ့ memory က လျှော့သွားပါတယ်။

## လေ့ကျင့်ခန်း ၆ — Bulk load နဲ့ write throughput

Vector ၁၀၀၀ ထဲ တစ်ခုထည့်တိုင်း sorted array ထဲ bisect insert လုပ်တာနဲ့ အားလုံး load ပြီးမှ တစ်ကြိမ်တည်း sort လုပ်တာ နှိုင်းပြမယ်။ pgvector README အတိုင်း index ကို load ပြီးမှ တည်ဆောက်တာက ပိုမြန်ပါတယ်နော်။

```python
# Build-after-load vs maintain-on-insert: measured in deterministic WORK UNITS, not wall-clock time.
import bisect
import math

N = 1000
values = [(i * 37) % 10007 for i in range(N)]      # fixed data: same every run

# Strategy 1: keep a sorted list up to date on every insert (like CREATE INDEX before loading).
sorted_index = []
moves = 0
for v in values:
    pos = bisect.bisect_left(sorted_index, v)
    moves += len(sorted_index) - pos               # elements this insert must shift right
    sorted_index.insert(pos, v)

# Strategy 2: append everything, then sort once (like pgvector: load first, build the index after).
raw_store = values[:]                              # N appends -> O(1) each
compares = int(N * math.log2(N))                   # model: one comparison per element per level

print(f"strategy 1 (insert + insort each time) : {moves:7d} element moves")
print(f"strategy 2 (load all, then sort once)  : {compares:7d} comparisons (model)")
print(f"work-unit ratio                        : {moves / compares:.1f}x")
print(f"both strategies hold the same order     : {sorted_index == sorted(raw_store)}")
# Expected output:
# strategy 1 (insert + insort each time) :  209113 element moves
# strategy 2 (load all, then sort once)  :    9965 comparisons (model)
# work-unit ratio                        : 21.0x
# both strategies hold the same order     : True
```

**အဓိကအယူဆ** — Bulk load လုပ်ပြီးမှ index တစ်ကြိမ်တည်း တည်ဆောက်တဲ့ build-after-load strategy က insert တိုင်း index ထိန်းတာထက် write throughput ကို အများကြီး မြှင့်ပေးလို့ pgvector မှာလည်း load ပြီးမှ `CREATE INDEX` လုပ်သင့်ပါတယ်။
