## လေ့ကျင့်ခန်း ၁ — Memory size တွက်ခြင်း

**Task:** 1,000,000 vectors, 768 dimensions, fp32 (float 32-bit) ဆိုပါစို့။ Memory size ကို bytes နှင့် GB နှစ်မျိုး တွက်ပြပါ။ ပြီးရင် int8 quantization (32-bit ကနေ 8-bit) ခံလိုက်ရင် size ဘယ်လောက် ဖြစ်မလဲ ဆက်တွက်ပါ။

**Hints:** fp32 vector တစ်ခုက dimension တစ်ခုကို 4 bytes ယူတယ်။ int8 က dimension တစ်ခုကို 1 byte ယူတယ်။ Python `**` operator နဲ့ တွက်လို့ရတယ်။

**Expected behavior:** fp32 အတွက် ၃၀၇၂၀၀၀၀၀၀ bytes (≈2.86 GB)၊ int8 အတွက် ၇၆၈၀၀၀၀၀၀ bytes (≈0.71 GB) ရပါမယ်။ ၄ ပုံ ၁ ပုံ လျှော့သွားတာကို မြင်ရပါမယ်။

## လေ့ကျင့်ခန်း ၂ — Binary quantization နဲ့ cosine

**Task:** ပြီးသား cosine similarity (မတူညီမှု တိုင်းတာနည်း) function နဲ့ အသုံးပြုပြီး vector ၂ ခုကို နှိုင်းပါ။ ပြီးမှ binary quantization (vector ကို 0/1 bits လျှော့ချခြင်း) — အပေါင်း ကို 1၊ အနှုတ် ကို 0 ပြောင်း — လုပ်ပြီး dot product နဲ့ ပြန်နှိုင်းပါ။

**Hints:** `math.sqrt` နဲ့ norm တွက်ပါ။ Binary vector အတွက် `1 if x > 0 else 0` ကို list comprehension သုံးပါ။ Binary dot product က overlap အရေအတွက်ပဲ ဖြစ်ပါတယ်။

**Expected behavior:** Original cosine နဲ့ binary approximation တို့ရဲ့ ကွာခြားချက်ကို မြင်ရပါမယ်။ Binary က recall ထက် လျှော့သွားနိုင်တယ်ဆိုတဲ့ အပေးအယူကို နားလည်ရပါမယ်။

## လေ့ကျင့်ခန်း ၃ — Product Quantization (PQ) အခြေခံ

**Task:** 4-dim vector ကို 2-dim subvector ၂ ခုခွဲပါ။ အလွယ်အားဖြင့် PQ (vector ကို အစိတ်အပိုင်း ခွဲပြီး အုပ်စုတစ်ခုစီကို code တစ်လုံးနဲ့ ကိုယ်စားပြုခြင်း) — subvector တစ်ခုစီကို အနီးဆုံး centroid (အုပ်စုရဲ့ အလယ်ချက်) နဲ့ အစားထိုးပါ။ 8-dim vector တစ်ခုကို 4 subvector လုပ်ပြီး ခန့်မှန်း distance တွက်ပါ။

**Hints:** Jégou et al., "Product Quantization for Nearest Neighbor Search" (arXiv:0903.2314) အရ PQ က subvector တွေကို သီးခြား quantize လုပ်တယ်။ centroid နည်းနည်း (ဥပမာ ၄ လုံး) သတ်မှတ်ပြီး Euclidean distance နဲ့ အနီးဆုံးကို ရွေးပါ။

**Expected behavior:** Approximate distance နဲ့ original distance ကို နှိုင်းယှဉ်နိုင်ပါမယ်။ PQ က memory သက်သာေdrdrrdပြီး တိကျမှု အနည်းငယ် လျှော့တာကို မြင်ရပါမယ်။

## လေ့ကျင့်ခန်း ၄ — Recall@k တိုင်းတာခြင်း

**Task:** 128 vectors (random seed 42) ကို ဖန်တီးပါ။ Brute-force (အားလုံး တစ်ခုချင်း စစ်ခြင်း) top-5 ကို ground truth အဖြစ် ထားပါ။ ပြီးမှ int8 quantization လုပ်ထားတဲ့ vector တွေနဲ့ top-5 ရှေ့ရှာပါ။ Recall@5 (မှန်တဲ့ အဖြေ ဘယ်လောက် ပြန်ရလဲ) တွက်ပါ။

**Hints:** `random.Random(42)` နဲ့ deterministic ဖြစ်အောင် လုပ်ပါ။ int8 အတွက် min/max scaling သုံးပါ — `round((x - mn) / (mx - mn) * 127 - 128)` ခန့်မှန်း ဖောင်မြူလာ တစ်ခု ရေးပါ။

**Expected behavior:** Recall@5 က 1.0 နဲ့ 1.0 အောက် ကြားထွက်ပါမယ်။ Quantization က recall ပေါ် သက်ရောက်မှုကို ကိန်းဂဏန်းနဲ့ မြင်ရပါမယ်။

## လေ့ကျင့်ခန်း ၅ — Sharding နဲ့ distributed search

**Task:** Vector 200 ခုကို shard (အချက်အပြုံ ခွဲဝေထားတဲ့ အပိုင်း) ၄ ပိုင်းခွဲပါ — hash-based နဲ့ dimension-based နှစ်နည်း ရေးပါ။ Query vector တစ်ခုကို တစ်ချိန်ထဲ shards အားလုံးမှာ ရှာပြီး ရလဒ်တွေကို merge လုပ်ပါ။

**Hints:** Hash-based က `id % 4` သုံးပါ။ Dimension-based က dimension အပိုင်းအစ တစ်ခုစီကို shard တစ်ခု ထားပါ — ဒါက Qdrant/Faiss တို့ရဲ့ sharding strategy နှစ်မျိုးနဲ့ ဆင်တယ်။ Result merge လုပ်တဲ့အခါ top-k ထပ်စစ်ပါ။

**Expected behavior:** နည်းနှစ်မျိုးလုံးနဲ့ ရလဒ်တူညီမှု ရှိမရှိ နှိုင်းယှဉ်နိုင်ပါမယ်။ Shard အရေအတွက် တိုးလို့ memory per shard လျှော့သွားတာကို မြင်ရပါမယ်။

## လေ့ကျင့်ခန်း ၆ — Bulk load နဲ့ write throughput

**Task:** Vector 1000 ခုကို load ပါ။ Strategy နှစ်မျိုး နှိုင်းပါ — (၁) insert တိုင်း index တည်ဆောက်ခြင်း၊ (၂) build after load (အားလုံး load ပြီးမှ index တစ်ခါတည်း တည်ဆောက်ခြင်း)။ `time.perf_counter()` နဲ့ ချိန်ပါ။

**Hints:** pgvector README က bulk load ရာနှုန်း မြှင့်ဖို့ index ကို load ပြီးမှ တည်ဆောက်ဖို့ ညွှန်ပါတယ်။ အလွယ်အားဖြင့် "index" က sorted array တစ်ခု ထားပါ — တစ်ခုတည်း sort လုပ်တာ vs တစ်ခုထည့်တိုင်း bisect insert လုပ်တာ နှိုင်းပါ။

**Expected behavior:** Build-after-load က ပိုမြန်တာကို seconds ဂဏန်းနဲ့ မြင်ရပါမယ်။ pgvector မှာ `CREATE INDEX` ကို load ပြီးမှ လုပ်သင့်တဲ့ အကြောင်းရင်းကို Burmese လေး နားလည်ရပါမယ်။
