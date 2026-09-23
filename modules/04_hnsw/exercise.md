## လေ့ကျင့်ခန်း ၁ — ef_search ပြောင်းပြီး recall တိုင်းချက်

**Task:** Python standard library နဲ့ ရေးထားတဲ့ brute-force cosine search ကို gold answer အဖြစ် ယူပါတယ်။ ပြီးရင် `ef_search` value (candidate အရေအတွက် — graph search မှာ စူးစမ်းသည့် အနိမ့်အမြင့်နယ်နိမိတ်) ကို ၁၀၊ ၂၅၊ ၅၀ ဆိုပြီး ပြောင်းပြီး recall@10 ကို တွက်ပါ။

**Hints:** recall@10 = (gold top-10 ထဲမှာ graph result နဲ့ တူတဲ့ အရေအတွက်) ÷ 10 ပါ။ graph search ကို candidate list ကို ef_search အထိ ဖွင့်ထားတဲ့ simulation နဲ့ ရေးနိုင်ပါတယ်။

**Expected behavior:** ef_search တန်ဖိုးတက်တာနဲ့ recall တက်ပြီး latency ဆိုတာ (တွက်ရသမျှ search step အရေအတွက်) လည်းတက်တာ မြင်ရပါမယ်။

## လေ့ကျင့်ခန်း ၂ — M parameter ရဲ့ သက်ရောက်မှု

**Task:** ရိုးရိုး single-layer graph တစ်ခုကို node တစ်ခုမှာ edge အများဆုံး M ခုနဲ့ ဆောက်ပါ (M — node တစ်ခုချင်းချင်း ချိတ်ဆက်မှု edge အရေအတွက်၊ pgvector docs မှာ `m` parameter လို့ ခေါ်ပါတယ်)။ M = ၅၊ M = ၁၅၊ M = ၃၀ အတွက် edge စုစုပေါင်း အရေအတွက်ကို တွက်ပြပါ။

**Hints:** edge တွက်ရာမှာ directed edge တစ်ခုစီကို ရေတွက်ပြီး တစ်ဖက်စီမှာ M အထိ အမြင့်ဆုံး အရေအတွက် ယူပါတယ်။ node အရေအတွက်ကို "assumption: 1,000 nodes" လို့ အမှတ်အသား ဝင်ရပါမယ်။

**Expected behavior:** M တက်ရင် edge အရေအတွက်တက်တယ်၊ ဒါက memory တက်စေတယ်ဆိုတာ ဂဏန်းနဲ့ ပြနိုင်ရပါမယ်။

## လေ့ကျင့်ခန်း ၃ — Index memory တွက်နည်း

**Task:** "Assumption: 1,000,000 vectors, 768 dimensions, fp32" ဆိုတဲ့ dataset အတွက် raw vector data တစ်ခုတည်းရဲ့ byte အရွယ်ကို တွက်ပါ။ ပြီးတော့ HNSW graph edge data (M=16) အတွက် ထပ်ဆောင်း memory ကိုလည်း ခန့်မှန်းပြပါ။

**Hints:** fp32 က dimension တစ်ခုမှာ 4 bytes ယူပါတယ်။ edge data အတွက် node တစ်ခါစီမှာ edge တစ်ခုချင်းစီက int32 (4 bytes) neighbor id ယူတယ်လို့ ယူဆပြီး တွက်ပါ။ ပုံသေနည်းကို ကုဒ်ထဲမှာ ပြရပါမယ်။

**Expected behavior:** vector data အတွက် ~2.9 GB နဲ့ graph edge data အတွက် ထပ်ဆောင်း တန်ဖိုး ထွက်ပြီး ပုံသေနည်းအားလုံး မြင်ရမယ်။

## လေ့ကျင့်ခန်း ၄ — Multi-layer graph simulation

**Task:** HNSW ရဲ့ multi-layer သဘောတရား (arXiv 1603.09320 — layer အပေါ်ဘက်မှာ node နည်းပြီး ရှာဖွေမှုကို မြန်စေတဲ့ ပုံစံ) ကို ရိုးရိုး Python နဲ့ ပုံဖော်ပါ။ Node တွေကို layer တွေထဲ တက်ရနိုင်မှု probability 0.5 နဲ့ ထည့်ပြီး layer တစ်ခုချင်းစီမှာ node အရေအတွက် ထုတ်ပြပါ။

**Hints:** `random.seed(42)` နဲ့ deterministic ဖြစ်အောင် လုပ်ပါ။ node id တစ်ခုက layer တစ်ခုကို ရောက်ရနိုင်ခြေမှာ geometric-style distribution (layer တက်တိုင်း တဝက်စီ) သုံးပါ။

**Expected behavior:** layer 0 မှာ node အများဆုံးရှိပြီး အပေါ်တက်တာနဲ့ အရေအတွက် ဆယ်ဆစီ လျော့တာကို distribution print နဲ့ မြင်ရပါမယ်။

## လေ့ကျင့်ခန်း ၅ — Filtered search ရဲ့ recall ဆုံးရှုံးမှု

**Task:** Metadata tag ပါတဲ့ vector dataset အသေးလေး (assumption: 500 items, tag "A"/"B" ခွဲထားတယ်) ကို ဆောက်ပါ။ ပြီးတော့ tag "A" သာ လက်ခံတဲ့ filtered search ရဲ့ recall@5 ကို unfiltered search နဲ့ နှိုင်းယှဉ်ပြပါ။

**Hints:** Filtered search မှာ graph ကို လမ်းလျှောက်ရင်း tag "B" node တွေကို ကျော်ရတယ် — ဒါက candidate ရောက်နိုင်မှုကို လျှော့စေပါတယ်။ deterministic ဖြစ်ဖို့ `random.seed` သုံးပါ။

**Expected behavior:** Filter တက်လာတာနဲ့ ef_search တူတူမှာ recall ကျဆင်းတာ (သို့) ef_search တိုးဖို့ လိုအပ်တာ မြင်ရပါမယ်။ pgvector docs က filter နဲ့ HNSW ဆက်ဆံရေးကို မှတ်ချက်နဲ့ ထည့်ပါ။

## လေ့ကျင့်ခန်း ၆ — Delete/update ရဲ့ ဆိုးကျိုးနဲ့ restore စစ်ဆေးခြင်း

**Task:** Graph ထဲက node ၁၀၀ ခုကို delete လုပ်တဲ့ simulation ရေးပါ — delete ဆိုတာ edge တွေကို ဖြတ်တယ် (relink မလုပ်ဘဲ)။ Delete မလုပ်ခင်နဲ့ ပြီးလို့ graph ကို rebuild လုပ်ပြီးချိန် နှိုင်းယှဉ် recall@10 သုံးမျိုးလုံး ထုတ်ပြပါ။

**Hints:** Delete လုပ်ထားတဲ့ node တွေကို search မှာ ကျော်ရပါမယ်။ Rebuild ဆိုတာ delete လုပ်ပြီး dataset အားလုံးနဲ့ graph အသစ်ပြန်ဆောက်တာပါ။ gold answer က brute-force ကြီးပါ။

**Expected behavior:** Delete only လုပ်ထားတဲ့ graph ရဲ့ recall ကကျပြီး rebuild လုပ်ရင် recall ပြန်တက်တာ ကိန်းဂဏန်းသုံးခုနဲ့ မြင်ရပါမယ်။ Delete နဲ့ update က index quality ထိခိုက်စေတဲ့အကြောင်းကို မှတ်ချက်ထဲ ရှင်းပြပါ (pgvector docs အရ delete က index ထဲဖျက်ပြီး rebuild လိုအပ်နိုင်ပါတယ်)။
