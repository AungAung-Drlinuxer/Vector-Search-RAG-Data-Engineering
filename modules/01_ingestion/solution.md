## လေ့ကျင့်ခန်း ၁ — JSON Data Serialization & Canonicalization

PostgreSQL တွင် `json` type သည် exact text representation အတိုင်း သိမ်းဆည်းပြီး `jsonb` type သည် parsed binary representation ဖြင့် သိမ်းဆည်းသောကြောင့် whitespace stripping နှင့် key deduplication တို့ကို internally ပြုလုပ်သည်။ Ingestion pipeline တွင် downstream database သို့ payload မပို့မီ canonical JSON serialization ပြုလုပ်ပုံကို အောက်ပါ script တွင် ပြသထားသည်။

```python
import json

# Postgres 'json' stores the exact input text; 'jsonb' stores a parsed binary
# form (deduplicated keys, normalized whitespace, indexed). Here we simulate
# what the pipeline would send into either column.
doc = {"doc_id": 1, "lang": "my"}

as_json_text = json.dumps(doc, ensure_ascii=False)
print("json.dumps output :", as_json_text)
print("key quotes present:", '"doc_id"' in as_json_text)
print("round-trip equal  :", json.loads(as_json_text) == doc)

# What jsonb-style canonicalization looks like: whitespace stripped by loads()
print("jsonb-style view   :", json.dumps(json.loads(" { \"doc_id\" : 1 , \"lang\" : \"my\" } "),
                                          ensure_ascii=False, separators=(",", ":")))
# Expected output:
# json.dumps output : {"doc_id": 1, "lang": "my"}
# key quotes present: True
# round-trip equal  : True
# jsonb-style view   : {"doc_id":1,"lang":"my"}
```

**အဓိကအယူအဆ** — Metadata querying နှင့် GIN indexing လိုအပ်ချက်များအတွက် `jsonb` type သည် query performance ပိုမိုမြင့်မားသည်။

---

## လေ့ကျင့်ခန်း ၂ — Text Extraction နှင့် Boilerplate Removal

HTML structure မှ `<nav>` နှင့် `<footer>` အစိတ်အပိုင်းများကို raw tag strip မပြုလုပ်မီ targeted marker (`[[BOILER]]`) ဖြင့် ကြိုတင် replace လုပ်ပြီး ဖယ်ရှားခြင်းဖြင့် core document content ကို သန့်ရှင်းစွာ ရယူနိုင်သည်။

```python
import re

html = """<html><body>
<nav>Home | About | Contact | Privacy Policy</nav>
<main><h1>RAG Pipeline Guide</h1>
<p>Corpus ingestion is the first step of a vector search system.</p>
<p>Deduplication keeps the index clean.</p></main>
<footer>Copyright 2024 Example Corp. All rights reserved.</footer>
</body></html>"""

# Step 1: replace boilerplate block contents with a marker BEFORE stripping tags
def remove_boilerplate(html_str):
    marked = re.sub(r'<nav>.*?</nav>', ' [[BOILER]] ', html_str, flags=re.DOTALL)
    marked = re.sub(r'<footer>.*?</footer>', ' [[BOILER]] ', marked, flags=re.DOTALL)
    # Step 2: strip all remaining tags
    text = re.sub(r'<[^>]+>', ' ', marked)
    # Step 3: drop the marker and clean whitespace
    text = re.sub(r'.*\[\[BOILER\]\].*', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

clean = remove_boilerplate(html)
print(clean)
print("Boilerplate removed:", "Privacy Policy" not in clean and "Copyright" not in clean)
print("Main content kept  :", "Corpus ingestion" in clean)
# Expected output:
# RAG Pipeline Guide Corpus ingestion is the first step of a vector search system. Deduplication keeps the index clean.
# Boilerplate removed: True
# Main content kept  : True
```

**အဓိကအယူအဆ** — Unstructured HTML parsing တွင် hierarchical markers များ သတ်မှတ်၍ boilerplate များကို strip ပြုလုပ်ခြင်းသည် retrieval noise ကို လျှော့ချပေးသည်။

---

## လေ့ကျင့်ခန်း ၃ — Unicode Normalization (NFC)

Visual အားဖြင့် ထပ်တူညီသော်လည်း underlying Unicode codepoints ကွဲပြားနေသော string များကို `unicodedata.normalize('NFC', ...)` ဖြင့် canonical composed representation ပြောင်းလဲပြီးမှ equality verification ပြုလုပ်ပုံ ဖြစ်သည်။

```python
import unicodedata

# Two visually identical strings: 'e' + COMBINING ACUTE ACCENT vs precomposed é
# The same NFC principle applies to any combined diacritics in corpus text.
s1 = "report final \u0065\u0301 version"   # 'e' + U+0301 combining acute
s2 = "report final \u00e9 version"          # precomposed U+00E9
print("s1:", s1)
print("s2:", s2)
print("Raw equal        :", s1 == s2)
print("codepoints s1    :", [hex(ord(c)) for c in s1[-9:-7]])
print("name of composed :", unicodedata.name('\u00e9'))

n1 = unicodedata.normalize('NFC', s1)
n2 = unicodedata.normalize('NFC', s2)
print("NFC equal        :", n1 == n2)
print("NFC length equal :", len(n1) == len(n2))
# Expected output:
# s1: report final é version
# s2: report final é version
# Raw equal        : False
# codepoints s1    : ['0x301', '0x20']
# name of composed : LATIN SMALL LETTER E WITH ACUTE
# NFC equal        : True
# NFC length equal : True
```

**အဓိကအယူအဆ** — Ingestion stage ၏ အစောပိုင်းတွင် NFC normalization ပြုလုပ်ခြင်းသည် hash mismatch နှင့် tokenization fragmentation ပြဿနာများကို ဖြေရှင်းပေးသည်။

---

## လေ့ကျင့်ခန်း ၄ — Content Fingerprinting ဖြင့် Duplicate Detection

Whitespace collapse normalization ပြုလုပ်ထားသော text ကို SHA-256 hash ထုတ်ယူပြီး content fingerprint အလိုက် documents များကို bucket grouping ပြုလုပ်သည့် logic ဖြစ်သည်။

```python
import hashlib
import re

def normalize(text):
    return re.sub(r'\s+', ' ', text).strip()

def fingerprint(text):
    return hashlib.sha256(normalize(text).encode('utf-8')).hexdigest()

docs = {
    1: "Vector search  needs  an index.",
    2: "Vector search needs an index.",        # same as 1 after normalization
    3: "RAG combines retrieval with generation.",
    4: "RAG combines retrieval with generation.",  # same as 3
    5: "Postgres stores vectors as arrays.",
}

groups = {}  # fingerprint -> [doc_ids]
for doc_id, text in sorted(docs.items()):
    fp = fingerprint(text)
    groups.setdefault(fp, []).append(doc_id)

print("Total docs:", len(docs))
print("Unique contents:", len(groups))
for fp, ids in groups.items():
    label = "DUPLICATE" if len(ids) > 1 else "unique"
    print(f"fp={fp[:12]}... ids={ids} -> {label}")
# Expected output:
# Total docs: 5
# Unique contents: 3
# fp=e9ca20d42f4d... ids=[1, 2] -> DUPLICATE
# fp=261ee20517ae... ids=[3, 4] -> DUPLICATE
# fp=ae6ca6f2cce3... ids=[5] -> unique
```

**အဓိကအယူအဆ** — Pre-normalization + SHA-256 fingerprinting သည် superficial whitespace differences များကို ignore လုပ်ပြီး exact duplicate contents များကို တိကျစွာ detect ပြုလုပ်နိုင်သည်။

---

## လေ့ကျင့်ခန်း ၅ — Incremental Update Diff Engine

Previous state နှင့် incoming batch တို့၏ fingerprints များကို နှိုင်းယှဉ်၍ `new`, `changed`, `deleted` categories များအဖြစ် ခွဲခြား သတ်မှတ်သည်။

```python
import hashlib
import re

def fingerprint(text):
    return hashlib.sha256(re.sub(r'\s+', ' ', text).strip().encode('utf-8')).hexdigest()

# Previous pipeline state: doc_id -> fingerprint
state = {
    1: fingerprint("old doc one"),
    2: fingerprint("doc two v1"),
    5: fingerprint("doc five"),
}

# New incoming batch: doc_id -> text
batch = {
    1: "old doc one",       # unchanged -> ignored
    2: "doc two v2",        # fingerprint differs -> changed
    3: "brand new doc",     # not in state -> new
    4: "another new doc",   # not in state -> new
}

new_ids, changed_ids = [], []
for doc_id, text in sorted(batch.items()):
    fp = fingerprint(text)
    if doc_id not in state:
        new_ids.append(doc_id)
    elif state[doc_id] != fp:
        changed_ids.append(doc_id)

deleted_ids = [doc_id for doc_id in sorted(state) if doc_id not in batch]

print("new    :", new_ids)
print("changed:", changed_ids)
print("deleted:", deleted_ids)
# Expected output:
# new    : [3, 4]
# changed: [2]
# deleted: [5]
```

**အဓိကအယူအဆ** — Fingerprint-based state diffing သည် computational overhead မြင့်မားသော full corpus re-indexing ကို ရှောင်လွှဲနိုင်စေသည်။

---

## လေ့ကျင့်ခန်း ၆ — Idempotent Upsert & Delete Pipeline

Batch တစ်ခုကို ထပ်ခါတလဲလဲ execute လုပ်သော်လည်း database state သည် deterministic ဖြစ်စွာ တူညီနေစေသော idempotent update pipeline ဖြစ်သည်။

```python
import hashlib
import re

def fingerprint(text):
    return hashlib.sha256(re.sub(r'\s+', ' ', text).strip().encode('utf-8')).hexdigest()

# In-memory stand-in for a Postgres table (doc_id -> {text, fp}).
# Real target would be: INSERT ... ON CONFLICT (doc_id) DO UPDATE SET text=..., fp=...
# followed by DELETE FROM docs WHERE doc_id = ANY(%s). RETURNING clauses are
# intentionally omitted because they would couple the pipeline to pgvector
# specifics and break idempotency reasoning in this simulation.

def run_pipeline(store, batch, deletes):
    """Deterministic, idempotent upsert + delete. No network, no LLM."""
    changed = 0
    for doc_id, text in batch:            # batch = [(doc_id, text), ...]
        fp = fingerprint(text)
        if store.get(doc_id, {}).get("fp") != fp:   # upsert only if changed
            store[doc_id] = {"text": text, "fp": fp}
            changed += 1
    for doc_id in deletes:
        if store.pop(doc_id, None) is not None:
            changed += 1
    return changed

store = {}
batch = [(1, "doc one text"), (2, "doc two text"), (3, "doc three text")]

first_run = run_pipeline(store, batch, deletes=[9])  # 9 doesn't exist yet
snapshot_after_first = dict(store)

second_run = run_pipeline(store, batch, deletes=[9])  # same batch again
snapshot_after_second = dict(store)

print("first run writes :", first_run)
print("second run writes :", second_run)
print("state identical   :", snapshot_after_first == snapshot_after_second)
print("state keys        :", sorted(store))
# Expected output:
# first run writes : 3
# second run writes : 0
# state identical   : True
# state keys        : [1, 2, 3]
```

**အဓိကအယူအဆ** — Ingestion logic တွင် idempotent state mutation ကို enforce လုပ်ထားခြင်းဖြင့် network failure recovery နှင့် orchestrator retries များတွင် side effects မဖြစ်ပေါ်စေရန် အာမခံနိုင်သည်။
