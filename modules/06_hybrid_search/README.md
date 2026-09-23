# M6 — Hybrid Search: Full-text၊ Trigram နှင့် RRF ပေါင်းစပ်ခြင်း

Vector search နဲ့ keyword search နှစ်ခုကို RRF နည်းနဲ့ ပေါင်းစပ်တဲ့ hybrid search အကြောင်း သင်ပါတယ်။

## ဒီ module မှာ ဘာသင်မလဲ

- PostgreSQL full-text search ရဲ့ အခြေခံကို သင်မယ် — `tsvector` (စကားလုံးတွေကို index လုပ်ထားတဲ့ format) နဲ့ `tsquery` (ရှာမယ့် စကားလုံး pattern) ပါ။
- Ranking ဘယ်လို အလုပ်လုပ်လဲ ဆိုတာကို `ts_rank` နဲ့ လက်တွေ့ ကြည့်ပါမယ်။
- Trigram similarity (စကားလုံးသုံးလုံးစီ ခွဲပြီး တူညီမှု တွက်တဲ့နည်း) နဲ့ typo ခံနိုင်တဲ့ ရှာဖွေမှုကို လေ့လာပါမယ်။
- Vector score နဲ့ keyword score ကို ပေါင်းတဲ့ နည်းနှစ်မျိုး ခွဲကြည့်ပါမယ် — weighted sum (အလေးချိန် ပေးပေါင်းခြင်း) နဲ့ RRF (Reciprocal Rank Fusion) ပါ။
- Score normalization (အမှတ်တွေကို တူညီတဲ့ scale ပြောင်းခြင်း) ဘာကြောင့် အရေးကြီးလဲ ဆိုတာကို နမူနာနဲ့ ပြပါမယ်။
- ရှာတဲ့ query တစ်ခုကို vector လမ်းနဲ့ keyword လမ်း နှစ်ခုလုံး ဖြန့်ပေးပုံကို သင်မယ်။
- RRF formula နဲ့ parameter k ရဲ့ သင်္ချာကို Python standard library နဲ့ တွက်ပြပါမယ်။

## သင်ခန်းစာများ

- **L1 — Full-Text Search အခြေခံ**: `to_tsvector`၊ `to_tsquery`၊ `plainto_tsquery` တွေရဲ့ ကွာခြားချက်။
- **L2 — Ranking နဲ့ GIN/GiST Index**: `ts_rank` အလုပ်လုပ်ပုံ၊ `tsvector` index မျိုးကွဲများ။
- **L3 — Trigram Similarity**: `similarity()` နဲ့ fuzzy matching (စာလုံးမှားယွင်းမှုကို ခံနိုင်တဲ့ ရှာဖွေမှု)။
- **L4 — Weighted Sum နဲ့ ပေါင်းခြင်း**: cosine score နဲ့ BM25-style score ကို အလေးချိန် ပေးပေါင်းပုံ။
- **L5 — Score Normalization ပြဿနာ**: scale မတူတဲ့ score တွေက ဘယ်လို ရလဒ် ပျက်စေလဲ။
- **L6 — Reciprocal Rank Fusion (RRF)**: rank-based fusion ရဲ့ သင်္ချာ၊ parameter k ရဲ့ သက်ရောက်မှု။
- **L7 — Hybrid Pipeline တစ်ခုလုံး**: query ကို နှစ်လမ်းဖြန့်ပြီး RRF နဲ့ ပေါင်းတဲ့ အဆင့်ဆင့် နမူနာ။

## လိုအပ်ချက်များ (Prerequisites)

- M1 (vector space basics) နဲ့ M2 (cosine similarity) သင်ခန်းစာတွေ ဖတ်ပြီးဖြစ်ရမယ်။
- M3 (HNSW-style graph search) က အိုင်ဒီယာ နားလည်ထားရမယ်။
- Python 3 ရှိရုံပါတယ် — external library ဘာမှ မလိုပါဘူး။
- PostgreSQL pgvector SQL တွေကို ဖတ်ရုံပါ — ဒီ module က SQL ကို run မခိုင်းပါဘူး။

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- Chunk တွေမှာ ရှာတဲ့ စကားလုံးအတိအကျ ပါလာရင် vector တစ်ခုတည်းနဲ့ မိသလို ခံစားရတဲ့ အခါ။
- အမည်တွေ၊ SKU တွေ၊ technical term တွေကို ရှာဖွေရာမှာ keyword matching က ပိုတိကျလို့။
- RAG pipeline မှာ retrieval quality (ရှာဖွေတဲ့ အရည်အသွေး) ကို မြှင့်တင်ချင်တဲ့ အခါ။
- Elasticsearch ဒါမှမဟုတ် OpenSearch ရဲ့ hybrid search feature တွေနဲ့ ချိတ်ဆက်တွေးချင်တဲ့ အခါ။

## ကိုးကား

ဒီ module က အောက်ပါ official documentation တွေကနေ ရေးထားတဲ့ မူရင်း လေ့လာသင်ယူမှု material ပါ — တခြား commercial course တစ်ခုခုရဲ့ သင်ခန်းစာကို ကူးယူ ပြန်ရေးထားတာ မဟုတ်ပါဘူး။

- PostgreSQL Text Search Controls: https://www.postgresql.org/docs/current/textsearch-controls.html
- PostgreSQL Text Search Indexes: https://www.postgresql.org/docs/current/textsearch-indexes.html
- Elasticsearch Reciprocal Rank Fusion: https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion
- OpenSearch Vector Search: https://opensearch.org/docs/latest/vector-search/
