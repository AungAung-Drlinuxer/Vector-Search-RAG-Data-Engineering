# M6 — Hybrid Search: Full-text၊ Trigram နှင့် RRF ပေါင်းစပ်ခြင်း

Vector search နှင့် keyword search တို့ကို RRF ဖြင့် ပေါင်းစပ်သော hybrid search အကြောင်း လေ့လာသည်။

## ဒီ module မှာ ဘာသင်မလဲ

- PostgreSQL full-text search အခြေခံ — `tsvector` (lexeme index format) နှင့် `tsquery` (query representation)။
- `ts_rank` ranking mechanism ကို လက်တွေ့လေ့လာခြင်း။
- **BM25** (Elasticsearch/OpenSearch ၏ default ranking) ပုံသေနည်း — tf saturation (`k1`) နှင့် length normalization (`b`) ကို လက်ဖြင့် တွက်ချက်ခြင်း။
- Trigram similarity ဖြင့် typo-tolerant search လုပ်ဆောင်ပုံ။
- Vector score နှင့် keyword score ပေါင်းစပ်နည်း နှစ်မျိုး — weighted sum နှင့် RRF (Reciprocal Rank Fusion)။
- Score normalization မရှိပါက fusion ရလဒ် ပျက်စီးပုံကို နမူနာဖြင့် ပြသခြင်း။
- Query တစ်ခုကို vector lane နှင့် keyword lane နှစ်လမ်းသို့ fan-out လုပ်ပုံ။
- RRF formula နှင့် parameter k ၏ သင်္ချာကို Python standard library ဖြင့် တွက်ချက်ပြသခြင်း။

## သင်ခန်းစာများ

- **L1 — Full-Text Search အခြေခံ**: `to_tsvector`၊ `to_tsquery`၊ `plainto_tsquery` တို့၏ ကွာခြားချက်။
- **L2 — Ranking နှင့် GIN/GiST Index**: `ts_rank` လုပ်ဆောင်ပုံ၊ `tsvector` index မျိုးကွဲများ။
- **L3 — Trigram Similarity**: `similarity()` နှင့် fuzzy matching။
- **L4 — BM25 Ranking**: ပုံသေနည်း၊ parameter `k1`/`b`၊ tf-idf နှင့် နှိုင်းယှဉ်ချက်။
- **L5 — Weighted Sum နှင့် ပေါင်းခြင်း**: cosine score နှင့် BM25-style score ကို အလေးချိန်ပေး၍ ပေါင်းပုံ။
- **L6 — Score Normalization ပြဿနာ**: scale မတူသော score များက ranking ရလဒ်ကို ပျက်စီးစေပုံ။
- **L7 — Reciprocal Rank Fusion (RRF)**: rank-based fusion ၏ သင်္ချာ၊ parameter k ၏ သက်ရောက်မှု။
- **L8 — Hybrid Pipeline တစ်ခုလုံး**: query ကို နှစ်လမ်း fan-out ပြီး RRF ဖြင့် fuse လုပ်သော အဆင့်ဆင့် နမူနာ။

## လိုအပ်ချက်များ (Prerequisites)

- M1 (vector space basics) နှင့် M2 (cosine similarity) သင်ခန်းစာများ ဖတ်ရှုပြီးဖြစ်ရမည်။
- M3 (HNSW-style graph search) ၏ သဘောတရားကို နားလည်ထားရမည်။
- Python 3 လုံလောက်သည် — external library မလိုအပ်ပါ။
- PostgreSQL pgvector SQL များကို ဖတ်ရှုရုံသာဖြစ်ပြီး ဒီ module က SQL execute မလုပ်ပါ။

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- Query term များ chunk အတွင်း အတိအကျပါရှိသော်လည်း dense vector search တစ်ခုတည်းက လွဲချော်နေသည့်အခါ။
- အမည်များ၊ SKU များ၊ technical term များ ရှာဖွေရာတွင် keyword matching ပိုတိကျသည့်အခါ။
- RAG pipeline ၏ retrieval quality ကို မြှင့်တင်လိုသည့်အခါ။
- Elasticsearch သို့မဟုတ် OpenSearch ၏ hybrid search feature များနှင့် ချိတ်ဆက် အကဲဖြတ်လိုသည့်အခါ။

## ကိုးကား

ဒီ module သည် အောက်ပါ official documentation များမှ ရေးသားထားသော မူရင်းလေ့လာမှု material ဖြစ်ပြီး commercial course တစ်ခုခု၏ သင်ခန်းစာကို ကူးယူပြန်ရေးထားခြင်း မဟုတ်ပါ။

- PostgreSQL Text Search Controls: https://www.postgresql.org/docs/current/textsearch-controls.html
- PostgreSQL Text Search Indexes: https://www.postgresql.org/docs/current/textsearch-indexes.html
- Elasticsearch Reciprocal Rank Fusion: https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion
- OpenSearch Vector Search: https://opensearch.org/docs/latest/vector-search/
