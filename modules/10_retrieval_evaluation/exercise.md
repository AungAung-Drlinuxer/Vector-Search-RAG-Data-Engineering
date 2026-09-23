## လေ့ကျင့်ခန်း ၁ — Golden set ဖွဲ့ပါ

Task: Python dictionary နဲ့ golden set တစ်ခု ဆောက်ပါ။ key က query string၊ value က မှန်တဲ့ chunk id တွေရဲ့ list ဖြစ်ရမယ်။ query ၃ ခုထည့်ပါ။

**Hints:** Golden set ဆိုတာ "query → မှန်တဲ့ chunk အမှတ်" စာရင်းပါပဲ။ id က string သုံးလို့ရတယ်။

**Expected behavior:** `len(golden)` က 3 ပြပါတယ်။ တစ်ခုချင်းစီ value က list ဖြစ်ပါတယ်။

## လေ့ကျင့်ခန်း ၂ — recall@k တွက်ပါ

Task: `retrieved` list နဲ့ `relevant` list လက်ခံတဲ့ `recall_at_k(retrieved, relevant, k)` function ရေးပါ။ ပုံသေနည်း — recall@k = (မှန်တဲ့ chunk အရေအတွက်) / (relevant အားလုံးအရေအတွက်)။

**Hints:** `retrieved[:k]` နဲ့ `relevant` ကို set အဖြစ် `set()` နဲ့ ဖြတ်ပါ။ relevant စာရင်းမရှိရင် 0.0 return လုပ်ပါ။

**Expected behavior:** retrieved=[a,b,c,d], relevant=[a,c,x], k=4 မှာ 2/3 ဖြစ်တဲ့ 0.666... ထွက်ပါတယ်။ k=2 မှာ 0.5 ထွက်ပါတယ်။

## လေ့ကျင့်ခန်း ၃ — precision@k နဲ့ MRR တွက်ပါ

Task: `precision_at_k` နဲ့ `mrr` function နှစ်ခု ရေးပါ။ MRR ပုံသေနည်း — 1 / (ပထမဆုံး မှန်တဲ့ result ရဲ့ အဆင့်)။ မှန်တဲ့ result တစ်ခုမှ မရှိရင် MRR = 0။

**Hints:** rank က 1 ကစပါတယ်၊ index မဟုတ်ပါ။ `enumerate(retrieved, start=1)` သုံးပါ။

**Expected behavior:** retrieved=[a,b,c], relevant=[b] မှာ MRR = 0.5 ထွက်ပါတယ်။ precision@2 က 0.5 ထွက်ပါတယ်။

## လေ့ကျင့်ခန်း ၄ — nDCG@k တွက်ပါ

Task: `ndcg_at_k(retrieved, relevant, k)` function ရေးပါ။ ideal ranking (မှန်တာအားလုံးရှေ့) နဲ့ တကယ်ရတဲ့ ranking ကို ယှဉ်ပါ။ gain က rank အတွက် `1/log2(rank+1)` သုံးပါ။

**Hints:** DCG = sum(1/log2(rank+1)) for relevant hits။ IDCG က ideal အတွက် တူညီတဲ့ပုံသေနည်းပါ။ nDCG = DCG / IDCG။ ideal မှာ relevant အရေအတွက်နဲ့ k ထဲက ပိုနည်းတာကို သတိထားပါ။

**Expected behavior:** retrieved=[a,b,c,d], relevant=[a,b], k=4 မှာ nDCG = 1.0 ထွက်ပါတယ်။ relevant=[d] ဖြစ်ရင် 1/log2(5) ≈ 0.4307 ထွက်ပါတယ်။

## လေ့ကျင့်ခန်း ၅ — document-level အကဲဖြတ်ခြင်း ပြောင်းပါ

Task: chunk id တွေမှာ document id ပါတဲ့ format (`doc1#chunk2` လိုမျိုး) သုံးပါ။ `recall_at_k_doc` function ရေးပါ — document level မှာ ဘယ် document တစ်ခုမျှ ရှာတွေ့ဖို့ အရေအတွက်ပဲ ရေတွက်ပါ။

**Hints:** document id က `#` ရှေ့အပိုင်းပါ။ `split("#")[0]` သုံးလို့ရတယ်။ relevant documents set ဆောက်ပါ။

**Expected behavior:** retrieved=[doc1#1, doc2#1, doc1#2], relevant=[doc1#1, doc1#2, doc3#1], k=3 မှာ doc1 တောင်ရ၊ doc3 မရ — 2/3 ထွက်ပါတယ်။

## လေ့ကျင့်ခန်း ၆ — Regression gate နဲ့ drift စစ်ပါ

Task: baseline metrics dict တစ်ခု (ဥပမာ `{"recall@5": 0.9, "mrr": 0.8}` — ကိုယ်တိုင် သတ်မှတ်ထားတဲ့ တန်ဖိုးများပါ) နဲ့ current metrics dict ယှဉ်တဲ့ `regression_gate(baseline, current)` function ရေးပါ။ တန်ဖိုးတစ်ခုမျှ ကျသွားရင် `False` return လုပ်ပြီး ဘယ် metric ကျလဲ ပရင့်ထုတ်ပါ။

**Hints:** Drift ဆိုတာ metric တွေ အချိန်ကြာမှ ပြောင်းသွားတာကို ဆိုလိုတယ်။ baseline ထက် မနည်းဖို့ စစ်ပါ (`current[m] < baseline[m]`)။ ပုံစံကို file ထဲ မှတ်ထားပြီး CI မှာ run လို့ရအောင် exit code နဲ့ တွဲတာက တကယ့် project မှာ လုပ်ဖို့ပါ — ဒီလေ့ကျင့်ခန်းမှာ function အဆင့်ပဲ လုပ်ပါ။

**Expected behavior:** current = `{"recall@5": 0.85, "mrr": 0.82}` မှာ recall@5 ကျလို့ `False` ထွက်ပြီး `recall@5 dropped` ဆိုတာ ပရင့်ထုတ်ပါတယ်။ current အားလုံး ကောင်းရင် `True` ထွက်ပါတယ်။
