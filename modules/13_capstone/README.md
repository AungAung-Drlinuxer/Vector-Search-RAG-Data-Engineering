# M13 — Capstone: End-to-end ဒီဇိုင်းနှင့် Storage/Memory/QPS တွက်စက်

Ingest ကနေ evaluate အထိ တစ်ခုတည်း pipeline ဒီဇိုင်းကို စုစည်းပြီး storage, memory နှင့် QPS တွေကို Python နဲ့ တွက်သင်ရမယ့် module ပါတယ်။

## ဒီ module မှာ ဘာသင်မလဲ

- Ingest → chunk → embed → index → retrieve → rerank → evaluate ကြားထဲက ဆက်စပ်မှုကို တစ်ပုံတည်း မြင်ရမယ်
- Storage တွက်ချက်မှု — chunk အရေအတွက် × dimension × bytes ဖော်မျူလာနဲ့ တွက်နည်း
- HNSW index (Malkov & Yashunin, 2016 စာတမ်းအရ graph-based ရှာဖွေမှု) memory ခန့်မှန်းချက်
- QPS (Query Per Second — စက္ကန့်အလိုက် query အရေအတွက်) နှင့် p95 latency (request ၉၅% ရောက်တဲ့ အချိန်)
- Chunking နှင့် embedding ရွေးချယ်မှုက query ရလဒ်အပေါ် ဘယ်လိုသက်ရောက်လဲ
- Offline, deterministic တွက်စက် script တစ်ခု ရေးတာ

## သင်ခန်းစာများ

- M13.1 — Pipeline တစ်ခုလုံးရဲ့ ပုံပန်းနဲ့ အဆင့်ဆင့် အလုပ်လုပ်ပုံ
- M13.2 — Storage တွက်စက် (chunk အရေအတွက် × dimension × bytes)
- M13.3 — HNSW index memory ခန့်မှန်းချက်
- M13.4 — QPS နှင့် p95 latency ခန့်မှန်းချက်
- M13.5 — Chunking/embedding ရွေးချယ်မှုအကျိုးသက်ရောက်မှု
- M13.6 — Capstone project — deterministic တွက်စက် script

## လိုအပ်ချက်များ (Prerequisites)

- M01 ကနေ M12 အထိ သင်ခန်းစာတွေ သင်ယူထားဖို့
- Python standard library အခြေခံ ကောင်းကောင်းသိထားဖို့
- Cosine similarity, HNSW graph, RRF, recall@k တို့ရဲ့ အယူအဆ နားလည်ထားဖို့
- PostgreSQL + pgvector အကြောင်း အခြေခံ ဖတ်ဖူးဖို့

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- Production မှာ deploy မလုပ်ခင် hardware အရွယ်အစား ခန့်မှန်းချင်တဲ့အခါ
- Pipeline design doc ရေးပြီး ကုန်ကျစရိတ် ခန့်မှန်းချင်တဲ့အခါ
- Chunk size နဲ့ embedding model ပြောင်းကြည့်ချင်တဲ့အခါ
- သင်ယူထားတဲ့ အချက်တွေကို တစ်နေရာတည်း ပြန်စုစည်းချင်တဲ့အခါ

## ကိုးကား

- pgvector — https://github.com/pgvector/pgvector
- HNSW paper — https://arxiv.org/abs/1603.09320
- Ragas evaluation framework docs — https://docs.ragas.io/

> ဒီ course က official open documentation တွေကနေ ကိုယ်တိုင်ရေးထားတဲ့ original လေ့လာရေး material ပါ။ Commercial course တွေရဲ့ သင်ခန်းစာတွေကို မကူးယူရေးထားပါဘူး။
