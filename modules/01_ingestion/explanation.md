# M1 — Corpus Ingestion: ရင်းမြစ်များ၊ Text ဆွဲထုတ်ခြင်း၊ Normalisation နှင့် Upsert/Delete

ဒီ module မှာ corpus (စုစည်းထားတဲ့ စာရွက်စာတမ်း အစု) ကို ဘယ်လို စုဆောင်းပြီး vector search အတွက် ပြင်ဆင်မလဲ ကို လေ့လာကြပါမယ်။ အားလုံးက original study material ပါ။ ရင်းမြစ်ကတော့ official open documentation (PostgreSQL docs, Hugging Face Datasets docs, Apache Airflow docs) တွေပဲ ဖြစ်ပါတယ်။

---

## Subtopic 1 — ရင်းမြစ် အမျိုးအစားများ နှင့် Text Extraction

### ဘာကို ဆိုလိုတာလဲ

ရင်းမြစ် (source) ဆိုတာ စာသား ရယူနိုင်တဲ့ နေရာ အားလုံး ကို ဆိုလိုတယ်။ ဥပမာ PDF၊ HTML၊ Markdown နဲ့ database row (ဇယား တစ်ကြောင်း) တို့ ပါတယ်။ Text extraction (text ဆွဲထုတ်ခြင်း) က ဒီ ရင်းမြစ်တွေကနေ ရှင်းလင်းတဲ့ စာသားကို ထုတ်ယူတဲ့ အဆင့် ပါတယ်။

### ဘာကြောင့် လဲ

Vector search မှာ quality (အရည်အသွေး) က ingestion (အချက်အလက် ထည့်သွင်းခြင်း) ကနေ စတင်ပါတယ်။ ဆွဲထုတ်တဲ့ အခါ HTML tag တွေ၊ navigation menu (မျက်နှာပြင် လမ်းညွှန် စာရင်း) တွေ ပါသွားရင် embedding မှာ အမှိုက် ဝင်သွားပါတယ်။ အမှိုက် ဝင်တဲ့ vector ကို ရှာတာက မှားယွင်းတဲ့ အဖြေ ပေးတတ်ပါတယ်။ ဒါကြောင့် extraction က ပထမဆုံး အရေးကြီးတဲ့ အဆင့် ဖြစ်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ ရင်းမြစ် အမျိုးအစားကို သတိမှတ်ပါ — တစ်မျိုးစီမှာ အမှိုက် pattern က မတူပါ။
၂။ အလိုရှိတဲ့ အပိုင်းကိုသာ ရွေးပါ — HTML မှာဆို `<main>` ထဲက စာသားလို့ သတ်မှတ်ပါ။
၃။ Boilerplate (page တိုင်းမှာ ထပ်တွဲနေတဲ့ header၊ footer စာ) ကို ဖယ်ရှားပါ။
၄။ ရလာတဲ့ စာသားကို နောက်ဆင့် (normalisation) အတွက် ပြင်ဆင်ပါ။

### ဥပမာ

```python
# Lesson-local extraction demo. In production you would use a real
# HTML parser and a PDF library; here we use a tiny deterministic mock.
import re

RAW_HTML = (
    "<html><body>"
    "<nav>Home | About | Contact</nav>"
    "<main><h1>Vector Search Basics</h1>"
    "<p>Vector search finds similar items.</p></main>"
    "<footer>(c) 2025 Example Corp</footer>"
    "</body></html>"
)

def extract_main_text(html):
    # Keep only the <main> block, then strip tags.
    m = re.search(r"<main>(.*?)</main>", html, re.S)
    main_html = m.group(1) if m else ""
    text = re.sub(r"<[^>]+>", " ", main_html)
    return " ".join(text.split())

print(extract_main_text(RAW_HTML))
# Expected output:
# Vector Search Basics Vector search finds similar items.
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

ရင်းမြစ် တခုချင်းစီက သူ့ပုံစံအတိုင်း အမှိုက် ရှိပါတယ်။ PDF မှာ page number (စာမျက်နှာ နံပါတ်) တွေ၊ HTML မှာ cookie banner (အသိပေး စာ) တွေ ပါလာတတ်ပါတယ်။ Hugging Face `datasets` library က document loading နဲ့ cleaning pipeline တွေကို တရားဝင် docs (https://huggingface.co/docs/datasets/index) မှာ ဖော်ပြထားပါတယ်။ Airflow ကတော့ ဒီလို extraction အဆင့်တွေကို scheduled pipeline (အချိန်ဇယားအလိုက် လည်ပတ်တဲ့ စီးဆင်းမှု) အဖြစ် စီမံပေးပါတယ် (https://airflow.apache.org/docs/)။

---

## Subtopic 2 — Unicode Normalisation

### ဘာကို ဆိုလိုတာလဲ

Unicode normalisation ဆိုတာ စာသားတွေကို စံတစ်မျိုးတည်း ပြောင်းပေးတဲ့ လုပ်ငန်း ပါတယ်။ မတူတဲ့ byte (ကွန်ပျူတာ အချက်အလက် အခြေခံ ယူနစ်) နှစ်ခုက မျက်နှာပြင်မှာ တူတဲ့ စာလုံး ဖြစ်နေတာ ရှိပါတယ်။ ဥပမာ combining diacritic (ပေါင်းစပ် အက္ခရာ အမှတ်) နဲ့ precomposed form (ကြိုပြင်ဆင်ထားတဲ့ ပုံစံ) ပါ။

### ဘာကြောင့် လဲ

တူတဲ့ စာလုံး နှစ်ခုက byte မတူရင် hash (အချက်အလက်ကနေ ထုတ်တဲ့ သေးငယ်တဲ့ လက်မှတ်) ချင်း မတူပါတယ်။ Hash မတူရင် duplicate (အထပ်) စစ်ခြင်း မှားပါတယ်။ Tokenizer တွေကလည်း မတူတဲ့ byte ကို မတူတဲ့ ရလဒ် ပေးတတ်ပါတယ်။ ဒါကြောင့် ingestion မှာ အရင်ဆုံး normalise လုပ်ဖို့ လိုပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ ရင်းမြစ် အားလုံးကနေ စာသား ရောက်လာပါ။
၂။ Python standard library က `unicodedata.normalize("NFC", text)` နဲ့ NFC form (စံစုစည်းပုံစံ) ပြောင်းပါ။
၃။ Whitespace (ကွက်လပ်) တွေကို တစ်ခုတည်း ဖြစ်အောင် ချုပ်ပါ။
၄။ Normalise ပြီးတဲ့ စာသားကိုသာ storage နဲ့ hashing မှာ သုံးပါ။

### ဥပမာ

```python
# NFC normalisation: same visible text, different byte sequences.
import unicodedata

# "e" + combining acute accent vs precomposed "é"
a = "cafe\u0301"          # e followed by combining accent
b = "caf\u00e9"           # single precomposed character
print(a == b)             # False before normalisation

na = unicodedata.normalize("NFC", a)
nb = unicodedata.normalize("NFC", b)
print(na == nb)           # True after NFC
print(len(a), len(na))    # lengths differ before/after
# Expected output:
# False
# True
# 5 4
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Corpus က လူများ ရေးထားတာ ဆိုရင် စာရိုက်ပုံ မတူတာတွေ အများကြီး ရှိပါတယ်။ Normalisation မလုပ်ဘဲ duplicate စစ်ရင် တူတဲ့ စာရွက် အများကြီးကို မတူဘူးလို့ ထင်ပါတယ်။ ဒါက storage နဲ့ search quality နှစ်ခုစလုံးကို ထိခိုက်ပါတယ်။

---

## Subtopic 3 — Duplicate စစ်ခြင်း (Hash / Content Fingerprint)

### ဘာကို ဆိုလိုတာလဲ

Content fingerprint (အနှစ်ချုပ် လက်မှတ်) ဆိုတာ စာသားတစ်ခုရဲ့ အနှစ်ချုပ် hash ပါ။ SHA-256 လို hash function (input တစ်ခုကနေ သေးငယ်တဲ့ လက်မှတ် ထုတ်ပေးတဲ့ ဖန်ရှင်) က စာသားကို ကိုယ်စားပြုပါတယ်။ ဒီ fingerprint တူရင် စာသားလည်း တူတယ်လို့ ယူဆနိုင်ပါတယ်။

### ဘာကြောင့် လဲ

Duplicate စာရွက်တွေ ထည့်လိုက်ရင် ရှာဖွေရာမှာ တူတဲ့ ရလဒ် ထပ်နေပါတယ်။ ရလဒ် ထပ်နေရင် အသုံးပြုသူက အချက်အလက် အမျိုးမျိုး မမြင်ရဘဲ တစ်ခုတည်းကိုပဲ မြင်ရပါတယ်။ Storage ကလည်း အလွန်အကျွံ ကုန်ပါတယ်။ ဒါကြောင့် ingestion မှာ duplicate ကို စစ်ရပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Normalise ပြီးတဲ့ စာသားကို ယူပါ။
၂။ `hashlib.sha256` နဲ့ fingerprint ထုတ်ပါ။
၃။ Fingerprint ကို seen set (မြင်ပြီးသား စာရင်း) ထဲ ရှိမရှိ စစ်ပါ။
၄။ ရှိရင် ချန်လိုက်ပါ — မရှိရင် ထည့်ပြီး set မှာ မှတ်ပါ။

### ဥပမာ

```python
# Exact-duplicate detection via SHA-256 fingerprints.
import hashlib

def fingerprint(text):
    # Hash the normalised text; hex digest is the fingerprint.
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

docs = ["Vector search finds similar items.",
        "Vector search finds similar items.",   # exact duplicate
        "Vector search ranks similar items."]   # different content

seen = set()
unique = []
for d in docs:
    fp = fingerprint(" ".join(d.split()))
    if fp not in seen:
        seen.add(fp)
        unique.append(d)
print(len(docs), len(unique))
print(unique[-1])
# Expected output:
# 3 2
# Vector search ranks similar items.
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

PostgreSQL မှာ JSONB column ထဲ document metadata (စာရွက်ရဲ့ အချက်အလက် အသေးစား) သိမ်းလို့ ရပါတယ် — JSONB ရဲ့ အမျိုးအစားနဲ့ indexing အကြောင်းကို တရားဝင် docs (https://www.postgresql.org/docs/current/datatype-json.html) မှာ ဖတ်နိုင်ပါတယ်။ Fingerprint ကို column တစ်ခု အဖြစ် သိမ်းပြီး `UNIQUE` constraint (ထပ်ခြင်း တားမြစ်ချက်) တပ်ရင် database ကနေ ကိုယ်တိုင် duplicate တားပါတယ်။

---

## Subtopic 4 — Incremental Update နှင့် Deletion Semantics

### ဘာကို ဆိုလိုတာလဲ

Incremental update (တစိုက်ရိုက် ပြင်ဆင်မှု) ဆိုတာ corpus ထဲက ပြောင်းလဲသွားတဲ့ အပိုင်းကိုသာ ပြန်ယူတာ ပါတယ်။ Deletion semantics (ဖျက်ခြင်း စည်းမျဉ်း) ကတော့ ရင်းမြစ်ကနေ ပျက်သွားတဲ့ document ကို vector index ထဲက ဘယ်လို ဖယ်ရမလဲ ဆိုတာ ပါတယ်။

### ဘာကြောင့် လဲ

Corpus တစ်ခွင်လုံးကို နောက်ဆုံးပေါ် အချက်အလက်နဲ့ ပြန်တည်ဆောက်ရင် ချိန်နဲ့ ကုန်စရိတ် အများကြီး ကုန်ပါတယ်။ ပြောင်းလဲမှုက စာရွက် ဆယ်ဂဏန်းပဲ ရှိတာနဲ့ အားလုံး ပြန်လုပ်တာက အလွန် ဖြုန်းတာ ပါ။ အပြန်အလှန်အားဖြင့် ဖျက်လိုက်တဲ့ document ကို index ထဲ မဖယ်ရင် ရှာလိုက်တဲ့အခါ သေပြီး လင့်ခ် ပေါ်လာပါတယ်။ ဒါက user experience ကို ပျက်စေပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Document တိုင်းကို သူ့ fingerprint နဲ့ မှတ်ထားပါ။
၂။ အသစ် ရောက်လာတဲ့ batch (အစု) ရဲ့ fingerprint တွေနဲ့ နောက်ဆုံး သိထားတဲ့ set ကို နှိုင်းပါ။
၃။ Fingerprint အသစ်ဖြစ်တာတွေကို upsert (ရှိရင် ပြင်၊ မရှိရင် ထည့်) လုပ်ပါ။
၄။ အရင် batch မှာ ရှိပြီး အသစ် batch မှာ မရှိတော့တာတွေကို delete လုပ်ပါ။

### ဥပမာ

```python
# Compute the add/update set and the delete set between two batches.
def fingerprint(text):
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

old_batch = {"doc_a": "alpha text", "doc_b": "beta text"}
new_batch = {"doc_a": "alpha text", "doc_b": "beta text v2", "doc_c": "gamma text"}

old_fps = {k: fingerprint(v) for k, v in old_batch.items()}
new_fps = {k: fingerprint(v) for k, v in new_batch.items()}

to_upsert = [k for k in new_fps if old_fps.get(k) != new_fps[k]]
to_delete = [k for k in old_fps if k not in new_fps]
print("upsert:", sorted(to_upsert))
print("delete:", sorted(to_delete))
# Expected output:
# upsert: ['doc_b', 'doc_c']
# delete: []
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

PostgreSQL + pgvector မှာ document id ကို primary key လုပ်ပြီး `INSERT ... ON CONFLICT ... DO UPDATE` (တိုက်ဆိုင်ရင် ပြင်၊ မဟုတ်ရင် ထည့်) statement နဲ့ upsert လုပ်လို့ ရပါတယ်။ ဒါက idempotency (အကြိမ်ကြိမ် လုပ်စေကာမှ ရလဒ်တူစေခြင်း) ကို အာမခံပေးပါတယ်။ Airflow docs (https://airflow.apache.org/docs/) မှာ DAG (task တွေရဲ့ မှီခိုမှု ဇယား) နဲ့ backfill (အရင်ပြန် ဖြည့်ခြင်း) အကြောင်း ဖော်ပြထားပြီး incremental pipeline တွေကို စီမံနိုင်ပါတယ်။

```sql
-- Valid for PostgreSQL with the pgvector extension.
INSERT INTO chunks (doc_id, content, embedding)
VALUES ('doc_b', 'beta text v2', '[0.1, 0.2, 0.3]')
ON CONFLICT (doc_id)
DO UPDATE SET content = EXCLUDED.content,
              embedding = EXCLUDED.embedding;
```

---

## Subtopic 5 — Ingestion ရဲ့ Idempotency

### ဘာကို ဆိုလိုတာလဲ

Idempotency (အကြိမ်ကြိမ် လုပ်စေကာမှ ရလဒ်တူစေခြင်း) ဆိုတာ ingestion job (အလုပ်တစ်ခု) ကို နှစ်ခေါက် run (လည်ပတ်) ချင်း ရလဒ်က တစ်ခေါက် run ချင်းနဲ့ အတူတူ ဖြစ်နေတာ ပါတယ်။

### ဘာကြောင့် လဲ

Pipeline တွေက network error (ကွန်ရက် ချို့ယွင်းမှု) တွေကြောင့် အလယ်မှာ ရပ်တတ်ပါတယ်။ Idempotent မဖြစ်တဲ့ job ကို ပြန် run ရင် document တွေ နှစ်ဆ ထပ်ပါ သွားပါတယ်။ ဒါက duplicate ပြဿနာကို ပြန်ဖန်တီးစေပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Document တိုင်းကို stable id (မပြောင်းလဲတဲ့ အမှတ်အသား) ပေးပါ — random id မဟုတ်ပါ။
၂။ Stable id ကို content fingerprint ကနေ ဆင်းပါ၊ ဒါမှမဟုတ် ရင်းမြစ်က URL လို မှန်ကန်တဲ့ id သုံးပါ။
၃။ ရေးတဲ့ အခါ upsert (replace-or-insert) pattern သုံးပါ။
၄။ Job ကို ဘယ်အချိန် run စေကာမှ corpus ရဲ့ အခြေအနေက တူနေစေဖို့ အဆင့်တိုင်းကို သေချာ စစ်ပါ။

### ဥပမာ

```python
# Idempotent ingestion: running "run_ingestion" twice gives the same store.
import hashlib

def stable_id(text):
    # Deterministic id from content, not a random value.
    return "doc-" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]

def run_ingestion(store, documents):
    # Upsert by stable id: re-running never duplicates.
    for text in documents:
        store[stable_id(text)] = text
    return store

store = {}
docs = ["alpha text", "beta text"]
run_ingestion(store, docs)
run_ingestion(store, docs)   # same batch twice, on purpose
print(len(store))
print(sorted(store.values()))
# Expected output:
# 2
# ['alpha text', 'beta text']
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

အချက်အလက် စနစ်တွေမှာ job ပျက်ပြီး ပြန် run တာက ပုံမှန် ဖြစ်စဉ် ပါ။ Airflow က task retry ကို တရားဝင် docs မှာ ဖော်ပြထားပြီး idempotent task ဒီဇိုင်းကို ထောက်ခံပါတယ်။ Ingestion ကို ပြန် run လုပ်တိုင်း vector ထပ်မပွားအောင် content hash နဲ့ စစ်တာ မဖြစ်မနေ လိုပါတယ်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Ingestion က တစ်ခါ run ပြီး ပြီးရော ဖြစ်တဲ့ အလုပ် မဟုတ်ပါဘူး။ Document ပြင်တာ၊ delete တာ၊ permission ပြောင်းတာ အားလုံး နောက်ဆက်တွဲ လုပ်ရပါတယ်။ Idempotent မဖြစ်ရင် duplicate chunk တွေ စုမိပြီး retrieval အရည်အသွေး ကျဆင်းပါတယ်။

## အနှစ်ခုပ်

- ရင်းမြစ်တိုင်းကို text အဖြစ် ဆွဲထုတ်ပြီး boilerplate ဖယ်ရှားပါ။
- Unicode normalization နှင့် whitespace သန့်ရှင်းမှု ကို အစပိုင်းမှာ လုပ်ပါ။
- Duplicate ကို content hash နဲ့ စစ်ပြီး upsert semantics သတ်မှတ်ပါ။
- Delete လုပ်တဲ့အခါ vector၊ metadata နှင့် cache အားလုံး ဖယ်ပါ။
- Task တိုင်း ပြန် run လို့ရအောင် idempotent ဖြစ်စေပါ။
