# M8 — Retrieval Serving Architecture: API၊ Cache နှင့် pgvector vs Vector DB

Retrieval ကို production တွင် serving လုပ်ရာ၌ လိုအပ်သော API ဒီဇိုင်း၊ caching၊ concurrency နှင့် vector store ရွေးချယ်မှုတို့ကို သင်ယူမည်ဖြစ်သည်။

> ဒီ course က official open documentation တွေကနေ ရေးထားတဲ့ မူရင်း self-study သင်ရိုးဖြစ်ပါတယ်။ အခြား commercial course ရဲ့ သင်ခန်းစာတွေကို ကူးယူခြင်း မရှိပါဘူး။

## ဒီ module မှာ ဘာသင်မလဲ

- Retrieval API ဒီဇိုင်း — metadata filter နှင့် ACL (Access Control List) ကို query interface ထဲ ပေါင်းစပ်ပုံ။
- Caching အလွှာများ — embedding cache နှင့် result cache တို့၏ လိုအပ်ချက်နှင့် သင့်တော်သော placement။
- Concurrency နှင့် connection pool အခြေခံများ။
- pgvector နှင့် Qdrant / Milvus / Weaviate / Chroma တို့၏ ကွာခြားချက်များ — workload အလိုက် ရွေးချယ်မှု decision framework။
- Hybrid architecture — Postgres ကို source of truth အဖြစ်ထားပြီး vector store ကို derived index အဖြစ် တွဲဖက်သုံးစွဲပုံ။

## သင်ခန်းစာများ

- M8.1 — Retrieval API ဒီဇိုင်း: filter နှင့် ACL ပါဝင်သော endpoint တစ်ခုကို Python standard library ဖြင့် implement လုပ်ပြမည်။
- M8.2 — Caching အလွှာများ: embedding cache နှင့် result cache ကို in-memory dict ဖြင့် တည်ဆောက်မည်။
- M8.3 — Concurrency နှင့် pool: `threading` ဖြင့် request များကို တပြိုင်တည်း handle လုပ်ပုံနှင့် pool exhaustion ဖြစ်ပေါ်ပုံအကြောင်းရင်း။
- M8.4 — pgvector vs Vector DB: Postgres + pgvector နှင့် Qdrant၊ Milvus၊ Weaviate၊ Chroma တို့အတွက် ရွေးချယ်မှု အခြေခံများ — official docs အခြေပြုသာ။
- M8.5 — Hybrid architecture: Postgres က source of truth ဖြစ်ပြီး vector store က read-optimized derived copy အဖြစ် ဆောင်ရွက်သော sync pattern။

## လိုအပ်ချက်များ (Prerequisites)

- M7 အထိ module များ ပြီးစီးထားရန် — cosine similarity၊ HNSW-style search နှင့် pgvector SQL အခြေခံ နားလည်ထားရန် လိုအပ်သည်။
- Python standard library (`threading`, `time`, `hashlib`) ဖြင့် ရေးသားနိုင်ရန် — network လိုအပ်ချက် မရှိပါ။
- Postgres + pgvector SQL ကို ဖတ်ရှုနားလည်နိုင်ရန် — lesson များတွင် SQL ကို execute မလုပ်စေဘဲ `pgvector` ၏ documented syntax အတိုင်း ပြသထားသည်။

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- RAG prototype ကို production API အဖြစ် migrate လုပ်ရန် ပြင်ဆင်သော အဆင့်တွင်။
- pgvector ဆက်လက်သုံးစွဲမည် သို့မဟုတ် dedicated vector DB သို့ ပြောင်းလဲမည် ဆုံးဖြတ်ရန် လိုအပ်သော အခြေအနေတွင်။
- Query latency လျှော့ချရန် cache layer ထည့်သွင်းလိုသော အခါ၊ user permission များကို retrieval path ထဲ ပေါင်းစပ်ရန် လိုအပ်သော အခါများတွင်လည်း သင့်လျော်သည်။

## ကိုးကား

- pgvector — https://github.com/pgvector/pgvector
- Qdrant Documentation — https://qdrant.tech/documentation/
- Weaviate Developer Docs — https://weaviate.io/developers/weaviate
- Chroma Docs — https://docs.trychroma.com/
- Milvus — https://github.com/milvus-io/milvus
