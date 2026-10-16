# M12 — Governance & Security: PII Redaction, ACLs, Multi-Tenancy & Audit Logging

Enterprise retrieval စနစ်များတွင် security နှင့် governance သည် search relevance ကဲ့သို့ပင် အရေးပါသော core requirements ဖြစ်သည်။ ဤ module တွင် PII redaction၊ database-enforced Row-Level Security (RLS)၊ multi-tenant isolation patterns၊ immutable audit logging၊ cascade deletion mechanics နှင့် data provenance metadata tracking တို့ကို programmatic နည်းလမ်းဖြင့် လေ့လာမည်။

---

## Subtopic 1 — Embedding Layer PII Persistence Risk & Automated Redaction

### Overview

Personally Identifiable Information (PII) ဆိုသည်မှာ လူပုဂ္ဂိုလ်တစ်ဦးချင်းစီ၏ privacy ကို ဖော်ထုတ်နိုင်သော အချက်အလက်များ (email, phone number, national ID, credit card number) ဖြစ်သည်။ Text ကို vector embedding ပြောင်းလဲရာတွင် raw text ကို sanitize မလုပ်ပါက အဆိုပါ sensitive အချက်အလက်များသည် high-dimensional semantic vector space အတွင်း၌ implicit representation အနေဖြင့် persist ဖြစ်ကျန်ခဲ့သည်။

### Engineering Rationale

Embedding model များသည် sensitive data ကို သီးခြားခွဲခြားဖယ်ထုတ်ပေးခြင်း မရှိပါ။ Vector representations များမှ text မူရင်းကို reconstruction ပြုလုပ်နိုင်သော vector inversion attacks များ သို့မဟုတ် prompt injection မှတစ်ဆင့် unauthorized retrieval ဖြစ်ပေါ်ပါက compliance ချိုးဖောက်မှု (GDPR, HIPAA, SOC 2) ဖြစ်စေသည်။ ထို့ကြောင့် ingestion pipeline ၏ အစောဆုံး gate တွင် pre-embedding redaction ကို မဖြစ်မနေ execute လုပ်ရသည်။

### Implementation Pattern

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

---

## Subtopic 2 — Database Row-Level Security (RLS) ဖြင့် Document ACL Enforcement

### Overview

Access Control List (ACL) သည် မည်သည့် user သို့မဟုတ် role သည် မည်သည့် document/chunk ကို ဖတ်ရှုခွင့်ရှိသည်ကို သတ်မှတ်သော authorization matrix ဖြစ်သည်။ PostgreSQL Row-Level Security (RLS) သည် ဤ access boundary ကို database engine level တွင် enforce လုပ်ပေးသည်။

### Engineering Rationale

Application layer တွင် authorization filter စစ်ဆေးခြင်း (`WHERE allowed_users @> ARRAY[current_user]`) သည် software bug သို့မဟုတ် developer error ကြောင့် မေ့ကျန်ခဲ့ပါက cross-user data leakage ချက်ချင်း ဖြစ်ပေါ်စေသည်။ PostgreSQL RLS [Row Security Documentation](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) အရ query တိုင်းတွင် dynamic security predicate ကို query optimizer အဆင့်မှ automatic inject လုပ်ပေးသဖြင့် leaks မဖြစ်နိုင်စေရန် အာမခံသည်။

### DDL & Query Architecture

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

### Python Emulation

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

---

## Subtopic 3 — Multi-Tenant Isolation Architectures

### Overview

Multi-tenant systems များတွင် မတူညီသော organization tenants များ၏ vector data များကို isolation model သုံးမျိုးဖြင့် ခွဲခြားနိုင်သည်:
1. **Shared Table + Tenant Column**: Resource utilization အမြင့်ဆုံး ဖြစ်သော်လည်း RLS/filter dependency မြင့်မားသည်။
2. **Schema per Tenant**: Single database အတွင်း schema namespace ဖြင့် isolate လုပ်သဖြင့် physical logical separation ရရှိသည်။
3. **Database / Cluster per Tenant**: Hardware/database level physical isolation ဖြစ်ပြီး enterprise security အမြင့်ဆုံး ဖြစ်သော်လည်း operational cost အမြင့်ဆုံး ဖြစ်သည်။

### Python Emulation

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

---

## Subtopic 4 — Immutable Audit Logging & Retention Deletion Policies

### Overview

Audit trail သည် access governance ၏ foundation ဖြစ်သည်။ မည်သည့် identity သည် မည်သည့် context ကို retrieve လုပ်ခဲ့သည်၊ မည်သည့် unauthorized requests များ ငြင်းပယ်ခံခဲ့ရသည်ကို append-only format ဖြင့် မှတ်တမ်းတင်ရမည်။

### Retention & Purge Mechanics

Data retention policy သတ်မှတ်ချက်အရ သို့မဟုတ် user deletion request အရ source document တစ်ခု ဖျက်သိမ်းပါက downstream chunks, vector embeddings, cache entries များနှင့် search indexes များကို cascade atomic purge ပြုလုပ်ရမည်။

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

---

## Subtopic 5 — Data Provenance, Source Licensing & Quality Verification

### Overview

Data Provenance သည် chunk တစ်ခုချင်းစီ၏ upstream source lineage (origin URL, ingestion timestamp, author) နှင့် license terms (commercial-use, attribution, copyleft restrictions) ကို ခြေရာခံခြင်း ဖြစ်သည်။ Unlicensed သို့မဟုတ် prohibited content များကို indexing မပြုလုပ်မီ reject ပြုလုပ်ရမည်။

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

## Summary Checklist

- Ingestion pipeline တွင် PII detection and regex redaction ကို vector embedding မပြုလုပ်မီ execute လုပ်ပါ။
- Application-level filters များအပေါ် တစ်ခုတည်း မမှီခိုဘဲ PostgreSQL Row-Level Security (RLS) ဖြင့် database-level ACL enforcement ပြုလုပ်ပါ။
- Multi-tenancy isolation model ကို compliance SLA (tenant column vs dedicated schema/database) အလိုက် ရွေးချယ်ပါ။
- Access နှင့် modification events တိုင်းအတွက် append-only immutable audit logs ထိန်းသိမ်းပါ။
- Document deletion request များတွင် chunks, vectors နှင့် cache များ အားလုံးပါဝင်သော cascade purge logic ကို အကောင်အထည်ဖော်ပါ။
- Ingestion gate တွင် license metadata validation ဖြင့် unapproved data indexing ကို ကာကွယ်ပါ။
