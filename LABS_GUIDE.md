# Local Hands-On Labs Guide — Vector Search & RAG Data Engineering

ဒီ course တွင် ပါဝင်သော module ၁၄ ခုလုံး (M00 မှ M13) ၏ algorithms၊ math calculations၊ vector search mechanics နှင့် data engineering pipelines များကို မိမိ local machine ပေါ်တွင် တိုက်ရိုက် run ၍ test လုပ်နိုင်သော hands-on labs environment ကို ပြင်ဆင်ပေးထားပါသည်။

---

## ၁။ အမြန်စတင်နည်း (Quickstart — Pure Python Standard Library)

Course အတွင်းရှိ core labs များ (စုစုပေါင်း ၈၅ ခု) သည် **Python standard library သာ အသုံးပြုထားသဖြင့် external dependency သွင်းရန် မလိုဘဲ** ချက်ချင်း run နိုင်ပါသည်။

### (က) Module အားလုံးကို တစ်ပြိုင်နက် Test လုပ်ရန်
```bash
python run_all_labs.py
```

### (ခ) Module တစ်ခုချင်းစီကို သီးခြား Run ရန်
```bash
# ဥပမာ - Module 01 (Ingestion & Deduplication)
python modules/01_ingestion/lab.py

# ဥပမာ - Module 04 (HNSW Graph Search)
python modules/04_hnsw/lab.py

# ဥပမာ - Module 06 (Hybrid Search & BM25)
python modules/06_hybrid_search/lab.py

# ဥပမာ - Module 13 (Capstone End-to-End & Capacity)
python modules/13_capstone/lab.py
```

### (ဂ) အသေးစိတ် Output များ ကြည့်ရှုလိုပါက (`--verbose`)
```bash
python run_all_labs.py --module 05_pgvector --verbose
```

---

## ၂။ Docker Compose ဖြင့် PostgreSQL + pgvector Live Test ပြုလုပ်ခြင်း

PostgreSQL database အစစ်ပေါ်တွင် pgvector extension၊ HNSW index၊ GIN metadata filter နှင့် Row-Level Security (RLS) များကို စမ်းသပ်လိုပါက repository ထဲရှိ `docker-compose.yml` ကို အသုံးပြုနိုင်ပါသည်။

### (က) Database Container စတင်ခြင်း
```bash
docker compose up -d
```
Container စတင်သည်နှင့် `docker/init.sql` script မှ အောက်ပါ schema များကို အလိုအလျောက် တည်ဆောက်ပေးပါသည်:
- `vector` extension (pgvector)
- `pg_trgm` extension (trigram matching)
- `chunks` table (vector column, jsonb metadata, full-text tsvector)
- HNSW cosine index (`vector_cosine_ops`)
- GIN metadata index (`jsonb_path_ops`)
- Row-Level Security (RLS) policies ပါဝင်သော `documents` table

### (ခ) Connection Parameters
- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `rag_course`
- **Username**: `postgres`
- **Password**: `postgres`

### (ဂ) Live Database Test Script Run ခြင်း
Optional dependencies များ သွင်းပါ:
```bash
pip install -r requirements.txt
```
Live integration test run ပါ:
```bash
python modules/05_pgvector/live_db_test.py
```

### (ဃ) Database ရပ်တန့်ခြင်း
```bash
docker compose down
```

---

## ၃။ Module အလိုက် Lab အကြောင်းအရာများ (Total: 85 Exercises)

| # | Module | Folder | စမ်းသပ်သည့် အဓိက Lab Exercises |
|---|---|---|---|
| M00 | Orientation | `modules/00_orientation/lab.py` | Pipeline stages 8 ခု၊ Cosine similarity၊ Search modality ရွေးချယ်မှု၊ RRF |
| M01 | Ingestion | `modules/01_ingestion/lab.py` | Boilerplate removal၊ NFC normalization၊ SHA-256 fingerprinting၊ Idempotent upsert |
| M02 | Chunking | `modules/02_chunking/lab.py` | Fixed-size၊ Overlap sliding window၊ Recursive splitting၊ Parent-child hierarchy |
| M03 | Embeddings | `modules/03_embeddings/lab.py` | Memory footprint (FP32)၊ L2 normalization၊ Matryoshka truncation၊ Embedding cache |
| M04 | HNSW | `modules/04_hnsw/lab.py` | Graph greedy traversal၊ M & ef_construction၊ ef_search tuning၊ Filtered recall |
| M05 | pgvector | `modules/05_pgvector/lab.py` | Distance operators (`<->`, `<=>`, `<#>` monotonic proof)၊ RRF၊ Index sizing helper |
| M06 | Hybrid Search | `modules/06_hybrid_search/lab.py` | Inverted index၊ BM25 formula၊ Trigram Jaccard၊ Score normalization၊ Hybrid fusion |
| M07 | Reranking | `modules/07_reranking/lab.py` | Cross-encoder vs Bi-encoder၊ Latency cost modeling၊ HyDE၊ Multi-query RRF၊ MMR |
| M08 | Serving | `modules/08_serving_architecture/lab.py` | Retrieval API interface၊ Two-tier cache (Query + Result)၊ Connection pooling simulation |
| M09 | Pipelines | `modules/09_pipelines_orchestration/lab.py` | Idempotency test၊ Backfill throughput rate limit၊ DLQ exponential retry၊ DAG sorting၊ CDC diff |
| M10 | Evaluation | `modules/10_retrieval_evaluation/lab.py` | Golden set structure၊ Recall@K၊ Precision@K၊ MRR၊ nDCG@K၊ Regression threshold |
| M11 | Scale | `modules/11_scale_performance/lab.py` | Scalar Quantization (INT8)၊ Binary Quantization၊ Product Quantization (PQ)၊ Sharding |
| M12 | Governance | `modules/12_governance_security/lab.py` | Ingestion regex PII redaction၊ In-query ACL filter၊ Multi-tenant isolation၊ Cascade delete |
| M13 | Capstone | `modules/13_capstone/lab.py` | Sizing calculator၊ Proximity graph benchmark၊ QPS & p95 latency၊ Unified end-to-end pipeline |
| M14 | GraphRAG | `modules/14_graph_rag_neo4j/lab.py` | Property Graph Cypher၊ Triples extraction & resolution၊ 2-hop BFS၊ Hybrid retrieval၊ Community detection |

---

## ၄။ File Structure Overview

```text
Vector-Search-RAG-Data-Engineering/
├── docker-compose.yml              # Local PostgreSQL + pgvector service
├── docker/
│   └── init.sql                   # Database initialization DDL & seed data
├── requirements.txt                # Optional live test dependencies
├── run_all_labs.py                 # Master automated lab test runner (85 exercises)
├── LABS_GUIDE.md                   # Lab execution instructions (ဤဖိုင်)
└── modules/
    ├── 00_orientation/
    │   ├── README.md
    │   ├── explanation.md
    │   ├── exercise.md
    │   ├── solution.md
    │   └── lab.py                  # Standalone runnable lab
    ├── ...
    └── 13_capstone/
        ├── README.md
        ├── explanation.md
        ├── exercise.md
        ├── solution.md
        └── lab.py                  # Standalone runnable lab
```
