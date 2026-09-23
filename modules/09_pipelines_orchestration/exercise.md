## လေ့ကျင့်ခန်း ၁ — Idempotent ပြန်လုပ်တာ စမ်းကြည့်ပါ

Idempotent (တစ်ခါထက်ပိုပြီး လုပ်တဲ့အခါ ရလဒ် မပြောင်းတဲ့သဘော) ဂုဏ်သတ္တိကို Python နဲ့ ပြပါမယ်။

**Task:** တူညီတဲ့ record နှစ်ခါ ထည့်လိုက်တာနဲ့ တစ်ခါတည်း ထည့်လိုက်တာ ရလဒ် တူမယ်လို့ သက်သေပြတဲ့ function ရေးပါ။

**Hints:** content-hash (အကြောင်းအရာရဲ့ ထပ်ခါတလင်း hash) ကို key အဖြစ်သုံးပြီး dict ထဲ ထည့်ပါ။ `hashlib.sha256` နဲ့ content hash တွက်ပါ။

**Expected behavior:** ဖိုင်နှစ်ခါ run ရင် output အတူတူပါတယ်။ list ထဲ record ၁၀ ခုပဲ ရှိပြီး အရေအတွက် မတိုးဘူးဆိုတာ မြင်ရပါလိမ့်မယ်။

## လေ့ကျင့်ခန်း ၂ — Backfill rate limit တွက်ပါ

Backfill (အရင် data အားလုံးကို နောက်ကမှ ပြန်ထည့်တာ) မှာ rate limit အရေးကြီးပါတယ်။

**Task:** ဒီ assumption နဲ့ အချိန်တွက်ပါ — chunk ၁,၀၀၀,၀၀၀ ခု၊ တစ်စက္ကန့်မှာ ၅,၀၀၀ chunk စီ process လုပ်လို့ရတယ်ဆိုပါ။

**Hints:** အချိန် = စုစုပေါင်းအရေအတွက် ÷ တစ်စက္ကန့် rate ဆိုတဲ formula ပြပါ။ စက္ကန့်ကနေ နာရီပြောင်းပါ။

**Expected behavior:** အချိန်ပေါင်း (၂၀၀ စက္ကန့် ≈ ၀.၀၆ နာရီ) ကို တွက်ဖို့ formula နဲ့အတူ ပြပါမယ်။ ကိုယ်တွက်ထားတဲ့ ဂဏန်းနဲ့ output ကို ကိုက်ညီစေပါ။

## လေ့ကျင့်ခန်း ၃ — Dead-letter queue နဲ့ retry ရေးပါ

Batch pipeline မှာ fail တဲ့ record တွေ မပျောက်သွားအောင် စီမံပါမယ်။

**Task:** Record တစ်ချို့ကို process လုပ်ရင် exception ပေးမယ်ဆိုပြီး၊ retry (ပြန်စမ်းခြင်း) ၃ ကြိမ် လုပ်ပြီး မအောင်ရင် dead-letter list ထဲ ထည့်တဲ့ Python function ရေးပါ။

**Hints:** `random` သုံးတော့ မရဘူးနော် — record id အမှတ်စဉ်အရ မှန်ချက် deterministic အရင်းပြပြီး fail အဖြစ် သတ်မှတ်ပါ။

**Expected behavior:** Fail တဲ့ record id တွေကို dead-letter ထဲ မြင်ရပြီး retry ၃ ကြိမ် လုပ်မှ ထည့်တယ်ဆိုတာ counter နဲ့ ပြနိုင်ပါတယ်။ Output ကို run တိုင်း တူစေပါ။

## လေ့ကျင့်ခန်း ၄ — Dual-write နဲ့ shadow index ပြောင်းကြည့်ပါ

Embedding version ပြောင်းတဲ့အခါ migration အဆင့်တွေကို simulation လုပ်ပါမယ်။

**Task:** Shadow index (ဟိုးအောက်မှာ အသစ် version ကို တိတ်တဆိတ် ဆောက်ထားတဲ့ index) ကို အရင် ဖြည့်ပြီး၊ cut-over (အသစ်ကို ကူးပြောင်းလိုက်တဲ့ အချက်) အချိန်မှာ read path ကို ပြောင်းတဲ့ script ရေးပါ။

**Hints:** Version string ("v1", "v2") နဲ့ index dict နှစ်ခု ထားပါ။ Cut-over မတိုင်ခင် query ရလဒ်ကို နှိုင်းယှဉ်ပြပါ။

**Expected behavior:** Cut-over မတိုင်ခင် v1 ရလဒ်ပဲ ပြပြီး ပြီးတော့ v2 ရလဒ် ပြမယ်ဆိုတာ output မှာ မြင်ရပါလိမ့်မယ်။

## လေ့ကျင့်ခန်း ၅ — DAG dependency ကို topological sort နဲ့ ဖြေရှင်းပါ

Airflow နဲ့ Dagster က task တွေကို DAG (directed acyclic graph — ညွှန်ပြမှု စွန်းမရှိတဲ့ graph) အဖြစ် မှတ်ယူပါတယ်။

**Task:** Task dependency table တစ်ခုကနေ run order တွက်ပေးတဲ့ topological sort function ရေးပါ။

**Hints:** `graphlib.TopologicalSorter` (standard library, Python ၃.၉+) သုံးပါ။ "chunk" → "embed" → "index" → "validate" dependency ဆောက်ပါ။

**Expected behavior:** Task တွေကို မှီခိုမှု အစီအစဉ်အတိုင်း run မယ့် order မှာ ထွက်လာပါတယ်။ Dependency ပျက်နေရင် `CycleError` ပြမယ်လို့ စမ်းကြည့်ပါ။

## လေ့ကျင့်ခန်း ၆ — Streaming window နဲ့ CDC style changelog စမ်းပါ

Streaming ingestion မှာ changelog ကို window ခွဲပြီး ချုပ်တာ လေ့ကျင့်ပါမယ်။

**Task:** Change data capture (data ပြောင်းလဲမှုကို ဖမ်းယူတဲနည်း) သဘောနဲ့ record တစ်ခုရဲ့ version နှစ်ခုကို diff လုပ်ပြီး INSERT/UPDATE/DELETE event ထုတ်ပေးတဲ Python function ရေးပါ။

**Hints:** Primary key နဲ့ ဟောင်း version၊ အသစ် version dict နှစ်ခု နှိုင်းယှဉ်ပါ။ Batch window ၅ ခုအတွက် event list ကို အရင် ပြပါ။

**Expected behavior:** ထည့်တဲ့ record တွေကို INSERT event၊ ပြောင်းတဲ့ record တွေကို UPDATE event၊ ဖျက်တဲ့ record တွေကို DELETE event အဖြစ် အတိအကျ မြင်ရပါလိမ့်မယ်။ Output ကို run တိုင်း တူညီအောင် deterministic ဖြစ်စေပါ။

အားလုံးအတွက် သတိပြုရမှာက — ဒီလေ့ကျင့်ခန်းတွေက runtime မှာ database ချိတ်မထားပါဘူးနော်။ စင်တာတော့ exercise ၅ မှာ ပြခဲ့သလို DAG သဘောကို Airflow (https://airflow.apache.org/docs/) နဲ့ Dagster (https://docs.dagster.io/) official doc တွေမှာ ဆက်ဖတ်ပါ။ pgvector အတွက်ကတော့ https://github.com/pgvector/pgvector မှာ ရှိပါတယ်။
