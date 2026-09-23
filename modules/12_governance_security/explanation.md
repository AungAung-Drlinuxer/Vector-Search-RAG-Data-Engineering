# M12 — Governance နှင့် လုံခြုံရေး: PII၊ ACL၊ Multi-tenancy နှင့် Audit

ဒီ module မှာ retrieval system တစ်ခုကို ဘယ်လို လုံခြုံအောင် ထိန်းသိမ်းမလဲ ဆိုတာကို လေ့လာရတယ်။
ရည်ညွှန်းထားတဲ့ တရားဝင် documentation တွေကတော့ [PostgreSQL Row Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)၊ [PostgreSQL Text Search Controls](https://www.postgresql.org/docs/current/textsearch-controls.html) နဲ့ [Ragas docs](https://docs.ragas.io/) တို့ ဖြစ်ပါတယ်။

## Subtopic 1 — Embedding ထဲ ကျန်နေတဲ့ PII (အချက်အလက် စာရင်းမှန်)

### ဘာကို ဆိုလိုတာလဲ

PII (Personally Identifiable Information) ဆိုတာ လူတစ်ယောက်ကို တိုက်ရိုက် မှတ်ယူနိုင်တဲ့ အချက်အလက်တွေပါ။
နာမည်၊ ဖုန်းနံပါတ်၊ နိုင်ငံသား အိုင်ဒီ စသည်တို့ ပါဝင်တယ်။
Embedding (စာသားကို နံပါတ် vector အဖြစ် ပြောင်းထားတဲ့ ကိုယ်စားပုံ) ထဲမှာလည်း PII ရောက်သွားနိုင်တယ်။

### ဘာကြောင့် လဲ

Document ထဲ PII ပါနေရင် embedding model က အဲဒါကို နံပါတ်တွေထဲ ပေါင်းသွင်းလိုက်တယ်။
Vector ကို ဖျက်ပြီးလို့ မပြန်ရဘူး မဟုတ်ပေမယ့်၊ အလွယ်တကူ မဖတ်နိုင်တယ်။
ဒါပေမယ့် vector database ထဲ မသင့်တော့တဲ့သူ ရောက်သွားရင် အချက်အလက် ပျောက်ဆုံးနိုင်တယ်။
ဒါကြောင့် document ကို embed လုပ်တော့မယ့်အခါ PII ကို အရင် စစ်ပြီး ဖျက်တာ (redaction) လိုအပ်တယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Document ကို ingest လုပ်တဲ့အခါ PII pattern တွေကို စစ်တယ်။
၂။ တွေ့ရင် `[REDACTED]` လိုမျိုး အစားထိုးလိုက်တယ်။
၃။ Redact လုပ်ပြီးတဲ့ စာသားကိုပဲ chunk လုပ်ပြီး embed လုပ်တယ်။
၄။ ဘယ် document မှာ ဘယ် PII type ဖျက်ခဲ့တယ်ဆိုတာ log မှတ်တယ်။
၅။ Audit (စစ်ဆေးမှု မှတ်တမ်း) အတွက် အဲဒီ log ကို သိမ်းထားတယ်။

### ဥပမာ

```python
import re

# Simple offline PII redaction with standard library regex only.
# A production system would use a dedicated PII detection service.
PATTERNS = {
    "phone": re.compile(r"\b09\d{9}\b"),
    "email": re.compile(r"\b[\w.]+@[\w.]+\.\w+\b"),
}

def redact(text):
    found = []
    for name, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            found.append((name, match.group(0)[:3] + "***"))
        text = pattern.sub("[REDACTED]", text)
    return text, found

text = "Contact 09123456789 or ma.ma@example.com for details."
clean, found = redact(text)
print(clean)
print(found)
# Expected output:
# Contact [REDACTED] or [REDACTED] for details.
# [('phone', '091***'), ('email', 'ma.***')]
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

PII ကို embedding store ထဲ ဝင်သွားရင် ပြန်ဖျက်ရတာ ခက်တယ်။
Store တစ်ခုလုံးကို စစ်ပြီး rebuild လုပ်ရမယ်။
အစပိုင်းမှာ စစ်တာက နောက်ပိုင်းမှာ ပြင်တာထက် ပို လွယ်တယ်။
Data privacy ဥပဒေတွေနဲ့လည်း ကိုက်ညီအောင် လိုအပ်တယ်။

## Subtopic 2 — Row-Level Security ဖြင့် Document ACL (ခွင့်ပြုချက် စာရင်း)

### ဘာကို ဆိုလိုတာလဲ

ACL (Access Control List) ဆိုတာ document တစ်ခုချင်းစီကို ဘယ် user တွေ ဖတ်ခွင့်ရှိလဲဆိုတဲ့ စာရင်းပါ။
PostgreSQL မှာ Row-Level Security (RLS) ဆိုတာ row တစ်ခုချင်း ခွင့်ပြုချက် ထိန်းတဲ့ စနစ်ပါ။
ဒီစနစ်ကို document-level ACL အဖြစ် သုံးလို့ ရတယ်။

### ဘာကြောင့် လဲ

RLS မရှိရင် application က query တိုင်းမှာ "owner = current_user" ဆိုတာကို ကိုယ်တိုင် ထည့်ပေးရတယ်။
တစ်နေရာမှာ မေ့လိုက်ရင် အခြားသူရဲ့ document တွေ ပေါ်သွားနိုင်တယ်။
PostgreSQL ရဲ့ [Row Security documentation](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) အရ RLS က query ထဲ အလိုအလျောက် filter ထည့်ပေးတယ်။
ဒါကြောင့် filter ကို မေ့ဖို့ မဖြစ်နိုင်တော့ပါဘူး။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Table ပေါ်မှာ `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` လုပ်တယ်။
၂။ Policy တစ်ခု ရေးတယ် — ဘယ် user က ဘယ် row ဖတ်ခွင့်ရှိလဲဆိုတာ။
၃။ Table မှာ `owner` column ထည့်ပြီး document တစ်ခုချင်း ပိုင်ရှင် မှတ်တယ်။
၄။ Retrieval query လည်း အဲဒီ policy အလို အလိုအလျောက် ကန့်သတ်ခံရတယ်။

### ဥပမာ

```sql
-- SQL for PostgreSQL with pgvector; not executed by the lessons.
CREATE TABLE docs (
    id bigserial PRIMARY KEY,
    owner text NOT NULL,
    body text NOT NULL,
    embedding vector(3)
);

ALTER TABLE docs ENABLE ROW LEVEL SECURITY;

CREATE POLICY docs_owner_read ON docs
    FOR SELECT
    USING (owner = current_user);
```

```python
# Simulating in Python what the RLS policy does to a retrieval query.
# The real system would run the SQL above in PostgreSQL.

def retrieve(user, query_embedding, corpus):
    # The policy "owner = current_user" acts as this filter automatically.
    allowed = [d for d in corpus if d["owner"] == user]
    def dot(a):
        return sum(x * y for x, y in zip(a, query_embedding))
    ranked = sorted(allowed, key=lambda d: dot(d["embedding"]), reverse=True)
    return [(d["id"], round(dot(d["embedding"]), 3)) for d in ranked[:2]]

corpus = [
    {"id": 1, "owner": "alice", "embedding": [1.0, 0.0, 0.0]},
    {"id": 2, "owner": "bob",   "embedding": [0.9, 0.1, 0.0]},
    {"id": 3, "owner": "alice", "embedding": [0.8, 0.2, 0.0]},
]
print(retrieve("alice", [1.0, 0.0, 0.0], corpus))
# Expected output:
# [(1, 1.0), (3, 0.8)]
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

RAG system မှာ search index နဲ့ ACL filter က တစ်ပြိုင်နက် လုပ်ရတယ်။
Filter ကို မေ့ရင် user တစ်ယောက်က မလုပ်သင့်တဲ့ document ကို ရှာတွေ့သွားမယ်။
Postgres RLS က အဲဒါကို database အဆင့်မှာ အာမခံပေးတယ်။

## Subtopic 3 — Multi-tenant Isolation (သုံးစွဲသူ များ ခွဲခြားခြင်း)

### ဘာကို ဆိုလိုတာလဲ

Multi-tenancy ဆိုတာ system တစ်ခုထဲမှာ customer (tenant) အများ တူတူနေထိုင်တာပါ။
Isolation ဆိုတာ tenant တစ်ယောက်ရဲ့ data က အခြား tenant ရောက်မသွားအောင် ခွဲခြားထားတာပါ။

### ဘာကြောင့် လဲ

Tenant တွေ ရောနှောသွားရင် data leak (အချက်အလက် ယိုစိမ့်မှု) ဖြစ်တယ်။
ဥပမာ — ကုမ္ပဏီ A ရဲ့ document ကို ကုမ္ပဏီ B ရဲ့ search ရလဒ်ထဲ ပေါ်သွားတာမျိုးပါ။
ဒါက ယုံကြည်မှု ဆုံးရှုံးမှု အကြီးအကျယ် ဖြစ်စေတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Tenant ID တစ်ခု ချထားတယ် — database တစ်ခုချင်း၊ schema တစ်ခုချင်း၊ ဒါမှမဟုတ် column တစ်ခုချင်း။
၂။ ရွေးချယ်စရာ သုံးမျိုးရှိတယ် — shared database + shared schema (column filter)၊ shared database + schema per tenant၊ database per tenant။
၃။ ပိုခွဲနိုင်ရင် ပိုလုံခြုံတယ်၊ ဒါပေမယ့် ကုန်ကျစရိတ် တက်တယ်။
၄။ Tenant ID ကို RLS policy ထဲ ထည့်ပြီး database အဆင့်မှာ အာမခံတယ်။
၅။ Cache layer တွေမှာလည်း tenant ID ကို key ထဲ မှတ်ပါစေရမယ်။

### ဥပမာ

```python
# Simulating tenant isolation on top of the RLS-style filter from Subtopic 2.

def search(tenant_id, query_embedding, corpus):
    # In PostgreSQL this is a policy like:
    #   USING (tenant_id = current_setting('app.tenant_id')::int)
    allowed = [d for d in corpus if d["tenant_id"] == tenant_id]
    def dot(a):
        return sum(x * y for x, y in zip(a, query_embedding))
    ranked = sorted(allowed, key=lambda d: dot(d["embedding"]), reverse=True)
    return [d["id"] for d in ranked[:2]]

corpus = [
    {"id": 1, "tenant_id": 100, "embedding": [0.9, 0.1]},
    {"id": 2, "tenant_id": 200, "embedding": [0.95, 0.05]},
    {"id": 3, "tenant_id": 100, "embedding": [0.5, 0.5]},
]
print("tenant 100 sees:", search(100, [1.0, 0.0], corpus))
print("tenant 200 sees:", search(200, [1.0, 0.0], corpus))
# Expected output:
# tenant 100 sees: [1, 3]
# tenant 200 sees: [2]
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Isolation က စာချုပ်အရ တာဝန်ရှိတဲ့ အချက်ပါ။
Application bug တစ်ခုကြောင့် tenant ချင်း data ယိုစိမ့်သွားရင် တရားဝင် ပြဿနာ ဖြစ်တယ်။
Database အဆင့် isolation က application bug ရဲ့ အကာအကွယ် ဖြစ်ပေးတယ်။

## Subtopic 4 — Audit Log နှင့် Retention / Delete ပြဋ္ဌာန်းချက်

### ဘာကို ဆိုလိုတာလဲ

Audit log ဆိုတာ ဘယ်သူက ဘယ်အချိန်မှာ ဘာကို ခွင့်ပြုချက်နဲ့ ဝင်ရောက်ခဲ့လဲဆိုတဲ့ မှတ်တမ်းပါ။
Retention (သိမ်းဆည်းချက် ကာလ) ဆိုတာ data ကို ဘယ်လောက်ကြာ သိမ်းမလဲဆိုတဲ့ စည်းမျဉ်းပါ။
Delete ပြဋ္ဌာန်းချက် ဆိုတာ ဖျက်ပိုင်ခွင့် တောင်းဆိုမှုကို ဘယ်လို လိုက်နောက်လုပ်မလဲဆိုတာပါ။

### ဘာကြောင့် လဲ

User က "ငါ့ data အားလုံး ဖျက်ပေးပါ" လို့ တောင်းရင် system က လိုက်ဖျက်နိုင်ရမယ်။
ဖျက်လို့ မရရင် ဥပဒေနဲ့ ပဋိပက္ခ ဖြစ်နိုင်တယ်။
Audit log မရှိရင် "ဘယ်သူ ဘာ ဖတ်ခဲ့လဲ" ဆိုတာ ပြန်မဖြေနိုင်ဘူး။
 incident (ဖြစ်စဉ်) စုံစမ်းစစ်ဆေးရတာ မဖြစ်နိုင်တော့ပါဘူး။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ တစ်ချက် read တိုင်းကို log မှတ်တယ် — user, document ID, အချိန်၊ ရလဒ်အရေအတွက်။
၂။ Document ဖျက်တဲ့အခါ embedding, chunk, log မှာရှိတဲ့ မိတ္တူတွေ အားလုံး ဖျက်ရမယ်။
၃။ Retention ကာလကုန်ရင် အလိုအလျောက် ဖျက်တဲ့ အလုပ် (purge job) လုပ်တယ်။
၄။ ဖျက်ပြီးတဲ့ event ကိုလည်း log မှာ မှတ်တယ် — ဘာကြောင့် ဖျက်ခဲ့လဲဆိုတဲ့ အကြောင်းပေါင်း။

### ဥပမာ

```python
import time

audit_log = []
corpus = {1: "doc one", 2: "doc two"}  # a real system would use PostgreSQL

def log_access(user, doc_id, action):
    audit_log.append({"user": user, "doc": doc_id,
                      "action": action, "ts": int(time.time())})

def delete_document(doc_id):
    log_access("system", doc_id, "delete")
    corpus.pop(doc_id, None)  # also delete embeddings and chunks in production

log_access("alice", 1, "read")
delete_document(2)
print(sorted(corpus))
print(len(audit_log), "events logged")
# Expected output:
# [1]
# 2 events logged
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Delete တစ်ခုလုံးကို အာမခံဖို့ — document, chunk, embedding, cache, backup — အားလုံး ပါဝင်ရမယ်။
Backup မှာ ကျန်နေတဲ့ copy တွေက အဓိက ပြဿနာ ဖြစ်တတ်တယ်။
Audit log က လုံခြုံရေး စစ်ဆေးချက်ရဲ့ အခြေခံ ဖြစ်တယ်။

## Subtopic 5 — Provenance / License မှတ်တမ်း နှင့် Quality စစ်ဆေးခြင်း

### ဘာကို ဆိုလိုတာလဲ

Provenance ဆိုတာ data တစ်ခု အနေနဲ့ ဘယ်အရင်းအမြစ်ကနေ ဘယ် license (အသုံးပြုခွင့်) နဲ့ ဝင်လာလဲဆိုတဲ့ မှတ်တမ်းပါ။
ရလဒ်တွေရဲ့ အရည်အသွေးကို တိုင်းတာခြင်းကိုတော့ [Ragas](https://docs.ragas.io/) လို evaluation framework တွေနဲ့ လုပ်လေ့ရှိတယ်။

### ဘာကြောင့် လဲ

License မသိဘဲ data ကို သုံးရင် တရားဥပဒေ ပြဿနာ ဖြစ်နိုင်တယ်။
ရလဒ်ထဲ ဘယ် source ကနေ လာတယ်ဆိုတာ မပြနိုင်ရင် ယုံကြည်မှု ကျတယ်။
Ragas docs အရ evaluation က RAG pipeline ရဲ့ အရည်အသွေးကို တိုင်းတာပေးတယ်။
ဒါပေမယ့် ဒီသင်ခန်းစာမှာ real evaluation မလုပ်ဘူး — offline စစ်နည်း လေ့လာမယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Ingest လုပ်တဲ့အခါ document တိုင်းမှာ source URL, license, ingest အချိန် မှတ်တယ်။
၂။ ပိတ်ပင်ထားတဲ့ license ဖြစ်ရင် ingest ကို ငြင်းပြတယ်။
၃။ Retrieval ရလဒ်တိုင်းမှာ source metadata ပါစေတယ်။
၄။ အရည်အသွေးကို စစ်တဲ့အခါ ရိုးရိုး consistency အချက်ပေါင်း သုံးနိုင်တယ် — retrieved chunk နဲ့ answer က ကိုက်ညီလားဆိုတာ။

### ဥပမာ

```python
def ingest(doc_text, license_type):
    # In a real system this metadata would live in a Postgres column.
    BLOCKED = {"no-derivatives", "proprietary-internal"}
    return {"text": doc_text, "license": license_type,
            "allowed": license_type not in BLOCKED}

def answer_with_provenance(query, chunks, licenses):
    best = max(chunks, key=len)  # deterministic stand-in for retrieval
    return {
        "answer": best[:20] + "...",
        "source_license": licenses[chunks.index(best)],
    }

docs = [
    ingest("PostgreSQL RLS filters rows automatically.", "open"),
    ingest("Internal payroll data for 2024.", "proprietary-internal"),
]
accepted = [d for d in docs if d["allowed"]]
result = answer_with_provenance(
    "How does RLS work?",
    [d["text"] for d in accepted],
    [d["license"] for d in accepted],
)
print(result)
# Expected output:
# {'answer': 'PostgreSQL RLS filte...', 'source_license': 'open'}
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

License စစ်တာက data pipeline ရဲ့ ပထမဆုံး ခုခံကာကွယ်မှု ဖြစ်ရပါတယ်။ မူရင်း စာရွက်စာတမ်း သုံးခွင့် မရှိရင် index ထဲ ထည့်တာနဲ့ အသုံးပြုသူဆီ ပြန်ဖြန့်တာ နှစ်ခုစလုံး ဥပဒေနဲ့ ဆန့်ကျင်နိုင်ပါတယ်။

Retrieval စနစ်က permission ကို မစစ်ရင် အသုံးပြုသူ မမြင်သင့်တဲ့ document ကို အဖြေထဲ ထည့်ပေးမိနိုင်ပါတယ်။ ACL ကို query အဆင့်မှာသာ စစ်ပြီး အဖြေဖန်တီးတဲ့ နေရာမှာ ပြန်စစ်တာ နှစ်ထပ်လုံခြုံရေး ဖြစ်ပါတယ်။

## အနှစ်ချုပ်

- PII ကို embedding မတွက်ခင် ရှာပြီး ဖျောက်ပါ။
- Document-level ACL ကို retrieval query ထဲ ထည့်ပါ။
- Tenant တစ်ခုချင်းစီကို သီးခြား index ဒါမှမဟုတ် partition နဲ့ ခွဲပါ။
- Audit log က ဘယ်သူ ဘယ်အချိန် ဘာရှာခဲ့လဲ ကို မှတ်ထားပါ။
- Retention နှင့် delete ကို vector၊ metadata နှင့် cache အားလုံးမှာ လုပ်ပါ။
