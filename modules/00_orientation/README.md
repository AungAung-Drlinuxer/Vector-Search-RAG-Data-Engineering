# M0 — RAG Data Engineering ရဲ့ မြေပုံ

ဒီ module က RAG (Retrieval-Augmented Generation) pipeline ရဲ့ အဆင့် ၈ ခုကို ခြေဆန့်ပြီး သင်ကြားပေးပါတယ်။

## ဒီ module မှာ ဘာသင်မလဲ

- RAG ဆိုတာ ဘာလဲ၊ ဘာကြောင့် လိုအပ်လဲ ဆိုတာကို အရင် နားလည်ပါမယ်။
- Pipeline အဆင့် ၈ ခု — ingest (data ယူတဲ့ အဆင့်) ကနေ evaluate (အရည်အသွေး တိုင်းတာတဲ့ အဆင့်) အထိ။
- Vector search, keyword search, hybrid search တို့ကို ဘယ်အချိန် ရွေးရမလဲ။
- Latency (စောင့်ရတဲ့ အချိန်) နဲ့ ကုန်ကျစရိတ် အတိုင်းအတာများ။
- Data engineer တာဝန်နဲ့ model engineer တာဝန် ခွဲခြားနည်း။

## သင်ခန်းစာများ

| သင်ခန်းစာ | အကြောင်းအရာ |
|---|---|
| M0.1 | RAG ဆိုတာ ဘာလဲ — ဘာကြောင့် လိုအပ်လဲ |
| M0.2 | Pipeline အဆင့် ၈ ခု အကုန်လိုက် လမ်းညွှန် |
| M0.3 | Chunking — data ကို အပိုင်းကြီး ခွဲနည်း |
| M0.4 | Embedding နဲ့ indexing အခြေခံ |
| M0.5 | Vector, keyword, hybrid — ဘယ်အချိန် ဘယ်ဟာလဲ |
| M0.6 | Latency နဲ့ ကုန်ကျစရိတ် စဉ်းစားနည်း |
| M0.7 | Data engineering တာဝန် နဲ့ model တာဝန် နယ်နိမိတ် |

## လိုအပ်ချက်များ (Prerequisites)

- Python အခြေခံ — function ရေးတတ်ရင် လုံလောက်ပါတယ်။
- List, dict, loop သုံးနိုင်ရမယ်။
- SQL အခြေခံ (PostgreSQL) က အထောက်အကူ ရှိပေမယ့် မဖြစ်မနေ မလိုပါဘူး။
- ဒီ course က offline standard-library Python ပဲ သုံးပါတယ်။ ဒေတာဘေ့စ် မချိတ်ပါဘူးနော်။

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- ကုမ္ပဏီရဲ့ document တွေကို LLM နဲ့ ဖြေရမယ့် စနစ် ဆောက်ချင်ရင်။
- RAG project ကို စီမံခန့်ခွဲမယ့် data engineer ဖြစ်ချင်ရင်။
- ဘယ် search အမျိုးအစား ရွေးရမလဲ ဆုံးဖြတ်ရမယ့် နေရာမှာ ရှိနေရင်။

## ကိုးကား

ဒီ course က official open documentation ကနေ ရေးထားတဲ့ မူရင်းလေ့လာစာ သင်ခန်းစာ ဖြစ်ပါတယ်။ စီးပွားဖြစ် course တစ်ခုခုကို ကူးယူ ရေးထားတာ မဟုတ်ပါဘူး။

- pgvector (PostgreSQL vector extension): https://github.com/pgvector/pgvector
- LlamaIndex docs: https://docs.llamaindex.ai/en/stable/
- LangChain text splitters: https://python.langchain.com/docs/concepts/text_splitters/
