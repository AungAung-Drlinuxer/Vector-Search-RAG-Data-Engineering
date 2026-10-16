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

1. `lessons/lesson_01_pii_persistence.md` — Ingestion gate တွင် PII detection နှင့် automated redaction
2. `lessons/lesson_02_rls_acl.md` — PostgreSQL Row-Level Security policies ဖြင့် query-level authorization
3. `lessons/lesson_03_multi_tenancy.md` — Multi-tenant architecture နှိုင်းယှဉ်ချက်နှင့် cross-tenant leak prevention
4. `lessons/lesson_04_audit_logging.md` — Retrieval access logs နှင့် compliance audit trails
5. `lessons/lesson_05_retention_provenance.md` — Data retention periods, cascade delete နှင့် source licensing metadata
6. `lessons/lesson_06_lab.md` — ACL-filtered retrieval, audit logging နှင့် cascade purge implementation

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
