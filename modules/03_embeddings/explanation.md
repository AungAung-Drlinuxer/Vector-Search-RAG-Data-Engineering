# M3 — Embedding Model ရွေးချယ်မှု၊ Dimension၊ Distance Metric နှင့် Caching

ဒီ module တွင် embedding model ရွေးချယ်မှု စံနှုန်းများ၊ dimension နှင့် storage တွက်ချက်ခြင်း၊ distance metric များ၏ ဆက်စပ်မှု၊ caching နှင့် version စီမံခန့်ခွဲမှုကို လေ့လာသည်။
ရည်ညွှန်း documentation များမှာ arXiv စာတမ်းများ (2210.07316, 2309.07597, 2212.03533, 2205.13147) နှင့် https://sbert.net/ တို့ ဖြစ်သည်။

---

## Subtopic 1 — Embedding Model ရွေးချယ်ခြင်း (multilingual, domain)

### ဘာကို ဆိုလိုတာလဲ

Embedding model သည် text ကို dense vector တစ်ခုအဖြစ် ပြောင်းလဲပေးသော model ဖြစ်သည်။
Vector အတွင်းတွင် စာသား၏ semantic information ကို numeric form ဖြင့် encode လုပ်ထားသည်။
Multilingual model သည် ဘာသာစကား များစွာကို single shared vector space တစ်ခုအတွင်း embed လုပ်နိုင်သော model ဖြစ်သည်။

### ဘာကြောင့် လဲ

Model ရွေးချယ်မှု မှားယွင်းပါက retrieval quality ကျဆင်းသည်။
ဥပမာ — English corpus ဖြင့် train လုပ်ထားသော model ကို မြန်မာစာအတွက် အသုံးပြုပါက semantic မတူညီသော စာသားများကို မြင့်မားသော similarity score ဖြင့် မှားယွင်းစွာ ရမှတ်ပေးသည်။
ထို့ကြောင့် corpus ၏ ဘာသာစကား ဖွဲ့စည်းမှုနှင့် domain ကို ဦးစွာ သတ်မှတ်ရန် လိုအပ်သည်။
MTEB စာတမ်း (arXiv 2210.07316) တွင် embedding model များ၏ လုပ်ငန်းဆောင်တာကို စမ်းသပ်သည့် benchmark ကို ဖော်ပြထားသည်။
Model ရွေးချယ်ရာတွင် benchmark ရလဒ်များကို အခြေခံ၍ ဆုံးဖြတ်သင့်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Corpus ၏ ဘာသာစကား ဖွဲ့စည်းမှုကို စစ်ဆေးပါ — monolingual (မြန်မာ) လား၊ multilingual လား။
၂။ Domain ကို သတ်မှတ်ပါ — ဥပမာ ဆေးဘက်ဆိုင်ရာ၊ ဥပဒေ၊ general text။
၃။ MTEB-style benchmark ရလဒ်များတွင် ဦးဆောင်နေသော model များကို နှိုင်းယှဉ်ပါ။
၄။ ကိုယ်ပိုင် data အတွက် သေးငယ်သော labeled evaluation set တစ်ခု တည်ဆောက်ပါ — benchmark စာရင်းများထက် ပိုမိုတိကျသော ဆုံးဖြတ်ချက် ရရှိစေသည်။
၅။ Model size၊ license၊ inference speed တို့ကို အထက်ပါ စံနှုန်းများနှင့် တွဲဖက်၍ ဆုံးဖြတ်ပါ။

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

မြန်မာ corpus အတွက် multilingual model ရွေးချယ်မှုသည် အရေးအပါဆုံး ဆုံးဖြတ်ချက် ဖြစ်သည်။
Model ရွေးချယ်မှု မှားယွင်းပါက downstream tuning ဖြင့် ပြင်ဆင်ရန် ခက်ခဲပြီး ကုန်ကျစရိတ် မြင့်မားသည်။
Embedding layer မှားယွင်းပါက စနစ်တစ်ခုလုံး၏ retrieval quality ကျဆင်းသွားသည်။

---

## Subtopic 2 — Dimension နှင့် Storage တွက်ချက်ခြင်း

### ဘာကို ဆိုလိုတာလဲ

Dimension (dim) ဆိုသည်မှာ vector တစ်ခုတွင် ပါဝင်သော scalar value အရေအတွက် ဖြစ်သည်။
ဥပမာ — dim 768 ဖြစ်ပါက vector တစ်ခုတွင် float value ၇၆၈ ခု ပါဝင်သည်။
Storage ဆိုသည်မှာ ထို value များ သိမ်းဆည်းရန် လိုအပ်သော disk ပမာဏ ဖြစ်သည်။

### ဘာကြောင့် လဲ

Dimension မြင့်လေ semantic representation ပိုမိုစုံလင်လေ ဖြစ်သော်လည်း storage ပမာဏလည်း တိုးပွားလေ ဖြစ်သည်။
Storage ပမာဏသည် search speed ကို သက်ရောက်မှုရှိပြီး infrastructure ကုန်ကျစရိတ်လည်း တိုးစေသည်။
ထို့ကြောင့် capacity ကို ကြိုတင်တွက်ချက်ပြီး ဒီဇိုင်းချရန် လိုအပ်သည်။
Formula — vector တစ်ခု၏ byte ပမာဏ = dim × 4 (fp32 အတွက်)။
fp32 သည် float value တစ်ခုကို 4 byte ဖြင့် သိမ်းဆည်းသော precision format ဖြစ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Vector အရေအတွက်ကို သတ်မှတ်ပါ။
၂။ Dimension ကို သတ်မှတ်ပါ။
၃။ Vector တစ်ခု၏ byte ပမာဏ = dim × 4 ဖြင့် တွက်ချက်ပါ။
၄။ စုစုပေါင်း byte = vector အရေအတွက် × vector တစ်ခု၏ byte ဖြင့် တွက်ချက်ပါ။
၅။ GB သို့ ပြောင်းရန် 10⁹ (1,000,000,000) ဖြင့် စားပါ။

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

Vector သန်းချီ သိမ်းဆည်းသောအခါ storage ပမာဏ သိသာစွာ တိုးပွားသည်။
ကြိုတင်တွက်ချက်ထားပါက server capacity planning ကို တိကျစွာ ပြုလုပ်နိုင်သည်။
pgvector တွင် vector type (vector သို့ halfvec) အလိုက် storage size ကွာခြားသည်။
PostgreSQL + pgvector stack တွင် index memory footprint ကိုပါ တွဲဖက်တွက်ချက်ရန် လိုအပ်သည်။

---

## Subtopic 3 — L2 Normalization နှင့် Cosine / Dot / L2 ဆက်စပ်မှု

### ဘာကို ဆိုလိုတာလဲ

L2 normalization ဆိုသည်မှာ vector ၏ L2 norm (magnitude) ကို 1 ဖြစ်အောင် ပြောင်းလဲသည့် operation ဖြစ်သည်။
Normalize ပြုလုပ်ပြီးနောက် vector တွင် direction information သာ ကျန်ရှိသည်။

### ဘာကြောင့် လဲ

Distance metric သုံးမျိုး၏ ဆက်စပ်မှုသည် ဒီ normalization အပေါ် မူတည်သည်။
Normalized vector များအတွက် cosine similarity နှင့် dot product သည် တူညီသော ranking ပေးသည်။
ထို့ကြောင့် normalized vector များကိုသာ သိမ်းဆည်းပါက dot product (ပိုမိုမြန်ဆန်သည်) ဖြင့် cosine နှင့် တူညီသော ရလဒ် ရရှိနိုင်သည်။
Normalization မပြုလုပ်ပါက dot product သည် magnitude ကြီးမားသော vector များကို ဦးစားပေးသဖြင့် ranking ပုံပျက်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Vector ၏ norm ကို တွက်ချက်ပါ — value တစ်ခုစီ၏ နှစ်ထပ်ကိန်း ပေါင်းလဒ်၏ square root ဖြစ်သည်။
၂။ Value တစ်ခုစီကို norm ဖြင့် စားပါ။
၃။ ရလဒ် vector ၏ norm သည် 1 ဖြစ်လာသည်။
၄။ Normalized vector များအတွက် cosine = dot ဖြစ်ကြောင်း စစ်ဆေးပါ။

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

Cosine သည် text retrieval တွင် အသုံးအများဆုံး metric ဖြစ်သည်။
Vector များ normalized ဖြစ်နေပါက dot product ကို အသုံးပြုခြင်းဖြင့် query speed မြင့်တက်ပြီး ရလဒ် ranking မှာ တူညီသည်။
PostgreSQL + pgvector တွင် `<=>` (cosine distance) နှင့် `<#>` (negative dot product) operator များ ရရှိနိုင်သည်။
Model အချို့ (arXiv 2212.03533 — GeText စာတမ်းအုပ်စု) သည် normalized output ကို တိုက်ရိုက်ထုတ်ပေးသည်။
SQL အသုံးပြုပုံ ဥပမာ —

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

Matryoshka embedding ဆိုသည်မှာ vector ၏ ရှေ့ပိုင်း prefix ကို သီးသန့် ဖြတ်ယူ၍ အသုံးပြုနိုင်သော representation ဖြစ်သည်။
အမည်မှာ ရုရှား matryoshka doll (အကြီးထဲတွင် အသေး ထည့်ထားသော အရုပ်) မှ ဆင်းသက်လာသည်။
ဥပမာ — dim 1024 vector ၏ ရှေ့ပိုင်း 256 dimension ကို သီးသန့် အသုံးပြုနိုင်သည်။

### ဘာကြောင့် လဲ

Storage ချွေတာလိုသော်လည်း accuracy ဆုံးရှုံးမှုကိုလည်း ကန့်သတ်လိုသည်။
Matryoshka နည်း (arXiv 2205.13147) တွင် training အဆင့်၌ prefix dimension များကိုပင် သီးသန့် objective ဖြင့် train လုပ်သဖြင့် prefix များတွင် semantic information စုစည်းနေသည်။
ထို့ကြောင့် truncate လုပ်ထားသော vector သည် production အသုံးပြုနိုင်သော quality ရှိသည်။
Screening အဆင့်တွင် dim အသေး၊ reranking အဆင့်တွင် dim အပြည့် — နှစ်ဆင့် ခွဲ၍ အသုံးပြုနိုင်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Model ၏ full-dimension vector output ကို ယူပါ။
၂။ လိုချင်သော truncated dim (ဥပမာ 256) ကို သတ်မှတ်ပါ။
၃။ Vector ၏ ရှေ့ပိုင်း prefix 256 dimension ကို ဖြတ်ယူပါ။
၄။ ဖြတ်ယူထားသော vector ကို ပြန်လည် L2 normalize ပြုလုပ်ပါ။
၅။ Truncated vector ဖြင့် screening ပြုလုပ်ပြီး၊ top candidate များကို full-dimension vector ဖြင့် rerank ပြုလုပ်ပါ။

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

Large-scale corpus တွင် storage နှင့် query ကုန်ကျစရိတ်သည် အဓိက ကန့်သတ်ချက် ဖြစ်သည်။
Matryoshka ဖြင့် truncated dim ကို အဆင့်တစ် (screening) တွင်လည်းကောင်း၊ full dim ကို အဆင့်နှစ် (reranking) တွင်လည်းကောင်း အသုံးပြုနိုင်သည်။
ဒီ နှစ်ဆင့် approach သည် speed နှင့် accuracy ကြား trade-off ကို ချိန်ညှိပေးသည်။

---

## Subtopic 5 — Batch Encoding၊ Cache နှင့် Embedding Version စီမံခန့်ခွဲမှု

### ဘာကို ဆိုလိုတာလဲ

Batch encoding ဆိုသည်မှာ text အုပ်စုတစ်ခုကို model ထဲသို့ တစ်ကြိမ်တည်း ပေးပို့၍ encode ပြုလုပ်ခြင်း ဖြစ်သည်။
Cache ဆိုသည်မှာ ယခင်တွက်ချက်ပြီးသော embedding များကို သိမ်းဆည်းထားပြီး ပြန်လည်တွက်ချက်မှု ရှောင်ရှားသည့် စနစ် ဖြစ်သည်။
Version စီမံခန့်ခွဲမှု ဆိုသည်မှာ embedding model ပြောင်းလဲသောအခါ vector များ၏ model version ကို ခြေရာခံ ထိန်းသိမ်းခြင်း ဖြစ်သည်။

### ဘာကြောင့် လဲ

တူညီသော text ကို ထပ်ခါထပ်ခါ encode ပြုလုပ်ပါက compute အချိန်နှင့် ကုန်ကျစရိတ် မြင့်မားသည်။
Embedding model ပြောင်းလဲလိုက်ပါက vector space တစ်ခုလုံး ပြောင်းလဲသွားသည်။
Version မတူညီသော vector များကို တစ် index တည်းတွင် ရောနှောရှာဖွေပါက similarity score များ အဓိပ္ပာယ်မရှိတော့ဘဲ ranking ပုံပျက်သည်။
ထို့ကြောင့် version tag ခံပြီး index ကို သီးသန့် တည်ဆောက်ရန် လိုအပ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Batch size သတ်မှတ်ပါ — ဥပမာ 32။
၂။ Text များကို batch များအလိုက် ခွဲပါ။
၃။ Cache key ကို (model_version, text hash) အဖြစ် တည်ဆောက်ပါ။
၄။ Cache hit ဖြစ်ပါက ပြန်လည်တွက်ချက်မှု မပြုလုပ်ဘဲ သိမ်းထားသော vector ကို အသုံးပြုပါ။
၅။ Model ပြောင်းလဲသောအခါ version အသစ်ဖြင့် embedding များကို ပြန်လည်တွက်ချက်ပြီး index အသစ် တည်ဆောက်ပါ — atomic swap ဖြင့် အစားထိုးပါ။
၆။ Cache ကို version ခွဲ၍ သိမ်းထားသဖြင့် model ပြောင်းပြီးနောက် version မကိုက်ညီသော cache ကို မှားယွင်းစွာ အသုံးပြုမိခြင်းကို ကာကွယ်နိုင်သည်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Embedding model တစ်ကြိမ် ပြောင်းလဲလိုက်ပါက index တစ်ခုလုံးကို ပြန်လည်တွက်ချက်ရသည်။ Version မှတ်တမ်း ရှိနေပါက chunk တစ်ခုစီကို ဘယ် model ဖြင့် တွက်ချက်ထားကြောင်း ခွဲခြားသိရှိနိုင်ပြီး migration ကို အဆင့်လိုက် လုပ်ဆောင်နိုင်သည်။

## အနှစ်ခုပ်

- Model ရွေးချယ်မှုသည် corpus ၏ ဘာသာစကားနှင့် domain အပေါ် မူတည်သည်။
- Dimension သည် storage ပမာဏနှင့် ကုန်ကျစရိတ်ကို တိုက်ရိုက် ဆုံးဖြတ်သည်။
- L2 normalization ပြုလုပ်ပြီးနောက် cosine နှင့် dot product တို့၏ ranking ရလဒ် တူညီသည်။
- Matryoshka truncation ဖြင့် storage ပမာဏ သေးငယ်သော index တည်ဆောက်နိုင်သည်။
- Embedding version ကို cache နှင့် index တို့တွင် တွဲဖက်မှတ်တမ်းတင်ထားရမည်။
