## လေ့ကျင့်ခန်း ၁ — Pipeline အဆင့်များကို အစီအစဉ်ချခြင်း

RAG pipeline ၏ အဆင့် ၈ ခုကို မှန်ကန်သော အစီအစဉ်ဖြင့် စီစဉ်ပါ။ ပေးထားသော အဆင့်များမှာ — retrieve၊ ingest၊ chunk၊ evaluate၊ embed၊ rerank၊ generate၊ index။

**Hints:** ပထမအဆင့်သည် data ရယူခြင်း၊ နောက်ဆုံးအဆင့်သည် ရလဒ် တိုင်းတာခြင်း ဖြစ်သည်။ LlamaIndex docs (https://docs.llamaindex.ai/en/stable/) တွင် pipeline အဆင့်များကို ဖတ်ကြည့်ပါ။

**Expected behavior:** `ingest → chunk → embed → index → retrieve → rerank → generate → evaluate` အစီအစဉ် ရရှိရမည်။ အဆင့်တစ်ခုချင်းစီကို ဒီနေရာတွင် ရှိရသည့် အကြောင်းရင်းကို တစ်ကြောင်းစီ ရှင်းပြနိုင်ရမည်။

## လေ့ကျင့်ခန်း ၂ — Chunk ၏ အဓိပ္ပာယ်ကို ရေးဖော်ခြင်း

Chunk (document မှ ခွဲထုတ်ထားသော retrieval unit အပိုင်းငယ်) ၏ အဓိပ္ပာယ်ကို ကိုယ်ပိုင် စကားလုံးဖြင့် ရေးဖော်ပါ။ ထို့နောက် အောက်ပါ chunk size နှစ်မျိုး၏ အားသာချက်/အားနည်းချက် ဇယား ဆွဲပါ — (က) chunk size အလွန်သေးခြင်း (ခ) chunk size အလွန်ကြီးခြင်း။

**Hints:** Chunk သေးပါက retrieval precision မြင့်သော်လည်း context ပြတ်တောက်သည်။ Chunk ကြီးပါက ဆန့်ကျင်ဘက် သက်ရောက်မှု ဖြစ်သည်။ LangChain text splitters docs (https://python.langchain.com/docs/concepts/text_splitters/) ကို ကိုးကားပါ။

**Expected behavior:** အားသာချက်/အားနည်းချက် နှစ်မျိုးလုံး ပါဝင်သော ဇယားတစ်ခု ရရှိရမည်။ Chunk size နှင့် retrieval quality အချိုးကျ ဆက်နွယ်မှုကို ဥပမာဖြင့် ပြသနိုင်ရမည်။

## လေ့ကျင့်ခန်း ၃ — Cosine similarity ကို Python ဖြင့် တွက်ချက်ခြင်း

Standard library သုံး၍ cosine similarity တွက်ချက်သော function ရေးပါ။ အောက်ပါ vector များကို သုံးပါ — `a = [1.0, 0.0]`၊ `b = [0.0, 1.0]`၊ `c = [1.0, 1.0]`။ a–b နှင့် a–c ၏ similarity ကို တွက်ပါ။

**Hints:** Formula မှာ — `(a · b) / (||a|| * ||b||)`။ Dot product နှင့် magnitude ကို `math` module ဖြင့် တွက်ပါ။ pgvector (https://github.com/pgvector/pgvector) တွင် `<=>` operator သည် ဒီ metric အတွက် ဖြစ်သည်။

**Expected behavior:** `a`–`b` similarity = `0.0` (orthogonal)။ `a`–`c` similarity ≈ `0.7071`။ Formula ကို code ထဲတွင် ပြသထားပြီး ရလဒ်ကိန်းဂဏန်းများမှာ deterministic ဖြစ်ရမည်။

## လေ့ကျင့်ခန်း ၄ — Vector search နှင့် keyword search ရွေးချယ်ခြင်း

အောက်ပါ query များအတွက် vector search၊ keyword search၊ hybrid — မည်သည်က သင့်တော်သည်ကို ရွေးချယ်ပြီး အကြောင်းပြပါ — (က) "error code E-4471" (ခ) "ဆီးချိုရောဂါအတွက် အစားအသောက် အကြံပြုချက်" (ဂ) "မြန်မာနိုင်ငံ ခရီးသွား အကြံပြုချက် ၂၀၂၄"။

**Hints:** Product code ကဲ့သို့ identifier သည် exact match လိုအပ်သည်။ Semantic paraphrase query သည် vector search ပိုသင့်တော်သည်။ Hybrid သည် နှစ်မျိုးလုံး လိုအပ်သော query အတွက် ဖြစ်သည်။

**Expected behavior:** Query တစ်ခုချင်းစီအတွက် ရွေးချယ်မှုနှင့် အကြောင်းပြချက် ၂–၃ စာကြောင်း ရရှိရမည်။ ရွေးချယ်မှုကို latency နှင့် retrieval quality နှစ်ခုစလုံးဖြင့် အကြောင်းပြနိုင်ရမည်။

## လေ့ကျင့်ခန်း ၅ — Embedding storage အရွယ်အစား တွက်ချက်ခြင်း

အောက်ပါ assumption များဖြင့် embedding storage footprint ကို တွက်ပါ — "1,000,000 chunks, 768 dimensions, fp32 representation"။ Chunk တစ်ခုအတွက် byte ဘယ်လောက် လိုအပ်သနည်း။ စုစုပေါင်း GB ဘယ်လောက် လိုအပ်သနည်း။

**Hints:** fp32 တွင် dimension တစ်ခုသည် 4 bytes ယူသည်။ Chunk တစ်ခု = `768 * 4` bytes။ 1,000,000 chunks အတွက် စုစုပေါင်းကို တွက်ပါ။ 1 GB = `1024 * 1024 * 1024` bytes သုံးပါ။

**Expected behavior:** Chunk တစ်ခု = `3072` bytes။ စုစုပေါင်း ≈ `2.86 GB`။ Arithmetic အဆင့်ဆင့် ပြသထားပြီး ကိန်းဂဏန်းများမှာ formula မှ ဆင်းသက်လာခြင်း ဖြစ်ရမည်။

## လေ့ကျင့်ခန်း ၆ — Reciprocal Rank Fusion တည်ဆောက်ခြင်း

Vector ranking နှင့် keyword ranking နှစ်ခုကို ပေါင်းစပ်သော Reciprocal Rank Fusion (RRF) ကို standard library Python ဖြင့် ရေးပါ။ Vector ranking: `["doc_c", "doc_a", "doc_b"]`။ Keyword ranking: `["doc_a", "doc_b", "doc_d"]`။ k=60 သုံးပါ။ ပေါင်းစပ်ပြီးနောက် final ranking ထုတ်ပါ။

**Hints:** RRF score မှာ — `sum(1 / (k + rank_i))`။ Rank သည် ၁ မှ စသည်။ `doc_c` သည် vector ranking တွင် rank 1၊ keyword ranking တွင် မပါဝင် — မပါဝင်သော ranking အတွက် score ထည့်သွင်းရန် မလိုပါ။ Score စုဆောင်းရန် dictionary သုံးပါ။

**Expected behavior:** `doc_a` score = `1/61 + 1/61 ≈ 0.0328`။ `doc_c` score = `1/61 ≈ 0.0164`။ Final ranking မှာ `doc_a > doc_b > doc_c > doc_d`။ Code ၏ နောက်ဆုံးတွင် `# Expected output:` comment ဖြင့် ဒီ ranking ပြသရမည်။ ဒီ exercise တွင် database connection မပါဝင်ပါ — pgvector hybrid search ၏ deterministic in-memory stand-in သဘောသာ ဖြစ်သည်။
