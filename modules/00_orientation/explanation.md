# M0 — RAG Data Engineering ရဲ့ မြေပုံ၊ Pipeline အဆင့်များနှင့် Vector Search ကို ဘယ်အချိန်သုံးမလဲ

ဒီ module သည် ဒီ course ၏ ပထမဆုံး အခြေခံ သင်ခန်းစာ ဖြစ်သည်။
RAG (Retrieval-Augmented Generation) ၏ pipeline မြေပုံကို ချပြသည်။
အကြောင်းအရာအားလုံးသည် official documentation များ — pgvector၊ LlamaIndex၊ LangChain ရှိ open docs များ — ကို အခြေခံသည်။

---

## Subtopic 1 — RAG Pipeline ရဲ့ အဆင့် ၈ ခု အကြည့်

### ဘာကို ဆိုလိုတာလဲ

RAG pipeline သည် document များမှ စတင်၍ အဖြေတစ်ခု ထုတ်ပေးသည့်အထိ အဆင့် ၈ ဆင့် ပါဝင်သော လုပ်ငန်းစီးဆင်းမှု ဖြစ်သည်။
အဆင့်များမှာ — ingest၊ chunk၊ embed၊ index၊ retrieve၊ rerank၊ generate၊ evaluate ဖြစ်သည်။
အနှစ်ချုပ်အားဖြင့် — data ရယူခြင်း၊ ခွဲခြမ်းခြင်း၊ vector အဖြစ် ပြောင်းလဲခြင်း၊ သိမ်းဆည်းခြင်း၊ ရှာဖွေခြင်း၊ အစီအစဉ် ပြန်စီခြင်း၊ အဖြေထုတ်ခြင်း၊ အရည်အသွေး စစ်ဆေးခြင်း တို့ ဖြစ်သည်။

### ဘာကြောင့် လဲ

အဆင့်များကို မခွဲခြားထားပါက စနစ်ကို observability မရှိဘဲ လည်ပတ်ရသည်။
အဖြေများ မှားယွင်းနေပါက အမှားသည် chunk၊ embed၊ retrieve အနက် မည်သည့်အဆင့်ကြောင့်ဖြစ်သည်ကို ခွဲခြား၍ မရနိုင်ပါ။
အဆင့် ၈ ခု ခွဲခြားထားပါက အဆင့်တစ်ခုချင်းစီကို သီးခြား တိုင်းတာ၍ ရသည်။
ဒါက data engineer ၏ အဓိက တာဝန် ဖြစ်သည်။
LlamaIndex docs တွင်လည်း RAG ကို အဆင့်ခွဲ၍ ရှင်းပြထားသည် — https://docs.llamaindex.ai/en/stable/ ကို ကြည့်ပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ **ingest** — source document (PDF၊ web page၊ database record) များကို စနစ်ထဲသို့ ရယူသည်။
၂။ **chunk** — စာရှည်များကို retrieve လုပ်၍ရသော အပိုင်းငယ်များအဖြစ် ခွဲခြမ်းသည်။
၃။ **embed** — chunk တစ်ခုချင်းစီကို numeric embedding vector အဖြစ် ပြောင်းလဲသည်။
၄။ **index** — vector များကို vector store ထဲ သိမ်းဆည်း၍ search လုပ်နိုင်အောင် စီစဉ်သည်။
၅။ **retrieve** — query ကို embed လုပ်ပြီး ဆင်တူသော chunk များကို ရှာဖွေသည်။
၆။ **rerank** — ရရှိလာသော candidate chunk များကို ပိုမိုတိကျသော scorer ဖြင့် အစီအစဉ် ပြန်စီသည်။
၇။ **generate** — ရွေးချယ်ထားသော chunk များနှင့်အတူ LLM ကို အဖြေထုတ်စေသည်။
၈။ **evaluate** — အဖြေ၏ အရည်အသွေးကို တိုင်းတာသည်။

### ဥပမာ

```python
# M0 pipeline map: print the 8 stages of a RAG pipeline.
# No database or vector engine is used here; this is a map, not a live system.

stages = [
    ("ingest",    "read raw documents into the system"),
    ("chunk",     "split long text into small pieces"),
    ("embed",     "turn each chunk into a numeric vector"),
    ("index",     "store vectors so they can be searched"),
    ("retrieve",  "find chunks similar to the question"),
    ("rerank",    "re-order the found chunks by usefulness"),
    ("generate",  "ask an LLM to answer using the chunks"),
    ("evaluate",  "measure how good the answer was"),
]

for i, (name, what) in enumerate(stages, 1):
    print(f"{i}. {name}: {what}")
# Expected output:
# 1. ingest: read raw documents into the system
# 2. chunk: split long text into small pieces
# 3. embed: turn each chunk into a numeric vector
# 4. index: store vectors so they can be searched
# 5. retrieve: find chunks similar to the question
# 6. rerank: re-order the found chunks by usefulness
# 7. generate: ask an LLM to answer using the chunks
# 8. evaluate: measure how good the answer was
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

အဆင့် ၁–၄ သည် offline (ingestion) ဘက်၊ အဆင့် ၅–၈ သည် online (query-time) ဘက် ဖြစ်သည်။
ဒီ နှစ်ပိုင်းကို ခွဲခြားသိရှိပါက စနစ်ကို တည်ငြိမ်အောင် ဒီဇိုင်းဆွဲနိုင်သည်။
Offline ပိုင်းသည် ကြိုတင် ပြင်ဆင်နိုင်သော နေရာ၊ online ပိုင်းသည် latency အနိမ့်ဆုံး လိုအပ်သော နေရာ ဖြစ်သည်။

---

## Subtopic 2 — Vector Search နဲ့ Keyword Search ကွာခြားချက်

### ဘာကို ဆိုလိုတာလဲ

**Keyword search** သည် token အလိုက် တိကျသော စကားလုံး ကိုက်ညီမှုကို ရှာဖွေသည်။
"database" ဟု ရှာပါက "database" စာလုံးပါသော chunk များသာ ရလဒ်ထွက်သည်။
**Vector search** သည် semantic similarity — အဓိပ္ပာယ်အရ ဆင်တူမှု — ကို ရှာဖွေသည်။
Cosine similarity ဖြင့် တိုင်းတာသည်။
**Hybrid** သည် နှစ်မျိုးကို ပေါင်းစပ် အသုံးပြုသည့် architecture ဖြစ်သည်။

### ဘာကြောင့် လဲ

Vector search သီးသန့် အသုံးပြုပါက အမည်၊ ကုတ်နံပါတ်၊ version identifier ကဲ့သို့ exact-match token များတွင် အမှားဖြစ်တတ်သည်။
"error E-4021" ကို ရှာပါက vector search သည် "E-4021" ကို semantic အရ ခွဲခြားနိုင်ခြင်း မရှိဘဲ keyword search က တိုက်ရိုက် ရှာဖွေတွေ့ရှိသည်။
Keyword search သီးသန့် အသုံးပြုပါက စကားလုံး မတူသော်လည်း အဓိပ္ပာယ် နီးစပ်သော query များ လွတ်သွားတတ်သည်။
"ဘယ်လို data တွေ သိမ်းထားလဲ" နှင့် "storage plan" သည် token မတူသော်လည်း အဓိပ္ပာယ် နီးစပ်သည်။
ဒါကြောင့် production စနစ်များတွင် hybrid ကို အများဆုံး ရွေးချယ်ကြသည်။
pgvector သည် vector search ကို PostgreSQL ထဲတွင် တိုက်ရိုက် ပေးစွမ်းနိုင်သည် — https://github.com/pgvector/pgvector ကို ကြည့်ပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Query ရောက်လာပါက နှစ်ဖက် parallel ရှာဖွေပါ — keyword retrieval တစ်ဖက်၊ vector retrieval တစ်ဖက်။
၂။ Vector retrieval အတွက် question ကို embed လုပ်ပါ။
၃။ Keyword retrieval အတွက် exact token များ ထုတ်ပါ။
၄။ ရလဒ်နှစ်ခုကို fusion လုပ်ပါ — နောက် module တွင် RRF (Reciprocal Rank Fusion) ကို လေ့လာရမည်။
၅။ ရွေးချယ်မှု စည်းမျဉ်း — exact identifier ပါပါက keyword၊ semantic query ဖြစ်ပါက vector၊ နှစ်မျိုးလုံး လိုအပ်ပါက hybrid။

### ဥပမာ

```python
# Standard-library example: cosine similarity between a question and two chunks.
# A real system would run this in a vector engine like pgvector
# (https://github.com/pgvector/pgvector); here we compute it in pure Python.

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def norm(a):
    return sum(x * x for x in a) ** 0.5

def cosine(a, b):
    return dot(a, b) / (norm(a) * norm(b))

# Scripted toy vectors, NOT real embeddings: 3 dimensions for readability.
# A real embedding model would give hundreds of dimensions.
question = [0.9, 0.1, 0.0]   # "how is data stored"
chunk_a  = [0.8, 0.2, 0.1]   # chunk about storage plans
chunk_b  = [0.0, 0.3, 0.9]   # chunk about team meetings

print("score_a =", round(cosine(question, chunk_a), 4))
print("score_b =", round(cosine(question, chunk_b), 4))
# Expected output:
# score_a = 0.9838
# score_b = 0.0349
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Retrieval strategy ရွေးချယ်မှု မှန်ကန်ပါက query အများစုအတွက် သက်ဆိုင်ရာ chunk များ ပြန်လည် ရရှိသည်။
ရွေးချယ်မှု မှားယွင်းပါက downstream အဆင့်များ အားလုံး၏ အရည်အသွေး ကျဆင်းသည်။
ဒါက embedding model အရည်အသွေး မြင့်မားမှုဖြင့် ပြန်လည် ကာမိနိုင်သော အချက် မဟုတ်ပါ။

---

## Subtopic 3 — Latency နဲ့ ကုန်ကျစရိတ် အတွက်အချေ

### ဘာကို ဆိုလိုတာလဲ

**Latency** သည် query ပေးချိန်မှ အဖြေ ရရှိချိန်အထိ ကြာမြင့်ချိန် ဖြစ်သည်။
**Cost** သည် pipeline လည်ပတ်ရန် လိုအပ်သော ငွေကုန်ကြေးကျနှင့် compute/storage resource များ ဖြစ်သည်။
အဓိက ကုန်ကျစရိတ်များမှာ — embedding generation၊ vector storage၊ retrieval query time တို့ ဖြစ်သည်။

### ဘာကြောင့် လဲ

Storage footprint ကို ကြိုတင် တွက်ချက်နိုင်ပါက capacity plan ကို ကြိုတင် ချမှတ်နိုင်သည်။
ပုံသေနည်းမှာ — `chunks × dimensions × bytes_per_float` ဖြစ်သည်။
fp32 တွင် float တစ်လုံးသည် 4 bytes ယူသည် (fp32 format ၏ သတ်မှတ်ချက်)။
မှန်းဆ၍ မတွက်ပါနှင့် — အောက်တွင် အဆင့်ဆင့် တွက်ပြထားသည်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ chunk အရေအတွက်ကို သတ်မှတ်ပါ (ဒီဥပမာတွင် 1,000,000)။
၂။ embedding dimension ကို သတ်မှတ်ပါ (ဒီဥပမာတွင် 768)။
၃။ vector တစ်ခု၏ size = `768 × 4` bytes။
၄။ စုစုပေါင်း = `chunks × vector_size`။
၅။ pgvector ၏ HNSW ကဲ့သို့ index များသည် graph structure ထပ်ဆောက်သဖြင့် storage အနည်းငယ် တိုးသည် — ဒီအဆင့်တွင် raw vector data ကိုသာ တွက်မည်။

### ဥပမာ

```python
# Worked example with clearly-labelled assumptions.
# Assumptions (not from any benchmark): 1,000,000 chunks,
# 768 dimensions per embedding, fp32 (4 bytes per float), no index overhead.

CHUNKS = 1_000_000
DIMS = 768
BYTES_PER_FLOAT = 4  # fp32

vector_bytes = DIMS * BYTES_PER_FLOAT
total_bytes = CHUNKS * vector_bytes
total_mb = total_bytes / (1024 * 1024)
total_gb = total_mb / 1024

print(f"one vector      = {vector_bytes} bytes")
print(f"total raw bytes = {total_bytes:,}")
print(f"total size      = {total_mb:,.0f} MB ({total_gb:,.2f} GB)")
# Expected output:
# one vector      = 3072 bytes
# total raw bytes = 3,072,000,000
# total size      = 2,930 MB (2.86 GB)
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Storage တွက်ချက်မှု မှားယွင်းပါက database capacity ပြည့်သွားနိုင်သည်။
Latency သည် retrieve နှင့် generate အဆင့်များတွင် အများဆုံး စုဆောင်းမိသည်။
Chunk အရေအတွက် လျှော့ချပါက latency ကျသော်လည်း coverage လျော့သည်။
ဒီ trade-off သည် data engineer ၏ ဆုံးဖြတ်ချက် ဖြစ်သည်။

---

## Subtopic 4 — Chunking အတွက် စည်းမျဉ်းများ

### ဘာကို ဆိုလိုတာလဲ

**Chunking** သည် document တစ်ခုကို embed လုပ်၍ retrieve ပြန်နိုင်သော retrieval unit (chunk) များအဖြစ် ခွဲခြမ်းခြင်း ဖြစ်သည်။
**Chunk size** သည် chunk တစ်ခု၏ စကားလုံး (သို့) character အရေအတွက်။
**Overlap** သည် chunk နှစ်ခုကြား ထပ်နေသော အပိုင်း — boundary တွင် အဓိပ္ပာယ် မပျက်စေရန် ဖြစ်သည်။

### ဘာကြောင့် လဲ

Chunk ရှည်လွန်းပါက embedding vector သည် အဓိပ္ပာယ် အမျိုးမျိုး ရောနှောနေပြီး similarity score ရောထွေးသွားသည်။
Chunk တိုလွန်းပါက LLM အတွက် လုံလောက်သော context မပါဝင်တော့ပါ။
LangChain docs သည် chunk size နှင့် overlap ရွေးချယ်မှုကို ဒီဇိုင်း ဆုံးဖြတ်ချက်တစ်ခုအဖြစ် ရှင်းပြထားသည် — https://python.langchain.com/docs/concepts/text_splitters/ ကို ကြည့်ပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ text ကို chunk size စကားလုံးအရ ခွဲပါ။
၂။ overlap စကားလုံး အရေအတွက်ကို နောက် chunk ထဲ ထပ်ထည့်ပါ။
၃။ chunk တစ်ခုချင်းစီတွင် metadata (source၊ chunk index) ပါစေပါ။
၄။ Sentence boundary တွင် ဖြတ်ပါက အဓိပ္ပာယ် ပိုမို ပြည့်စုံသည်။

### ဥပမာ

```python
# Simple fixed-size chunker with overlap, standard library only.

def chunk_words(text, size, overlap):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + size
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = end - overlap  # move back so chunks overlap
    return chunks

text = "RAG stores facts in chunks so answers stay grounded in real documents every time"
# Assumption: chunk size 5 words, overlap 2 words.
chunks = chunk_words(text, size=5, overlap=2)
for i, c in enumerate(chunks):
    print(f"chunk {i}: {c}")
# Expected output:
# chunk 0: RAG stores facts in chunks
# chunk 1: in chunks so answers stay
# chunk 2: answers stay grounded in real
# chunk 3: in real documents every time
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Chunking သည် pipeline ၏ အစောဆုံး အဆင့် ဖြစ်သော်လည်း နောက်ဆုံး အရည်အသွေးအထိ သက်ရောက်မှု ရှိသည်။
Chunk boundary ကောင်းမွန်ပါက retrieval precision မြင့်သည်။
Boundary မှားယွင်းပါက downstream တွင် ပြန်လည် ကုစား၍ မရနိုင်တော့ပါ။

---

## Subtopic 5 — Data Engineering တာဝန်နဲ့ Model တာဝန် ခွဲခြားချက်

### ဘာကို ဆိုလိုတာလဲ

RAG စနစ်တွင် တာဝန် နယ်နိမိတ် နှစ်ခု ရှိသည်။
**Data engineering တာဝန်** — ingestion၊ chunking၊ indexing၊ pipeline စနစ်တကျ လည်ပတ်မှု။
**Model တာဝန်** — embedding model ရွေးချယ်မှု၊ LLM ရွေးချယ်မှု၊ prompt ဒီဇိုင်း။
နယ်နိမိတ် ခွဲခြားနိုင်ပါက incident တစ်ခု၏ root cause ကို မြန်ဆန်စွာ ခွဲခြားနိုင်သည်။

### ဘာကြောင့် လဲ

အဖြေမှားယွင်းသည့်အခါ အပြစ်ကို model ဘက်သို့ အလွယ်တကူ လွှဲပြောလေ့ ရှိသည်။
သို့သော် လက်တွေ့တွင် မသန့်စင်ရသေးသော document၊ chunk boundary မှားယွင်းမှု၊ metadata အမှားများက အဓိက root cause ဖြစ်လေ့ ရှိသည်။
Root cause ဘက် မှားယွင်းစွာ စုံစမ်းပါက incident resolution အချိန် တိုးသည်။
ဒါကြောင့် တာဝန် နယ်နိမိတ် နှစ်ခုကို ကြိုတင် ခွဲခြားထားသင့်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ အမှားအယွင်းများကို အမျိုးအစားခွဲပါ — data error၊ chunking error၊ embedding error၊ index error၊ prompt error။
၂။ Data ဘက်ကို data engineer က ပိုင်သည် — ingestion၊ chunking၊ metadata၊ versioning။
၃။ Model ဘက်ကို ML engineer က ပိုင်သည် — embedding model၊ reranker၊ generation prompt။
၄။ Retrieval quality ကို နှစ်ဖက်ပူးပေါင်း တိုင်းတာရသည် — recall@k နှင့် အဖြေမှန်နှုန်း။
၅။ တာဝန် မခွဲထားပါက "data မှားလား၊ model မှားလား" ဆိုသည့် မေးခွန်းကို ဖြေဆိုနိုင်သူ မရှိတော့ပါ။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

RAG စနစ်များတွင် ပြဿနာ အများစုသည် generation ဘက်တွင် မဟုတ်ဘဲ retrieval ဘက်တွင် ဖြစ်သည်။ ဒါကြောင့် pipeline အဆင့်တိုင်းကို သီးခြား တိုင်းတာနိုင်သော အခြေအနေ ထားရှိဖို့ လိုသည်။

## အနှစ်ခုပ်

- RAG pipeline တွင် အဆင့် ၈ ခု ရှိပြီး အဆင့်တစ်ခုချင်းစီကို သီးခြား တိုင်းတာနိုင်သည်။
- Vector search သည် semantic similarity အတွက်၊ keyword search သည် exact token matching အတွက် သင့်တော်သည်။
- ကုန်ကျစရိတ်နှင့် latency ကို အဆင့်တိုင်းတွင် ချိန်ခွင်လျှာ ညှိရသည်။
- Data engineer နှင့် ML engineer တာဝန် နယ်နိမိတ်ကို ကြိုတင် ခွဲခြားထားပါ။
- Retrieval quality ကောင်းမွန်မှသာ generation quality ကောင်းနိုင်သဖြင့် retrieval ကို ဦးစွာ စစ်ဆေးပါ။
