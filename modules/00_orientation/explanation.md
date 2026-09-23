# M0 — RAG Data Engineering ရဲ့ မြေပုံ၊ Pipeline အဆင့်များနှင့် Vector Search ကို ဘယ်အချိန်သုံးမလဲ

ဒီ module က ဒီ course ရဲ့ ပထမဆုံး အခြေခံသင်ခန်းစာ ဖြစ်ပါတယ်။
RAG (Retrieval-Augmented Generation — ရှာဖွေမှုနဲ့ ပေါင်းစပ်ထားတဲ့ စာကြောင်း ထုတ်ပေးမှု) ရဲ့ မြေပုံကို ကြည့်ပါမယ်။
အားလုံးရဲ့ အခြေခံက official documentation တွေပဲ ဖြစ်ပါတယ် — pgvector, LlamaIndex, LangChain ရဲ့ open docs တွေပါ။

---

## Subtopic 1 — RAG Pipeline ရဲ့ အဆင့် ၈ ခု အကြည့်

### ဘာကို ဆိုလိုတာလဲ

RAG pipeline ဆိုတာ document တွေကနေ စတာပြီး အဖြေကောင်းတစ်ခု ထွက်လာတဲ့ အဆင့် ၈ ဆင့်ရှိတဲ့ လမ်းကြောင်း ဖြစ်ပါတယ်။
အဆင့်တွေက — ingest, chunk, embed, index, retrieve, rerank, generate, evaluate ပါ။
ရိုးရှင်းအောင် ပြောရရင် — အချက်အလက်ကို ယူပါ၊ ဖြတ်ပါ၊ vector ထဲ ပြောင်းပါ၊ သိမ်းပါ၊ ရှာပါ၊ အစီအစဉ်ပြန်ပါ၊ အဖြေရေးပါ၊ စစ်ပါ ဆိုတာပါပဲ။

### ဘာကြောင့် လဲ

အဆင့်တွေ မခွဲထားရင် စနစ်က ထိန်းချုပ်လို့ မရပါဘူး။
ဥပမာ — အဖြေတွေ မှားနေရင်၊ အမှားက chunk လား၊ embed လား၊ retrieve လား ဆိုတာ မသိရပါဘူး။
အဆင့် ၈ ခု ခွဲထားရင် တစ်ခုချင်းစီကို ခွဲစစ်လို့ ရပါတယ်။
ဒါက data engineer ရဲ့ အဓိက အလုပ် ဖြစ်ပါတယ်။
LlamaIndex docs မှာလည်း RAG ကို အဆင့်ခွဲပြီး ရှင်းပြထားပါတယ် — https://docs.llamaindex.ai/en/stable/ ကို ကြည့်ပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ **ingest** — document (PDF, web page, database record) တွေကို စနစ်ထဲ ယူလာပါတယ်။
၂။ **chunk** — စာရှည်ကြီးကို အပိုင်းလေးတွေ ဖြတ်ပါတယ် (chunk ဆိုတာ စာအပိုင်းလေး ဖြစ်ပါတယ်)။
၃။ **embed** — chunk တစ်ခုချင်းစီကို vector (ကိန်းတန်း — အမှတ်အသားတွေရဲ့ အစဉ်) အဖြစ် ပြောင်းပါတယ်။
၄။ **index** — vector တွေကို vector store ထဲ သိမ်းပါတယ်။
၅။ **retrieve** — မေးခွန်းကို vector အဖြစ် ပြောင်းပြီး ဆင်တူတဲ့ chunk တွေကို ရှာပါတယ်။
၆။ **rerank** — ရှာတွေ့တဲ့ chunk တွေကို အရေးကြီးစွာ ပြန်စီပါတယ်။
၇။ **generate** — ရွေးချယ်ထားတဲ့ chunk တွေနဲ့အတူ LLM ကို ဖြေဆိုခိုင်းပါတယ်။
၈။ **evaluate** — အဖြေအရည်အသွေးကို တိုင်းတာပါတယ်။

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

အဆင့် ၁-၄ က offline ဘက်ပါ၊ အဆင့် ၅-၈ က online (မေးချိန်) ဘက်ပါ။
ဒီ နှစ်ခု ခွဲတတ်ရင် စနစ်ကို တည်ငြိမ်အောင် လုပ်လို့ ရပါတယ်။
Offline ပိုင်းက ကြိုပြင်ဆင်လို့ ရတဲ့နေရာ၊ online ပိုင်းက မြန်မြန်ပြန်ရရတဲ့နေရာပါ။

---

## Subtopic 2 — Vector Search နဲ့ Keyword Search ကွာခြားချက်

### ဘာကို ဆိုလိုတာလဲ

**Keyword search** ဆိုတာ စကားလုံးချင်း တစ်ခုပေါ်တစ်ခု ကိုက်တာကို ရှာတာပါ။
"database" ဆို ရှာရင် "database" စာလုံးပါတဲ့ chunk ပဲ ထွက်လာပါတယ်။
**Vector search** ဆိုတာ အဓိပ္ပာယ်အရ ဆင်တူတာကို ရှာတာပါ။
cosine similarity (vector နှစ်ခုကြား ထောင့်နဲ့ တွက်တဲ့ ဆင်တူမှု အမှတ်) နဲ့ တိုင်းပါတယ်။
**Hybrid** ဆိုတာ နှစ်မျိုးလုံး ပေါင်းသုံးတာပါ။

### ဘာကြောင့် လဲ

Vector search ချည်းပဲ ဆိုရင် အမည်၊ ကုတ်နံပါတ်၊ ဗားရှင်း စတာတွေ မှားတတ်ပါတယ်။
"error E-4021" လို့ ရှာရင် vector က "E-4021" ကို နားမလည်ပါဘူး၊ keyword က တိုက်ရိုက်ရှာတွေ့ပါတယ်။
Keyword ချည်းပဲ ဆိုရင် သံစဉ်အရ ဆင်တဲ့ မေးခွန်းတွေ မှားတတ်ပါတယ်။
"ဘယ်လို data တွေ သိမ်းထားလဲ" နဲ့ "storage plan" က စကားလုံးမတူပေမယ့် အဓိပ္ပာယ် နီးစပ်ပါတယ်။
ဒါကြောင့် hybrid က အသုံးအများဆုံး ရွေးချယ်မှု ဖြစ်ပါတယ်။
pgvector က vector search ကို PostgreSQL ထဲမှာ တိုက်ရိုက်ပေးပါတယ် — https://github.com/pgvector/pgvector ကို ကြည့်ပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ မေးခွန်းလာရင် နှစ်ခြမ်း လုပ်ပါ — keyword နဲ့ ရှာတာတစ်ခြမ်း၊ vector နဲ့ ရှာတာတစ်ခြမ်း။
၂။ vector search အတွက် question ကို embed လုပ်ပါတယ်။
၃။ keyword အတွက် exact token တွေ ထုတ်ပါတယ်။
၄။ ရလဒ်နှစ်ခုကို ရောမွှေပါ — နောက် module မှာ RRF (Reciprocal Rank Fusion) ကို တွေ့ပါမယ်။
၅။ ရွေးချယ်မှု စည်းမျဉ်း — အမည်/ကုတ်ရှိရင် keyword၊ အဓိပ္ပာယ်ရှာရင် vector၊ နှစ်မျိုးလုံးလိုရင် hybrid။

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

ရွေးချယ်မှုမှန်ရင် မေးခွန်းတော်တော်များများ ပြန်လည် ရပါတယ်။
ရွေးချယ်မှုမှားရင် အောက်ပိုင်းအဆင့်တွေ အားလုံး မှားသွားပါတယ်။
ဒါက ဘယ် model ကောင်းလို့မှ မြင့်မားလာတဲ့ အချက် ဖြစ်ပါတယ်။

---

## Subtopic 3 — Latency နဲ့ ကုန်ကျစရိတ် အတွက်အချေ

### ဘာကို ဆိုလိုတာလဲ

**Latency** ဆိုတာ မေးပြီးမှ အဖြေရရှိအထိ စောင့်ရတဲ့ အချိန်ပါ။
**Cost** ဆိုတာ pipeline လည်ပတ်ဖို့ ကုန်တဲ့ ပိုက်ဆံနဲ့ စက်အရင်းအမြစ်ပါ။
အဓိက ကုန်ကျစရိတ်တွေက — embed ခြင်း စရိတ်၊ vector သိမ်းရတဲ့ storage၊ ရှာဖွေချိန်ပါ။

### ဘာကြောင့် လဲ

Storage အရွယ်ကို မြင်ရရင် ဘယ် plan ယူရမလဲ ကို ကြိုတွက်လို့ ရပါတယ်။
တွက်တဲ့ ပုံသေနည်းက — `chunks × dimensions × bytes_per_float` ပါ။
fp32 မှာ float တစ်လုံးက 4 bytes ယူပါတယ် (ဒါက fp32 format ရဲ့ သဘာဝ သတ်မှတ်ချက်ပါ)။
မှန်းဆပြီး မတွက်ပါနဲ့ — ကိုယ်တိုင်တွက်ပြပါမယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ chunk အရေအတွက်ကို သတ်မှတ်ပါ (ဒီဥပမာမှာ 1,000,000)။
၂။ embedding dimension ကို သတ်မှတ်ပါ (ဒီဥပမာမှာ 768)။
၃။ vector တစ်ခုရဲ့ size = `768 × 4` bytes လို့ တွက်ပါ။
၄။ စုစုပေါင်း = `chunks × vector_size` ပါ။
၅။ pgvector ရဲ့ indexing (HNSW တို့) က graph structure ထပ်ဆောက်လို့ storage နည်းနည်း တိုးပါတယ် — ဒီအဆင့်မှာ vector data ချည်းပဲ တွက်ပါမယ်။

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

Storage တွက်မမှန်ရင် database က full သွားတတ်ပါတယ်။
Latency က retrieve နဲ့ generate အဆင့်မှာ အများဆုံး ဖြစ်ပါတယ်။
Chunk အရေအတွက်နည်းရင် latency ကျပေမယ့် အချက်အလက် လျှော့ပါတယ်။
ဒီ trade-off က data engineer ရဲ့ ဆုံးဖြတ်ချက်ပါ။

---

## Subtopic 4 — Chunking အတွက် စည်းမျဉ်းများ

### ဘာကို ဆိုလိုတာလဲ

**Chunking** ဆိုတာ စာရှည်ကြီးကို ဖြတ်တာပါ။
**Chunk size** ဆိုတာ အပိုင်းတစ်ခုရဲ့ စကားလုံး (သို့) character အရေအတွက်ပါ။
**Overlap** ဆိုတာ အပိုင်းနှစ်ခု ထပ်နေတဲ့ အပိုင်းပါ — အဓိပ္ပာယ် မပျက်အောင်ပါ။

### ဘာကြောင့် လဲ

Chunk ရှည်လွန်းရင် အမှားအင်အား သက်ရောက်တတ်ပါတယ်၊ embed က အဓိပ္ပာယ် နှစ်သက်ကွဲသွားတတ်ပါတယ်။
Chunk တိုလွန်းရင် အဓိပ္ပာယ်ပြည့်မီတဲ့ အချက်အလက် မပါပါဘူး။
LangChain docs က chunk size နဲ့ overlap ကို ရွေးရတဲ့ ဆုံးဖြတ်ချက်လို့ ပြောပါတယ် — https://python.langchain.com/docs/concepts/text_splitters/ ကို ကြည့်ပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ text ကို chunk size စကားလုံးအရ ခွဲပါ။
၂။ overlap စကားလုံး အရေအတွက်ကို နောက် chunk ထဲ ထပ်ထည့်ပါ။
၃။ အပိုင်းတစ်ခုချင်း metadata (အရင်းအမြစ်၊ နံပါတ်) ထည့်ပါ။
၄။ sentence ပိုင်းစည်းနဲ့ ဖြတ်ရင် အဓိပ္ပာယ် ပိုမှန်ပါတယ်။

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

Chunking က pipeline ရဲ့ အစောဆုံး အဆင့်ပေမယ့် နောက်ဆုံးအထိ သက်ရောက်ပါတယ်။
Chunk ကောင်းရင် retrieve က သဘာဝကျပါတယ်။
မကောင်းရင် အောက်ပိုင်းမှာ ကုစားလို့ မရတော့ပါဘူး။

---

## Subtopic 5 — Data Engineering တာဝန်နဲ့ Model တာဝန် ခွဲခြားချက်

### ဘာကို ဆိုလိုတာလဲ

RAG မှာ တာဝန်နှစ်မျိုး ရှိပါတယ်။
**Data engineering တာဝန်** — ingest, chunk, index, pipeline စနစ်တကျလည်ပတ်အောင် လုပ်တာပါ။
**Model တာဝန်** — embedding model ရွေး၊ LLM ရွေး၊ prompt ရေးတာပါ။
ခွဲခြားတတ်ရင် ပြဿနာက ဘယ်ဘက်မှာလဲ ဆိုတာ မြန်မြန် ရှာတွေ့ပါတယ်။

### ဘာကြောင့် လဲ

အဖြေမှားတဲ့အခါ အားလုံးက model ကို တိုင်တတ်ပါတယ်။
ဒါပေမယ့် တကယ်တော့ ကြိုမစစ်တဲ့ document၊ မကောင်းတဲ့ chunk၊ metadata မှားတာတွေက အဓိကအကြောင်းရင်း ဖြစ်တတ်ပါတယ်။
ပြဿနာဘက် မှားတိုင်း အချိန်ကုန်ပါတယ်။
ဒါကြောင့် တာဝန်နှစ်မျိုး ကြိုပြီး ခွဲသိထားသင့်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ အမှားတွေကို ဇယားနဲ့ ခွဲထုတ်ပါ — data အမှား၊ chunk အမှား၊ embedding အမှား၊ index အမှား၊ prompt အမှား။
၂။ Data ဘက်ကို data engineer က ပိုင်ပါတယ် — ingestion၊ chunking၊ metadata၊ versioning။
၃။ Model ဘက်ကို ML engineer က ပိုင်ပါတယ် — embedding model၊ reranker၊ generation prompt။
၄။ Retrieval quality ကို နှစ်ဖက်စလုံး တူတူ စစ်ရပါတယ် — recall@k နဲ့ အဖြေမှန်နှုန်း။
၅။ တာဝန် မခွဲထားရင် "data မှားလား၊ model မှားလား" ဆိုတာ ဘယ်သူမှ မဖြေနိုင်တော့ပါဘူး။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

RAG စနစ်တွေမှာ ပြဿနာ အများစုက generation မဟုတ်ဘဲ retrieval ဖြစ်တတ်ပါတယ်။ ဒါကြောင့် pipeline အဆင့်တိုင်းကို သီးခြား တိုင်းတာနိုင်တဲ့ အခြေအနေ ထားရှိဖို့ လိုပါတယ်။

## အနှစ်ခုပ်

- RAG က အဆင့် ၈ ခု ရှိပြီး တစ်ဆင့်ချင်း တိုင်းတာလို့ ရပါတယ်။
- Vector search က အဓိပ္ပာယ် ဆင်တူမှုအတွက်၊ keyword က အတိအကျ စကားလုံးအတွက် သင့်ပါတယ်။
- ကုန်ကျစရိတ်နှင့် latency ကို အဆင့်တိုင်းမှာ ချိန်ရပါတယ်။
- Data engineer နှင့် ML engineer တာဝန်ကို ကြိုခွဲထားပါ။
- Retrieval ကောင်းမှ generation ကောင်းနိုင်တာမို့ အရင်ဆုံး retrieval ကို စစ်ပါ။
