# Vector Search & RAG Data Engineering — Study ROADMAP

ဒီ course သည် module scope တိုင်းတွင် အမည်တပ်ဖော်ပြထားသည့် official open documentation များမှ original သင်ခန်းစာ ဖြစ်သည်။ Commercial course များ၏ သင်ခန်းစာကို ပြန်လည်ရေးသားထားခြင်း မဟုတ်ပါ။

တွက်ချက်မှုတိုင်းသည် assumption များ သတ်မှတ်ပြီး formula ဖြင့် ပြသထားသည် — မည်သည့် named system အတွက်မှ memory, latency, QPS ဂဏန်းများကို ဖန်တီးခြင်း မရှိပါ။ Lab များသည် Python standard library ဖြင့်သာ လည်ပတ်ပြီး database မချိတ်ပါ — retrieval mechanics များကို ground-up implementation ဖြင့် လေ့လာရသည်။

## M0 — `00_orientation/` — RAG Architecture Map

RAG pipeline ၏ stage ၈ ခု (ingest → chunk → embed → index → retrieve → rerank → generate → evaluate) ကို end-to-end အနေဖြင့် ပြသသည်။ Vector search, keyword search, hybrid search တို့၏ ရွေးချယ်မှု criteria ကို ဥပမာဖြင့် ရှင်းလင်းသည်။

**Learning outcome** — RAG pipeline တစ်ခုလုံးကို အနှစ်ချုပ် ပုံဆွဲနိုင်ပြီး query characteristics အပေါ် အခြေခံ၍ search modality ရွေးချယ်နိုင်ရမည်။

Checkpoint questions —
- Pipeline တွင် chunking ကို embedding အဆင့်ထက် ရှေ့ထားရခြင်း၏ အကြောင်းရင်း
- Keyword search က vector search ထက် သင့်လျော်သော query characteristics
- Evaluate stage ကို pipeline နောက်ဆုံးတွင်သာ ထားခြင်း၏ risk

## M1 — `01_ingestion/` — Corpus Ingestion

Source အမျိုးအစားများ (PDF, HTML, Markdown, database row) မှ text extraction ကို လေ့လာသည်။ Boilerplate removal, Unicode normalization, duplicate detection (SHA-256 content fingerprint), incremental update, deletion semantics, upsert idempotency တို့ကို deterministic code ဖြင့် ပြသသည်။

**Learning outcome** — Source file မှ clean text ထုတ်ယူပြီး content fingerprint ဖြင့် duplicate detection implement လုပ်နိုင်ရမည်။

Checkpoint questions —
- Unicode NFC vs NFD က ingestion duplicate detection ကို ထိခိုက်ပုံ
- Content fingerprint သည် exact-match duplicate detection ထက် ပို၍ အသုံးဝင်သော အခြေအနေ
- Upsert operation ကို idempotent ဖြစ်စေရန် stable id design

## M2 — `02_chunking/` — Chunking Strategies & Metadata Design

Retrieval unit (chunk) ခွဲခြမ်းမှု strategy များ — fixed-size, recursive, token-based, semantic, parent-child (small-to-big) — ကို လေ့လာသည်။ Overlap ရွေးချယ်မှု, chunk size နှင့် retrieval quality trade-off, structure-preserving chunking, metadata schema design ပါဝင်သည်။

**Learning outcome** — Document type အလိုက် chunking strategy ရွေးချယ်ပြီး metadata column schema ဒီဇိုင်းရေးဆွဲနိုင်ရမည်။

Checkpoint questions —
- Chunk size မြင့်မားခြင်း/သေးငယ်ခြင်း၏ retrieval impact (precision vs context completeness)
- Overlap ဖြေရှင်းပေးသည့် boundary-splitting ပြဿနာ
- Parent-child retrieval သင့်လျော်သော use case

## M3 — `03_embeddings/` — Embedding Models, Dimensions & Caching

Embedding model ရွေးချယ်မှု criteria (multilingual, domain), dimension နှင့် storage calculation, L2 normalization နှင့် distance metric (cosine, dot product, L2) ဆက်စပ်မှုကို formula ဖြင့် လေ့လာသည်။ Matryoshka representation (truncatable embedding), batch encoding, embedding cache design ပါဝင်သည်။

**Learning outcome** — 1M chunks × 768 dimensions × fp32 assumption ဖြင့် storage calculation တွက်ချက်နိုင်ပြီး cosine similarity ကို standard library ဖြင့် implement လုပ်နိုင်ရမည်။

Checkpoint questions —
- fp32 တွင် dimension တစ်ခု၏ byte footprint နှင့် ၎င်း၏ အကြောင်းရင်း
- L2-normalized vector များအတွက် dot product နှင့် cosine equivalence
- Embedding cache invalidation ကို model version ပြောင်းလဲချိန်တွင် ကိုင်တွယ်ပုံ

## M4 — `04_hnsw/` — HNSW Index Internals

HNSW multi-layer graph structure ကို လေ့လာသည်။ Build-time parameters (`M`, `ef_construction`), query-time parameter (`ef_search`), recall-latency trade-off, index memory estimation, delete/update semantics, filtered search behaviour တို့ ပါဝင်သည်။ HNSW-style graph search ကို standard library ဖြင့် implement လုပ်ပြသည်။

**Learning outcome** — Parameter ပြောင်းလဲမှု၏ recall/speed impact ကို ခန့်မှန်းနိုင်ပြီး small-scale graph search ကို ကိုယ်တိုင် implement လုပ်နိုင်ရမည်။

Checkpoint questions —
- Upper layer များတွင် node density နည်းပါးရခြင်း၏ ရည်ရွယ်ချက် (long-range navigation)
- `ef_search` တိုးမြှင့်ခြင်း၏ recall/latency impact
- Filtered search တွင် HNSW graph traversal ၏ recall degradation mechanism

## M5 — `05_pgvector/` — PostgreSQL + pgvector

pgvector extension schema design ကို လေ့လာသည်။ `vector` column, operator class, distance operators (`<->` L2, `<=>` cosine, `<#>` inner product), HNSW vs IVFFlat index selection, `lists`/`m`/`ef_construction` tuning, jsonb metadata + GIN index filtering ပါဝင်သည်။ SQL များသည် PostgreSQL + pgvector official syntax ဖြစ်ပြီး course က run မပေးပါ — reader environment တွင် စမ်းသပ်ရန် ရည်ရွယ်သည်။

**Learning outcome** — pgvector table schema ရေးသားပြီး distance operator ရွေးချယ်ကာ ANN query ရေးနိုင်ရမည်။

Checkpoint questions —
- `<->` နှင့် `<=>` operators ၏ semantic ကွာခြားချက်
- IVFFlat သင့်လျော်သော workload characteristics
- WHERE clause metadata filter နှင့် vector index execution plan interaction

## M6 — `06_hybrid_search/` — Hybrid Search & RRF

Vector search နှင့် keyword search ပေါင်းစပ်မှုကို လေ့လာသည်။ PostgreSQL full-text search (`tsvector`/`tsquery`, GIN index), BM25 ranking (tf saturation `k1`, length normalization `b`, IDF), trigram similarity, score normalization, Reciprocal Rank Fusion တို့ ပါဝင်သည်။ Fusion algorithm များကို standard library ဖြင့် implement လုပ်ပြသည်။

**Learning outcome** — RRF formula ကို ကိုယ်တိုင်တွက်ချက်နိုင်ပြီး hybrid retrieval pipeline ဒီဇိုင်းရေးဆွဲနိုင်ရမည်။

Checkpoint questions —
- Weighted sum fusion သင့်လျော်သော အခြေအနေ vs RRF
- `tsvector` column ၏ query execution mechanism
- Hybrid search ၏ retrieval quality improvement mechanism (lexical + semantic coverage)

## M7 — `07_reranking/` — Reranking & Query Transformation

Bi-encoder (independent encoding) နှင့် cross-encoder (joint scoring) architecture ကွာခြားချက်ကို လေ့လာသည်။ Reranking latency cost, top-k selection, HyDE (Hypothetical Document Embedding), multi-query expansion, MMR (Maximal Marginal Relevance) diversity selection တို့ ပါဝင်သည်။ LLM အစား deterministic stand-in အသုံးပြုသည်။

**Learning outcome** — Rerank stage ဒီဇိုင်းရေးဆွဲနိုင်ပြီး HyDE/multi-query transformation ရွေးချယ်မှု ဆုံးဖြတ်နိုင်ရမည်။

Checkpoint questions —
- Cross-encoder precision မြင့်မားသော်လည်း first-stage retrieval အဖြစ် မသုံးနိုင်ရခြင်း၏ computational အကြောင်းရင်း
- MMR ၏ diversity mechanism (λ parameter ရဲ့ relevance-diversity trade-off)
- Rerank stage ထည့်သွင်းခြင်း၏ end-to-end latency impact

## M8 — `08_serving_architecture/` — Retrieval Serving Architecture

Retrieval API design ကို လေ့လာသည် — ACL integration (in-query filter), caching layers (embedding cache, result cache), concurrency နှင့် connection pool management ပါဝင်သည်။ pgvector vs Qdrant/Milvus/Weaviate/Chroma ရွေးချယ်မှု decision framework ကို official documentation link များဖြင့် ရှင်းလင်းသည်။ Hybrid architecture (PostgreSQL source of truth + dedicated vector store) migration pattern ပါဝင်သည်။

**Learning outcome** — ACL ပါဝင်သော retrieval API interface ဒီဇိုင်းရေးဆွဲနိုင်ပြီး cache layer placement ဆုံးဖြတ်နိုင်ရမည်။

Checkpoint questions —
- Result cache ၏ staleness window risk နှင့် mitigation (TTL / invalidation)
- Embedding cache key တွင် ပါဝင်သင့်သော components (model version, input normalization)
- pgvector ကို first-choice vector store အဖြစ် ရွေးချယ်ရခြင်း၏ operational အကြောင်းရင်း

## M9 — `09_pipelines_orchestration/` — Data Pipeline & Orchestration

Batch နှင့် streaming ingestion pattern များကို လေ့လာသည်။ Idempotency, backfill, rate limiting, dead-letter queue (DLQ), retry semantics, change data capture (CDC) အခြေခံများ ပါဝင်သည်။ Embedding model version migration အတွက် dual-write / shadow index / cut-over strategy နှင့် Airflow/Dagster DAG orchestration သဘောတရား ပါဝင်သည်။

**Learning outcome** — Retry-safe ingestion pipeline flowchart ရေးဆွဲနိုင်ပြီး model version migration plan ရေးသားနိုင်ရမည်။

Checkpoint questions —
- Pipeline idempotency သည် partial-failure recovery တွင် မည်သို့ အာမခံချက် ပေးသနည်း
- DLQ သုံးသင့်သော failure class များ
- Embedding version ပြောင်းလဲချိန်တွင် index ကို parallel rebuild လုပ်ရခြင်း၏ အကြောင်းရင်း

## M10 — `10_retrieval_evaluation/` — Retrieval Evaluation

Golden set construction နှင့် retrieval metric များကို လေ့လာသည်။ recall@k, precision@k, MRR, nDCG တို့ကို formula ဖြင့် တွက်ချက်ပြသည်။ Chunk-level vs document-level evaluation, CI regression gate, deterministic LLM judge pattern ပါဝင်သည်။

**Learning outcome** — Golden set ဖွဲ့စည်းနိုင်ပြီး recall@k/nDCG ကို ကိုယ်တိုင်တွက်ချက်ကာ regression gate သတ်မှတ်နိုင်ရမည်။

Checkpoint questions —
- recall@k သည် precision@k ထက် ပိုမိုအရေးပါသော use case
- MRR ၏ rank-sensitive scoring behaviour (rank 1 vs rank 5)
- Golden set size နည်းပါးခြင်း၏ evaluation variance impact

## M11 — `11_scale_performance/` — Scale & Performance

Quantization အခြေခံများ — scalar (fp32→int8), binary, product quantization (PQ) — ကို လေ့လာသည်။ Memory-recall trade-off, oversampling + re-scoring recovery, dimension reduction, sharding/partitioning strategy, index rebuild, write throughput optimization ပါဝင်သည်။ Memory estimation များကို assumption + formula ဖြင့် ပြသသည်။

**Learning outcome** — Quantization option တစ်ခုစီ၏ memory reduction ကို တွက်ချက်နိုင်ပြီး dataset အတွက် sharding strategy ရွေးချယ်နိုင်ရမည်။

Checkpoint questions —
- fp32 → int8 quantization ၏ memory reduction factor (တွက်ချက်ပြရန်)
- Binary quantization ၏ recall impact နှင့် recovery mechanism
- Sharding သည် query latency ကို အမြဲတမ်း လျှော့ချပါသလား (fan-out cost)

## M12 — `12_governance_security/` — Governance & Security

Embedding အတွင်း PII persistence risk ကို လေ့လာသည်။ Row-Level Security (RLS), document-level ACL integration, multi-tenant isolation pattern ၃ မျိုး, audit logging, retention policy, data provenance/license tracking ပါဝင်သည်။

**Learning outcome** — ACL-integrated retrieval query ဒီဇိုင်းရေးဆွဲနိုင်ပြီး tenant isolation approach ၃ မျိုးကို နှိုင်းယှဉ်နိုင်ရမည်။

Checkpoint questions —
- Embedding vector အတွင်း PII leakage ၏ risk profile (vector inversion attack)
- Database-enforced RLS သည် application-layer check ထက် ပိုမိုယုံကြည်စိတ်ချရခြင်း၏ အကြောင်းရင်း
- Shared index + metadata filter approach ၏ security failure mode

## M13 — `13_capstone/` — Capstone: End-to-end Design

Pipeline stage အားလုံး (ingest → chunk → embed → index → retrieve → rerank → evaluate) ကို တစ်ခုတည်းသော design document အဖြစ် စုစည်းသည်။ Storage calculation (chunk count × dimension × bytes), HNSW index memory estimation, QPS capacity planning တို့ကို assumption + formula ဖြင့် အပြည့်အစုံ တွက်ချက်ပြသည်။ တွက်ချက်မှုတိုင်းသည် offline, deterministic ဖြစ်ရမည်။

**Learning outcome** — Organization တစ်ခုအတွက် RAG retrieval stack design document နှင့် capacity/cost estimation ရေးသားနိုင်ရမည်။

Checkpoint questions —
- 10M chunks × 768 dimensions × fp32 ၏ vector storage footprint
- QPS estimation တွင် cache hit ratio ထည့်သွင်းပုံ
- Capstone design ဆုံးဖြတ်ချက်များအနက် assumption-dependent ဖြစ်သော အစိတ်အပိုင်းများ

## ၆ ပတ် လေ့လာမှု အစီအစဉ်

| ပတ် | Modules | အလေးထား |
|---|---|---|
| ၁ | M0–M2 | Data pipeline အခြေခံ — ingestion, chunking lab များ implement လုပ်ရန်။ မိမိ source data ရွေးချယ်ပြီး စတင်ရန် |
| ၂ | M3–M4 | Embedding computation, distance metrics, HNSW graph search lab များ။ LoRA/QLoRA concepts ကို official documentation ဖြင့် ဖတ်ရှုရန် (embedding fine-tuning အသိအမြင်) |
| ၃ | M5–M7 | pgvector schema, hybrid search, reranking ပေါင်းစပ်စမ်းသပ်ရန်။ Supervised fine-tuning နှင့် preference optimization concepts ကို official paper များဖြင့် ဖတ်ရှုရန် |
| ၄ | M10 | Retrieval evaluation — golden set ဖွဲ့စည်းပြီး metric များ ကိုယ်တိုင်တွက်ချက်ရန် |
| ၅ | M8, M11 | Serving architecture, quantization, sharding — memory estimation lab များ |
| ၆ | M9, M12–M13 | Orchestration, governance, capstone design အပြီးသတ် |

**မှတ်ချက်** — Lab အားလုံးသည် Python standard library ဖြင့်သာ လည်ပတ်ပြီး database မချိတ်ပါ။ Quantization, LoRA/QLoRA, fine-tuning တို့ကို လက်တွေ့ lab အဖြစ် မထည့်သွင်းထားဘဲ official documentation reference ဖြင့် conceptual understanding ကို စစ်ဆေးသည်။

## လက်တွေ့ စီမံကိန်း အကြံပြုချက်

- မိမိအလုပ် (သို့) စိတ်ဝင်စားသော domain မှ document 100–500 ကို source corpus အဖြစ် ရွေးချယ်ရန်
- Module တိုင်း၏ checkpoint question များကို မှတ်တမ်းတင်ရန်
- M10 ရောက်ချိန်တွင် corpus အတွက် golden set (အနည်းဆုံး query ၃၀) ဖွဲ့စည်းရန်
- အလုပ်အားလုံးကို git repository တွင် သိမ်းဆည်းပြီး အပတ်စဉ် commit ရန်
- Capstone design document ကို team နှင့် မျှဝေကာ peer review ခံယူရန်

## Capstone Requirements

မိမိရွေးချယ်သော corpus တစ်ခုအတွက် ပြည့်စုံသော RAG retrieval stack ဒီဇိုင်း ရေးသားရမည်။ မဖြစ်မနေ ပါဝင်ရမည့် အစိတ်အပိုင်းများ —

- Ingestion plan နှင့် idempotency strategy
- Chunking strategy + ရွေးချယ်မှု အကြောင်းပြချက်
- Embedding model ရွေးချယ်မှု + dimension
- Index type + parameter values
- Hybrid search နှင့် reranking ဆုံးဖြတ်ချက်များ
- Evaluation plan (golden set + metrics)
- Storage / index memory / QPS / cost estimation
- Governance plan (ACL, retention, PII handling)

တင်ပြချက်တွင် ဂဏန်းတိုင်းအတွက် formula သို့မဟုတ် official documentation reference ညွှန်းဆိုရမည်။ ဒီဇိုင်းကို peer review ခံယူပြီး limitation များ မှတ်တမ်းတင်ထားပါက production-grade design document ဖြစ်လာမည်။
