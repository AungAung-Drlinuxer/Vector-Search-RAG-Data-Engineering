# M1 — Corpus Ingestion: Data Sources, Text Extraction, Normalization & Upsert/Delete Semantics

RAG pipeline အတွက် corpus ingestion အဆင့်သည် downstream retrieval quality တစ်ခုလုံး၏ အခြေခံ foundation ဖြစ်သည်။ ဤ module တွင် source parsing, text extraction, normalization, deduplication နှင့် idempotent update logic များကို standard library ဖြင့် programmatic နည်းလမ်းအတိုင်း လေ့လာမည်။

---

## Subtopic 1 — Source Formats နှင့် Text Extraction Architecture

### Overview

RAG ingestion တွင် source format အမျိုးမျိုး (PDF, HTML, Markdown, relational database records) မှ raw text ကို extract လုပ်ရသည်။ Extraction အဆင့်၏ အဓိက ရည်မှန်းချက်မှာ semantic value မရှိသော navigation elements, footers, ad banners နှင့် styling tags ကဲ့သို့သော boilerplate များကို ဖယ်ရှားပြီး clean body text ကို ရယူရန် ဖြစ်သည်။

### Engineering Rationale

Embedding model များသည် fixed context window (ဥပမာ 512 သို့မဟုတ် 8192 tokens) ရှိပြီး token capacity အကန့်အသတ်ရှိသည်။ Extraction အဆင့်တွင် boilerplate များ ရောနှောပါဝင်သွားပါက vector representation သည် dilution ဖြစ်သွားပြီး retrieval relevance တိကျမှု ကျဆင်းစေသည်။ ထို့ကြောင့် structural parsing နှင့် tag stripping ကို pipeline အစပိုင်းတွင် စနစ်တကျ ပြုလုပ်ရသည်။

### Implementation Steps

1. Source format အလိုက် parser architecture ကို ခွဲခြားသတ်မှတ်ပါ။
2. Document body ကို container selector (ဥပမာ `<main>`, `<article>`) ဖြင့် scope သတ်မှတ်ပါ။
3. Header, footer, navigation စသည့် boilerplate blocks များကို regex သို့မဟုတ် DOM filter ဖြင့် ဖယ်ရှားပါ။
4. Multiple whitespace များကို single space အဖြစ် collapse လုပ်ပြီး string normalize ပြုလုပ်ပါ။

### Python Implementation

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

### Production Considerations

Production pipeline များတွင် unstructured documents များအတွက် Hugging Face `datasets` (https://huggingface.co/docs/datasets/index) သို့မဟုတ် dedicated document loader များကို အသုံးပြုပြီး orchestration အတွက် Apache Airflow (https://airflow.apache.org/docs/) ဖြင့် batch extraction tasks များကို schedule ပြုလုပ်လေ့ရှိသည်။

---

## Subtopic 2 — Unicode Normalization (NFC)

### Overview

Unicode တွင် visually တူညီသော glyph တစ်ခုတည်းကို binary representation ပုံစံ နှစ်မျိုးဖြင့် သိမ်းဆည်းနိုင်သည်။ ဥပမာ - Precomposed character (`é` - `U+00E9`) နှင့် Decomposed character sequence (`e` + combining acute accent - `U+0065 U+0301`) တို့ ဖြစ်သည်။ Unicode normalization သည် ဤ representation များကို standard canonical form (NFC) သို့ ပြောင်းလဲပေးသည်။

### Engineering Rationale

String equality comparison နှင့် cryptographic hashing (SHA-256) တို့သည် binary byte sequence အပေါ် တိုက်ရိုက် အခြေခံသည်။ Text ကို normalize မလုပ်ပါက visually တူညီသော စာသားနှစ်ခုသည် binary byte မတူသဖြင့် hash match မဖြစ်ဘဲ deduplication စနစ် ကျိုးပေါက်သွားနိုင်သည်။ ထို့အပြင် tokenizer များသည် decomposed codepoints များကို token အကွဲများအဖြစ် encode လုပ်မိသဖြင့် vector similarity score များ လွဲချော်နိုင်သည်။

### Implementation Steps

1. Ingestion entry point တွင် incoming string တိုင်းကို လက်ခံပါ။
2. Python `unicodedata.normalize('NFC', text)` ဖြင့် Canonical Decomposition followed by Canonical Composition ပြုလုပ်ပါ။
3. Whitespace formatting ကို standard space အဖြစ် collapse လုပ်ပါ။

### Python Implementation

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

### Production Considerations

Multilingual corpus များ (ဥပမာ Burmese, Thai, European languages) တွင် diacritic marks နှင့် zero-width characters များ အမြောက်အမြား ပါဝင်နိုင်သဖြင့် normalization ကို ingestion stage ၏ အစောဆုံး gate အဖြစ် မဖြစ်မနေ ထည့်သွင်းထားရမည်။

---

## Subtopic 3 — Content Fingerprinting ဖြင့် Duplicate Detection

### Overview

Content fingerprinting သည် document content အပေါ်တွင် cryptographic hash (SHA-256) တွက်ချက်၍ compact identifier တစ်ခု ထုတ်ယူခြင်း ဖြစ်သည်။ ဤ fingerprint သည် identical content များကို indexing မပြုလုပ်မီ လျင်မြန်စွာ detect လုပ်နိုင်ရန် ကူညီပေးသည်။

### Engineering Rationale

Corpus အတွင်း identical သို့မဟုတ် near-identical documents များ ထပ်ခါတလဲလဲ ပါဝင်နေပါက vector storage ကုန်ကျစရိတ် မြင့်တက်စေသည့်အပြင် retrieval အဆင့်တွင် top-k candidates များအားလုံး duplicate chunks များဖြင့် ပြည့်နှက်သွားပြီး answer diversity ကို ထိခိုက်စေသည်။ Ingestion gate တွင် fingerprinting ဖြင့် deduplicate လုပ်ခြင်းသည် index bloat ကို ကာကွယ်ပေးသည်။

### Implementation Steps

1. Normalized clean text ကို UTF-8 encode ပြုလုပ်ပါ။
2. `hashlib.sha256` ဖြင့် hex digest ထုတ်ယူပါ။
3. In-memory set သို့မဟုတ် database index ရှိ fingerprint index နှင့် compare လုပ်ပါ။
4. Fingerprint ရှိပြီးသား ဖြစ်ပါက duplicate အဖြစ် skip လုပ်ပါ။

### Python Implementation

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

### Production Considerations

PostgreSQL schema တွင် metadata များကို `jsonb` column ဖြင့် သိမ်းဆည်းနိုင်ပြီး (https://www.postgresql.org/docs/current/datatype-json.html) fingerprint အတွက် `UNIQUE` index constraint သတ်မှတ်ခြင်းဖြင့် database level တွင် duplicate write များကို atomic ဖြစ်စွာ တားဆီးနိုင်သည်။

---

## Subtopic 4 — Incremental Update နှင့် Deletion Semantics

### Overview

Corpus သည် static မဟုတ်ဘဲ dynamic updates ဖြစ်ပေါ်နေသည်။ Incremental update သည် ပြောင်းလဲသွားသော (changed) သို့မဟုတ် အသစ်ထည့်သွင်းသော (new) documents များကိုသာ process လုပ်ပြီး မူရင်းရင်းမြစ်မှ ပျက်ပြယ်သွားသော documents များကို index မှ ဖယ်ရှား (delete/tombstone) သည့် mechanism ဖြစ်သည်။

### Engineering Rationale

Dataset တစ်ခုလုံးကို full re-index လုပ်ခြင်းသည် compute နှင့် API cost အလွန်များပြားသည်။ Fingerprint diffing အားဖြင့် delta ပြောင်းလဲမှုများကိုသာ selectively process လုပ်ခြင်းသည် ingestion throughput ကို မြှင့်တင်ပေးသည်။ Index မှ ဖယ်ရှားရန် ပျက်ကွက်ပါက stale results များ query ထဲ ပြန်ပါလာမည် ဖြစ်သည်။

### Implementation Steps

1. လက်ရှိ database state (doc_id -> fingerprint) ကို ရယူပါ။
2. Incoming batch ၏ fingerprints များကို compute လုပ်ပါ။
3. State တွင် မရှိသေးသော IDs များကို `new` အဖြစ် သတ်မှတ်ပါ။
4. State တွင် ရှိသော်လည်း fingerprint မတူညီပါက `changed` (upsert target) အဖြစ် သတ်မှတ်ပါ။
5. State တွင် ရှိသော်လည်း batch တွင် မပါဝင်တော့သော IDs များကို `deleted` အဖြစ် သတ်မှတ်ပါ။

### Python Implementation

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

### Database Semantics

PostgreSQL + pgvector stack တွင် document-level updates များကို `ON CONFLICT` upsert pattern ဖြင့် atomic စွာ execute လုပ်နိုင်သည်:

```sql
-- Valid for PostgreSQL with the pgvector extension.
INSERT INTO chunks (doc_id, content, embedding)
VALUES ('doc_b', 'beta text v2', '[0.1, 0.2, 0.3]')
ON CONFLICT (doc_id)
DO UPDATE SET content = EXCLUDED.content,
              embedding = EXCLUDED.embedding;
```

---

## Subtopic 5 — Pipeline Idempotency Design

### Overview

Idempotency ဆိုသည်မှာ execution တစ်ခုကို မည်မျှပင် အကြိမ်ကြိမ် run စေကာမူ final state သည် တစ်ကြိမ်သာ execute လုပ်သကဲ့သို့ မပြောင်းလဲဘဲ တူညီနေခြင်း (f(f(x)) = f(x)) ကို ဆိုလိုသည်။

### Engineering Rationale

Distributed data pipelines များ (Airflow, Kubernetes jobs) တွင် network blip, container OOM သို့မဟုတ် timeout များကြောင့် task retry ပြုလုပ်ရလေ့ရှိသည်။ Pipeline သည် idempotent မဖြစ်ပါက retry လုပ်တိုင်း duplicate rows များ တိုးပွားလာမည် ဖြစ်သည်။

### Implementation Pattern

1. Random UUID အစား deterministic content hash သို့မဟုတ် source natural key မှ derived stable ID ကို အသုံးပြုပါ။
2. Raw append write အစား UPSERT (insert on conflict update) pattern ကို အသုံးပြုပါ။
3. Execution intermediate state များကို transactional သို့မဟုတ် atomic blocks ဖြင့် manage လုပ်ပါ။

### Python Implementation

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

## Summary Checklist

- Source document parsing တွင် targeted extraction ဖြင့် boilerplate noise ကို ဖယ်ရှားပါ။
- Hash computation မပြုလုပ်မီ Unicode NFC normalization ကို မဖြစ်မနေ run ပါ။
- SHA-256 content fingerprints များဖြင့် exact duplicates များကို filter လုပ်ပါ။
- Delta updates များအတွက် fingerprint diffing ဖြင့် incremental processing ကို enforce လုပ်ပါ။
- Retry-safe ဖြစ်စေရန် stable deterministic IDs နှင့် upsert semantics ဖြင့် idempotency ကို အာမခံပါ။
