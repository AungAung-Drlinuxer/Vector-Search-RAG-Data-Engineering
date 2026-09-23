# Vector Search & RAG Data Engineering

Vector Search နဲ့ RAG (Retrieval-Augmented Generation — ရှာဖွေမှုနဲ့ ဖြည့်စွက်ပြီး စာတန်းထိုးတဲ့ မော်ဒယ်) Data Engineering အတွက် ကိုယ့်ဘာသာ လေ့လာနိုင်တဲ့ course ပါ။

## လွတ်လပ်မှု (Independence)

ဒီ course က original သင်ခန်းစာ ပါ။ အခြေခံကတော့ တစ်ခုချင်းရဲ့ module scope မှာ ဖော်ပြထားတဲ့ တရားဝင် open documentation တွေ သာ ဖြစ်ပါတယ်။ Vendor ရဲ့ တရားဝင် training ကို ကူးယူထားတာ မဟုတ်ပါ။ ပွဲအခကြေးငွေပေးရတဲ့ commercial course တစ်ခုကို ပြန်ရေးထားတာလည်း မဟုတ်ပါ။ နမူနာ code တွေက တရားဝင် doc ထဲက mechanics တွေကို standard-library Python နဲ့ ကိုယ်တိုင် ပြန်ဆောက်ထားတာ ဖြစ်ပါတယ်။

## ဒီ course မှာ ဘာသင်မလဲ

RAG system တစ်ခုကို data engineer အနေနဲ့ တည်ဆောက်ဖို့ လိုအပ်တာတွေကို အာရုံစိုက်ပါတယ်။ Text ဆွဲထုတ်တာ၊ chunk ဖြတ်တာ၊ embedding ဖန်တီးတာ၊ HNSW index အတွင်းပိုင်း၊ hybrid search၊ reranking၊ pipeline orchestration၊ evaluation နဲ့ governance အထိ ဖြန့်ကျက် သင်ကြားပါတယ်။ Code တွေက network မသုံးပါ။ Database လည်း ချိတ်မထားပါ။ Retrieval mechanics တွေကို pure Python နဲ့ ပြန်ဆောက်ပြပါတယ်။ တကယ့် system ကိုတော့ prose နဲ့ ရှင်းပြပြီး တရားဝင် link ပေးထားပါတယ်။

## RAG Pipeline အဆင့်များ

၁။ ingest — ရင်းမြစ်ကနေ ဒေတာ ဆွဲယူခြင်း — M1
၂။ chunk — စာကြောင်းကို အပိုင်းလိုက် ဖြတ်ခြင်း — M2
၃။ embed — အပိုင်းတစ်ခုစီကို vector အဖြစ် ပြောင်းခြင်း — M3
၄။ index — vector တွေကို မြန်မြန် ရှာနိုင်အောင် စီစဉ်ခြင်း — M4, M5
၅။ retrieve — query နဲ့ ဆီးစပ်တဲ့ အပိုင်းတွေ ရှာခြင်း — M5, M6
၆။ rerank — ရှာမိတဲ့ အပိုင်းတွေကို ပြန်စီခြင်း — M7
၇။ generate — ရှာမိတဲ့ အပိုင်းတွေနဲ့ အဖြေ ဖန်တီးခြင်း — M0, M8
၈။ evaluate — ရှာဖွေမှု အရည်အသွေး တိုင်းခြင်း — M10

## Modules

- `00_orientation/` — M0 — RAG architecture မြေပုံ၊ pipeline အဆင့် ၈ ခု၊ search အမျိုးအစား ရွေးချယ်ပုံ
- `01_ingestion/` — M1 — Corpus ingestion၊ text extraction၊ normalisation၊ upsert/delete
- `02_chunking/` — M2 — Chunking မဟာဗျူဟာ၊ metadata ဒီဇိုင်း
- `03_embeddings/` — M3 — Embedding model ရွေးချယ်မှု၊ dimension၊ distance metric၊ caching
- `04_hnsw/` — M4 — HNSW index အတွင်းပိုင်း၊ parameter၊ recall၊ memory
- `05_pgvector/` — M5 — PostgreSQL + pgvector schema၊ operator၊ index၊ tuning
- `06_hybrid_search/` — M6 — Full-text၊ trigram နဲ့ RRF ပေါင်းစပ်ခြင်း
- `07_reranking/` — M7 — Cross-encoder၊ HyDE၊ multi-query၊ MMR
- `08_serving_architecture/` — M8 — Retrieval API၊ cache၊ pgvector vs vector DB
- `09_pipelines_orchestration/` — M9 — Batch/streaming ingestion၊ backfill၊ migration
- `10_retrieval_evaluation/` — M10 — recall@k၊ MRR၊ nDCG၊ golden set၊ regression gate
- `11_scale_performance/` — M11 — Quantization၊ sharding၊ rebuild၊ write throughput
- `12_governance_security/` — M12 — PII၊ ACL၊ multi-tenancy၊ audit
- `13_capstone/` — M13 — End-to-end ဒီဇိုင်း၊ storage/memory/QPS တွက်စက်

## ဒီ course ရဲ့ ဒေတာဘေ့စ် ဦးတည်ချက်

SQL နမူနာတွေက PostgreSQL မှာ pgvector extension ထည့်သုံးတဲ့ stack ကို ဦးတည်ပါတယ်။ SQL ကို course က တကယ် run မှာ မဟုတ်ပါ။ Reader ကိုယ်တိုင် စမ်းသုံးဖို့အတွက် ပြသထားတာပါ။ Lab တွေအားလုံးက database မချိတ်ဘဲ standard-library Python နဲ့သာ လည်ပတ်ပါတယ်။ Cosine similarity၊ HNSW-style graph search၊ RRF၊ recall@k တို့ကို ကိုယ်တိုင် ပြန်ဆောက်ပြပါတယ်။ ဒီ mechanics တွေက Qdrant၊ Milvus၊ Weaviate လို dedicated vector store တွေရဲ့ အလုပ်လုပ်ပုံနဲ့လည်း တိုက်ရိုက် ဆက်စပ်ပါတယ်။

## Folder ဖွဲ့စည်းပုံ

Module တစ်ခုစီမှာ file လေးခု ပါဝင်ပါတယ် —

- `README.md` — module scope နဲ့ လေ့လာရမယ့် အချက်များ
- `explanation.md` — သဘောတရား ရှင်းပြချက်၊ code နဲ့ တွက်ချက်မှုများ
- `exercise.md` — ကိုယ်တိုင် လုပ်ရမယ့် လက်တွေ့ ပျိုးထုတ်ချက်
- `solution.md` — အဖြေနဲ့ ရှင်းလင်းချက်

## လေ့လာပုံ နည်းလမ်း

Module တွေကို အစီအစဉ်အတိုင်း တစ်ခုပြီးတစ်ခု လေ့လာပါ။ တစ် module အတွက် — ၁။ `README.md` ဖတ်ပါ။ ၂။ `explanation.md` ကနေ သဘောတရား နားလည်ပါ။ ၃။ `exercise.md` ကို ကိုယ်တိုင် အရင် လုပ်ကြည့်ပါ။ ၄။ မရှင်းရင် `solution.md` နဲ့ နှိုင်းယှဉ်ပါ။ Code တွေကို ကူး၍ run ကြည့်ပြီး ရလဒ်တွေ ပြောင်းလဲကြည့်ပါ။ စာအုပ်ထဲက number တွေကို ကိုယ်ပိုင် တွက်ချက်ပြီး စစ်ကြည့်ပါ။

## လိုအပ်ချက်များ (Prerequisites)

ဒီ course က လုံးဝ အစပြုသူအတွက် မဟုတ်ပါ။ လိုအပ်တာတွေက —

- Python အခြေခံ — dict၊ list comprehension၊ function
- SQL / PostgreSQL အခြေခံ — SELECT၊ JOIN၊ index သဘောတရား
- RAG / LLM အကြောင်း အခြေခံ နားလည်မှု

## ကိုးကား

တစ်ခုချင်းရဲ့ module scope ထဲမှာ ကိုးကားစာအုပ်တွေ အသေးစိတ် ဖော်ပြထားပါတယ်။ အဓိက တရားဝင် open documentation တွေကတော့ —

- pgvector — https://github.com/pgvector/pgvector
- PostgreSQL — https://www.postgresql.org/docs/
- Qdrant — https://qdrant.tech/documentation/
- Milvus — https://github.com/milvus-io/milvus
- Weaviate — https://weaviate.io/developers/weaviate
- Chroma — https://docs.trychroma.com/
- HNSW paper (Malkov & Yashunin, arXiv:1601.06867) — https://arxiv.org/abs/1601.06867

## သတိပြုရန်

ဒီ course ထဲက number တွေအားလုံးက ၂ မျိုးထဲမှ တစ်မျိုး ဖြစ်ပါတယ် — (က) သင်ခန်းစာထဲက ဖော်ပြထားတဲ့ formula နဲ့ တွက်ထုတ်ထားတာ၊ (ခ) module scope ထဲက နာမည်တပ်ထားတဲ့ တရားဝင် documentation ကနေ ကောက်နုတ်ထားတာပါ။ Recall value၊ latency၊ QPS၊ memory size တို့ကို မတင်းကား ဖန်တီးထားခြင်း မရှိပါ။ Index ရဲ့ recall နဲ့ behaviour က corpus အရွယ်အစား၊ parameter တန်ဖိုးတွေနဲ့ engine version အပေါ် မူတည်ပါတယ်။ ဒါကြောင့် ကိုယ်ပိုင်ဒေတာပေါ်မှာ ကိုယ်တိုင် တိုင်းတာဖို့ လိုပါတယ်။ LLM call တွေက runtime မှာ တကယ် မဖြစ်ပါ — scripted deterministic stand-in သာ သုံးထားပါတယ်။

## ဒီ course ကို ဘယ်လို သုံးမလဲ

- အစဉ်လိုက် ဖတ်ပါ — M1–M3 (data ဘက်) ကို အရင်၊ ပြီးမှ M4–M5 (index)၊ နောက် M6–M8 (retrieval အရည်အသွေး) ဆက်ပါ။
- Module တိုင်းရဲ့ lab ကို ကိုယ်တိုင် run ပြီး result ကို စာရွက်ပေါ် ချရေးပါ — pipeline အဆင့်တိုင်းရဲ့ ဂဏန်းကို မြင်အောင် လုပ်ပါ။
- Database မလိုပါ — lab အားလုံး standard library နဲ့သာ run ပါတယ်။ SQL နမူနာများကို ကိုယ့် Postgres မှာ စမ်းချင်ရင် သီးသန့် စမ်းပါ။
- M10 (evaluation) ရောက်တဲ့အခါ ကိုယ့် corpus အတွက် golden set လေး (query ၂၀–၅၀ ခု) ကို ရေးထားရင် နောက်ဆုံး module များ အလွန် အကျိုးရှိပါတယ်။

## ဘယ်လို မေးခွန်းတွေကို ဖြေပေးလဲ

- ကိုယ့် corpus အတွက် chunk အရွယ် ဘယ်လောက် ထားရမလဲ။
- Embedding model တစ်ခုကနေ တစ်ခု ပြောင်းရင် index ကို ဘယ်လို migrate လုပ်မလဲ။
- HNSW ရဲ့ `m`၊ `ef_construction`၊ `ef_search` ကို ဘယ်လို ရွေးမလဲ။
- Vector search နဲ့ keyword search ကို ဘယ်လို ပေါင်းမလဲ (RRF ရဲ့ သင်္ချာ အပါ)။
- Storage၊ index memory နဲ့ QPS ကို ဘယ်လို ကြိုတွက်မလဲ။
- Permission (ACL) ကို retrieval query ထဲ ဘယ်လို ထည့်မလဲ။

## လုပ်ငန်းသုံး စစ်ဆေးစာရင်း

- Chunk တိုင်းမှာ source၊ section၊ page၊ permission metadata ပါပါသလား။
- Ingestion ကို ပြန် run လုပ်ရင် duplicate မဖြစ်အောင် idempotent ဖြစ်ပါသလား။
- Eval set နဲ့ recall@k ကို CI gate အဖြစ် ထားပြီးပါသလား။
- PII ကို embedding မတွက်ခင် စစ်ပြီးပါသလား။
- Embedding model version ကို index၊ cache နဲ့ metadata မှာ မှတ်ထားပါသလား။

## ဒီ course နဲ့ ကိုက်ညီတဲ့ တာဝန်

- Retrieval/pipeline engineer — ingestion၊ chunking၊ index ကို ပိုင်ပြီး အရည်အသွေးကို တိုင်းတာသူ။
- AI application engineer — retrieval API ကို ဒီဇိုင်းပြီး generation အလွှာနဲ့ တွဲသူ။
- Data platform engineer — vector store ၏ storage၊ backup၊ tenancy၊ governance ကို စီမံသူ။
