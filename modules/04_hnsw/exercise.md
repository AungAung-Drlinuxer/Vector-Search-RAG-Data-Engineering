## လေ့ကျင့်ခန်း ၁ — ef_search ပြောင်းပြီး recall တိုင်းချက်

**Task:** Python standard library ဖြင့် ရေးထားသော brute-force cosine search ကို gold answer အဖြစ် သတ်မှတ်ပါ။ ထို့နောက် `ef_search` (graph search တွင် ထိန်းထားသော candidate list အရွယ်အစား) ကို ၁၀၊ ၂၅၊ ၅၀ ဟု ပြောင်းလဲ၍ recall@10 ကို တွက်ချက်ပါ။

**Hints:** recall@10 = (gold top-10 နှင့် ကိုက်ညီသော result အရေအတွက်) ÷ 10။ Graph search ကို candidate list ကို ef_search အထိ ကန့်သတ်သော simulation အဖြစ် ရေးနိုင်သည်။

**Expected behavior:** ef_search တိုးသည်နှင့်အမျှ recall တက်ပြီး၊ evaluate လုပ်သော search step အရေအတွက် (latency proxy) လည်း တက်သည်ကို တွေ့ရမည်။

## လေ့ကျင့်ခန်း ၂ — M parameter ရဲ့ သက်ရောက်မှု

**Task:** Node တစ်ခုလျှင် edge အများဆုံး M ခု ရှိသော single-layer graph တစ်ခု တည်ဆောက်ပါ (pgvector docs တွင် `m` parameter)။ M = ၅၊ M = ၁၅၊ M = ၃၀ အတွက် စုစုပေါင်း edge အရေအတွက်ကို တွက်ချက်ပါ။

**Hints:** Directed edge တစ်ခုချင်းစီကို ရေတွက်ပြီး node တစ်ခုလျှင် M အထိ upper bound ယူပါ။ Node အရေအတွက်ကို "assumption: 1,000 nodes" ဟု အမှတ်အသား ထည့်ပါ။

**Expected behavior:** M တိုးပါက edge အရေအတွက် တိုးပြီး memory footprint တက်သည်ကို ကိန်းဂဏန်းဖြင့် ပြသနိုင်ရမည်။

## လေ့ကျင့်ခန်း ၃ — Index memory တွက်နည်း

**Task:** "Assumption: 1,000,000 vectors, 768 dimensions, fp32" dataset အတွက် raw vector data ၏ byte အရွယ်အစားကို တွက်ချက်ပါ။ ထို့နောက် HNSW graph edge data (M=16) အတွက် ထပ်ဆောင်း memory ကို ခန့်မှန်းပါ။

**Hints:** fp32 သည် dimension တစ်ခုလျှင် 4 bytes ယူသည်။ Edge data အတွက် edge တစ်ခုချင်းစီသည် int32 (4 bytes) neighbor id ယူသည်ဟု ယူဆ၍ တွက်ချက်ပါ။ Formula ကို code အတွင်း ပြသရမည်။

**Expected behavior:** Vector data အတွက် ~2.9 GB နှင့် graph edge data အတွက် ထပ်ဆောင်း တန်ဖိုး ထွက်ရှိပြီး formula အားလုံး မြင်ရမည်။

## လေ့ကျင့်ခန်း ၄ — Multi-layer graph simulation

**Task:** HNSW ၏ multi-layer သဘောတရား (arXiv 1603.09320 — upper layer တွင် node နည်းပြီး search ကို မြန်ဆန်စေသည်) ကို Python ဖြင့် ပုံဖော်ပါ။ Node များကို layer တက်ရောက်နိုင်မှု probability 0.5 ဖြင့် ထည့်သွင်းပြီး layer တစ်ခုချင်းစီ၏ node အရေအတွက်ကို ထုတ်ပြပါ။

**Hints:** `random.seed(42)` ဖြင့် deterministic ဖြစ်အောင် ပြုလုပ်ပါ။ Node တစ်ခု၏ layer ရောက်ရှိနိုင်မှုအတွက် geometric-style distribution (layer တစ်ခုတက်တိုင်း probability တစ်ဝက်) သုံးပါ။

**Expected behavior:** Layer 0 တွင် node အများဆုံး ရှိပြီး layer အမြင့်တက်သည်နှင့်အမျှ အရေအတွက် ထက်ဝက်စီ လျော့ကျသည့် distribution ကို print ဖြင့် မြင်ရမည်။

## လေ့ကျင့်ခန်း ၅ — Filtered search ရဲ့ recall ဆုံးရှုံးမှု

**Task:** Metadata tag ပါဝင်သော vector dataset (assumption: 500 items, tag "A"/"B" ခွဲထားသည်) တည်ဆောက်ပါ။ ထို့နောက် tag "A" သာ လက်ခံသော filtered search ၏ recall@5 ကို unfiltered search နှင့် နှိုင်းယှဉ်ပါ။

**Hints:** Filtered search တွင် graph traversal အတွင်း tag "B" node များကို ကျော်ရသဖြင့် ရောက်ရှိနိုင်သော candidate လျော့နည်းသည်။ Deterministic ဖြစ်ရန် `random.seed` သုံးပါ။

**Expected behavior:** Filter တင်းကျပ်လာပါက ef_search တူညီနေစဉ် recall ကျဆင်းခြင်း (သို့မဟုတ်) ef_search တိုးရန် လိုအပ်ခြင်းကို တွေ့ရမည်။ pgvector docs အရ filter နှင့် HNSW ဆက်နွယ်မှုကို မှတ်ချက်အဖြစ် ထည့်ပါ။

## လေ့ကျင့်ခန်း ၆ — Delete/update ရဲ့ ဆိုးကျိုးနဲ့ restore စစ်ဆေးခြင်း

**Task:** Graph အတွင်း node ၁၀၀ ခုကို delete လုပ်သော simulation ရေးပါ — delete သည် edge များကို ဖြတ်သည် (relink မပြုလုပ်ပါ)။ Delete မလုပ်မီ၊ delete ပြီးချိန်၊ rebuild ပြီးချိန် — recall@10 သုံးမျိုးလုံးကို နှိုင်းယှဉ် ထုတ်ပြပါ။

**Hints:** Delete လုပ်ထားသော node များကို search တွင် ကျော်ရမည်။ Rebuild ဆိုသည်မှာ ကျန်ရှိသော dataset အားလုံးဖြင့် graph အသစ် ပြန်လည် တည်ဆောက်ခြင်း ဖြစ်သည်။ Gold answer သည် brute-force search ဖြစ်သည်။

**Expected behavior:** Delete-only graph ၏ recall ကျပြီး rebuild ပြုလုပ်ပါက recall ပြန်တက်သည်ကို ကိန်းဂဏန်း သုံးခုဖြင့် မြင်ရမည်။ Delete နှင့် update က index quality ကို ထိခိုက်စေပုံကို မှတ်ချက်ဖြင့် ရှင်းပြပါ (pgvector docs အရ delete သည် index အတွင်း အမှတ်အသားကျန်ရစ်ပြီး rebuild လိုအပ်နိုင်သည်)။