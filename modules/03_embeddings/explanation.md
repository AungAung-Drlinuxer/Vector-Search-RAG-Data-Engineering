# M3 — Embedding Model ရွေးချယ်မှု၊ Dimension၊ Distance Metric နှင့် Caching

ဒီ module မှာ embedding model ဘယ်လိုရွေးမလဲ၊ dimension နဲ့ storage ဘယ်လိုတွက်မလဲ၊ distance metric တွေရဲ့ ဆက်စပ်မှု၊ caching နဲ့ version စီမံခန့်ခွဲမှုကို လေ့လာကြပါမယ်။
ရည်ညွှန်း documentation တွေကတော့ arXiv စာတမ်း (2210.07316, 2309.07597, 2212.03533, 2205.13147) တွေနဲ့ https://sbert.net/ ပါ။

---

## Subtopic 1 — Embedding Model ရွေးချယ်ခြင်း (multilingual, domain)

### ဘာကို ဆိုလိုတာလဲ

Embedding model ဆိုတာ text ကို number အစုအဝေး (vector) အဖြစ်ပြောင်းပေးတဲ့ model ပါ။
Vector ထဲမှာ စကားလုံးရဲ့ အဓိပ္ပာယ်ကို number တွေနဲ့ capture လုပ်ထားပါတယ်။
Multilingual model ဆိုတာ ဘာသာစကား များစွာကို တစ်ခုတည်းရဲ့ vector space ထဲမှာ ပြောင်းပေးနိုင်တဲ့ model ကို ဆိုလိုပါတယ်။

### ဘာကြောင့် လဲ

Model မှားရွေးရင် ရှာတွေ့မှု အရည်အသွေး ကျဆင်းပါတယ်။
ဥပမာ — အင်္ဂလိပ် corpus နဲ့ train လုပ်ထားတဲ့ model ကို မြန်မာစာ နဲ့ သုံးရင် အဓိပ္ပာယ်မတူတဲ့ စာတွေကို ဆင်တူတယ်လို့ မှားပြပါတယ်။
ဒါကြောင့် corpus က ဘာသာ ဘယ်လောက်ပါလဲ၊ domain က ဘာလဲဆိုတာကို အရင်စဉ်းစားရပါတယ်။
MTEB စာတမ်း (arXiv 2210.07316) မှာ embedding တွေရဲ့ တကယ့်အလုပ်လုပ်ပုံကို စမ်းသပ်တဲ့ benchmark အကြောင်း ရှင်းပြထားပါတယ်။
ဒါကြောင့် model ရွေးတဲ့အခါ benchmark ရလဒ်ကို ကြည့်ပြီး ရွေးသင့်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ ကိုယ့် corpus ရဲ့ ဘာသာစကား အခြေအနေကို စစ်ပါ — မြန်မာလား၊ multilingual လား။
၂။ Domain ကို သတ်မှတ်ပါ — ဥပမာ ဆေးဘက်စာ၊ ဥပဒေစာ၊ general စာ။
၃။ ထိပ်တန်း MTEB-style benchmark ရလဒ်တွေနဲ့ နာမည်ကြီး model တွေကို နှိုင်းယှဉ်ပါ။
၄။ ကိုယ့် data အတွက် ကိုယ်ပိုင် သေးသေးလေး evaluation set ဆောက်ပါ — လက်တွေ့ကျပါတယ်။
၅။ Model size၊ license၊ speed တွေကို အထက်ဖော်ပြချက်တွေနဲ့ တွဲပြီး ဆုံးဖြတ်ပါ။

### ဥပမာ

```python
# A deterministic stand-in for model selection scoring.
# In a real pipeline we would download candidate models from
# https://sbert.net/ and run them on a small labeled evaluation set.

candidates = [
    {"name": "model-a", "multilingual": True, "dim": 384},
    {"name": "model-b", "multilingual": False, "dim": 768},
    {"name": "model-c", "multilingual": True, "dim": 1024},
]

corpus_languages = {"my", "en"}  # Myanmar + English corpus

def eligible(model):
    return model["multilingual"] and all(l in {"my", "en"} for l in [])

for m in candidates:
    ok = m["multilingual"]
    print(f"{m['name']}: multilingual={m['multilingual']}, dim={m['dim']}, "
          f"fits_corpus={ok}")
# Expected output:
# model-a: multilingual=True, dim=384, fits_corpus=True
# model-b: multilingual=False, dim=768, fits_corpus=False
# model-c: multilingual=True, dim=1024, fits_corpus=True
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

မြန်မာ corpus အတွက် multilingual model ရွေးတာက အရေးအကြီးဆုံး ဆုံးဖြတ်ချက်ပါ။
မှားရင် နောက်ပိုင်း tuning လုပ်တာ ခက်ပြီး အချိန်ကုန်ပါတယ်။
Model တစ်ခြမ်းလွဲရင် နောက်စနစ်တစ်ခုလုံး လွဲသွားတတ်ပါတယ်နော်။

---

## Subtopic 2 — Dimension နှင့် Storage တွက်ချက်ခြင်း

### ဘာကို ဆိုလိုတာလဲ

Dimension (dim) ဆိုတာ vector တစ်ခုထဲမှာ number ဘယ်လောက်ပါလဲဆိုတာကို ဆိုလိုပါတယ်။
ဥပမာ — 768 dim ဆိုရင် vector ထဲမှာ number ၇၆၈ လုံးပါတယ်။
Storage ကတော့ ဒီ number တွေကို သိမ်းဖို့ disk ဘယ်လောက်လိုမလဲ ဆိုတာပါ။

### ဘာကြောင့် လဲ

Dimension မြင့်ရင် အဓိပ္ပာယ် ပိုစုံပေမယ့် storage လည်း များပါတယ်။
Storage ကြောင့် ရှာဖွေမှု speed ထိခိုက်ပြီး ကုန်ကျစရိတ်လည်း တက်ပါတယ်။
ဒါကြောင့် ကြိုတွက်ပြီး ဒီဇိုင်းလုပ်ဖို့ လိုပါတယ်။
Formula ကတော့ — တစ် vector ရဲ့ byte = dim × 4 (fp32 အတွက်) ပါ။
fp32 ဆိုတာ number တစ်ခုကို 4 byte နဲ့ သိမ်းတဲ့ နည်းပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Vector အရေအတွက်ကို သတ်မှတ်ပါ။
၂။ Dimension ကို သတ်မှတ်ပါ။
၃။ တစ် vector bytes = dim × 4 လို့ တွက်ပါ။
၄။ စုစုပေါင်း bytes = အရေအတွက် × တစ် vector bytes လို့ တွက်ပါ။
၅။ GB ပြောင်းဖို့ 10 ကိုး (1,000,000,000) နဲ့ စားပါ။

### ဥပမာ

```python
# Worked example with clearly labelled assumptions:
# ASSUMPTION: 1,000,000 chunks, 768 dimensions, fp32 (4 bytes per value).

n_vectors = 1_000_000
dim = 768
bytes_per_value = 4  # fp32

per_vector_bytes = dim * bytes_per_value
total_bytes = n_vectors * per_vector_bytes
total_gb = total_bytes / 1_000_000_000

print(f"per vector : {per_vector_bytes} bytes")
print(f"total      : {total_bytes:,} bytes")
print(f"total      : {total_gb} GB")
# Expected output:
# per vector : 3072 bytes
# total      : 3,072,000,000 bytes
# total      : 3.072 GB
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Vector သန်းပေါင်းများစွာ သိမ်းတဲ့အခါ storage က ဂိုးဗလာ တက်သွားတတ်ပါတယ်။
ကြိုတွက်ထားရင် server capacity ကို မှန်မှန်ကန်ကန် စားပါတယ်။
pgvector မှာ သိမ်းတဲ့ vector type (vector သို့ halfvec) အလိုက် size က ပြောင်းပါတယ်။
PostgreSQL + pgvector stack မှာ index memory ကိုပါ တွဲတွက်ဖို့ လိုပါတယ်နော်။

---

## Subtopic 3 — L2 Normalization နှင့် Cosine / Dot / L2 ဆက်စပ်မှု

### ဘာကို ဆိုလိုတာလဲ

L2 normalization ဆိုတာ vector ရဲ့ အလျား (length) ကို 1 အဖြစ် ပြောင်းလိုက်တဲ့ လုပ်ဆောင်ချက်ပါ။
အလျားဆိုတာ vector ရဲ့ magnitude (ပမာဏ) ကို ဆိုလိုပါတယ်။
Normalize လုပ်ပြီးရင် vector ရဲ့ ဦးတည်ချက် (direction) ကိုပဲ ကျန်ပါတယ်။

### ဘာကြောင့် လဲ

Distance metric သုံးမျိုးရဲ့ ဆက်စပ်မှုက ဒီ normalization အပေါ် မူတည်ပါတယ်။
Normalize လုပ်ထားတဲ့ vector တွေမှာ — cosine similarity နဲ့ dot product က တူညီတဲ့ ranking ပေးပါတယ်။
ဒါကြောင့် pgvector မှာ normalized vector တွေသာ သိမ်းရရင် dot product (fast) ကို သုံးပြီး cosine နဲ့ တူညီတဲ့ ရလဒ်ရပါတယ်။
Normalize မလုပ်ရင် dot product က vector ပမာဏကြီးတဲ့ အရာတွေကို မြှောက်ပေးလို့ ranking မှားပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Vector တစ်ခုရဲ့ norm (အလျား) ကို တွက်ပါ — တန်ဖိုးတစ်ခုစီရဲ့ နှစ်ထပ်ကိန်းပေါင်း၊ ပြီးရင် အမြစ်ပြန်။
၂။ တန်ဖိုးတစ်ခုစီကို norm နဲ့ စားပါ။
၃။ ရလဒ် vector ရဲ့ norm က 1 ဖြစ်သွားပါတယ်။
၄။ Normalized vector တွေအတွက် cosine = dot ဖြစ်တာကို စစ်ပါ။

### ဥပမာ

```python
import math

def l2_normalize(v):
    norm = math.sqrt(sum(x * x for x in v))
    return [x / norm for x in v], norm

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def cosine(a, b):
    # For general vectors: dot / (norm(a) * norm(b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot(a, b) / (na * nb)

a = [3.0, 4.0]
b = [6.0, 8.0]

print("raw cosine :", cosine(a, b))
print("raw dot    :", dot(a, b))  # inflated by magnitude

na, _ = l2_normalize(a)
nb, _ = l2_normalize(b)
print("norm of na :", math.sqrt(sum(x * x for x in na)))
print("dot (norm) :", dot(na, nb))
print("cos(norm)  :", cosine(na, nb))
# Expected output:
# raw cosine : 1.0
# raw dot    : 50.0
# norm of na : 1.0
# dot (norm) : 1.0
# cos(norm)  : 1.0
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Cosine က စာသားရှာဖွေမှုမှာ သုံးများတဲ့ metric ပါ။
Normalize လုပ်ထားရင် dot product နဲ့ ပိုမြန်စေပြီး ရလဒ်တူပါတယ်။
PostgreSQL + pgvector မှာ `<=>` (cosine) နဲ့ `<#>` (negative dot) operator တွေကို သုံးလို့ရပါတယ်။
Model တချို့ (arXiv 2212.03533 — GeText စာတမ်းအုပ်စု) က normalize လုပ်ထားတဲ့ output ပေးပါတယ်။
SQL ကို ဒီလို သုံးလို့ရပါတယ် —

```sql
-- Valid for PostgreSQL with the pgvector extension (never executed here).
CREATE TABLE chunks (
    id   bigint PRIMARY KEY,
    body text,
    emb  vector(768)
);
-- Cosine distance search for the top 5 nearest chunks.
SELECT id, body
FROM chunks
ORDER BY emb <=> $1::vector      -- the bound parameter must hold exactly 768 numbers
LIMIT 5;                         -- a '[...]' literal with fewer fails: expected 768 dimensions
```

---

## Subtopic 4 — Matryoshka ဖြင့် Dimension ဖြတ်ခြင်း

### ဘာကို ဆိုလိုတာလဲ

Matryoshka embedding ဆိုတာ vector ရဲ့ ရှေ့ပိုင်း အပိုင်းကိုပဲ ဖြတ်သုံးလို့ရတဲ့ model ကို ဆိုလိုပါတယ်။
နာမည်က ရုရှား puppet အထုပ် (အကြီးထဲ အသေးဝင်) ကနေ လာပါတယ်။
ဥပမာ — 1024 dim vector ရဲ့ ရှေ့ 256 ခုကိုပဲ သုံးလို့ရပါတယ်။

### ဘာကြောင့် လဲ

Storage ချွေတာချင်ပေမယ့် accuracy လည်း ဆုံးရှုံးစေချင်ပါတယ်။
Matryoshka နည်း (arXiv 2205.13147) က သင်ယူချိန်မှာ ရှေ့ပိုင်း dims တွေကို အဓိပ္ပာယ်အပြည့် ပါအောင် စောစော train လုပ်ပေးပါတယ်။
ဒါကြောင့် ဖြတ်လိုက်တဲ့ အပိုင်းက လုပ်ငန်းသုံးစရဲ့ အရည်အသွေး ရှိပါတယ်။
Reranking မှာ ကြီးတဲ့ dim အပြည့်၊ screening မှာ သေးတဲ့ dim — ဒီလို နှစ်ဆင့် သုံးလို့ရပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Model ထုတ်ပေးတဲ့ vector အပြည့်ကို ယူပါ။
၂။ ကိုယ်လိုချင်တဲ့ dim (ဥပမာ 256) ကို သတ်မှတ်ပါ။
၃။ Vector ရဲ့ ရှေ့ပိုင်း 256 ခုကို ဖြတ်ယူပါ။
၄။ ဖြတ်ထားတဲ့ အပိုင်းကို ပြန် normalize လုပ်ပါ။
၅။ ချက်ချင်း screening လုပ်ပြီး ကောင်းတဲ့ candidate တွေကို အပြည့်နဲ့ rerank လုပ်ပါ။

### ဥပမာ

```python
import math

def l2_normalize(v):
    norm = math.sqrt(sum(x * x for x in v))
    return [x / norm for x in v]

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

# Stand-in for a 1024-dim Matryoshka model output: we use a small vector
# with a repeating pattern so truncation loss is visible but deterministic.
full = l2_normalize([1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 2.0])

def truncate_renorm(v, k):
    return l2_normalize(v[:k])

def ranking(query, docs):
    # Return doc indices ordered by dot-product score, best first.
    scores = [(dot(query, d), i) for i, d in enumerate(docs)]
    scores.sort(reverse=True)
    return [i for _, i in scores]

docs = [truncate_renorm(full[:], 4), truncate_renorm(full[:], 2)]

print("full ranking   :", ranking(full, docs))
print("short ranking  :", ranking(truncate_renorm(full, 4), docs))
print("truncated norm :", math.sqrt(sum(x * x for x in truncate_renorm(full, 4))))
# Expected output:
# full ranking   : [0, 1]
# short ranking  : [0, 1]
# truncated norm : 1.0
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Large corpus မှာ storage နဲ့ search ကုန်ကျစရိတ်က အဓိက ပြဿနာပါ။
Matryoshka နဲ့ သေးတဲ့ dim ကို အဆင့်တစ် (screening) မှာ သုံးပြီး ကြီးတဲ့ dim ကို အဆင့်နှစ် (rerank) မှာ သုံးနိုင်ပါတယ်။
ဒါက speed နဲ့ accuracy ကို ချိန်ညှိပေးပါတယ်နော်။

---

## Subtopic 5 — Batch Encoding၊ Cache နှင့် Embedding Version စီမံခန့်ခွဲမှု

### ဘာကို ဆိုလိုတာလဲ

Batch encoding ဆိုတာ text အစုအဝေးကို တစ်ခါတည်း model ထဲ ထည့်တဲ့ နည်းပါ။
Cache ဆိုတ်ာ တစ်ခါတွက်ပြီးတဲ့ embedding ကို နောက်ထပ် မတွက်ရအောင် သိမ်းထားတဲ့ စနစ်ပါ။
Version စီမံခန့်ခွဲမှု ဆိုတာ model ပြောင်းတဲ့အခါ embedding တွေကို ဘယ်လို နောက်ဆက် ဆက်ထားမလဲဆိုတာပါ။

### ဘာကြောင့် လဲ

တူညီတဲ့ text ကို ထပ်ခါထပ်ခါ encode လုပ်ရင် အချိန်နဲငွေ အမြောက်အမြား ဆုံးပါတယ်။
Model ပြောင်းလိုက်တဲ့အခါ vector space တစ်ခုလုံး ပြောင်းသွားပါတယ်။
အသစ်နဲ့ အဟောင်း vector တွေကို ရောရှာရင် ranking မှားပါတယ်။
ဒါကြောင့် version tag ခံပြီး သီးသန့် index ဆောက်ဖို့ လိုပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Batch size သတ်မှတ်ပါ — ဥပမာ 32။
၂။ Text တွေကို batch အလိုက် ခွဲပါ။
၃။ Cache key ကို (model_version, text hash) နဲ့ ဆောက်ပါ။
၄။ Cache မှာ ရှိရင် မတွက်ပဲ ယူသုံးပါ။
၅။ Model ပြောင်းတဲ့အခါ version အသစ်နဲ့ တွက်ပြီး index အသစ်ဆောက်ပါ — တစ်ခါတည်း လဲလှယ်ပါ။
၆။ Cache ကို version ခွဲထားတာကြောင့် model ပြောင်းရင် အဟောင်း cache ကို မှားသုံးတာ ရှောင်နိုင်ပါတယ်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Embedding ကို တစ်ခါ ပြောင်းလိုက်ရင် index တစ်ခုလုံး ပြန်တွက်ရပါတယ်။ Version မှတ်ထားရင် ဘယ် chunk က ဘယ် model နဲ့ တွက်ထားလဲ သိပြီး migration ကို တစ်ဆင့်ချင်း လုပ်နိုင်ပါတယ်။

## အနှစ်ခုပ်

- Model ရွေးချယ်မှုက ဘာသာစကားနှင့် domain ပေါ်မှာ မူတည်ပါတယ်။
- Dimension က storage နှင့် ကုန်ကျစရိတ်ကို တိုက်ရိုက် ဆုံးဖြတ်ပါတယ်။
- Normalize လုပ်ပြီးရင် cosine နှင့် dot product အဖြေ တူပါတယ်။
- Matryoshka ဖြင့် dimension ဖြတ်တာက သေးတဲ့ index ကို ဖန်တီးပေးပါတယ်။
- Embedding version ကို cache နှင့် index မှာ တွဲမှတ်ထားပါ။
