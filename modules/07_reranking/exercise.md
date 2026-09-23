## လေ့ကျင့်ခန်း ၁ — Bi-encoder နဲ့ Cross-encoder ကွာခြားချက် ဖော်ပြခြင်း

**Task:** bi-encoder နဲ့ cross-encoder ရဲ့ ကွာခြားချက်ကို ကိုယ်ပိုင် စကားလုံးတွေနဲ့ ၃ ကြိမ် ရေးပါ။ တစ်ခုစီအတွက် ဘယ်အချိန် သုံးသင့်တယ်ဆိုတာလည်း ထည့်ပြောပေးပါ။ ( sbert.net မှာ ဖော်ပြထားတဲ့ အတိုအဆှန်အတိုင်း ဖြစ်ရမယ်နော် )

**Hints:** bi-encoder က query နဲ့ document ကို သီးသန့် embed လုပ်တယ်။ cross-encoder က နှစ်ခုကို တွဲပြီး တစ်ပြိုင်နက် သုံးသပ်တယ်။ latency က အဓိက ခွဲခြားချက်ပါ။

**Expected behavior:** ရလဒ်မှာ embedding သီးသန့် သုံးတဲ့ အချက်၊ တွဲသုံးတဲ့ အချက်၊ နဲ့ offline တွင် cache လုပ်လို့ ရ/မရ ကွာခြားချက် ပါဝင်ပါတယ်။

## လေ့ကျင့်ခန်း ၂ — Cosine Score နဲ့ Manual Reranking

**Task:** query တစ်ခုနဲ့ document ၅ ခုရှိတဲ့ စာရင်းတစ်ခု သတ်မှတ်ပါ။ ပထမ ဦးစွာ cosine similarity နဲ့ score တွေ တွက်ပါ။ ပြီးရင် score အမြင့်ဆုံး ၃ ခုကို ပြန်ရွေးပြပါ။ ရွေးထားတဲ့ ၃ ခုကို နောက်ဆုံးမှာ အမြင့်ဆုံးက ရှေ့ရှိစေမယ့် အစီအစဉ်နဲ့ ထုတ်ပြပါ။

**Hints:** standard library ထဲက math နဲ့ sorted ကိုသာ သုံးပါ။ key=lambda နဲ့ reverse=True ကို သတိရပါ။

**Expected behavior:** Program က document ၅ ခုလုံးရဲ့ cosine score ကို ပုံနှိပ်ပြီး၊ top-3 rerank လုပ်ထားတဲ့ အစီအစဉ်ကို နောက်ဆုံးမှာ ပြပါတယ်။

## လေ့ကျင့်ခန်း ၃ — Latency ကုန်ကျစရိတ် တွက်ချက်ခြင်း

**Task:** reranking တစ်ခါလုပ်ရင် ဘယ်လောက် စရိတ်ကြာတယ်ဆိုတာ တွက်ပြပါ။ ယူဆချက် — cross-encoder တစ်ခါ call လုပ်ရင် 50 ms ကြာတယ်၊ top-k မှာ 20 ရှိတယ်။ ကျွန်တော်တို့ rerank မလုပ်ဘဲ retrieve တာနဲ့ ဘယ်လောက် ခြားတယ်ဆိုတာ ရှင်းပြပါ။

**Hints:** 20 × 50 ms = 1,000 ms ပါ။ တွက်ချက်ပုံ formula ကို code ထဲမှာ comment နဲ့ ပြပါ။

**Expected behavior:** Code က တွက်ချက်မှု အဆင့်ဆင့်ကို ပုံနှိပ်ပြပြီး နောက်ဆုံးမှာ စုစုပေါင်း latency ကို ပြပါတယ်။ ကိန်းဂဏန်းတွေက ယူဆချက်ပေါ် မူတည်တယ်ဆိုတာ comment လို့ ရေးပါ။

## လေ့ကျင့်ခန်း ၄ — HyDE (Hypothetical Document Embedding) စမ်းသပ်ခြင်း

**Task:** query တစ်ခုကို "hypothetical answer" (တွေးဆ ထားတဲ့ အဖြေစာ) တစ်ခုအဖြစ် ပြောင်းရေးပါ။ ပြီးရင် ထိုစာနဲ့ document တွေကို cosine similarity တွက်ပါ။ query တိုက်ရိုက် သုံးတဲ့ score နဲ့ နှိုင်းယှဉ်ပြပါ။

**Hints:** တကယ့် LLM မသုံးပါနော် — hypothetical answer ကို code ထဲမှာ hardcoded လုပ်ပါ။ ဘာကြောင့်လဲဆိုတော့ lesson တွေက offline ဖြစ်ရလို့ပါ။ arxiv.org/abs/2212.10496 က HyDE စာတမ်း ဖြစ်ပါတယ်။

**Expected behavior:** နှစ်မျိုးသော score list (query-direct နဲ့ HyDE) ပုံနှိပ်ပြီး ဘယ်ဟာ ပိုတူညီမှုရှိတယ်ဆိုတာ ရှင်းပြနိုင်ပါတယ်။

## လေ့ကျင့်ခန်း ၅ — Multi-query Expansion နဲ့ RRF Fusion

**Task:** query တစ်ခုကို မတူတဲ့ ပုံစံ ၃ မျိုးဖြင့် ရေးပါ ( paraphrase ၃ ခု )။ တစ်ခုစီအတွက် ranked list တစ်ခုစီ သတ်မှတ်ပါ။ ပြီးရင် Reciprocal Rank Fusion (RRF) နဲ့ တစ်ခုတည်းသော ranking ပြုလုပ်ပါ။

**Hints:** RRF formula — score = sum of 1 / (k + rank)၊ k = 60 ကို ယူဆပါ။ docs.ragas.io က metrics တွေအတွက် တရားဝင် documentation ပါ။

**Expected behavior:** နောက်ဆုံးမှာ fused ranking က document ID တွေ အစီအစဉ်မှန်နဲ့ ထွက်ပါတယ်။ တစ် query ချင်းရဲ့ rank တွေက အလွယ် ကြည့်နိုင်ရပါတယ်။

## လေ့ကျင့်ခန်း ၆ — MMR (Maximal Marginal Relevance) အပြည့်အစုံ

**Task:** document ၆ ခုရဲ့ embedding တွေ သတ်မှတ်ပါ။ lambda တန်ဖိုး ၂ မျိုး (0.3 နဲ့ 0.9) သုံးပြီး MMR နဲ့ ရွေးပါ။ နှစ်ခုစလုံးရဲ့ ရလဒ်ကို နှိုင်းယှဉ်ပြပါ။

**Hints:** MMR formula — score = lambda × sim(q, d) − (1 − lambda) × max sim(d, selected)။ selected list ဗလာ ဆိုရင် ပထမ ရွေးချယ်မှုက အမြင့်ဆုံး relevance အတိုင်း ဖြစ်ပါတယ်။

**Expected behavior:** lambda = 0.9 မှာ relevance က ပိုထင်ရှားပြီး၊ lambda = 0.3 မှာ diversity ( ရလဒ် ကွဲပြားမှု ) က ပိုထင်ရှားတာ မြင်ရပါတယ်။ ရလဒ် ကွာခြားချက်ကို ကိုယ်ပိုင် စာသားနဲ့ ရှင်းပြပါ။
