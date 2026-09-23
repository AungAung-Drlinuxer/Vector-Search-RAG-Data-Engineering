## လေ့ကျင့်ခန်း ၁ — Pipeline အဆင့်များကို အစီအစဉ်ချမယ်

RAG pipeline ရဲ့ အဆင့် ၈ ခုကို မှန်မှန်ကန်ကန် အစီအစဉ်ချပါ။ အဆင့်တွေကတော့ retrieve, ingest, chunk, evaluate, embed, rerank, generate, index ပါ။

**Hints:** ပထမဆုံး data ကို စုပါတယ်။ နောက်ဆုံးမှာ ရလဒ်ကို တိုင်းတာပါတယ်။ LlamaIndex docs (https://docs.llamaindex.ai/en/stable/) မှာ pipeline အဆင့်တွေကို ဖတ်ကြည့်ပါ။

**Expected behavior:** `ingest → chunk → embed → index → retrieve → rerank → generate → evaluate` ဆိုတဲ့ အစီအစဉ် ရပါတယ်။ အဆင့်တစ်ခုချင်းကို ဘာကြောင့် အဲဒီနေရာမှာ ရှိရတယ်ဆိုတာ တစ်ကြောင်းစီ ရှင်းပြနိုင်ရပါမယ်။

## လေ့ကျင့်ခန်း ၂ — Chunk ဆိုတာ ဘာလဲ ရေးဖော်မယ်

Chunk (စာပိုဒ်ငယ် — document ကနေ ခွဲထုတ်လိုက်တဲ့ အပိုင်းသေး) ဆိုတာကို ကိုယ်ပိုင်စာလုံး သုံးပြီး ရှင်းပါ။ ဒါပြီး အောက်မှာ ဖော်ပြထားတဲ့ chunk တွေရဲ့ အားသာချက်၊ အားနည်းချက်ကို ဇယားဆွဲပါ — (က) chunk အရွယ်အစား အလွန်သေးတာ (ခ) chunk အရွယ်အစား အလွန်ကြီးတာ။

**Hints:** Chunk သေးရင် search ရှာတဲ့အခါ တိကျတယ်။ ဒါပေမယ့် အချက်အလက် ပြတ်တယ်။ Chunk ကြီးရင် ဆန့ကျင်ဘက်ပါ။ LangChain text splitters docs (https://python.langchain.com/docs/concepts/text_splitters/) ကို ကိုးကားပါ။

**Expected behavior:** အားသာချက်၊ အားနည်းချက် ၂ ခုစလုံး နားလည်သွားတဲ့ ဇယားတစ်ခု ရပါတယ်။ chunk အရွယ်အစားနဲ့ ရလဒ် အရည်အသွေး ချိတ်ဆက်ပုံကို ဥပမာနဲ့ ပြနိုင်ရပါမယ်။

## လေ့ကျင့်ခန်း ၃ — Cosine similarity ကို Python နဲ့ တွက်မယ်

Standard library သုံးပြီး cosine similarity (vector နှစ်ခုရဲ့ ထောင့် — ဘယ်လောက် နီးနီးတူတူရှိလဲဆိုတဲ့ တိုင်းတာမှု) တွက်တဲ့ function ရေးပါ။ ဒီ vector နှစ်ခုကို သုံးပါ — `a = [1.0, 0.0]`, `b = [0.0, 1.0]` နဲ့ `c = [1.0, 1.0]`။ a နဲ့ b၊ a နဲ့ c ရဲ့ similarity တွက်ပါ။

**Hints:** Formula က — `(a · b) / (||a|| * ||b||)`။ Dot product နဲ့ magnitude ကို `math` module နဲ့ တွက်ပါ။ pgvector (https://github.com/pgvector/pgvector) မှာ `<=>` operator က ဒီကိန်းဂဏန်းအတွက်ပါ။

**Expected behavior:** `a` နဲ့ `b` ရဲ့ similarity = `0.0` ရပါတယ် (ထောင့်မှန်ကျ)။ `a` နဲ့ `c` ရဲ့ similarity ≈ `0.7071` ရပါတယ်။ Code မှာ formula ပြပြီး တွက်ပြရမှာ ဖြစ်လို့ ကိန်းဂဏန်းတွေ တည်တည်ရှိရှိ ထွက်ပါတယ်။

## လေ့ကျင့်ခန်း ၄ — Vector search နဲ့ keyword search ရွေးမယ်

အောက်ပါ query တွေအတွက် vector search (အဓိပ္ပာယ်အရ တူတာရှာတာ)၊ keyword search (စာလုံးအတိအက ကိုက်တာရှာတာ) ဒါမှမဟုတ် hybrid (နှစ်မျိုးပေါင်း) — ဘယ်ဟာ သင့်တော်လဲ ရွေးပြီး အကြောင်းပြပါ — (က) "error code E-4471" (ခ) "ဆီးချိုရောဂါအတွက် အစားအသောက် အကြံပြုချက်" (ဂ) "မြန်မာနိုင်ငံ ခရီးသွား အကြံပြုချက် ၂၀၂၄"။

**Hints:** Product code တွေက တိအက ကိုက်ရမယ်။ သဘောတရား ဆွဲကူးရှာတာက အဓိပ္ပာယ်အရ ရှာတာ ပိုသင့်တယ်။ Hybrid က နှစ်မျိုးလုံး လိုအပ်တဲ့ အခါမှာ အသုံးဝင်တယ်။

**Expected behavior:** Query တစ်ခုချင်း ရွေးချယ်မှုနဲ့ အကြောင်းပြချက် ၂-၃ စာကြောင်း ရပါတယ်။ "ဘာကြောင့် ဒီ search အမျိုးအစားက ပိုသင့်တယ်" ဆိုတာကို latency (တုံ့ပြန်ချိန်) နဲ့ ရလဒ် အရည်အသွေး နှစ်ခုစလုံး သုံးပြီး ရှင်းပြနိုင်ရပါမယ်။

## လေ့ကျင့်ခန်း ၅ — Chunking ရဲ့ memory အရွယ်အစား တွက်မယ်

ဒီ assumption တွေနဲ့ embedding storage တွက်ပါ — "1,000,000 chunks, 768 dimensions, fp32 (float 32-bit) representation"။ တစ် chunk ကို ဘယ်နှစ် byte လိုမလဲ။ စုစုပေါင်း ဘယ်နှစ် GB လိုမလဲ။

**Hints:** fp32 ဆိုတာ dimension တစ်ခုကို 4 byte ယူတယ်။ ဒါဆို chunk တစ်ခု = `768 * 4` bytes။ ဒါဆို 1,000,000 chunks အတွက် စုစုပေါင်း တွက်ပါ။ 1 GB = `1024 * 1024 * 1024` bytes သုံးပါ။

**Expected behavior:** Chunk တစ်ခုက `3072` bytes ရပါတယ်။ စုစုပေါင်း ≈ `2.86 GB` ရပါတယ်။ Arithmetic အဆင့်ဆင့် ပြထားပြီး ကိန်းဂဏန်းတွေက formula ကနေ ဆင်းလာတာ ဖြစ်ပါတယ်။

## လေ့ကျင့်ခန်း ၆ — Reciprocal Rank Fusion ကို ကိုယ်တိုင်ဆောက်မယ်

Vector search နဲ့ keyword search ရဲ့ ranking နှစ်ခုကို ပေါင်းစပ်တဲ Reciprocal Rank Fusion (RRF — ranking နှစ်ခုကို အဆင့်နေရာအရ ပေါင်းတဲ့ method) ကို standard library Python နဲ့ ရေးပါ။ Vector ranking: `["doc_c", "doc_a", "doc_b"]`။ Keyword ranking: `["doc_a", "doc_b", "doc_d"]`။ k=60 သုံးပါ။ ပေါင်းပြီးရင် နောက်ဆုံး ranking ထုတ်ပါ။

**Hints:** RRF score က — `sum(1 / (k + rank_i))`။ rank က ၁ ကနေ စပါတယ်။ `doc_c` က vector ranking မှာ rank 1၊ keyword ranking မှာ မရှိပါဘူး — မရှိရင် score ထည့်စရာ မလိုပါဘူး။ Dictionary သုံးပြီး score စုပါ။

**Expected behavior:** `doc_a` ရဲ့ score = `1/61 + 1/61 ≈ 0.0328` ရပါတယ်။ `doc_c` ရဲ့ score = `1/61 ≈ 0.0164` ရပါတယ်။ နောက်ဆုံး ranking က `doc_a > doc_b > doc_c > doc_d` ဆိုတဲ့ အစီအစဉ် ထွက်ပါတယ်။ Code ရဲ့ နောက်ဆုံးမှာ `# Expected output:` comment ထည့်ပြီး ဒီ ranking ပြရမှာပါ။ ဒီ exercise မှာ database မချိတ်ပါဘူး — pgvector မှာ hybrid search လုပ်ရင် ဒီနမူနာ အတုအစား သဘောသဘာဝနဲ့ တူပါတယ်။
