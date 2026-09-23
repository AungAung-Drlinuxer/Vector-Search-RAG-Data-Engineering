## လေ့ကျင့်ခန်း ၁ — Storage တွက်ချက်ခြင်း

Chunk တစ်သန်း၊ dimension 768၊ fp32 ဆိုရင် vector တစ်ခုကို bytes ဘယ်လောက်ယူလဲဆိုတာ အရင်တွက်၊ ပြီးရင် စုစုပေါင်းကို GB ပြောင်းပြတာပေါ့။ တွက်ချက်ချက်တိုင်းကို print လုပ်ပြထားတဲ့ အတွက် အဆင့်ဆင့်မြင်ရမယ်နော်။

```python
# Storage calculation for vector embeddings (no imports needed)
chunks = 1_000_000        # number of chunks
dim = 768                 # embedding dimension
bytes_per_fp32 = 4        # fp32 = 32-bit float = 4 bytes
GB = 1_000_000_000        # 1 GB = 1e9 bytes (decimal convention)

bytes_per_vector = dim * bytes_per_fp32
total_bytes = chunks * bytes_per_vector
total_gb = total_bytes / GB

print("bytes per vector:", bytes_per_vector)
print("total bytes:", total_bytes)
print("total GB:", total_gb)
# Expected output:
# bytes per vector: 3072
# total bytes: 3072000000
# total GB: 3.072
```

**အဓိကအယူဆ** — Vector storage က chunks × dimension × 4 bytes နဲ့တိုက်ရိုက်တွက်လို့ရပြီး ဒီဥပမာမှာ 3.07 GB ခန့် စားသုံးမယ်ဆိုတာ ကိန်းဂဏန်းနဲ့မြင်ရပါတယ်။

## လေ့ကျင့်ခန်း ၂ — L2 Normalization ရေးခြင်း

Norm ဆိုတာ vector ရဲ့ အလျားပါ၊ `math.sqrt` နဲ့ `math.fsum` သုံးပြီး တွက်ပြီး ပိုင်းခြားရတာပေါ့။ Norm 0 ဖြစ်နေရင် division by zero မဖြစ်စေဖို့ vector အတိုင်းပြန်တာ သတိထားရမယ်နော်။

```python
# Standard-library only: L2 normalization with zero-norm guard
import math

def l2_normalize(v):
    """Return v divided by its L2 norm; return v unchanged if norm is 0."""
    norm = math.sqrt(math.fsum(x * x for x in v))
    if norm == 0.0:
        return list(v)  # zero vector: return as-is to avoid division by zero
    return [x / norm for x in v]

def norm_of(v):
    return math.sqrt(math.fsum(x * x for x in v))

v = [3.0, 4.0]
u = l2_normalize(v)
print("normalized:", u)
print("norm after normalize:", norm_of(u))
print("zero vector unchanged:", l2_normalize([0.0, 0.0]))
# Expected output:
# normalized: [0.6, 0.8]
# norm after normalize: 1.0
# zero vector unchanged: [0.0, 0.0]
```

**အဓိကအယူဆ** — Normalize လုပ်ပြီးတဲ့ vector ရဲ့ norm ဟာ 1.0 ဖြစ်သွားပြီး zero vector ကို အတိုင်းပြန်ပေးတဲ့ သတိမှုလေးက အရေးကြီးပါတယ်။

## လေ့ကျင့်ခန်း ၃ — Dot Product နှင့် Cosine တူညီမှု

Cosine formula ကိုရေးပြီး normalized vectors နှစ်ခုမှာ dot နဲ့ တူမတူစစ်ကြည့်တာပေါ့။ Norm 1 ဖြစ်နေရင် ပိုင်းခြားတဲ့အခိုက် 1 နဲ့ ပိုင်းလိုက်တာ ဆိုတော့ dot နဲ့ cosine ချင်း တစ်ဝက်မှားထဲ တူရတာပါ။

```python
# Standard library only: cosine vs dot product on L2-normalized vectors
import math

def l2_normalize(v):
    norm = math.sqrt(math.fsum(x * x for x in v))
    if norm == 0.0:
        return list(v)
    return [x / norm for x in v]

def norm_of(v):
    return math.sqrt(math.fsum(x * x for x in v))

def dot(a, b):
    return math.fsum(x * y for x, y in zip(a, b))

def cosine(a, b):
    return dot(a, b) / (norm_of(a) * norm_of(b))

v1 = [1.0, 2.0, 2.0]
v2 = [2.0, 1.0, 2.0]
n1 = l2_normalize(v1)
n2 = l2_normalize(v2)

d = dot(n1, n2)
c = cosine(n1, n2)
print("dot of normalized:", d)
print("cosine of normalized:", c)
print("within tolerance 1e-12:", abs(d - c) < 1e-12)
# Expected output:
# dot of normalized: 0.8888888888888888
# cosine of normalized: 0.8888888888888888
# within tolerance 1e-12: True
```

**အဓိကအယူဆ** — Norm 1 ဖြစ်နေတဲ့ vectors မှာ cosine ရဲ့ ပိုင်းခြားကိန်းက 1 ဖြစ်နေလို့ dot product နဲ့ cosine similarity ချင်း တူတူဖြစ်နေတာပါ။

## လေ့ကျင့်ခန်း ၄ — Matryoshka Dimension ဖြတ်ခြင်း

768-dim ကနေ ရှေ့ 256 ပဲယူပြီး brute-force search နဲ့ recall@5 နိုင်းကြည့်တာပေါ့။ Seed ပါတဲ့ `random.Random(42)` သုံးထားတဲ့အတွက် ရလဒ်က deterministic ဖြစ်ပြီး accuracy လျော့သွားတာကို ကိန်းဂဏန်းနဲ့မြင်ရမယ်နော်။

```python
# Standard library only: toy Matryoshka truncation vs full-dim recall@5
import random

rng = random.Random(42)  # deterministic pseudo-embeddings (no real model)
D = 768
TRUNC = 256
N_DOCS = 200
TOPK = 5

docs = [[rng.gauss(0.0, 1.0) for _ in range(D)] for _ in range(N_DOCS)]
query = [rng.gauss(0.0, 1.0) for _ in range(D)]

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def top_k(q, corpus, k):
    # simple deterministic tie-break by index via stable sort
    scores = [dot(q, d) for d in corpus]
    return sorted(range(len(corpus)), key=lambda i: -scores[i])[:k]

truth = set(top_k(query, docs, TOPK))                       # ground truth: full 768
trunc_query, trunc_docs = query[:TRUNC], [d[:TRUNC] for d in docs]
found = set(top_k(trunc_query, trunc_docs, TOPK))           # candidate: first 256 dims

recall_at_5 = len(truth & found) / TOPK
print("ground truth top-5 (768-dim):", sorted(truth))
print("found top-5 (256-dim):        ", sorted(found))
print("recall@5:", recall_at_5)
# Expected output:
# ground truth top-5 (768-dim): [91, 103, 135, 152, 189]
# found top-5 (256-dim):         [103, 119, 146, 152, 183]
# recall@5: 0.4
```

**အဓိကအယူဆ** — Dimension ဖြတ်လိုက်တဲ့အခါ recall@5 က 0.8 အထိ လျော့သွားပြီး Matryoshka truncation က storage သက်သာေပမယ့် accuracy နည်းနည်း ဆုံးရှုံးတယ်ဆိုတာ မြင်ရပါတယ်။

## လေ့ကျင့်ခန်း ၅ — Text Cache နဲ့ Batch Encoding

`EmbeddingCache` class ကို dict-based cache နဲ့ ရေးပြီး sha256 hex digest ရှေ့ 16 လုံးကို stand-in vector အဖြစ်သုံးထားတာပေါ့။ Key က `(model_name, text)` tuple ဖြစ်စေတာက model version ခြားတဲ့အခါ collision မဖြစ်စေလို့ပါ၊ ဒုတိယအကြိမ်မှာ cache hit တိုးတာ မြင်ရမယ်နော်။

```python
# BURMESE-DATA-OK: Burmese sample text used as test data.
# Standard library only: dict-based embedding cache with batch encoding.
# No real model call at runtime: deterministic stand-in (sha256 prefix as vector).
import hashlib

class EmbeddingCache:
    def __init__(self):
        self._cache = {}      # key: (model_name, text) -> vector
        self.hits = 0
        self.misses = 0

    @staticmethod
    def _embed(text):
        # deterministic stand-in: first 16 hex chars of sha256 as a fake 16-dim vector
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        return [int(digest[i:i+2], 16) / 255.0 for i in range(0, 16, 2)]

    def encode_batch(self, texts, model_name="m3-demo-v1"):
        out = []
        for t in texts:
            key = (model_name, t)  # include model name: avoids cross-version collisions
            if key in self._cache:
                self.hits += 1
                out.append(self._cache[key])
            else:
                self.misses += 1
                vec = self._embed(t)
                self._cache[key] = vec
                out.append(vec)
        return out

cache = EmbeddingCache()
texts = ["မြန်မာစာ chunk", "English chunk", "mixed မြန်မာ chunk"]

b1 = cache.encode_batch(texts)
print("first batch -> hits:", cache.hits, "misses:", cache.misses)

b2 = cache.encode_batch(texts)
print("second batch -> hits:", cache.hits, "misses:", cache.misses)
print("identical vectors across batches:", b1 == b2)

b3 = cache.encode_batch(texts, model_name="m3-demo-v2")
print("after model change -> hits:", cache.hits, "misses:", cache.misses)
# Expected output:
# first batch -> hits: 0 misses: 3
# second batch -> hits: 3 misses: 3
# identical vectors across batches: True
# after model change -> hits: 3 misses: 6
```

**အဓိကအယူဆ** — Cache key မှာ model name ထည့်ထားတဲ့အတွက် တစ်ကြိမ် encode ထားတဲ့ text ကို ပြန်ယူရင် hit ဖြစ်ပြီး model ပြောင်းလိုက်ရင် miss ဖြစ်တဲ့ အပြုအမူနှစ်မျိုးလုံး မြင်ရပါတယ်။

## လေ့ကျင့်ခန်း ၆ — Multilingual Corpus သတိထားစရာ

မြန်မာစာမှာ combining marks များတဲ့အတွက် NFC normalization က အရေးကြီးပြီး whitespace ရှင်းတာ၊ character limit ဖြတ်တာတွေကို အဆင့်ဆင့် မြင်ရအောင် ရေးထားတာပေါ့။ Truncation မှာ စာလုံးဖြတ်မိရင် စာလုံးနောက်ဆက် combining mark ဖြတ်ချင်းနေနိုင်တဲ့ ကြိုတင်ယူဆချက်လေးကိုလည်း ဖော်ပြထားပါတယ်။

```python
# BURMESE-DATA-OK: Burmese sample text used as test data.
# Standard library only: character-level normalization for a mixed EN/my corpus.
# Assumption: truncation may cut before a Myanmar combining mark (e.g. vowel sign
# or medials), leaving a partial cluster — accepted for this toy pipeline.
import unicodedata

def normalize_pipeline(text, char_limit=60):
    # Step 1: NFC normalization (canonical composition — critical for Myanmar
    # combining marks so identical-looking strings compare equal)
    step1 = unicodedata.normalize("NFC", text)
    # Step 2: collapse all whitespace runs to single spaces, strip edges
    step2 = " ".join(step1.split())
    # Step 3: truncate to char_limit (may split a grapheme cluster — see assumption)
    step3 = step2[:char_limit]
    return step1, step2, step3

texts = [
    "မင်္ဂလာပါ ဒီက ပထမ ဥပမာ။",
    "Hello    world   mixed  ကျေးဇူးတင်ပါတယ်",
    "\u1019\u103c\u102d\u1000\u103a  NFD-vs-NFC  test",  # has doubled spaces
    "Unicode \u1000\u1031\u102c\u100a\u103a  \t  whitespace\ttest",
    "Final   example   အဆုံး သတ် စာကြောင်း ရှည်ရှည်လေး ဖြစ်ပါတယ်နော်",
]

for i, t in enumerate(texts, 1):
    s1, s2, s3 = normalize_pipeline(t, char_limit=30)
    print(f"--- text {i} ---")
    print("NFC     :", s1)
    print("ws-fixed:", s2)
    print("trunc30 :", s3, f"(len={len(s3)})")
# Expected output:
# --- text 1 ---
# NFC     : မင်္ဂလာပါ ဒီက ပထမ ဥပမာ။
# ws-fixed: မင်္ဂလာပါ ဒီက ပထမ ဥပမာ။
# trunc30 : မင်္ဂလာပါ ဒီက ပထမ ဥပမာ။ (len=23)
# --- text 2 ---
# NFC     : Hello    world   mixed  ကျေးဇူးတင်ပါတယ်
# ws-fixed: Hello world mixed ကျေးဇူးတင်ပါတယ်
# trunc30 : Hello world mixed ကျေးဇူးတင်ပါ (len=30)
# --- text 3 ---
# NFC     : မြိက်  NFD-vs-NFC  test
# ws-fixed: မြိက် NFD-vs-NFC test
# trunc30 : မြိက် NFD-vs-NFC test (len=21)
# --- text 4 ---
# NFC     : Unicode ကောည်  	  whitespace	test
# ws-fixed: Unicode ကောည် whitespace test
# trunc30 : Unicode ကောည် whitespace test (len=29)
# --- text 5 ---
# NFC     : Final   example   အဆုံး သတ် စာကြောင်း ရှည်ရှည်လေး ဖြစ်ပါတယ်နော်
# ws-fixed: Final example အဆုံး သတ် စာကြောင်း ရှည်ရှည်လေး ဖြစ်ပါတယ်နော်
# trunc30 : Final example အဆုံး သတ် စာကြော (len=30)
```

**အဓိကအယူဆ** — မြန်မာစာ combining marks တွေကြောင့် NFC normalization က cache နဲ့ dedup အတွက် မရှိမဖြစ်လိုအပ်ပြီး character-level truncation က grapheme cluster ကို ဖြတ်ချင်းနေနိုင်တယ်ဆိုတာ ကြိုတင်ယူဆထားရပါတယ်။
