## လေ့ကျင့်ခန်း ၁ — Storage တွက်ချက်ခြင်း

Chunks တစ်သန်း (1,000,000)၊ dimension 768၊ fp32 (32-bit float) ဟု ယူဆပါ။ Vector storage ပမာဏကို bytes နှင့် GB ဖြင့် တွက်ချက်ပါ။ တွက်ချက်မှုအဆင့်တိုင်းကို ဖော်ပြပါ။

**Hints:** fp32 သည် 4 bytes ဖြစ်သည်။ စုစုပေါင်း bytes = chunk အရေအတွက် × dimension × 4။ 1 GB = 1,000,000,000 bytes (decimal convention) ဟု ယူဆနိုင်သည်။

**Expected behavior:** 768 × 4 = 3,072 bytes per vector ရရှိသည်။ စုစုပေါင်း 3,072,000,000 bytes ≈ 3.07 GB ဖြစ်သည်။

## လေ့ကျင့်ခန်း ၂ — L2 Normalization ရေးခြင်း

Standard-library Python ဖြင့် `l2_normalize(v)` function ရေးပါ။ Vector ၏ L2 norm ဖြင့် စားပြီး ရလဒ် vector ကို ပြန်ပါ။

**Hints:** norm = sqrt(sum of squared components)။ `math.sqrt` နှင့် `math.fsum` ကို သုံးပါ။ Norm = 0 ဖြစ်ပါက vector ကို မပြောင်းလဲဘဲ ပြန်ပါ (division by zero ကာကွယ်ရန်)။

**Expected behavior:** `l2_normalize([3.0, 4.0])` သည် `[0.6, 0.8]` ပြန်သည်။ Normalize ပြီးနောက် norm = 1.0 ဖြစ်သည်။

## လေ့ကျင့်ခန်း ၃ — Dot Product နှင့် Cosine တူညီမှု

L2-normalized vectors နှစ်ခုအတွက် dot product နှင့် cosine similarity တူညီကြောင်း စစ်ဆေးပါ။ cosine = dot(v1, v2) / (norm(v1) × norm(v2)) formula ကို ရေးပြပါ။

**Hints:** လေ့ကျင့်ခန်း ၂ ၏ `l2_normalize` ကို အသုံးပြုပါ။ Norm 1 ဖြစ်နေပါက cosine နှင့် dot တူညီရသည့် အကြောင်းရင်းကို တစ်ကြောင်းတည်းဖြင့် ရှင်းပြပါ။

**Expected behavior:** Normalized vectors နှစ်ခုတွင် dot product တန်ဖိုးနှင့် cosine တန်ဖိုးသည် tolerance အတွင်း တူညီသည်။

## လေ့ကျင့်ခန်း ၄ — Matryoshka Dimension ဖြတ်ခြင်း

768-dim vector တစ်ခုမှ ရှေ့ပိုင်း 256 dimensions ကိုသာ ဖြတ်ယူပြီး retrieval accuracy ကို နှိုင်းယှဉ်ပါ။ Toy brute-force search ဖြင့် recall@5 တွက်ချက်ပါ။

**Hints:** `v[:256]` ဖြင့် dimension ဖြတ်ယူပါ။ Full 768-dim ၏ top-5 ကို ground truth အဖြစ် ယူပါ။ Recall@5 = overlap / 5။ Vectors ကို seed ပါသော `random.Random(42)` ဖြင့် တည်ဆောက်ပါ (deterministic ဖြစ်စေရန်)။

**Expected behavior:** Truncated 256-dim version သည် 768-dim ၏ top-5 ထဲမှ အများစုကို ပြန်လည်ရရှိသည် (recall@5 < 1.0 ဖြစ်သော်လည်း 0.5 ထက် မြင့်သည်)။ Truncation ကြောင့် accuracy လျော့နည်းသွားကြောင်း ကိန်းဂဏန်းဖြင့် တွေ့ရသည်။

## လေ့ကျင့်ခန်း ၅ — Text Cache နှင့် Batch Encoding

`EmbeddingCache` class ရေးပါ — dict-based cache နှင့် `encode_batch(texts)` method ပါဝင်ရမည်။ Encoding အတွက် `hashlib.sha256(text)` ၏ hex digest ရှေ့ 16 လုံးကို stand-in vector အဖြစ် သုံးပါ — `# No real model call at runtime: deterministic stand-in` comment ထည့်ပါ။

**Hints:** Cache key ကို (model_name, text) tuple ဖြစ်စေပါ — version ကွဲပြားသောအခါ collision မဖြစ်စေရန်။ Text တစ်ခုကို နှစ်ကြိမ် encode လုပ်ပါက ဒုတိယအကြိမ်တွင် cache hit ဖြစ်ရမည်။

**Expected behavior:** Batch တစ်ခုကို နှစ်ကြိမ် encode လုပ်ပါက ဒုတိယအကြိမ်တွင် vectors တူညီပြီး cache hit အရေအတွက် တိုးလာသည်။ Model name ပြောင်းလဲပါက cache miss ဖြစ်သည်။

## လေ့ကျင့်ခန်း ၆ — Multilingual Corpus သတိထားစရာ

မြန်မာစာ (Unicode) နှင့် English ရောနှောထားသော texts ငါးခုအတွက် character-level normalization pipeline ရေးပါ — NFC normalize (`unicodedata.normalize('NFC', ...)`)၊ whitespace collapse၊ character limit truncation တို့ ပါဝင်ရမည်။ ပြီးလျှင် pipeline အဆင့်တစ်ခုစီ၏ သက်ရောက်မှုကို ရှင်းပြပါ။

**Hints:** မြန်မာစာတွင် combining marks များပြားသဖြင့် normalization သည် အရေးကြီးသည်။ `unicodedata` module သည် standard library ဖြစ်သည်။ Truncation တွင် grapheme cluster ဖြတ်မိနိုင်ခြေကို ကြိုတင်ယူဆချက် (assumption) အဖြစ် ဖော်ပြပါ။

**Expected behavior:** ရောနှောထားသော input များမှ NFC-normalized ဖြစ်ပြီး၊ whitespace တစ်ခုတည်းသာ ပါဝင်သော၊ character limit အတွင်းကျသော output များ ရရှိသည်။ အဆင့်တစ်ခုစီ၏ output ကို အစဉ်လိုက် တွေ့ရသည်။
