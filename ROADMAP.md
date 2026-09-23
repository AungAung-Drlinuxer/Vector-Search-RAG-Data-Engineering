# Vector Search & RAG Data Engineering — လေ့လာမှု လမ်းညွှန် (ROADMAP)

ဒီ course က original လေ့လာမှု စာပိုင်းပဲ ဖြစ်ပါတယ်။ တစ်ခုချင်းရဲ့ module scope မှာ နာမည်တပ်ထားတဲ့ တရားဝင် open documentation တွေကနေ ရေးထားတာပါ။ အခြား commercial course တစ်ခုခုရဲ့ သင်ခန်းစာကို ပြန်မရေးထားပါဘူး။

ဒီ course မှာ တွက်ချက်မှုတွေက သတ်မှတ်ထားတဲ့ ယူဆချက် (assumption) တွေနဲ့ formula ပြပြီး တွက်ပြထားတာပါ။ ဘယ်နာမည်တပ် system အတွက်မှ မှတ်ဉာဏ်၊ latency၊ QPS စတဲ့ ကိန်းဂဏန်းကို မကြံစဉ်ပါဘူး။ Python standard library သုံးပြီး တကယ့် database နဲ့ မချိတ်ပါဘူး — retrieval mechanic တွေကို ကိုယ်တိုင်ပြန်ရေးပြီး လေ့လာရမှာပါ။

## M0 — `00_orientation/` — RAG Data Engineering ရဲ့ မြေပုံ

RAG (Retrieval-Augmented Generation — အချက်အလက် ရှာဖွေပြီးမှ အဖြေရေးတဲ့ နည်း) pipeline ရဲ့ အဆင့် ၈ ခုကို အစအဆုံး မြင်အောင် ပြပါတယ်။ ingest → chunk → embed → index → retrieve → rerank → generate → evaluate ဆိုတဲ့ အဆင့်တွေပါ။ vector search၊ keyword search နဲ့ hybrid search ကို ဘယ်အချိန် ရွေးရမလဲဆိုတာကို ဥပမာနဲ့ ရှင်းပြပါတယ်။

ဒီ module ပြီးရင် လုပ်နိုင်ရမည့်အရာ — RAG pipeline တစ်ခုလုံးကို စက္ကန့်ပိုင်း ရေးဆွဲပြီး၊ မေးခွန်းတစ်ခုအတွက် search အမျိုးအစား ရွေးချယ်နိုင်ရမယ်။

- RAG pipeline မှာ chunking က embed ထက် ရှေ့မှာ ဘာကြောင့် လိုအပ်လဲ။
- Keyword search က vector search ထက် သင့်တော်တဲ့ အခြေအနေကို ဥပမာ တစ်ခုပေးပါ။
- evaluate အဆင့်ကို နောက်ဆုံးမှ ထားရင် ဘာပြဿနာ ဖြစ်နိုင်လဲ။

## M1 — `01_ingestion/` — Corpus Ingestion

ရင်းမြစ် အမျိုးအစားများ (PDF၊ HTML၊ Markdown၊ database row) ကနေ text ဆွဲထုတ်နည်းကို သင်ပါတယ်။ boilerplate (စာမျက်နှာရဲ့ header/footer စတဲ့ အပိုအပိုင်းများ) ဖယ်ရှားခြင်း၊ unicode normalization (စာလုံး ပုံစံ တစ်သွေတည်း ပြောင်းခြင်း) နဲ့ duplicate စစ်ခြင်း (hash နဲ့ content fingerprint) ကို လက်တွေ့ ကုဒ်နဲ့ ပြပါတယ်။ upsert (ရှိရင် ပြင်၊ မရှိရင် ထည့်) နဲ့ delete သဘောတရားလည်း ပါပါတယ်။

ဒီ module ပြီးရင် လုပ်နိုင်ရမည့်အရာ — ရင်းမြစ်ဖိုင်တစ်ခုကနေ သန့်စင်တဲ့ text ထုတ်ပြီး၊ duplicate ဖြစ်နေတဲ့ စာပိုဒ်ကို hash နဲ့ ရှာနိုင်ရမယ်။

- Unicode NFC နဲ့ NFD ကွာခြားချက်က ingestion မှာ ဘာကို ထိခိုက်လဲ။
- Content fingerprint က exact duplicate ထက် ဘာအတွက် ပိုအသုံးဝင်လဲ။
- Upsert ကို idempotent (အကြိမ်ကြိမ် လုပ်လည်း ရလဒ် အတူတူ ရမယ်) ဖြစ်အောင် ဘယ်လို သေချာမလဲ။

## M2 — `02_chunking/` — Chunking မဟာဗျူဟာနှင့် Metadata ဒီဇိုင်း

Chunk (ရှာဖွေမှုရဲ့ အသေးဆုံး စာတစ်ခု) ခွဲနည်းတွေကို သင်ပါတယ် — fixed-size၊ recursive၊ token-based၊ semantic နှင့် parent-child chunking။ overlap (နောက် chunk နဲ့ ထပ်တဲ့ အပိုင်း) ရွေးချယ်မှု၊ chunk အရွယ်နဲ့ retrieval အရည်အသွေးရဲ့ အပေးအယူကို ရှင်းပြပါတယ်။ heading နဲ့ စာရွက် structure ကို ထိန်းသိမ်းနည်း၊ metadata schema ဒီဇိုင်းလည်း ပါပါတယ်။

ဒီ module ပြီးရင် လုပ်နိုင်ရမည့်အရာ — စာရွက်အမျိုးအစားအလိုက် သင့်တော်တဲ့ chunking strategy ရွေးပြီး၊ metadata column တွေ ဒီဇိုင်းဆွဲနိုင်ရမယ်။

- Chunk က ကြီးရင် retrieval မှာ ဘာအားသာပြီး၊ ငယ်ရင် ဘာဆိုးရွားလဲ။
- Overlap က ဘာပြဿနာကို ဖြေရပါတယ်။
- Parent-child chunking ကို ဘယ်အခြေအနေမျိုးမှာ သုံးသင့်လဲ။

## M3 — `03_embeddings/` — Embedding Model၊ Dimension၊ Distance Metric နှင့် Caching

Embedding (စာကို ကိန်းစဉ်တစ်ခု ဖြစ်ပြောင်းတဲ့ representation) model ရွေးချယ်မှု၊ dimension နဲ့ storage တွက်ချက်မှုကို သင်ပါတယ်။ L2 normalization လုပ်ပြီးရင် cosine၊ dot product၊ L2 distance တွေ ဆက်စပ်ပုံကို formula နဲ့ ပြပါတယ်။ Matryoshka representation (dimension ဖြတ်ပြီး သုံးနိုင်တဲ့ embedding) နဲ့ embedding cache ဒီဇိုင်းလည်း ပါပါတယ်။

ဒီ module ပြီးရင် လုပ်နိုင်ရမည့်အရာ — 1,000,000 chunks၊ 768 dimensions၊ fp32 ဆိုတဲ့ ယူဆချက်နဲ့ storage ကို ကိုယ်တိုင်တွက်နိုင်ရမယ်။ cosine similarity ကို standard library နဲ့ ရေးနိုင်ရမယ်။

- fp32 မှာ dimension တစ်ခုက byte ဘယ်နှစ်ခု ယူလဲ၊ ဘာကြောင့်လဲ။
- Vector တွေ normalized ဖြစ်နေရင် dot product နဲ့ cosine က ဘာကြောင့် တူတူပဲ ဖြစ်လဲ။
- Embedding cache က model ပြောင်းတဲ့အခါ ဘာကြောင့် အဆင်မပြေဘူးလဲ။

## M4 — `04_hnsw/` — HNSW Index အတွင်းပိုင်း

HNSW (Hierarchical Navigable Small World — အလွှာများစွာ ပါတဲ့ graph နဲ့ အနီးစပ်ဆုံး ဆိုလိုရပ် ရှာတဲ့ algorithm) ရဲ့ multi-layer graph သဘောတရားကို သင်ပါတယ်။ M နဲ့ ef_construction (index ဆောက်ချိန် parameter)၊ ef_search (query ရှာချိန် parameter) တွေရဲ့ သက်ရောက်မှု၊ recall နဲ့ latency အပေးအယူကို ရှင်းပြပါတယ်။ index memory တွက်နည်း၊ build time၊ filtered search သဘောတရားလည်း ပါပါတယ်။ အသေးစား HNSW-style graph search ကို standard library Python နဲ့ ရေးပြပါမယ်။

ဒီ module ပြီးရင် လုပ်နိုင်ရမည့်အရာ — M၊ ef_construction၊ ef_search တွေ ပြောင်းလိုက်ရင် recall နဲ့ speed ဘယ်လို ပြောင်းမလဲ ခန့်မှန်းနိုင်ရမယ်။ သေးငယ်တဲ့ graph search ကို ကိုယ်တိုင် implement လုပ်နိုင်ရမယ်။

- HNSW မှာ layer အပေါ်ဆုံးက အမှတ် ဘာကြောင့် နည်းလဲ။
- ef_search ကို တိုးလိုက်ရင် recall နဲ့ latency ဘယ်လို ပြောင်းလဲ။
- Filtered search ကို HNSW က ဘယ်လို ကိုင်ရလဲ၊ ဘာအခက်အခဲ ရှိလဲ။

## M5 — `05_pgvector/` — PostgreSQL + pgvector

pgvector extension နဲ့ schema ဒီဇိုင်းကို သင်ပါတယ်။ `vector` column၊ operator class၊ distance operator (`<->`၊ `<=>`၊ `<#>`) တွေကို SQL ဥပမာနဲ့ ပြပါတယ်။ HNSW နဲ့ IVFFlat index ရွေးချယ်မှု၊ `lists`/`m`/`ef_construction` သတ်မှတ်ခြင်း၊ jsonb metadata နဲ့ filtering တွေလည်း ပါပါတယ်။ SQL တွေက PostgreSQL + pgvector အတွက် တရားဝင် syntax ပဲ ဖြစ်ပြီး ဒီ course က  run မပေးပါဘူး — စာဖတ်ပြီး လက်တွေ့ environment မှာ ကိုယ်တိုင် စမ်းကြည့်ရမှာပါ။

ဒီ module ပြီးရင် လုပ်နိုင်ရမည့်အရာ — pgvector table တစ်ခု schema ရေးပြီး၊ distance operator မှန်ကို ရွေးပြီး ANN query ရေးနိုင်ရမယ်။

- `<->` နဲ့ `<=>` ကွာခြားချက်က ဘာလဲ။
- IVFFlat ကို ရွေးသင့်တဲ့ အခြေအနေ ဘယ်လိုအမျိုးအစားလဲ။
- Metadata filter ကို WHERE clause မှာ ထည့်ရင် index နဲ့ ဘယ်လို ဆက်စပ်လဲ။

## M6 — `06_hybrid_search/` — Hybrid Search နှင့် RRF

Vector search နဲ့ keyword search ကို ပေါင်းစပ်နည်းကို သင်ပါတယ်။ PostgreSQL full-text search (`tsvector`၊ `tsquery`) နဲ့ ranking၊ trigram similarity ကို SQL ဥပမာနဲ့ ပြပါတယ်။ Vector score နဲ့ BM25-style score ကို ပေါင်းနည်း (weighted sum နဲ့ Reciprocal Rank Fusion) ကို standard library Python နဲ့ ရေးပြပါမယ်။

ဒီ module ပြီးရင် လုပ်နိုင်ရမည့်အရာ — RRF (Reciprocal Rank Fusion — rank တွေကနေ score ပေါင်းတဲ့ နည်း) formula ကို ကိုယ်တိုင်တွက်ပြီး၊ hybrid retrieval pipeline တစ်ခု ဒီဇိုင်းနိုင်ရမယ်။

- Weighted sum က RRF ထက် ဘယ်အချိန် အဆင်ပြေလဲ။
- tsvector column က query တစ်ခုမှာ ဘယ်လို အလုပ်လုပ်လဲ။
- Hybrid search က retrieval အရည်အသွေးကို ဘာကြောင့် မြှင့်တယ်လဲ။

## M7 — `07_reranking/` — Reranking နှင့် Query ပြောင်းလဲခြင်း

Bi-encoder (embedding ချင်း နှိုင်းတဲ့ မော်ဒယ်) နဲ့ cross-encoder (query နဲ့ document ကို တွဲဖက် ဖတ်တဲ့ မော်ဒယ်) ကွာခြားချက်ကို သင်ပါတယ်။ Reranking ရဲ့ latency ကုန်ကျစရိတ်၊ top-k ရွေးချယ်မှု၊ HyDE (Hypothetical Document Embedding — တွေးဆင်းခြင်း စာတု နဲ့ ရှာတဲ့နည်း)၊ multi-query expansion နဲ့ MMR (Maximal Marginal Relevance — အတူတူ ရလဒ် လျှော့ပြီး စုံစုံလင်းလင်း ရအောင် ရွေးတဲ့နည်း) တွေ ပါပါတယ်။ LLM နေရာမှာ deterministic stand-in သုံးပြပါမယ်။

ဒီ module ပြီးရင် လုပ်နိုင်ရမည့်အရာ — Retrieval ရလဒ်ကို ပြန်စဉ်တဲ့ rerank အဆင့်တစ်ခု ဒီဇိုင်းနိုင်ရမယ်။ HyDE နဲ့ multi-query တွေကို ဘယ်အချိန် သုံးမလဲ ဆုံးဖြတ်နိုင်ရမယ်။

- Cross-encoder က bi-encoder ထက် ပိုတိကျပေမယ့် ဘာကြောင့် အားလုံးအတွက် မသုံးရလဲ။
- MMR က diversity ကို ဘယ်လို တိုးပေးလဲ။
- Rerank အဆင့်ကို ထည့်ရင် latency ဘယ်လို ပြောင်းလဲ။

## M8 — `08_serving_architecture/` — Retrieval Serving Architecture

Retrieval API ဒီဇိုင်းကို သင်ပါတယ် — filter နဲ့ ACL (Access Control List — ဘယ်သူ ဘာဖတ်ရလဲဆိုတဲ့ စာရင်း) ပါဝင်မှု၊ caching အလွှာများ (embedding cache၊ result cache)၊ concurrency နဲ့ connection pool တွေ ပါပါတယ်။ pgvector နဲ့ Qdrant/Milvus/Weaviate/Chroma စတဲ့ vector engine တွေ ရွေးချယ်ရေးကို တရားဝင် documentation လင့်ခ်နဲ့ ကြည့်ပြီး ရှင်းပြပါတယ်။

ဒီ module ပြီးရင် လုပ်နိုင်ရမည့်အရာ — Filter နဲ့ ACL ပါတဲ့ retrieval API တစ်ခုရဲ့ interface ဒီဇိုင်းဆွဲနိုင်ရမယ်။ Cache အလွှာ ဘယ်နေရာမှာ တင်မလဲ ရွေးနိုင်ရမယ်။

- Result cache က stale (အချိန်ကျနေတဲ့) အချက်အလက် ပြနိုင်တဲ့ အန္တရာယ်က ဘာလဲ။
- Embedding cache key မှာ ဘယ် element တွေ ပါသင့်လဲ။
- pgvector ကို စတင်ရွေးတဲ့ အခြေခံအကြောင်းပြချက်တွေ ဘာတွေလဲ။

## M9 — `09_pipelines_orchestration/` — Data Pipeline နှင့် Orchestration

Batch နဲ့ streaming ingestion ကို သင်ပါတယ်။ Idempotent (ထပ်လုပ်လည်း ရလဒ် အတူတူ) ပြန်လုပ်နိုင်မှု၊ backfill (အတိတ် data ပြန်ထည့်ခြင်း) နဲ့ rate limit၊ dead-letter (ကျန်နေတဲ့ အချက်အလက်ကို သီးသန့် သိမ်းတဲ့နေရာ) နဲ့ retry စနစ်၊ change data capture အခြေခံတွေ ပါပါတယ်။ Embedding model version ပြောင်းတဲ့အခါ migration လုပ်နည်းလည်း သင်ပါတယ်။

ဒီ module ပြီးရင် လုပ်နိုင်ရမည့်အရာ — Retry ခံနိုင်တဲ့ ingestion pipeline တစ်ခုရဲ့ flow chart ရေးနိုင်ရမယ်။ Model version ပြောင်းချိန် migration စီမံချက်ရေးနိုင်ရမယ်။

- Idempotency က pipeline ကို ဘာကြောင့် လုံခြုံစေလဲ။
- Dead-letter queue ကို ဘယ်အချိန် သုံးသင့်လဲ။
- Embedding version ပြောင်းရင် index ကို ဘာကြောင့် တစ်ပြိုင်နက် rebuild ရလဲ။

## M10 — `10_retrieval_evaluation/` — Retrieval အကဲဖြတ်ခြင်း

Golden set (query → မှန်တဲ့ chunk အမှတ် ဆိုတဲ့ စာရင်း) ဖွဲ့ခြင်းနဲ့ metric တွေကို သင်ပါတယ်။ recall@k၊ precision@k၊ MRR (Mean Reciprocal Rank — မှန်တဲ့ ရလဒ်ရဲ့ rank ပျမ်းမျှ) နဲ့ nDCG (Normalized Discounted Cumulative Gain — rank အလိုက် အလေးချိန် ပေးတဲ့ metric) တွေကို formula နဲ့ တွက်ပြပါတယ်။ Chunk-level နဲ့ document-level အကဲဖြတ်မှု၊ LLM judge ကို offline/deterministic stand-in နဲ့ စမ်းနည်း ပါပါတယ်။

ဒီ module ပြီးရင် လုပ်နိုင်ရမည့်အရာ — Golden set တစ်ခု ဖွဲ့ပြီး၊ recall@k နဲ့ nDCG ကို ကိုယ်တိုင်တွက်နိုင်ရမယ်။ Regression gate (အရည်အသွေး ကျမသွားအောင် တားတဲ့ စစ်ဆေးချက်) တစ်ခု သတ်မှတ်နိုင်ရမယ်။

- Recall@k က precision@k ထက် ဘယ်အချိန် ပိုအရေးကြီးလဲ။
- MRR က rank ၁ မှာ မှန်တာနဲ့ rank ၅ မှာ မှန်တာကို ဘယ်လို ကွာပြလဲ။
- Golden set ကို သေးငယ်ရင် evaluation ရလဒ် ဘယ်လို ယုံလို့ မရလဲ။

## M11 — `11_scale_performance/` — Scale နှင့် Performance

Quantization (ကိန်းဂဏန်းကို ကုန်ခန့်အောင် ချုံ့ခြင်း) အခြေခံကို သင်ပါတယ် — scalar/binary quantization နဲ့ product quantization (PQ)။ Memory နဲ့ recall ရဲ့ အပေးအယူ၊ dimension ဖြတ်ခြင်း၊ sharding/partitioning မဟာဗျူဟာ၊ index rebuild နှင့် write throughput တွေ ပါပါတယ်။ Memory တွက်ချက်မှုတွေကို ယူဆချက် သတ်မှတ်ပြီး formula နဲ့ ပြပါမယ်။

ဒီ module ပြီးရင် လုပ်နိုင်ရမည့်အရာ — Quantization option တစ်ခုစီအတွက် memory ခန့်မှန်းချက် တွက်နိုင်ရမယ်။ ကိုယ့် dataset အတွက် သင့်တော်တဲ့ sharding မဟာဗျူဟာ ရွေးနိုင်ရမယ်။

- fp32 ကနေ int8 ချုံ့ရင် memory က ဘယ်လောက် လျှော့လဲ — တွက်ပြပါ။
- Binary quantization က recall ကို ဘယ်လို သက်ရောက်လဲ။
- Sharding က query latency ကို အခါခပ်သိမ်း လျှော့ပေးလား၊ ရှင်းပြပါ။

## M12 — `12_governance_security/` — Governance နှင့် လုံခြုံရေး

Embedding ထဲ ကျန်နေနိုင်တဲ့ PII (Personally Identifiable Information — ပုဂ္ဂလိက မှတ်ချက်များ) အန္တရာယ်ကို သင်ပါတယ်။ Row-level security နဲ့ document-level ACL ကို retrieval query ထဲ ထည့်ခြင်း၊ multi-tenant isolation (တစ်ဆိုင်တည်းသုံး party ခွဲခြားခြင်း) နည်းလမ်းများ၊ audit log နှင့် access control စစ်ဆေးမှု တွေ ပါပါတယ်။

ဒီ module ပြီးရင် လုပ်နိုင်ရမည့်အရာ — ACL ပါတဲ့ retrieval query တစ်ခု ဒီဇိုင်းနိုင်ရမယ်။ Tenant တစ်ခုစီရဲ့ data ကို ခွဲထားနည်း ၃ မျိုး နှိုင်းယှဉ်နိုင်ရမယ်။

- Embedding ထဲ PII ကျနေရင် ဘာဆိုးကျိုး ဖြစ်နိုင်လဲ။
- Row-level security က application-level check ထက် ဘာကြောင့် ပိုယုံကြည်ရလဲ။
- Multi-tenant index တစ်ခုတည်မှာ filter နဲ့ ခွဲတာက ဘာအန္တရာယ် ရှိလဲ။

## M13 — `13_capstone/` — Capstone: End-to-end ဒီဇိုင်းနှင့် တွက်စက်

Ingest → chunk → embed → index → retrieve → rerank → evaluate အဆင့်တွေကို တစ်ခုတည်း ဒီဇိုင်းအဖြစ် စုစည်းပါတယ်။ Storage တွက်ချက်မှု (chunk အရေအတွက် × dimension × bytes)၊ HNSW index memory ခန့်မှန်းချက်၊ QPS (Queries Per Second — စက္ကန့်အလိုက် query အရေအတွက်) ခန့်မှန်းချက်တွေကို ယူဆချက် သတ်မှတ်ပြီး formula အပြည့်အစုံနဲ့ တွက်ပြပါတယ်။ အားလုံးက offline၊ deterministic ဖြစ်ရမယ်။

ဒီ module ပြီးရင် လုပ်နိုင်ရမည့်အရာ — ကိုယ့် organization အတွက် RAG retrieval stack တစ်ခုလုံးရဲ့ ဒီဇိုင်းစာတမ်းနဲ့ ကုန်ကျစရိတ် တွက်ချက်မှု ရေးနိုင်ရမယ်။

- Chunk 10 million၊ dimension 768၊ fp32 ဆိုရင် vector storage က ဘယ်လောက် ယူလဲ။
- Cache hit ratio ကို QPS တွက်ချက်မှုထဲ ဘယ်လို ထည့်သွင်းမလဲ။
- Capstone ဒီဇိုင်းမှာ ဘယ်ဆုံးဖြတ်ချက်တွေက ယူဆချက်အပေါ် မူတည်လဲ။

## ၆ ပတ် လေ့လာမှု အစီအစဉ်

- **ပတ် ၁** — M0 မှ M2 : data pipeline အခြေခံ၊ ingestion နဲ့ chunking တွေ လက်တွေ့လုပ်ပါ။ ရင်းမြစ် data ကိုယ်တိုင် ရွေးပြီး စတင်ပါ။
- **ပတ် ၂** — M3 နှင့် M4 : embedding တွက်ချက်မှု၊ distance metric နဲ့ HNSW graph search lab တွေ လုပ်ပါ။ LoRA (Low-Rank Adaptation — ကြီးတဲ့ မော်ဒယ်ကို ကျဉ်းကျဉ်း parameter နဲ့ လေ့ကျင့်တဲ့နည်း) နှင့် QLoRA (quantized base model ပေါ်မှာ LoRA လုပ်တဲ့နည်း) အယူအဆတွေကို တရားဝင် documentation နဲ့ ဖတ်ပြီး embedding model fine-tune အတွက် အသိအမြင် စုဆောင်းပါ။
- **ပတ် ၃** — M5 မှ M7 : pgvector schema၊ hybrid search၊ reranking တွေကို ပေါင်းပြီး စမ်းပါ။ Supervised fine-tuning (မှန်တဲ့ အဖြေနဲ့ လေ့ကျင့်ခြင်း) နှင့် preference optimisation (ကြိုက်/မကြိုက် နှိုင်းယှဉ်ချက်နဲ့ လေ့ကျင့်ခြင်း) ဆိုင်ရာ အယူအဆတွေကို တရားဝင် စာပိုင်းတွေနဲ့ ဖတ်ပါ။
- **ပတ် ၄** — M10 : retrieval evaluation ကို အရင်စာလုပ်ပြီး ကိုယ့် pipeline ရဲ့ golden set ဖွဲ့ပါ။ Metric တွေ ကိုယ်တိုင် တွက်ပါ။
- **ပတ် ၅** — M8 နှင့် M11 : serving architecture၊ quantization နဲ့ sharding တွေကို လေ့လာပါ။ Memory တွက်ချက်မှု lab တွေ လုပ်ပါ။
- **ပတ် ၆** — M9 နှင့် M12 မှ M13 : orchestration၊ governance နဲ့ capstone ဒီဇိုင်းကို အပြီးသတ်ပါ။

မှတ်ချက် — ဒီ course ရဲ့ lab တွေ အားလုံးက Python standard library နဲ့ပဲ လုပ်ရမှာပါ။ Database နဲ့ တကယ် မချိတ်ပါဘူး။ Quantization၊ LoRA/QLoRA၊ fine-tuning စတဲ့ ကိုယ်တိုင်လုပ်ရမှာတွေကို lab အနေနဲ့ မထည့်ပါ — တရားဝင် documentation ညွှန်းပြီး နားလည်စေတဲ့ နေရာကနေ စစ်ဆေးပါတယ်။

## လက်တွေ့ စီမံကိန်း အတွက် အကြံပြုချက်

- ကိုယ့်အလုပ် (သို့) စိတ်ဝင်စားတဲ့ နယ်ပယ်က စာရွက် ၁၀၀ ကနေ ၅၀၀ ကို ရင်းမြစ် အဖြစ် ရွေးပါ။
- တစ် module စီမှာ checkpoint မေးခွန်းတွေကို စာရွက်ပေါ် ဖြေပြီး သိမ်းထားပါ။
- M10 ရောက်တဲ့အခါ ကိုယ့် corpus အတွက် golden set အနည်းဆုံး query ၃၀ ဖွဲ့ပါ။
- အားလုံးကို git repo တစ်ခုထဲ သိမ်းပြီး တစ်ပတ်ကို တစ်ခါ commit လုပ်ပါ။
- Capstone ဒီဇိုင်းစာတမ်းကို ကိုယ့်အဖွဲ့နဲ့ မျှဝေပြီး တခြားသူတွေရဲ့ ဆန်းစစ်မှု ခံယူပါ။

## Capstone

Capstone မှာ ကိုယ်ရွေးချယ်တဲ့ corpus တစ်ခုအတွက် စုံစုံလင်းလင်း RAG retrieval stack တစ်ခု ဒီဇိုင်းရမယ်ပါတယ်။ ပါရမည် အချက်တွေက — ingestion plan၊ chunking strategy နဲ့ အကြောင်းပြချက်၊ embedding model ရွေးချယ်မှုနှင့် dimension၊ index အမျိုးအစားနှင့် parameter၊ hybrid search နှင့် reranking ဆုံးဖြတ်ချက်၊ evaluation စီမံချက် (golden set နှင့် metric)၊ storage/QPS/ကုန်ကျစရိတ် တွက်ချက်မှု၊ နှင့် governance (ACL၊ retention၊ PII) အစီအစဉ်တို့ ဖြစ်ပါတယ်။

တင်ပြချက်မှာ ကိန်းဂဏန်းတိုင်းအတွက် formula ဒါမှမဟုတ် official doc ကို ညွှန်ပြရပါမယ်။ ဒီဇိုင်းကို အဖွဲ့နဲ့ ဆန်းစစ်ပြီး အားနည်းချက်ကို မှတ်တမ်းတင်ထားရင် လေးစားခံရတဲ့ အလုပ်တစ်ခု ဖြစ်ပါတယ်။
