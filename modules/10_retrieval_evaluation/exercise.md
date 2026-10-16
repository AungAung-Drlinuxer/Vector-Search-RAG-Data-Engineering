## လေ့ကျင့်ခန်း ၁ — Golden set ဖွဲ့ပါ

Task: Python dictionary ဖြင့် golden set တစ်ခု တည်ဆောက်ပါ။ Key သည် query string၊ value သည် relevant chunk id list ဖြစ်ရမည်။ Query ၃ ခု ထည့်သွင်းပါ။

**Hints:** Golden set သည် "query → relevant chunk ids" mapping ဖြစ်သည်။ Chunk id အဖြစ် string သုံးနိုင်သည်။

**Expected behavior:** `len(golden)` သည် 3 return ပြန်သည်။ Value တစ်ခုချင်းစီသည် list type ဖြစ်သည်။

## လေ့ကျင့်ခန်း ၂ — recall@k တွက်ပါ

Task: `retrieved` list နှင့် `relevant` list လက်ခံသော `recall_at_k(retrieved, relevant, k)` function ရေးပါ။ Formula — recall@k = (top-k အတွင်းရှိ relevant အရေအတွက်) / (relevant စုစုပေါင်း)။

**Hints:** `retrieved[:k]` နှင့် `relevant` ကို `set()` ဖြင့် set အဖြစ်ပြောင်း၍ overlap ရှာပါ။ Relevant စာရင်း empty ဖြစ်ပါက 0.0 return ပြန်ပါ။

**Expected behavior:** retrieved=[a,b,c,d], relevant=[a,c,x], k=4 တွင် 2/3 = 0.666... ထွက်သည်။ k=2 တွင် 0.5 ထွက်သည်။

## လေ့ကျင့်ခန်း ၃ — precision@k နဲ့ MRR တွက်ပါ

Task: `precision_at_k` နှင့် `mrr` function နှစ်ခု ရေးပါ။ MRR formula — 1 / (ပထမဆုံး relevant result ၏ rank)။ Relevant result တစ်ခုမှ မရှိပါက MRR = 0 ဖြစ်သည်။

**Hints:** Rank သည် 1-based ဖြစ်ပြီး index မဟုတ်ပါ။ `enumerate(retrieved, start=1)` သုံးပါ။

**Expected behavior:** retrieved=[a,b,c], relevant=[b] တွင် MRR = 0.5 ထွက်သည်။ precision@2 သည် 0.5 ထွက်သည်။

## လေ့ကျင့်ခန်း ၄ — nDCG@k တွက်ပါ

Task: `ndcg_at_k(retrieved, relevant, k)` function ရေးပါ။ Ideal ranking (relevant အားလုံး ရှေ့ဆုံး) နှင့် actual ranking ကို နှိုင်းယှဉ်ပါ။ Gain အတွက် `1/log2(rank+1)` သုံးပါ။

**Hints:** DCG = sum(1/log2(rank+1)) over relevant hits။ IDCG အတွက်လည်း ideal ranking ပေါ်တွင် တူညီသော formula သုံးသည်။ nDCG = DCG / IDCG။ Ideal ranking တွင် min(|relevant|, k) ကို သုံးရမည်ကို သတိပြုပါ။

**Expected behavior:** retrieved=[a,b,c,d], relevant=[a,b], k=4 တွင် nDCG = 1.0 ထွက်သည်။ relevant=[d] ဖြစ်ပါက 1/log2(5) ≈ 0.4307 ထွက်သည်။

## လေ့ကျင့်ခန်း ၅ — document-level အကဲဖြတ်ခြင်း ပြောင်းပါ

Task: Chunk id တွင် document id ပါဝင်သော format (`doc1#chunk2` ပုံစံ) သုံးပါ။ `recall_at_k_doc` function ရေးပါ — relevant chunk တစ်ခုကို ၎င်း၏ document top-k အတွင်း ရောက်ရှိပါက covered အဖြစ် ရေတွက်ပါ။

**Hints:** Document id သည် `#` ၏ ရှေ့အပိုင်းဖြစ်ပြီး `split("#")[0]` ဖြင့် ရယူနိုင်သည်။ Retrieved docs set ကို အရင်တည်ဆောက်ပါ။

**Expected behavior:** retrieved=[doc1#1, doc2#1, doc1#2], relevant=[doc1#1, doc1#2, doc3#1], k=3 တွင် doc1 covered ဖြစ်ပြီး doc3 မ covered ဖြစ်သဖြင့် 2/3 ထွက်သည်။

## လေ့ကျင့်ခန်း ၆ — Regression gate နဲ့ drift စစ်ပါ

Task: Baseline metrics dict တစ်ခု (ဥပမာ `{"recall@5": 0.9, "mrr": 0.8}` — ကိုယ်တိုင်သတ်မှတ်ထားသော တန်ဖိုးများ) နှင့် current metrics dict ကို နှိုင်းယှဉ်သော `regression_gate(baseline, current)` function ရေးပါ။ Metric တစ်ခုခု ကျဆင်းပါက `False` return ပြန်ပြီး ကျဆင်းသော metric ကို print ထုတ်ပါ။

**Hints:** Drift ဆိုသည်မှာ metric များ အချိန်ကြာလာသည်နှင့်အမျှ တဖြည်းဖြည်း ကျဆင်းလာခြင်းဖြစ်သည်။ Metric တစ်ခုချင်းစီကို baseline နှင့် နှိုင်းယှဉ်ပါ (`current[m] < baseline[m]`)။ ရလဒ်ကို file တွင် persist လုပ်ပြီး CI တွင် exit code ဖြင့် ချိတ်ဆက်ခြင်းသည် production အဆင့် အလုပ်ဖြစ်သည် — ဒီလေ့ကျင့်ခန်းတွင် function အဆင့်သာ implement လုပ်ပါ။

**Expected behavior:** current = `{"recall@5": 0.85, "mrr": 0.82}` တွင် recall@5 ကျဆင်းသဖြင့် `False` return ပြန်ပြီး `recall@5 dropped` ကို print ထုတ်သည်။ Current metric အားလုံး baseline အထက် ရှိပါက `True` return ပြန်သည်။
