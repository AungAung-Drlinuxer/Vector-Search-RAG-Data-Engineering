# M0 — RAG Data Engineering ရဲ့ မြေပုံ

ဒီ module သည် RAG (Retrieval-Augmented Generation) pipeline ၏ အဆင့် ၈ ခုကို အနှံ့အပြား သုံးသပ်ထားသည်။

## ဒီ module မှာ ဘာသင်မလဲ

- RAG ၏ အဓိပ္ပာယ်နှင့် လိုအပ်ချက်အကြောင်းရင်းများ။
- Pipeline အဆင့် ၈ ခု — ingest (data ရယူသည့်အဆင့်) မှ evaluate (အရည်အသွေး တိုင်းတာသည့်အဆင့်) အထိ။
- Vector search၊ keyword search၊ hybrid search တို့၏ ရွေးချယ်မှု စံနှုန်းများ။
- Latency နှင့် ကုန်ကျစရိတ် အတိုင်းအတာများ။
- Data engineer တာဝန်နှင့် model engineer တာဝန် ခွဲခြားသတ်မှတ်နည်း။

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

- Python အခြေခံ — function ရေးနိုင်ရုံဖြင့် လုံလောက်သည်။
- List၊ dict၊ loop အသုံးပြုနိုင်ရမည်။
- SQL အခြေခံ (PostgreSQL) ရှိပါက အထောက်အကူ ဖြစ်သော်လည်း မဖြစ်မနေ မလိုအပ်ပါ။
- ဒီ course သည် offline standard-library Python ကိုသာ အသုံးပြုသည်။ Database connection မပါဝင်ပါ။

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- ကုမ္ပဏီ document များကို LLM ဖြင့် ဖြေဆိုစေမည့် စနစ် တည်ဆောက်မည်ဖြစ်ပါက။
- RAG project ကို စီမံခန့်ခွဲမည့် data engineer အခန်းကဏ္ဍအတွက်။
- Search architecture အမျိုးအစား ဆုံးဖြတ်ရမည့် တာဝန်ရှိပါက။

## ကိုးကား

ဒီ course သည် official open documentation များကို အခြေခံ၍ ရေးသားထားသော မူရင်း လေ့လာစာ သင်ခန်းစာ ဖြစ်သည်။ စီးပွားဖြစ် course တစ်ခုခုမှ ကူးယူထားခြင်း မဟုတ်ပါ။

- pgvector (PostgreSQL vector extension): https://github.com/pgvector/pgvector
- LlamaIndex docs: https://docs.llamaindex.ai/en/stable/
- LangChain text splitters: https://python.langchain.com/docs/concepts/text_splitters/
