# M2 — Chunking မဟာဗျူဟာများနှင့် Metadata ဒီဇိုင်း

ဒီ module တွင် document များကို chunk များအဖြစ် ခွဲခြမ်းခြင်းနှင့် chunk တစ်ခုစီအတွက် metadata ဒီဇိုင်းချခြင်းကို လေ့လာသည်။
ရည်ညွှန်းအရင်းအမြစ်များ — LangChain Text Splitters concept docs, LlamaIndex docs, Hugging Face Tokenizers docs။

## ၁။ Chunking ဆိုတာ ဘာလဲ နှင့် ဘာကြောင့် လိုအပ်လဲ

### ဘာကို ဆိုလိုတာလဲ
Chunking သည် document တစ်ခုကို embed လုပ်၍ retrieve ပြန်နိုင်သော retrieval unit (chunk) များအဖြစ် ခွဲခြမ်းခြင်း ဖြစ်သည်။
Vector search တွင် chunk တစ်ခုစီကို embedding vector အဖြစ် ပြောင်းလဲပြီး index ထဲ သိမ်းဆည်းသည်။
LangChain docs က text splitter များကို “long text into smaller chunks” ပြောင်းလဲပေးသော tool အဖြစ် သတ်မှတ်ထားသည်။

### ဘာကြောင့် လဲ
ပထမ — embedding model များတွင် maximum input length ကန့်သတ်ချက် ရှိသည်။
Document တစ်ခုလုံးကို vector တစ်ခုတည်းဖြင့် embed လုပ်ပါက အဓိပ္ပာယ်အားလုံး vector တစ်ခုအတွင်း ပြွမ်းသွားပြီး retrieval resolution ကျဆင်းသည်။
ဥပမာ — စာကြောင်း ၅၀ ပါဝင်သော document တွင် အဖြေစာကြောင်း တစ်ကြောင်းသာ ပါဝင်ပါက၊ vector တစ်ခုတည်းက အဖြေ၏ signal ကို ပျမ်းမျှပြုလုပ်လိုက်သကဲ့သို့ ဖြစ်သွားသည်။
ဒုတိယ — retrieval အဆင့်တွင် chunk သေးလေ answer နှင့် သက်ဆိုင်သော အပိုင်းကို တိကျစွာ ရရှိလေ ဖြစ်သည်။
သို့သော် chunk သေးလွန်းပါက context ပြတ်တောက်ပြီး အဓိပ္ပာယ် လျော့နည်းသွားသည်။
ထို့ကြောင့် chunk size သည် retrieval quality နှင့် တိုက်ရိုက် ဆက်နွယ်နေသည်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ Raw document ကို ယူသည်။
၂။ Chunking strategy (fixed-size၊ recursive၊ token-based) တစ်မျိုး ရွေးချယ်သည်။
၃။ Overlap size ကို သတ်မှတ်သည်။
၄။ Chunk တစ်ခုစီကို embed လုပ်ပြီး store ထဲ ထည့်သည်။
၅။ Query အချိန်တွင် query vector နှင့် chunk vector များကို similarity အရ နှိုင်းယှဉ်သည်။

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
Production RAG တွင် chunking သည် data pipeline ၏ ပထမဆုံး အဆင့် ဖြစ်သည်။
ဒီအဆင့်တွင် အမှားပါပါက downstream retrieval၊ reranking၊ generation အဆင့်များ အားလုံး ကျဆင်းသွားသည်။
Embedding model အရည်အသွေး မြင့်မားသော်လည်း chunking မှားယွင်းပါက မှန်ကန်သော အဖြေ ထုတ်ပေးနိုင်ခြင်း မရှိပါ။

## ၂။ Splitter အမျိုးအစားများ — fixed-size၊ recursive၊ token-based၊ semantic

### ဘာကို ဆိုလိုတာလဲ
Fixed-size splitter သည် character count အတိုင်း စာသားကို ပုံသေအရွယ်အစားဖြင့် ဖြတ်တောက်သည်။ Semantic boundary ကို ထည့်သွင်းစဉ်းစားခြင်း မရှိပါ။
Recursive splitter သည် paragraph → sentence → word အဆင့်ဆင့် separator များဖြင့် စာသားကို သဘာဝ boundary တွင် ခွဲထုတ်သည်။
LangChain docs အရ recursive character splitter သည် separator list ကို အစဉ်လိုက် စမ်းသပ်ပြီး အကောင်းဆုံး boundary ကို ရွေးချယ်သည်။
Token-based splitter သည် tokenizer ဖြင့် token count ကို တိုင်းတာပြီး chunk size သတ်မှတ်သည်။
Hugging Face tokenizers docs အရ tokenizer သည် “raw text into tokens” ပြောင်းလဲပေးသည်။
Semantic chunking သည် စာသား၏ semantic meaning ပြောင်းလဲမှုကို တိုင်းတာပြီး boundary သတ်မှတ်သည်။

### ဘာကြောင့် လဲ
Fixed-size သည် အကောင်အထည်ဖော်ရ လွယ်ကူသော်လည်း စာကြောင်းအလယ်တွင် ဖြတ်တောက်နိုင်သည်။
“budget was 1.2 million” ကဲ့သို့ numeric fact ကို ထက်ဝက် ဖြတ်တောက်ပါက အဓိပ္ပာယ် ပျက်ပြယ်သွားသည်။
Recursive နည်းသည် paragraph boundary ကို ဦးစွာ ဦးစားပေးသဖြင့် သဘာဝကျသော boundary ရရှိသည်။
Token-based သည် model ၏ context window နှင့် တိုက်ရိုက် ကိုက်ညီသဖြင့် တိကျသည်။
Semantic သည် အဓိပ္ပာယ်အရ boundary သတ်မှတ်သဖြင့် အရည်အသွေး အမြင့်ဆုံးဖြစ်သော်လည်း embedding ကုန်ကျစရိတ် ပိုမိုမြင့်မားသည်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ Recursive splitter သည် separator list ("\n\n", "\n", " ", "") ကို အစဉ်အတိုင်း စမ်းသပ်သည်။
၂။ Chunk သည် သတ်မှတ်အရွယ်ထက် ကြီးနေပါက နောက်ထပ် separator (ပိုသေးသော granularity) ဖြင့် ပြန်လည်ခွဲထုတ်သည်။
၃။ သင့်လျော်သော boundary ရရှိပါက ခွဲထုတ်ပြီး chunk size အတွင်း merge လုပ်သည်။
၄။ Token-based တွင် tokenizer ဖြင့် token count ရေတွက်ပြီး အရွယ်အစား ကန့်သတ်သည်။
၅။ Semantic တွင် အပိုင်းတိုင်း၏ embedding ကွာခြားချက်ကို တိုင်းတာပြီး threshold ကျော်လွန်ပါက chunk အသစ် ဖွင့်သည်။

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
Document အမျိုးအစားပေါ်မူတည်၍ splitter ရွေးချယ်ရသည်။
Markdown နှင့် code အတွက် structure-aware splitter များ ရှိပြီး LangChain နှင့် LlamaIndex တို့က ပံ့ပိုးထားသည်။
စာသားအခြေပြု document များအတွက် recursive splitter သည် သင့်လျော်သော default ဖြစ်သည်။

## ၃။ Overlap ရွေးချယ်မှုနှင့် chunk အရွယ် အပေးအယူ

### ဘာကို ဆိုလိုတာလဲ
Overlap သည် chunk နှစ်ခုကြားတွင် ထပ်နေသော စာသားအပိုင်း ဖြစ်သည်။
Chunk size သည် chunk တစ်ခု၏ အရှည် ဖြစ်သည်။
ဒီ parameter နှစ်ခုသည် retrieval quality နှင့် storage cost ကြား trade-off တစ်ခုအဖြစ် ဆက်နွယ်နေသည်။

### ဘာကြောင့် လဲ
Overlap မပါဝင်ပါက အရေးကြီးသော fact သည် chunk boundary အလယ်တွင် ကျရောက်နိုင်သည်။
ဥပမာ — “လစာက ၁၂ သိန်းဖြစ်တယ်” ဆိုသည့် fact နှစ်ပိုင်း ခွဲလိုက်ပါက chunk တစ်ခုမှလည်း အဖြေ အပြည့်အစုံ မရရှိတော့ပါ။
Overlap သည် boundary ပြတ်တောက်မှုကို လျှော့ချပေးသော်လည်း storage ပမာဏ တိုးပွားစေသည်။
Chunk သေးပါက retrieval precision မြင့်သော်လည်း chunk တစ်ခုတွင် ပါဝင်သော context ပမာဏ လျော့နည်းသည်။
Chunk ကြီးပါက context ပြည့်စုံသော်လည်း မသက်ဆိုင်သော အပိုင်းများလည်း ပါဝင်လာသည်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ Document အမျိုးအစားကို သုံးသပ်သည်။
၂။ Chunk size အတွက် baseline တစ်ခု သတ်မှတ်သည်။
၃။ Overlap ကို chunk size ၏ ဆယ်ရာခိုင်နှုန်း အနည်းငယ်မှ စတင်သည်။
၄။ Retrieval quality (recall@k) ကို တိုင်းတာပြီး size/overlap ကို ချိန်ညှိသည်။
၅။ Storage ကုန်ကျစရိတ်နှင့် quality တိုးတက်မှုကို နှိုင်းယှဉ်ပြီး သင့်လျော်သော တန်ဖိုး ရပ်တန့်သည်။

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
Overlap တိုးလာသည်နှင့်အမျှ storage ကုန်ကျစရိတ်နှင့် embedding volume တိုးပွားသည်။
ဒီဥပမာတွင် overlap=100 သည် သိမ်းဆည်းရသော character ပမာဏ ၂၅% ခန့် တိုးစေသည်။
အကောင်းဆုံး overlap တန်ဖိုးသည် dataset ပေါ်မူတည်၍ ကွာခြားသဖြင့် ကိုယ်ပိုင် dataset ဖြင့် တိုင်းတာပြီး ရွေးချယ်ရန် လိုအပ်သည်။

## ၄။ Heading/structure ထိန်းသိမ်းခြင်းနှင့် parent-child၊ small-to-big retrieval

### ဘာကို ဆိုလိုတာလဲ
Structure-preserving chunking သည် document ၏ heading နှင့် စာပိုဒ် hierarchy ကို chunking လုပ်စဉ် ထိန်းသိမ်းထားခြင်း ဖြစ်သည်။
Parent-child chunking တွင် retrieval ကို child (အပိုင်းငယ်) များဖြင့် ပြုလုပ်ပြီး၊ context ပြန်လည်ပေးပို့ရာတွင် parent (အပိုင်းကြီး) ကို အသုံးပြုသည်။
ဒီ pattern ကို small-to-big retrieval ဟု ခေါ်သည် — retrieval unit သေးငယ်ပြီး generation unit ကြီးမားသည်။

### ဘာကြောင့် လဲ
Retrieval အဆင့်တွင် semantic scope ကျဉ်းသော chunk သေးလေ matching precision မြင့်လေ ဖြစ်သည်။
သို့သော် LLM ကို ပေးပို့ရာတွင် chunk သေးလွန်းပါက context မလုံလောက်ပါ။
ဥပမာ — “ကုန်ကျစရိတ် အမျိုးအစား” ကဲ့သို့ query တစ်ခုကို စာကြောင်းတစ်ကြောင်းအရွယ် child chunk ဖြင့် match လုပ်နိုင်သည်။
သို့သော် အဖြေ ပြည့်စုံရန် ကပ်လျက် စာပိုဒ် (parent) တစ်ခုလုံး လိုအပ်နိုင်သည်။
ထို့ကြောင့် retrieval unit နှင့် generation unit ကို ခွဲခြားထားခြင်းက ပိုမိုထိရောက်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ Document ကို heading အလိုက် parent chunk များ ခွဲထုတ်သည်။
၂။ Parent တစ်ခုစီကို child chunk အသေးများ ထပ်မံခွဲထုတ်သည်။
၃။ Child တိုင်းတွင် parent ID ကို metadata အဖြစ် သိမ်းဆည်းသည်။
၄။ Retrieval ကို child vector များဖြင့်သာ ပြုလုပ်သည်။
၅။ Top child များ ရရှိပါက သက်ဆိုင်ရာ parent chunk များကို ပြန်လည်ဆွဲထုတ်ပြီး LLM ကို ပေးပို့သည်။

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
Heading ကို ထိန်းသိမ်းထားပါက chunk တစ်ခု၏ section context ကို ပြန်လည်သိရှိနိုင်သည်။
ဥပမာ — “ကုန်စျေးနှုန်း” heading အောက်ရှိ “၅၀%” ဆိုသည့် တန်ဖိုးသည် လျှော့စျေးဖြစ်ကြောင်း heading context ဖြင့် ခွဲခြားနိုင်သည်။
Small-to-big သည် LlamaIndex တွင် တရားဝင် ပံ့ပိုးထားသော pattern ဖြစ်ပြီး retrieval precision နှင့် context completeness နှစ်ခုလုံးကို ရရှိစေသည်။

## ၅။ Chunk metadata ဒီဇိုင်း — source၊ section၊ page၊ permission

### ဘာကို ဆိုလိုတာလဲ
Metadata သည် chunk တစ်ခု၏ vector နှင့် စာသားအပြင် သိမ်းဆည်းထားသော အပို attribute များ ဖြစ်သည်။
ဥပမာ — source document၊ section heading၊ page number၊ permission (access control) တို့ ပါဝင်သည်။

### ဘာကြောင့် လဲ
Metadata မပါဝင်သော chunk သည် မူလအရင်းအမြစ် မသိရသော စာသားအပိုင်းတစ်ခုသာ ဖြစ်သည်။
အဖြေတွင် “ဘယ် document ၏ ဘယ် page မှ လာသလဲ” ပြန်လည်ညွှန်းဆိုရန် source၊ section၊ page၊ chunk index တို့ လိုအပ်သည်။ Citation ပြသခြင်းနှင့် permission filtering နှစ်ခုစလုံးအတွက် metadata သည် အခြေခံ လိုအပ်ချက် ဖြစ်သည်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Metadata မပါသော chunk သည် မူလအရင်းအမြစ် မသိရသော စာသားအပိုင်းသာ ဖြစ်သည်။ ထို့ကြောင့် citation မပေးနိုင်သော အဖြေများ ဖြစ်ပေါ်ပြီး၊ ACL စစ်ဆေး၍ မရသဖြင့် လုံခြုံရေး အန္တရာယ် ဖြစ်လာသည်။

## အနှစ်ခုပ်

- Chunk size သည် retrieval quality နှင့် ကုန်ကျစရိတ်ကို တိုက်ရိုက် ဆုံးဖြတ်သည်။
- Overlap သည် boundary တွင် fact ပြတ်တောက်မှုကို ကာကွယ်သည်။
- Structure (heading၊ list) ကို ထိန်းသိမ်းသော chunking က retrieval quality ပိုမိုမြင့်မားသည်။
- Metadata (source၊ page၊ permission) သည် citation နှင့် filtering အတွက် မရှိမဖြစ် လိုအပ်သည်။
- Chunking မဟာဗျူဟာကို eval set ဖြင့် တိုင်းတာပြီး ရွေးချယ်ရမည်။
