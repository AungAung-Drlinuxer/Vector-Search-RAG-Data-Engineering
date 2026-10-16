# M13 — Capstone: End-to-End System Design & Capacity Sizing Engine

Ingestion မှ Evaluation အထိ RAG data engineering pipeline အဆင့် ၈ ခုလုံးကို comprehensive architecture design အဖြစ် ပေါင်းစည်းပြီး Storage, HNSW Memory Footprint နှင့် QPS Capacity Planning များကို mathematical modeling ဖြင့် တည်ဆောက်သည့် Capstone module ဖြစ်သည်။

## သင်ယူလေ့လာမည့် အကြောင်းအရာများ

- End-to-end RAG architecture: Ingestion → Chunking → Embedding → Indexing → Retrieval → Reranking → Generation → Evaluation lifecycle
- Vector storage formulation: Chunk volume × Embedding dimension × Precision bytes (fp32 vs fp16/halfvec)
- HNSW index memory profiling: Multi-layer graph topology, `M`, `ef_construction` နှင့် link overheads
- QPS (Queries Per Second) throughput နှင့် p95/p99 latency profiling
- Chunk size / Overlap parameters များ၏ downstream retrieval precision နှင့် context completeness အပေါ် သက်ရောက်မှု
- Deterministic, offline capacity planning calculator engine တည်ဆောက်ခြင်း

## Module အစိတ်အပိုင်းများ

- M13.1 — End-to-end pipeline lifecycle နှင့် component interactions
- M13.2 — Raw vector storage estimation (chunk count × dimensions × bytes)
- M13.3 — HNSW graph topology memory estimation (vector buffer + adjacency list)
- M13.4 — QPS throughput နှင့် percentile latency modeling
- M13.5 — Parameter sensitivity analysis (chunking granularities & embedding dimensions)
- M13.6 — Capstone implementation: End-to-end deterministic retrieval & capacity engine

## Prerequisites

- Modules M01 မှ M12 အထိ သင်ခန်းစာများ အားလုံး
- Python 3 standard library
- Vector search concepts (Cosine similarity, HNSW mechanics, RRF fusion, Recall@K evaluation)
- PostgreSQL + pgvector architecture အခြေခံ

## Production Use Cases

- Infrastructure procurement အတွက် vector database cluster RAM နှင့် NVMe storage sizing ပြုလုပ်ခြင်း
- Production deployment မတိုင်မီ architectural design document (RFC) ရေးသားခြင်း
- Cost-to-performance optimization (FP32 vs Halfvec / Scalar Quantization trade-offs)

## References

- pgvector Official Documentation: https://github.com/pgvector/pgvector
- HNSW Paper (Malkov & Yashunin, 2016): https://arxiv.org/abs/1603.09320
- Ragas Retrieval Evaluation Framework: https://docs.ragas.io/
