# Vector Search & RAG Data Engineering

Vector search နှင့် RAG (Retrieval-Augmented Generation) system များအတွက် data engineering ပိုင်းကို အာရုံစိုက်သည့် self-study course ဖြစ်သည်။ Retrieval pipeline ၏ အစိတ်အပိုင်းတိုင်း — ingestion မှ governance အထိ — ကို ဦးတည်သည်။

## Scope နှင့် Independence

ဒီ course သည် original သင်ခန်းစာ ဖြစ်ပြီး module scope တိုင်းတွင် ဖော်ပြထားသည့် official open documentation များ (pgvector, PostgreSQL, Qdrant, Milvus, Weaviate, LangChain, LlamaIndex, HNSW paper) ပေါ်တွင်သာ အခြေခံသည်။ Commercial vendor training ကို ကူးယူခြင်း မဟုတ်ပါ။ နမူနာ code များသည် official documentation မှ mechanics များကို Python standard library ဖြင့် ပြန်လည်တည်ဆောက်ထားခြင်း ဖြစ်သည်။

## Course ၏ ဦးတည်ချက်

RAG system တစ်ခုကို data engineer အနေဖြင့် တည်ဆောက်ရာတွင် လိုအပ်သော အစိတ်အပိုင်းများ — text extraction, chunking strategy, embedding model selection, HNSW index internals, hybrid retrieval, reranking, pipeline orchestration, evaluation metrics, governance — ကို ဖြန့်ကျက်သင်ကြားသည်။

Lab များအားလုံးသည် deterministic ဖြစ်ပြီး network/database မလိုအပ်ပါ — retrieval mechanics များကို pure Python ဖြင့် ပြန်လည် implement လုပ်ခြင်းအားဖြင့် algorithm အလုပ်လုပ်ပုံကို တိုက်ရိုက် လေ့လာနိုင်သည်။ Production system များအတွက် ဆုံးဖြတ်ချက် framework များကို prose ဖြင့် ရှင်းပြပြီး official documentation link များ ချိတ်ဆက်ထားသည်။

## RAG Pipeline Architecture

| # | Stage | လုပ်ဆောင်ချက် | Module |
|---|---|---|---|
| 1 | ingest | Source system များမှ raw document များ ဆွဲယူခြင်း | M1 |
| 2 | chunk | Document ကို retrieval unit များအဖြစ် ခွဲခြမ်းခြင်း | M2 |
| 3 | embed | Chunk တစ်ခုစီကို vector representation အဖြစ် ပြောင်းလဲခြင်း | M3 |
| 4 | index | Vector များကို ANN search structure ဖြင့် စီစဉ်သိမ်းဆည်းခြင်း | M4, M5 |
| 5 | retrieve | Query vector နှင့် similarity-based candidate ရှာဖွေခြင်း | M5, M6 |
| 6 | rerank | Candidate များကို precision-oriented model ဖြင့် ပြန်လည်စီစဉ်ခြင်း | M7 |
| 7 | generate | Retrieved context ဖြင့် LLM response ထုတ်လုပ်ခြင်း | M0, M8 |
| 8 | evaluate | Retrieval quality ကို metric များဖြင့် တိုင်းတာခြင်း | M10 |

## Modules

| Module | Folder | ခေါင်းစဉ် |
|---|---|---|
| M0 | `00_orientation/` | RAG architecture map၊ pipeline stage ၈ ခု၊ search modality ရွေးချယ်မှု framework |
| M1 | `01_ingestion/` | Corpus ingestion၊ text extraction၊ Unicode normalization၊ duplicate detection၊ upsert/delete semantics |
| M2 | `02_chunking/` | Chunking strategies (fixed/recursive/token/semantic)၊ overlap trade-off၊ metadata schema design |
| M3 | `03_embeddings/` | Embedding model selection၊ dimension၊ distance metric ဆက်စပ်မှု၊ Matryoshka၊ caching |
| M4 | `04_hnsw/` | HNSW multi-layer graph internals၊ `M`/`ef_construction`/`ef_search`၊ recall-latency trade-off၊ index memory |
| M5 | `05_pgvector/` | PostgreSQL + pgvector schema၊ distance operators၊ HNSW/IVFFlat index tuning၊ jsonb filtering |
| M6 | `06_hybrid_search/` | Full-text search၊ BM25၊ trigram similarity၊ score normalization၊ RRF fusion |
| M7 | `07_reranking/` | Bi-encoder vs cross-encoder၊ reranking cost၊ HyDE၊ multi-query expansion၊ MMR |
| M8 | `08_serving_architecture/` | Retrieval API design၊ ACL integration၊ caching layers၊ concurrency၊ vector engine ရွေးချယ်မှု |
| M9 | `09_pipelines_orchestration/` | Batch/streaming ingestion၊ idempotency၊ backfill၊ DLQ/retry၊ embedding version migration၊ DAG orchestration |
| M10 | `10_retrieval_evaluation/` | Golden set၊ recall@k၊ precision@k၊ MRR၊ nDCG၊ chunk/document-level evaluation၊ CI regression gate |
| M11 | `11_scale_performance/` | Scalar/binary/product quantization၊ dimension reduction၊ sharding၊ index rebuild၊ write throughput |
| M12 | `12_governance_security/` | PII redaction၊ Row-Level Security၊ ACL၊ multi-tenancy isolation၊ audit log၊ retention |
| M13 | `13_capstone/` | End-to-end design consolidation၊ storage/index memory/QPS capacity planning |
| M14 | `14_graph_rag_neo4j/` | Knowledge Graph RAG (GraphRAG)၊ Neo4j Property Graph၊ Triples extraction၊ 2-hop BFS၊ Text-to-Cypher၊ Community Detection |

## Database ဦးတည်ချက်

SQL နမူနာများသည် PostgreSQL + pgvector stack ကို ဦးတည်သည်။ Course ကိုယ်တိုင်က SQL run မပေးပါ — reader ၏ environment တွင် စမ်းသပ်ရန် ရည်ရွယ်သည်။ Lab များအားလုံးသည် database မလိုဘဲ Python standard library ဖြင့်သာ လည်ပတ်သည်။ Cosine similarity, HNSW-style graph search, RRF, recall@k တို့ကို ground-up implementation ဖြင့် လေ့လာရပြီး ဤ mechanics များသည် Qdrant, Milvus, Weaviate စသည့် dedicated vector store များ၏ အလုပ်လုပ်ပုံနှင့် တိုက်ရိုက် ဆက်စပ်သည်။

## Folder Structure

Module တစ်ခုစီတွင် file ၅ ခု ပါဝင်သည် —

| File | အကြောင်းအရာ |
|---|---|
| `README.md` | Module scope နှင့် learning objectives |
| `explanation.md` | သဘောတရား ရှင်းလင်းချက်၊ formula၊ deterministic code example |
| `exercise.md` | ကိုယ်တိုင် implement လုပ်ရမည့် လေ့ကျင့်ခန်း |
| `solution.md` | Reference implementation နှင့် ရှင်းလင်းချက် |
| `lab.py` | Local machine ပေါ်တွင် တိုက်ရိုက် run ၍ test လုပ်နိုင်သော executable lab |

## Hands-on Labs & Local Testing

Course တစ်ခုလုံးတွင် ပါဝင်သော algorithm များနှင့် pipeline အားလုံးကို local တွင် automated test ပြုလုပ်နိုင်ရန် lab environment ပြင်ဆင်ထားသည် (အသေးစိတ်ကို `LABS_GUIDE.md` တွင် ဖတ်ရှုပါ) —

```bash
# Core Labs အားလုံး (၈၅ ခု) ကို ချက်ချင်း run ပြီး စစ်ဆေးရန် (Python standard library only)
python run_all_labs.py

# သီးခြား module တစ်ခုတည်း စမ်းသပ်ရန်
python modules/01_ingestion/lab.py

# PostgreSQL + pgvector live database ဖြင့် စမ်းသပ်ရန်
docker compose up -d
python modules/05_pgvector/live_db_test.py
```

## လေ့လာမှု နည်းလမ်း

Module များကို အစဉ်လိုက် လေ့လာရန် အကြံပြုသည်။ Module တစ်ခုစီအတွက် workflow —

1. `README.md` — scope နှင့် objectives သိရှိရန်
2. `explanation.md` — သဘောတရားနှင့် mechanics နားလည်ရန်
3. `exercise.md` — reference implementation မကြည့်မီ ကိုယ်တိုင် implement လုပ်ရန်
4. `solution.md` — ကိုယ်ရေးသားမှုနှင့် နှိုင်းယှဉ်ရန်

Code များကို run ပြီး parameter ပြောင်းလဲကာ output ကို တိုင်းတာရန် — pipeline stage တစ်ခုစီ၏ quantitative behaviour ကို မိမိ corpus ဖြင့် အတည်ပြုရန် လိုအပ်သည်။

## Prerequisites

Beginner-oriented course မဟုတ်ပါ။ လိုအပ်သော အရည်အချင်းများ —

- Python — dict, list comprehension, function, standard library အသုံးပြုနိုင်မှု
- SQL / PostgreSQL — SELECT, JOIN, index fundamentals
- RAG / LLM architecture အခြေခံ နားလည်မှု

## ဂဏန်းတန်ဖိုးများအပေါ် မူဝါဒ

Course အတွင်း ဂဏန်းတိုင်းသည် အောက်ပါ ၂ မျိုးအနက် တစ်မျိုးသာ ဖြစ်သည် —

1. သင်ခန်းစာတွင် ဖော်ပြထားသော formula + assumption ဖြင့် တွက်ချက်ထားသော တန်ဖိုး
2. Module scope အတွင်း အမည်တပ်ဖော်ပြထားသော official documentation မှ ကောက်နုတ်ချက်

Recall, latency, QPS, memory size တန်ဖိုးများကို တီထွင်ဖန်တီးထားခြင်း မရှိပါ။ Index ၏ recall နှင့် behaviour သည် corpus characteristics, parameter values, engine version ပေါ်တွင် မူတည်သဖြင့် production decision အတွက် မိမိ data ပေါ်တွင် ကိုယ်တိုင် benchmark လုပ်ရန် လိုအပ်သည်။ LLM call များသည် runtime တွင် အမှန်တကယ် ဖြစ်ပေါ်ခြင်း မရှိဘဲ scripted deterministic stand-in များသာ အသုံးပြုသည်။

## အသုံးပြုမှု လမ်းညွှန်

- **အစဉ်လိုက် လေ့လာရန်** — M1–M3 (data layer) → M4–M5 (index layer) → M6–M8 (retrieval quality + serving) → M9–M13 (operations + evaluation + design)
- **Lab အားလုံးကို run ရန်** — Module တိုင်း၏ code ကို run ပြီး ရလဒ်မှတ်တမ်း တင်ထားရန်။ Parameter sensitivity ကို ကိုယ်တိုင် တိုင်းတာခြင်းသည် course ၏ အဓိက တန်ဖိုး ဖြစ်သည်။
- **Database မလိုအပ်ပါ** — SQL နမူနာများကို ကိုယ်ပိုင် PostgreSQL + pgvector environment တွင် သီးသန့် စမ်းသပ်နိုင်သည်။
- **Golden set စောစီးစွာ ဖွဲ့ရန်** — M10 ရောက်ချိန်တွင် မိမိ corpus အတွက် golden set (query ၂၀–၅၀) ရှိနေပါက evaluation module အကျိုးရှိမှု သိသိသာသာ မြင့်တက်သည်။

## ဖြေရှင်းပေးသည့် Design မေးခွန်းများ

- Corpus characteristics အပေါ် အခြေခံ၍ chunk size/overlap ဘယ်လို ရွေးမလဲ
- Embedding model migration အတွက် index re-embedding strategy
- HNSW `M`, `ef_construction`, `ef_search` tuning methodology
- Vector score နှင့် BM25 score fusion (weighted sum vs RRF) ရွေးချယ်မှု
- Storage, index memory, QPS capacity planning formula
- ACL ကို retrieval query အတွင်း integration (pre-filter design)

## Production Checklist

- Chunk metadata တွင် source, section, page, permission ပါဝင်မှု ရှိ/မရှိ
- Ingestion pipeline ၏ idempotency (re-run တွင် duplicate မဖြစ်မှု)
- Evaluation set + recall@k ကို CI gate အဖြစ် automate လုပ်ထားမှု
- Embedding ထည့်သွင်းခြင်း မတိုင်မီ PII detection/redaction pipeline
- Embedding model version ကို index, cache, metadata တွင် track လုပ်ထားမှု

## Target Roles

| Role | Course relevance |
|---|---|
| Retrieval/pipeline engineer | Ingestion, chunking, indexing, quality measurement — module 1–6, 9–10 |
| AI application engineer | Retrieval API design, generation layer integration — module 7–8 |
| Data platform engineer | Vector store operations, capacity, tenancy, governance — module 8, 11–13 |

## ကိုးကားချက်များ

Module scope တိုင်းတွင် ကိုးကား documentation များ အသေးစိတ် ပါဝင်သည်။ အဓိက official source များ —

- pgvector — https://github.com/pgvector/pgvector
- PostgreSQL Documentation — https://www.postgresql.org/docs/
- Qdrant — https://qdrant.tech/documentation/
- Milvus — https://github.com/milvus-io/milvus
- Weaviate — https://weaviate.io/developers/weaviate
- Chroma — https://docs.trychroma.com/
- HNSW paper (Malkov & Yashunin, arXiv:1601.06867) — https://arxiv.org/abs/1601.06867
