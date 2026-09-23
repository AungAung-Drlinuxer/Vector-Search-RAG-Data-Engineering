# M2 — Chunking မဟာဗျူဟာများနှင့် Metadata ဒီဇိုင်း

ဒီ module မှာ document ကို အပိုင်းလေးတွေခွဲတဲ့ နည်း (chunking) နဲ့ အပိုင်းတစ်ခုချင်းဆီ metadata တွဲတဲ့ ဒီဇိုင်းကို လေ့လာကြမယ်နော်။
ရည်ညွှန်းချက် — LangChain Text Splitters concept docs, LlamaIndex docs, Hugging Face Tokenizers docs တွေပါ။

## ၁။ Chunking ဆိုတာ ဘာလဲ နှင့် ဘာကြောင့် လိုအပ်လဲ

### ဘာကို ဆိုလိုတာလဲ
Chunking ဆိုတာ document ရှည်ကြီးကို အပိုင်းငယ်လေးတွေ (chunks) အဖြစ် ခွဲတာပါတယ်။
Vector search မှာ ခွဲလိုက်တဲ့ အပိုင်းတစ်ခုချင်းစီကို embedding vector အဖြစ် ပြောင်းပြီး သိမ်းတယ်။
LangChain docs က text splitter တွေကို “long text into smaller chunks” ပြောင်းတဲ့ tool လို့ ဖွင့်ဆိုပါတယ်။

### ဘာကြောင့် လဲ
ပထမ — embedding model တွေမှာ input အရှည် အကန့်အသတ်ရှိတယ်။
Document တစ်ခုလုံးကို တစ် vector နဲ့ သိမ်းလိုက်ရင် အဓိပ္ပာယ် အားလုံး တစ်နေရာတည်း ပြေ့ငြံသွားတယ်။
ဥပမာ — စာ ၅၀ ကြောင်းစာမှာ အဖြေတစ်ကြောင်းပဲ ပါရင်၊ vector တစ်ခုတည်းက အဖြေကို မြုပ်ကွယ်ပစ်တယ်။
ဒုတိယ — retrieval ပြန်ဖတ်ရတဲ့ အချိန်မှာ အပိုင်းသေးသေးလေ အဖြေနဲ့ ဆိုင်တဲ့ အပိုင်းရ လွယ်တယ်။
ဒါပေမယ့် သေးလွန်းရင် အချက်အလက် ပိုင်းခြားခံရပြီး အဓိပ္ပာယ် လျော့သွားတယ်။
ဒါကြောင့် chunk အရွယ်က retrieval အရည်အသွေးနဲ့ တိုက်ရိုက်ဆက်နွယ်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ Raw document ကို ယူတယ်။
၂။ ခွဲပုံစံ (fixed-size၊ recursive၊ token-based) တစ်မျိုးရွေးတယ်။
၃။ Overlap (နောက်အပိုင်းနဲ့ ထပ်တဲ့ အပိုင်း) ဆိုင်ရာ အရွယ်သတ်မှတ်တယ်။
၄။ Chunk တစ်ခုချင်းကို embedding ပြောင်းပြီး store ထဲထည့်တယ်။
၅။ ရှာတဲ့အခါ query vector နဲ့ chunk vectors တွေကို နှိုင်းရတယ်။

### ဥပမာ

```python
# Simple fixed-size character chunking with overlap, standard library only.
text = ("RAG systems retrieve relevant text chunks and pass them to a model. "
        "Chunking decides what the model gets to see at answer time. "
        "Good boundaries preserve meaning; bad boundaries split facts apart.")

chunk_size = 60   # characters per chunk
overlap = 15       # characters shared between consecutive chunks

chunks = []
start = 0
while start < len(text):
    end = min(start + chunk_size, len(text))
    chunks.append(text[start:end])
    if end == len(text):
        break
    start = end - overlap

for i, c in enumerate(chunks):
    print(i, repr(c))
# Expected output:
# 0 'RAG systems retrieve relevant text chunks and pass them to a'
# 1 ' pass them to a model. Chunking decides what the model gets '
# 2 'the model gets to see at answer time. Good boundaries preser'
# 3 'undaries preserve meaning; bad boundaries split facts apart.'
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
Production RAG မှာ chunking က data pipeline ရဲ့ ပထမဆုံး အဆင့်ပါ။
ဒီအဆင့်မှာ မှားရင် အောက်ဘက် retrieval၊ reranking၊ generation အားလုံး မှားသွားတယ်။
အကောင်းဆုံး embedding model ရှိထားတောင် ခွဲမှားရင် အဖြေ မှန်အောင် မရနိုင်ဘူးနော်။

## ၂။ Splitter အမျိုးအစားများ — fixed-size၊ recursive၊ token-based၊ semantic

### ဘာကို ဆိုလိုတာလဲ
Fixed-size splitter က စာလုံးရေ (character) အရွယ်အတိုင်းအတာအတိုင်း တုံးတုံးပြတ်တာပါတယ်။
Recursive splitter က paragraph → sentence → word စာခွဲနိုင်တဲ့ သင်္ချာ အဆင့်ဆင့်နဲ့ သဘားကျကျ ခွဲတာပါတယ်။
LangChain docs အရ recursive character splitter က separator list ကို အစဉ်လိုက် စမ်းပြီး အကောင်းဆုံး boundary ရွေးတယ်။
Token-based splitter က tokenizer (စာကို model နားလည်တဲ့ ယူနစ်လေးတွေအဖြစ် ပြောင်းတဲ့ ကိရိယာ) နဲ့ အရေအတွက်ရေတယ်။
Hugging Face tokenizers docs အရ tokenizer က “raw text into tokens” ပြောင်းပေးတယ်။
Semantic chunking က စာပိုင်းတွေရဲ့ အဓိပ္ပာယ် ပြောင်းလဲမှုကို ကြည့်ပြီး ခွဲတာပါတယ်။

### ဘာကြောင့် လဲ
Fixed-size လွယ်ပေမယ့် စာကြောင်းအလယ်မှာ ပြတ်တတ်တယ်။
“budget was 1.2 million” ဆိုတဲ့ ဂဏန်းကို ထက်ဝက် ဖြတ်လိုက်ရင် ဂဏန်းအဓိပ္ပာယ် ပျက်တယ်။
Recursive နည်းက paragraph အပိုင်းအစိတ်ကို အရင်လိုက်တာကြောင့် သဘားကျတဲ့ boundary ရတယ်။
Token-based က model ရဲ့ context window နဲ့ တိုက်ရိုက်ကိုက်တာကြောင့် တိကျတယ်။
Semantic က အဓိပ္ပာယ်အရ ခွဲလို့ အကောင်းဆုံးပေမယ့် ကုန်ကျစရိတ် ပိုများတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ Recursive splitter က separator list ("\n\n", "\n", " ", "") ကို အစဉ်အတိုင်း စမ်းတယ်။
၂။ Chunk က အရွယ်ထက် ကြီးရင် နောက် separator ပိုသေးတာနဲ့ ပြန်ခွဲတယ်။
၃။ သင့်တင့်တဲ့ boundary တွေ့တာနဲ့ ခွဲပြီး merge လုပ်တယ်။
၄။ Token-based မှာ tokenizer နဲ့ token ရေတွက်ပြီး အရွယ်ကန့်သတ်တယ်။
၅။ Semantic မှာ အပိုင်းတိုင်း embedding နဲ့ ခြားနားမှုကြည့်ပြီး threshold ကျော်ရင် အပိုင်းသစ် ဖွင့်တယ်။

### ဥပမာ

```python
# Recursive-style split: prefer larger separators first, standard library only.
import re

def recursive_split(text, chunk_size, separators):
    # Try each separator in order until one splits the text small enough.
    for sep in separators:
        parts = text.split(sep) if sep != "" else list(text)
        if all(len(p) <= chunk_size for p in parts) or sep == separators[-1]:
            # Merge adjacent parts up to chunk_size, re-inserting separator.
            chunks, buf = [], ""
            for p in parts:
                candidate = (buf + sep + p) if buf else p
                if len(candidate) <= chunk_size:
                    buf = candidate
                else:
                    if buf:
                        chunks.append(buf)
                    buf = p
            if buf:
                chunks.append(buf)
            return chunks
    return [text]

doc = ("Intro: system overview.\n\n"
       "Data: we split documents into chunks.\n\n"
       "Search: cosine similarity ranks chunks.")

result = recursive_split(doc, 45, ["\n\n", "\n", " ", ""])
for i, c in enumerate(result):
    print(i, repr(c))
# Expected output:
# 0 'Intro: system overview.'
# 1 'Data: we split documents into chunks.'
# 2 'Search: cosine similarity ranks chunks.'
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
Document အမျိုးအစားအလိုက် splitter ရွေးရတယ်။
Markdown နဲ့ code အတွက် structure-aware splitter တွေရှိပြီး LangChain နဲ့ LlamaIndex မှာ ပြင်းပြင်းထားပါတယ်။
ပုံမှန် စာရေးစာတွေအတွက် recursive က မှန်ကန်တဲ့ default ဖြစ်နေတယ်နော်။

## ၃။ Overlap ရွေးချယ်မှုနှင့် chunk အရွယ် အပေးအယူ

### ဘာကို ဆိုလိုတာလဲ
Overlap ဆိုတာ chunk နှစ်ခုကြား ထပ်နေတဲ့ စာအပိုင်းပါတယ်။
Chunk size က အပိုင်းတစ်ခုရဲ့ အရှည်ပါ။
ဒီနှစ်ခုက တစ်ခုနဲ့တစ်ခု ဆန့်ကျင်ဘက်ဖြစ်နေတယ်။

### ဘာကြောင့် လဲ
Overlap မပါရင် အရေးကြီးတဲ့ အချက်အလက်က chunk boundary အပေါ်မှာ အလယ်မှာ ရောက်နေတတ်တယ်။
ဥပမာ — “လစာက ၁၂ သိန်းဖြစ်တယ်” ဆိုတာကို နှစ်ခုဖြတ်လိုက်ရင် ဘယ် chunk မှာမှ အဖြေပြည့် မရတော့ဘူး။
Overlap က ဒီပြဿနာကို လျှော့ပေးတယ်၊ ဒါပေမယ့် store အရွယ် တိုးစေတယ်။
Chunk သေးရင် retrieval တိကျတယ်၊ ဒါပေမယ့် အချက်အလက် အံ့အားသွေးရှာ ကွာတယ်။
Chunk ကြီးရင် အချက်အလက် ပြည့်တယ်၊ ဒါပေမယ့် မဆိုင်တဲ့ အပိုင်းလည်း ဝင်လာတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ Document အမျိုးအစားကို သုံးသပ်တယ်။
၂။ Chunk size ကို စမ်းသပ်ဖို့ baseline တစ်ခု ချထားတယ်။
၃။ Overlap ကို chunk size ရဲ့ ဆယ်ရာခိုင်နှုန်း အနည်းငယ် စတင်တယ်။
၄။ Retrieval quality (recall@k) ကို တိုင်းပြီး size/overlap ချိန်တယ်။
၅။ Store ကုန်ကျစရိတ်နဲ့ တိုးလာတဲ့ quality ကို နှိုင်းပြီး ရပ်တယ်။

### ဥပမာ

```python
# Compare storage cost of different overlap settings.
# Assumption stated by the lesson: 1,000,000 characters of text, chunk_size = 500.
total_chars = 1_000_000
chunk_size = 500

for overlap in [0, 50, 100]:
    # Step per chunk = chunk_size - overlap; last chunk may be shorter.
    step = chunk_size - overlap
    n_chunks = 0
    start = 0
    while start < total_chars:
        n_chunks += 1
        start += step
    stored = n_chunks * chunk_size  # upper bound on stored characters
    print(f"overlap={overlap}: chunks={n_chunks}, stored_chars~{stored}")
# Expected output:
# overlap=0: chunks=2000, stored_chars~1000000
# overlap=50: chunks=2223, stored_chars~1111500
# overlap=100: chunks=2500, stored_chars~1250000
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
Overlap တိုးတိုင်း store ကုန်ကျစရိတ်နဲ့ embedding ရေ တိုးတယ်။
ဒီ ဥပမာမှာ overlap ၁၀၀ က အချက်အလက် ၂၅ ရာခိုင်နှုန်း ပိုသိမ်းရတယ်။
ဘယ် overlap က အကောင်းဆုံးလဲဆိုတာ dataset အလိုက် ကွာတာကြောင့် ကိုယ်ပိုင် dataset နဲ့ တိုင်းပြီး ရွေးရတယ်နော်။

## ၄။ Heading/structure ထိန်းသိမ်းခြင်းနှင့် parent-child၊ small-to-big retrieval

### ဘာကို ဆိုလိုတာလဲ
Structure-preserving chunking က document ရဲ့ heading၊ စာပိုဒ် အဆင့်အတန်းကို ခွဲရင်းနဲ့ ထိန်းသိမ်းတာပါတယ်။
Parent-child chunking က အပိုင်းငယ် (child) တွေကို ရှာပြီး အဖြေပေးတဲ့အခါ အပိုင်းကြီး (parent) ကို ပြန်သုံးတာပါတယ်။
Small-to-big retrieval လို့လည်း ခေါ်တယ် — ရှာတာက သေးသေး၊ ဖတ်တာက ကြီးကြီး။

### ဘာကြောင့် လဲ
ရှာတဲ့အချိန်မှာ အဓိပ္ပာယ်က ကွဲပြားတဲ့ အပိုင်းသေးလေ တိကျလေပါတယ်။
ဒါပေမယ့် LLM ကို ပေးတဲ့အခါ အပိုင်းသေးလွန်းရင် အချက်အလက် မလုံလောက်ဘူး။
ဥပမာ — “ကုန်ကျစရိတ် အမျိုးအစား” ဆိုတဲ့ အကြောင်းအရာကို စာကြောင်းတစ်ကြောင်းတည်းနဲ့ ရှာရင် ရင်နိုင်တယ်။
ဒါပေမယ့် အဖြေပြည့်ဖို့ နားမှာရှိတဲ့ စာပိုဒ်တစ်ခုလုံး လိုတတ်တယ်။
ဒါကြောင့် ရှာတဲ့ unit နဲ့ ဖတ်တဲ့ unit ကို ခွဲထားတာက ပိုကောင်းတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ Document ကို heading အလိုက် parent အပိုင်းတွေ ခွဲတယ်။
၂။ Parent တစ်ခုစီကို child အပိုင်းသေးတွေ ထပ်ခွဲတယ်။
၃။ Child တိုင်းမှာ parent ရဲ့ ID ကို metadata အနေနဲ့ မှတ်တယ်။
၄။ Retrieval မှာ child vectors တွေနဲ့ပဲ ရှာတယ်။
၅။ Top child တွေရရင် သက်ဆိုင်တဲ့ parent တွေကို ပြန်ဆွဲပြီး LLM ကို ပေးတယ်။

### ဥပမာ

```python
# Small-to-big retrieval: search over children, return parents.
# Assumption: toy corpus, cosine similarity computed in pure Python.
import math

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb)

parents = {
    "P1": "Refund policy: items can be returned within 30 days with receipt.",
    "P2": "Shipping: standard delivery takes 5-7 business days.",
}
children = {
    "C1": ("P1", "returned within 30 days", [1.0, 0.1, 0.0]),
    "C2": ("P1", "with receipt", [0.1, 0.9, 0.0]),
    "C3": ("P2", "delivery takes 5-7", [0.0, 0.1, 1.0]),
}

query = [0.9, 0.2, 0.0]  # stands in for an embedding of "how do I return an item?"

# In a real system this similarity search would run in a vector database.
scores = [(cid, cosine(query, vec)) for cid, (_, _, vec) in children.items()]
scores.sort(key=lambda t: t[1], reverse=True)

top_child = scores[0][0]
parent_id = children[top_child][0]
print("top child:", top_child, "parent:", parent_id)
print("context sent to model:", parents[parent_id])
# Expected output:
# top child: C1 parent: P1
# context sent to model: Refund policy: items can be returned within 30 days with receipt.
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
Heading ထိန်းထားရင် chunk တစ်ခုက ဘယ် section ကနေလာတယ်ဆိုတာ သိသွားတယ်။
ဥပမာ — “ကုန်ပိုင်း” heading အောက်က “၅၀%” ဆိုတာက လျှော့စျေး ဆိုတာ သိရတယ်။
Small-to-big က LlamaIndex မှာ တရားဝင်ထောက်ခံတဲ့ pattern တစ်ခုဖြစ်ပြီး retrieval precision နဲ့ context completeness နှစ်ခုလုံး ရစေတယ်။

## ၅။ Chunk metadata ဒီဇိုင်း — source၊ section၊ page၊ permission

### ဘာကို ဆိုလိုတာလဲ
Metadata ဆိုတာ chunk တစ်ခုရဲ့ vector နဲ့ စာသားအပြင် သိမ်းထားတဲ့ အပိုသတင်းအချက်ပါတယ်။
ဥပမာ — source document၊ section heading၊ page နံပါတ်၊ permission (ဘယ်သူ ဖတ်ခွင့်ရှိလဲ) တွေပါ။

### ဘာကြောင့် လဲ
Metadata မရှိရင် chunk က လွင့်ပျံတဲ့ စာပိုင်းတစ်ခုပဲ ဖြစ်နေတယ်။
အဖြေမှာ “ဘယ် document က ဘယ် page ကနေလာလဲ” ပြန်ညွှန်ဖို့ source၊ section၊ page၊ chunk index တို့ လိုပါတယ်။ Citation ပြဖို့နဲ့ permission filter လုပ်ဖို့ နှစ်ခုစလုံးအတွက် metadata က အခြေခံ ဖြစ်ပါတယ်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Metadata မပါတဲ့ chunk က ဘယ်ကလာမှန်း မသိတဲ့ စာသားတစ်ပိုင်း ဖြစ်ပါတယ်။ အဲဒါက citation မပေးနိုင်တဲ့ အဖြေကို ဖြစ်စေပြီး၊ ACL စစ်လို့ မရတာကြောင့် လုံခြုံရေး အန္တရာယ် ဖြစ်လာပါတယ်။

## အနှစ်ခုပ်

- Chunk အရွယ်က retrieval အရည်အသွေးနှင့် ကုန်ကျစရိတ်ကို တိုက်ရိုက် ဆုံးဖြတ်ပါတယ်။
- Overlap က နယ်စပ် အချက်အလက် ပြတ်တာကို ကာကွယ်ပါတယ်။
- Structure (heading၊ list) ကို ထိန်းထားတဲ့ chunking က ပိုကောင်းပါတယ်။
- Metadata (source၊ page၊ permission) က citation နှင့် filter အတွက် မဖြစ်မနေ လိုပါတယ်။
- Chunking မဟာဗျူဟာကို eval set နဲ့ တိုင်းပြီး ရွေးပါ။
