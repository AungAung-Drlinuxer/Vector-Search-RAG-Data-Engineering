## လေ့ကျင့်ခန်း ၁ — Memory size တွက်ခြင်း

**Task:** 1,000,000 vectors, 768 dimensions, fp32 ဟု ယူဆပြီး memory footprint ကို bytes နှင့် GB နှစ်မျိုးဖြင့် တွက်ချက်ပါ။ ထို့နောက် int8 quantization (32-bit → 8-bit) ပြီးနောက် footprint မည်မျှဖြစ်မည်ကို ဆက်တွက်ပါ။

**Hints:** fp32 vector သည် dimension တစ်ခုအတွက် 4 bytes၊ int8 သည် 1 byte ယူသည်။ ဂဏန်းပေါင်းစက်အစား Python `**` operator ဖြင့် တွက်နိုင်သည်။

**Expected behavior:** fp32 အတွက် ၃၀၇၂၀၀၀၀၀၀ bytes (≈2.86 GB)၊ int8 အတွက် ၇၆၈၀၀၀၀၀၀ bytes (≈0.71 GB) ရမည်။ ၄ ဆ reduction ကို မြင်ရမည်။

## လေ့ကျင့်ခန်း ၂ — Binary quantization နဲ့ cosine

**Task:** ရှိပြီးသား cosine similarity function ဖြင့် vector နှစ်ခုကို နှိုင်းယှဉ်ပါ။ ထို့နောက် binary quantization — positive ကို 1၊ negative ကို 0 ပြောင်း — လုပ်ပြီး dot product ဖြင့် ပြန်နှိုင်းယှဉ်ပါ။

**Hints:** `math.sqrt` ဖြင့် norm တွက်ပါ။ Binary vector အတွက် `1 if x > 0 else 0` ကို list comprehension ဖြင့် သုံးပါ။ Binary dot product သည် နှစ်ဖက်လုံး 1 ဖြစ်သော position အရေအတွက်နှင့် ညီမျှသည်။

**Expected behavior:** Original cosine နှင့် binary approximation တို့၏ ကွာခြားချက်ကို တွေ့ရမည်။ Binary quantization သည် memory သက်သာစေသော်လည်း approximation error ကြောင့် recall ကျဆင်းနိုင်သည့် trade-off ကို နားလည်ရမည်။

## လေ့ကျင့်ခန်း ၃ — Product Quantization (PQ) အခြေခံ

**Task:** 4-dim vector ကို 2-dim subvector နှစ်ခု ခွဲပါ။ PQ ၏ အခြေခံ mechanism အတိုင်း subvector တစ်ခုစီကို အနီးဆုံး centroid ဖြင့် အစားထိုးပါ။ 8-dim vector တစ်ခုကို subvector ၄ ခု ခွဲပြီး approximate distance တွက်ပါ။

**Hints:** Jégou et al., "Product Quantization for Nearest Neighbor Search" (arXiv:0903.2314) အရ PQ သည် subspace တစ်ခုချင်းစီကို သီးခြား quantize လုပ်သည်။ Centroid အရေအတွက် နည်းနည်း (ဥပမာ ၄ ခု) သတ်မှတ်ပြီး Euclidean distance အနည်းဆုံး centroid ကို ရွေးပါ။

**Expected behavior:** Approximate distance နှင့် exact distance ကို နှိုင်းယှဉ်နိုင်မည်။ PQ သည် memory footprint သိသိသာသာ လျှော့ချပြီး precision အနည်းငယ် ဆုံးရှုံးကြောင်း တွေ့ရမည်။

## လေ့ကျင့်ခန်း ၄ — Recall@k တိုင်းတာခြင်း

**Task:** Vector 128 ခု (random seed 42) ဖန်တီးပါ။ Brute-force top-5 ကို ground truth အဖြစ် သတ်မှတ်ပါ။ ထို့နောက် int8 quantization လုပ်ထားသော vector များဖြင့် top-5 search လုပ်ပြီး recall@5 တွက်ပါ။

**Hints:** `random.Random(42)` ဖြင့် deterministic ဖြစ်အောင် လုပ်ပါ။ int8 အတွက် min/max scaling formula — `round((x - mn) / (mx - mn) * 127 - 128)` — ရေးပါ။

**Expected behavior:** Recall@5 သည် 1.0 သို့မဟုတ် 1.0 အောက် တန်ဖိုး ထွက်မည်။ Quantization ၏ recall အပေါ် သက်ရောက်မှုကို ဂဏန်းဖြင့် တိုင်းတာနိုင်မည်။

## လေ့ကျင့်ခန်း ၅ — Sharding နဲ့ distributed search

**Task:** Vector 200 ခုကို shard ၄ ပိုင်း ခွဲပါ — hash-based နှင့် dimension-based နည်းလမ်းနှစ်မျိုး ရေးပါ။ Query vector တစ်ခုကို shard အားလုံး၌ search လုပ်ပြီး ရလဒ်များကို merge လုပ်ပါ။

**Hints:** Hash-based အတွက် `id % 4` သုံးပါ။ Dimension-based အတွက် dimension slice တစ်ခုစီကို shard တစ်ခု၌ ထားပါ — ဤနည်းလမ်းနှစ်မျိုးသည် Qdrant/FAISS တို့၏ sharding strategy နှစ်မျိုးနှင့် ကိုက်ညီသည်။ Merge လုပ်ပြီးနောက် global top-k ကို ထပ်ရွေးပါ။

**Expected behavior:** နည်းလမ်းနှစ်မျိုး၏ ရလဒ် တူညီမှု ရှိ/မရှိ နှိုင်းယှဉ်နိုင်မည်။ Shard အရေအတွက် တိုးလာသည်နှင့်အမျှ memory per shard လျော့ကျသွားသည်ကို တွေ့ရမည်။

## လေ့ကျင့်ခန်း ၆ — Bulk load နဲ့ write throughput

**Task:** Vector 1000 ခု load လုပ်ပါ။ Strategy နှစ်မျိုး နှိုင်းယှဉ်ပါ — (၁) insert တိုင်း၌ index ထိန်းသိမ်းခြင်း၊ (၂) build after load (data အားလုံး load ပြီးမှ index တစ်ကြိမ်တည်း တည်ဆောက်ခြင်း)။ `time.perf_counter()` ဖြင့် အချိန်တိုင်းတာပါ။

**Hints:** pgvector README သည် bulk load throughput မြှင့်တင်ရန် index ကို load ပြီးမှ တည်ဆောက်ရန် ညွှန်ကြားထားသည်။ ရိုးရှင်းသော stand-in အနေဖြင့် "index" ကို sorted array တစ်ခုအဖြစ် ထားပါ — တစ်ကြိမ်တည်း sort လုပ်ခြင်း နှင့် insert တိုင်း၌ bisect insert လုပ်ခြင်းတို့ကို နှိုင်းယှဉ်ပါ။

**Expected behavior:** Build-after-load က ပိုမြန်ကြောင်း ဂဏန်းဖြင့် တွေ့ရမည်။ pgvector တွင် `CREATE INDEX` ကို load ပြီးမှသာ လုပ်သင့်သည့် အကြောင်းရင်းကို နားလည်ရမည်။
