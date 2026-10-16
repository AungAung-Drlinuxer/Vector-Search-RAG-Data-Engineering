# M1 — Corpus Ingestion: Data Sources, Text Extraction, Normalization & Upsert/Delete Semantics

RAG system အတွက် source document များမှ clean text ထုတ်ယူခြင်း၊ Unicode normalization၊ content fingerprinting နှင့် idempotent upsert/delete pipeline တည်ဆောက်ခြင်းတို့ကို လေ့လာသည့် module ဖြစ်သည်။

> ဤ module သည် PostgreSQL, Hugging Face Datasets နှင့် Apache Airflow official documentation များကို အခြေခံ၍ ရေးသားထားသော original study material ဖြစ်သည်။ Commercial vendor training မှ ကူးယူထားခြင်း မဟုတ်ပါ။

## သင်ယူလေ့လာမည့် အကြောင်းအရာများ

- Source types (PDF, HTML, Markdown, database records) ၏ extraction architecture
- Boilerplate removal (headers, footers, navigation elements) ဖြင့် retrieval noise လျှော့ချခြင်း
- Unicode normalization (NFC) ၏ အရေးပါမှုနှင့် character encoding variance ကိုင်တွယ်ပုံ
- SHA-256 content fingerprinting ဖြင့် duplicate detection စနစ် တည်ဆောက်ခြင်း
- Incremental updates၊ deletion semantics နှင့် tombstoning logic
- Production ingestion pipeline များတွင် idempotency အာမခံနိုင်မည့် pattern များ

## Module အစိတ်အပိုင်းများ

1. `lessons/lesson_01_sources.md` — Source formats နှင့် structured JSON conversion patterns
2. `lessons/lesson_02_extraction.md` — Text extraction နှင့် targeted boilerplate removal
3. `lessons/lesson_03_normalisation.md` — Unicode normalization (NFC) နှင့် hash-based duplicate detection
4. `lessons/lesson_04_upsert_delete.md` — Incremental updates၊ deletion semantics နှင့် pipeline idempotency

## Prerequisites

- Python 3 standard library အခြေခံ (list, dict, regex, hashlib, unicodedata)
- Basic terminal workflow
- External database connection မလိုအပ်ပါ — Ingestion logic နှင့် data structures များကို deterministic pure Python ဖြင့် တည်ဆောက်ပြထားသည်။

## Production Use Cases

- Enterprise RAG system များအတွက် resilient ingestion pipeline ဒီဇိုင်းရေးဆွဲခြင်း
- Source data ပြောင်းလဲမှုများတွင် duplicate chunks မဖြစ်စေဘဲ incremental update ပြုလုပ်ခြင်း
- Airflow/orchestrator များတွင် failure recovery နှင့် retry-safe pipeline execution သေချာစေခြင်း

## References

- PostgreSQL JSON types: https://www.postgresql.org/docs/current/datatype-json.html
- Hugging Face Datasets documentation: https://huggingface.co/docs/datasets/index
- Apache Airflow documentation: https://airflow.apache.org/docs/
