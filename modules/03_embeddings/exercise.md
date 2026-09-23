## လေ့ကျင့်ခန်း ၁ — Storage တွက်ချက်ခြင်း

Chunks တစ်သန်း (1,000,000)၊ dimension 768၊ fp32 (32-bit float) ဆိုပါစို့။ Vector storage အရွယ်ကို bytes နှင့် GB မှာ တွက်ပါ။ တွက်ချက်မှုအဆင့်တိုင်းကို ဖော်ပြပါ။

**Hints:** fp32 က 4 bytes ပါ။ စုစုပေါင်း bytes = chunk အရေအတွက် × dimension × 4 ပါ။ 1 GB = 1,000,000,000 bytes လို့ ယူဆလို့ရပါတယ်။

**Expected behavior:** 768 × 4 = 3,072 bytes per vector ရပါတယ်။ စုစုပေါင်း 3,072,000,000 bytes ≈ 3.07 GB ဆိုတဲ့ အဖြေ ရပါတယ်။

## လေ့ကျင့်ခန်း ၂ — L2 Normalization ရေးခြင်း

standard-library Python နဲ့ `l2_normalize(v)` function ရေးပါ။ Vector တစ်ခုရဲ့ norm (အလျား) နဲ့ ပိုင်းခြားပြီး အဖြေ vector ကို ပြန်ပါ။

**Hints:** norm = sqrt(sum of squared components) ပါ။ `math.sqrt` နဲ့ `math.fsum` ကိုသုံးပါ။ Norm = 0 ဖြစ်နေရင် ဘာမှမလုပ်ဘဲ vector အတိုင်းပြန်ပါ (division by zero ကို ကာကွယ်ပါ)။

**Expected behavior:** `l2_normalize([3.0, 4.0])` က `[0.6, 0.8]` ရပါတယ်။ Normalize ပြီးရင် norm = 1.0 ဖြစ်ပါတယ်။

## လေ့ကျင့်ခန်း ၃ — Dot Product နှင့် Cosine တူညီမှု

L2-normalized vectors နှစ်ခုအတွက် dot product နဲ့ cosine similarity တူညီကြောင်း စစ်ပါ။ cosine = dot(v1, v2) / (norm(v1) × norm(v2)) formula ကို ရေးပြပါ။

**Hints:** လေ့ကျင့်ခန်း ၂ က `l2_normalize` ကို အသုံးချပါ။ Norm 1 ဖြစ်နေရင် ဘာကြောင့် cosine နဲ့ dot တူရတယ်ဆိုတာ တစ်ကြောင်းရှင်းပြပါ။

**Expected behavior:** Normalize လုပ်ထားတဲ့ vectors နှစ်ခုမှာ dot product တန်ဖိုးနဲ့ cosine တန်ဖိုး တစ်ဝက်မှား (tolerance) အတွင်း တူညီပါတယ်။

## လေ့ကျင့်ခန်း ၄ — Matryoshka Dimension ဖြတ်ခြင်း

768-dim vector တစ်ခုကနေ ရှေ့ 256 dimensions ပဲ ယူပြီး ရှာဖွေမှု အမှန်တောင်းမှု (accuracy) နှိုင်းယှဉ်ပါ။ အလွယ်ချောက်စစ်ဆပုံစံ (a toy brute-force search) နဲ့ recall@5 တွက်ပါ။

**Hints:** `v[:256]` နဲ့ dimension ဖြတ်ပါ။ Full 768 ရဲ့ top-5 ကို ground truth အဖြစ်ယူပါ။ Recall@5 = overlap / 5 ပါ။ Vectors ကို seed ပါတဲ့ `random.Random(42)` နဲ့ တည်ဆောက်ပါ (deterministic ဖြစ်စေဖို့)။

**Expected behavior:** ဖြတ်ထားတဲ့ 256-dim version က 768-dim ရဲ့ top-5 ထဲက အများစု ပြန်ရပါတယ် (recall@5 < 1.0 ဒါပေမယ့် 0.5 ထက် ပိုမြင့်ပါတယ်)။ ဖြတ်လိုက်တဲ့အခါ accuracy လျော့သွားတယ်ဆိုတာ ကိန်းဂဏန်းနဲ့မြင်ရပါတယ်။

## လေ့ကျင့်ခန်း ၅ — Text Cache နဲ့ Batch Encoding

`EmbeddingCache` class ရေးပါ — dict-based cache နဲ့ `encode_batch(texts)` method ပါဝင်ရမယ်။ Encoding က `hashlib.sha256(text)` ရဲ့ hex digest ရှေ့ 16 လုံးကို stand-in vector အဖြစ်သုံးပါ (နမူနာအလွယ်အကူစား) — `# No real model call at runtime: deterministic stand-in` လို့ comment ထည့်ပါ။

**Hints:** Cache မှာ key က (model_name, text) tuple ဖြစ်စေပါ — version ခြားတဲ့အခါ collision မဖြစ်စေဖို့ပါ။ နှစ်ကြိမ် encoding လုပ်ရင် ဒုတိယအကြိမ်မှာ cache hit ဖြစ်ရပါတယ်။

**Expected behavior:** Batch တစ်ခုကို နှစ်ကြိမ် encoding လုပ်ရင် ဒုတိယအကြိမ်မှာ vector တူညီပြီး cache hit အရေအတွက် တိုးလာပါတယ်။ Model name ပြောင်းလိုက်ရင် cache miss ဖြစ်ပါတယ်။

## လေ့ကျင့်ခန်း ၆ — Multilingual Corpus သတိထားစရာ

မြန်မာစာ (Unicode) နဲ့ English ရောထားတဲ့ texts ငါးခုအတွက် character-level normalization pipeline ရေးပါ — NFC normalize (`unicodedata.normalize('NFC', ...)`)၊ whitespace ရှင်းလင်းခြင်း၊ စာကြောင်းရှည်ဖြတ်ခြင်း (character limit) လုပ်ပါ။ ပြီးရင် pipeline တစ်ဆင့်ချင်းစီ ဘာဖြစ်လဲဆိုတာ ရှင်းပြပါ။

**Hints:** မြန်မာစာက combining marks များပါတာကြောင့် normalization အရေးကြီးပါတယ်။ `unicodedata` module က standard library ပါ။ Truncation လုပ်တဲ့အခါ စာလုံးဖြတ်မိရင် ဘာဖြစ်နိုင်လဲ ဆိုတာ သုံးပိုင်ဆိုင်ခွင့် (license) မလို မိမိကြိုတင်ယူဆချက် (assumption) အဖြစ် ဖော်ပြပါ။

**Expected behavior:** နှစ်မျိုးရောထားတဲ့ input တွေက NFC-normalized၊ whitespace တစ်ခုတည်းသာရှိတဲ့၊ character limit အတွင်းရောက်တဲ့ output တွေ ရပါတယ်။ တစ်ခုပြီးတစ်ခု အဆင့်ဆင့် output ကို ရှင်းလင်းစွာမြင်ရပါတယ်။
