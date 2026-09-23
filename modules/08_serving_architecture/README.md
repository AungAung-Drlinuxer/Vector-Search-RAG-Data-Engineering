# M8 — Retrieval Serving Architecture: API၊ Cache နှင့် pgvector vs Vector DB

Retrieval ကို production မှာ ဘယ်လို serving လုပ်မလဲဆိုတာ သင်ယူရမှာပါ — API ဒီဇိုင်း၊ caching၊ concurrency နှင့် vector store ရွေးချယ်မှု။

> ဒီ course က official open documentation တွေကနေ ရေးထားတဲ့ မူရင်း self-study သင်ရိုးဖြစ်ပါတယ်။ အခြား commercial course ရဲ့ သင်ခန်းစာတွေကို ကူးယူခြင်း မရှိပါဘူးနော်။

## ဒီ module မှာ ဘာသင်မလဲ

- Retrieval API တစ်ခု ဒီဇိုင်းဆွဲနည်း — filter (metadata စစ်ခြင်း) နှင့် ACL (Access Control List — ဘယ် user က ဘယ် data မြင်ရမလဲ ကန့်သတ်ချင်း) ပါဝင်စေနည်း။
- Caching အလွှာများ — embedding cache နှင့် result cache ဘာကြောင့်လိုအပ်လဲ၊ ဘယ်နေရာမှာ သိမ်းသင့်လဲ။
- Concurrency (တပြိုင်တည် request များ ဆက်တိုက်လာခြင်း) နှင့် connection pool (database connection တွေ ပြန်လည်အသုံးပြုနိုင်တဲ့ အစု) အခြေခံ။
- pgvector နှင့် Qdrant / Milvus / Weaviate / Chroma တို့ရဲ့ ကွာခြားချက် — ဘယ်အချိန်မှာ ဘယ်ဟာ သင့်တော့လဲ။
- Hybrid architecture — Postgres ကို source of truth (အချက်အလက် အတည်အမှန်ဆုံး သိမ်းနေရာ) အဖြစ် ထားပြီး vector store ကို သီးသန့် သုံးနည်း။

## သင်ခန်းစာများ

- M8.1 — Retrieval API ဒီဇိုင်း: filter နှင့် ACL ပါတဲ့ endpoint တစ်ခု စတိုင်လ်ယူနိုင်အောင် Python standard library နဲ့ ရေးပြပါမယ်။
- M8.2 — Caching အလွှာများ: embedding cache နှင့် result cache ကို in-memory dict နဲ့ ပြန်ဆောက်ပြပါမယ်။
- M8.3 — Concurrency နှင့် pool: `threading` နဲ့ request များ တပြိုင်တည် handle လုပ်ပုံ၊ pool exhaustion (connection အားလုံး ယူလို့ပြီးနေတဲ့ အခြေအနေ) ဘာကြောင့်ဖြစ်လဲ။
- M8.4 — pgvector vs Vector DB: Postgres + pgvector နဲ့ Qdrant၊ Milvus၊ Weaviate၊ Chroma တို့ရဲ့ ရွေးချယ်စရာ အခြေခံများ၊ official docs က ပြောတာတွေနဲ့သာ။
- M8.5 — Hybrid architecture: Postgres က source of truth ဖြစ်ပြီး vector store က read-optimized မှတ်တမ်းသဖွယ် လုပ်ထားတဲ့ sync pattern။

## လိုအပ်ချက်များ (Prerequisites)

- M7 အထိ module တွေ ပြီးထားဖို့ — cosine similarity၊ HNSW-style search နှင့် pgvector SQL အခြေခံ နားလည်ထားဖို့ လိုပါတယ်။
- Python standard library (`threading`, `time`, `hashlib`) နဲ့ ရေတွက်နိုင်ဖို့၊ network မလိုပါဘူးနော်။
- Postgres + pgvector SQL ကို ဖတ်နိုင်ဖို့ — lesson တွေက SQL ကို run မချုပ်ပါဘူး၊ ပြောပြပြီးသား `pgvector` စနစ်ရဲ့ syntax အတိုင်း ပြပါမယ်။

## ဘယ်အချိန်မှာ အသုံးဝင်လဲ

- RAG prototype တစ်ခုကို production API အဖြစ် တင်ဖို့ ပြင်ဆင်နေတဲ့ အချိန်မှာ အသုံးဝင်ပါတယ်။
- pgvector ကို ဆက်သုံးမလား၊ vector DB သီးသန့် ပြောင်းသွားမလား ဆုံးဖြတ်ရခက်နေတဲ့ အခါမှာ အထောက်အကူ ဖြစ်ပါတယ်။
- Query အမြန်မှု တက်အောင် cache layer ထည့်ချင်တဲ့ အခါ၊ user permission တွေကို retrieval ထဲ ထည့်သွင်းရတဲ့ အခါမှာလည်း သင့်တော့ပါတယ်နော်။

## ကိုးကား

- pgvector — https://github.com/pgvector/pgvector
- Qdrant Documentation — https://qdrant.tech/documentation/
- Weaviate Developer Docs — https://weaviate.io/developers/weaviate
- Chroma Docs — https://docs.trychroma.com/
- Milvus — https://github.com/milvus-io/milvus
