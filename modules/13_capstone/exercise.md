# M13 — Capstone လေ့ကျင့်ခန်းများ

ဒီလေ့ကျင့်ခန်းတွေက M13 မော်ဂျူးအတွက် အင်္ဂလိပ်လို official docs (pgvector GitHub, HNSW paper arXiv:1603.09320, Ragas docs) ကနေ ရေးထားတဲ့ မူရင်း လေ့ကျင့်ခန်းတွေ ဖြစ်ပါတယ်။ Python standard library သာ သုံးပါမယ်။ network မ ချိတ်ပါဘူး။

## လေ့ကျင့်ခန်း ၁ — Storage အရွယ် တွက်ပါ

**Task:** 1,000,000 chunks, 768 dimensions, fp32 (4 bytes per value) ဆိုတဲ့ သတ်မှတ်ချက် (assumption) နဲ့ အကြမ်းဖျင်း vector data ရဲ့ ဘိုက်အရေအတွက် (bytes) ကို တွက်ပြပါ။

**Hints:** bytes = chunks × dims × 4 ပါ။ Python `print` နဲ့ ပြပါ။ fp32 ဆိုသည်က တစ်ခုချင်းစီ 4 bytes ယူတဲ့ float အမျိုးအစား ဖြစ်ပါတယ်။

**Expected behavior:** 3,072,000,000 bytes (≈ 3 GB) ဆိုတဲ့ ဂဏန်း ရပါတယ်။ တွက်ပုံ formula ကိုပါ ပြထားရပါမယ်။

## လေ့ကျင့်ခန်း ၂ — Chunk size ရွေးမှုရဲ့ အကျိုးသက်ရောက်မှု

**Task:** chunk size ချင်း နှိုင်းယှဉ်ပါ — 100,000 words စာအုပ်တစ်အုပ်ကို (a) 200-word chunks, (b) 800-word chunks နဲ့ စီပါ။ chunk အရေအတွက် နှစ်ခု တွက်ပြပါ။

**Hints:** chunks = ceil(words / chunk_size) ပါ။ `math.ceil` သုံးပါ။ overlap မထည့်ဘူးလို့ ရိုးရိုး ထားပါ။

**Expected behavior:** (a) 500 chunks, (b) 125 chunks ရပါတယ်။ 200-word chunk က precision ကောင်းပေမယ့် chunk များတယ်၊ 800-word chunk က context များပေမယ့် စာကြောင်းတွေ ပျောက်လွယ်တယ်ဆိုတာ တစ်ကြောင်း ရှင်းပြပါ။

## လေ့ကျင့်ခန်း ၃ — HNSW-style graph ဆောက်ပြီး search လုပ်ပါ

**Task:** 100 ချက် (2D vector) ကနေ level 0 သာ ပါတဲ့ ရိုးရိုး graph တစ်ခု ဆောက်ပါ။ entry point ကနေ greedy search (အနီးဆုံး အိမ်နီးချင်းကို ဆက်လိုက်တဲ့ နည်း) လုပ်ပါ။

**Hints:** တစ်ချက်ချင်းစီက အနီးဆုံး M=4 ချက်နဲ့ ချိတ်ပါ။ search မှာ လက်ရှိ အကွာအဝေးထက် နီးတဲ့ အိမ်နီးချင်း မတွေ့တော့ရင် ရပ်ပါ။ ဒါက HNSW အတွေးကို အလွယ်ပြတဲ့ version ပါ — real HNSW က multi-layer ဖြစ်ပါတယ် (arXiv:1603.09320)။

**Expected behavior:** query တစ်ခုကို exact nearest neighbor (brute-force နဲ့ တူတဲ့) ရလာသလား မဟုတ် သလားကို ပြပါ။ small dataset မှာတော့ များသောအားဖြင့် တူပါတယ်။

## လေ့ကျင့်ခန်း ၄ — Recall@k တိုင်းပါ

**Task:** exercise ၃ ရဲ့ graph search နဲ့ brute-force search နှစ်ခုကို query 100 ခုမှာ run ပါ။ recall@5 (brute-force top-5 ထဲက ဘယ်နှစ်ခု ထပ်တွက်လဲ) ပျမ်းမျှ တိုင်းပါ။

**Hints:** recall@k = |graph_top_k ∩ exact_top_k| / k ပါ။ query တွေကို fixed seed နဲ့ `random.Random(42)` သုံးပြီး ထုတ်ပါ — deterministic ဖြစ်ဖို့ လိုပါတယ်။

**Expected behavior:** 0.0 နဲ့ 1.0 ကြားမှာရှိတဲ့ recall တန်ဖိုးတစ်ခု ရပါတယ်။ seed 42 နဲ့ run တိုင်း တူတဲ့ တန်ဖိုး ပြန်ရပါမယ်။

## လေ့ကျင့်ခန်း ၅ — QPS တွက်ပါ

**Task:** exercise ၃ ရဲ့ search ကို query 1,000 ခုမှာ ချိန်တာ (timing) တိုင်းပါ — `time.perf_counter` သုံးပါ။ ပြီးရင် QPS (Query Per Second — စက္ကန့်တစ်ခါ လက်ခံနိုင်တဲ့ query အရေအတွက်) တွက်ပါ။

**Hints:** QPS = 1000 / total_seconds ပါ။ p95 latency (95% က ဒီအချိန်ထက် မကျော်ဘူး) ကိုလည်း sorted latencies ထဲက index `int(0.95 * len)` နဲ့ ထုတ်ပါ။

**Expected behavior:** QPS နဲ့ p95 latency တန်ဖိုးတွေ ရပါတယ်။ ကိစ္စက ဂဏန်းက စက်ပေါ်မူတည်တယ်ဆိုတာ comment ထဲ ရေးပါ။ QPS formula ကို ပြပါ။

## လေ့ကျင့်ခန်း ၆ — End-to-end pipeline ဒီဇိုင်းပါ

**Task:** ingest → chunk → embed → index → retrieve → rerank → evaluate ကို တစ်ခုတည်း script ထဲ စုပါ — အားလုံး deterministic standard-library Python နဲ့ပါ။

**Hints:** ၁။ စာ ၁၀၀ ကြောင်းကို 100-word chunks စီပါ။ ၂။ embed အစား hash-based deterministic vector သုံးပါ (comment ထဲ — real system က embedding model သုံးပါတယ်လို့ ရေးပါ)။ ၃။ exercise ၃ ရဲ့ graph search နဲ့ retrieve လုပ်ပါ။ ၄။ rerank အတွက် top-20 ကနေ exact cosine နဲ့ top-5 ပြန်စဉ်ပါ။ ၅။ recall@5 တိုင်းပါ — Ragas docs မှာ ဒီမျိုး metric တွေက evaluation အတွက် ဖြစ်ပါတယ်။

**Expected behavior:** script တစ်ခုတည်း run လို့ ရပါတယ်။ output မှာ chunk အရေအတွက်, recall@5, QPS ပြပါ။ seed 42 နဲ့ run နှစ်ခါ ရလဒ် တူရပါမယ်။

> မှတ်ချက် — ဒီလေ့ကျင့်ခန်းတွေက pgvector + PostgreSQL ရဲ့ အလုပ်လုပ်ပုံကို Python နဲ့ ပြန်လုပ်တာ ဖြစ်ပါတယ်။ production မှာတော့ pgvector (https://github.com/pgvector/pgvector) က HNSW index တွေကို `CREATE INDEX ... USING hnsw` နဲ့ ထည့်ပေးပါတယ်။
