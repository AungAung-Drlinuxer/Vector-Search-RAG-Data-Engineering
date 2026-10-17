# M12 — Governance & Security: PII Redaction, ACLs, Multi-Tenancy & Audit Logging

Enterprise RAG နှင့် vector search စနစ်များတွင် ဒေတာလုံခြုံရေး၊ access control enforcement၊ multi-tenant isolation၊ compliance audit trails နှင့် data lifecycle retention စည်းမျဉ်းများကို စနစ်တကျ ဒီဇိုင်းရေးဆွဲသည့် module ဖြစ်သည်။

## သင်ယူလေ့လာမည့် အကြောင်းအရာများ

- Embedding vectors အတွင်း PII (Personally Identifiable Information) persistence risk နှင့် pre-embedding redaction
- PostgreSQL pgvector တွင် Row-Level Security (RLS) နှင့် document-level ACL integration
- Multi-tenancy isolation models (shared table vs schema-per-tenant vs database-per-tenant)
- Immutable append-only audit logging architecture နှင့် access trace verification
- Cascade deletion mechanics, tombstones နှင့် orphan chunks ကာကွယ်ခြင်း
- Document provenance, licensing metadata နှင့် compliance retention policies

## Module အစိတ်အပိုင်းများ

| File | အကြောင်းအရာ |
|---|---|
| `README.md` | Module scope နှင့် learning objectives |
| `explanation.md` | Subtopic ၅ ခု၏ သဘောတရားရှင်းလင်းချက်၊ RLS/redaction pattern နှင့် deterministic example |
| `exercise.md` | ကိုယ်တိုင် implement လုပ်ရမည့် လေ့ကျင့်ခန်း ၆ ခု |
| `solution.md` | Reference implementation နှင့် ရှင်းလင်းချက် |
| `lab.py` | Standard library သာ သုံး၍ local တွင် ချက်ချင်း run နိုင်သော executable lab |

### `explanation.md` — Subtopic ဖွဲ့စည်းပုံ

1. Embedding Layer PII Persistence Risk နှင့် Automated Redaction
2. Database Row-Level Security (RLS) ဖြင့် Document ACL Enforcement
3. Multi-Tenant Isolation Architectures
4. Immutable Audit Logging နှင့် Retention Deletion Policies
5. Data Provenance, Source Licensing နှင့် Quality Verification

## Prerequisites

- Modules M1 (Ingestion) နှင့် M5 (pgvector schema & operators)
- Python 3 standard library
- PostgreSQL DDL/DML comprehension (external database connection မလိုအပ်ဘဲ deterministic pure Python ဖြင့် programmatic simulation ပြုလုပ်ထားသည်)

## Production Use Cases

- GDPR/CCPA စည်းမျဉ်းများအရ "Right to be Forgotten" deletion requests များကို cascade purge ပြုလုပ်ခြင်း
- SaaS enterprise application များတွင် multi-tenant data leak လုံးဝမဖြစ်ပေါ်စေရန် RLS ဖြင့် isolate လုပ်ခြင်း
- Internal compliance audits များအတွက် retrieval query logs များကို immutable audit trail အဖြစ် ထိန်းသိမ်းခြင်း

## References

- PostgreSQL Row Security Policies: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- PostgreSQL Text Search Controls: https://www.postgresql.org/docs/current/textsearch-controls.html
- Ragas Retrieval Evaluation & Governance: https://docs.ragas.io/
