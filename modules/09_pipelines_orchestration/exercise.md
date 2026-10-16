## လေ့ကျင့်ခန်း ၁ — Idempotent ပြန်လုပ်တာ စမ်းကြည့်ပါ

Idempotent ဂုဏ်သတ္တိကို Python ဖြင့် implement လုပ်ပြမည်။

**Task:** တူညီသော record ကို နှစ်ကြိမ် insert လုပ်ခြင်းနှင့် တစ်ကြိမ် insert လုပ်ခြင်း၏ ရလဒ် တူညီကြောင်း သက်သေပြသော function ရေးပါ။

**Hints:** content hash ကို key အဖြစ်သုံးပြီး dict ထဲ ထည့်ပါ။ `hashlib.sha256` ဖြင့် content hash တွက်ပါ။

**Expected behavior:** နှစ်ကြိမ် run သော်လည်း output တူညီရမည်။ Store ထဲတွင် record ၁၀ ခုသာ ရှိပြီး အရေအတွက် မတိုးကြောင်း တွေ့ရမည်။

## လေ့ကျင့်ခန်း ၂ — Backfill rate limit တွက်ပါ

Backfill တွင် rate limit စီမံမှုသည် အရေးပါသည်။

**Task:** အောက်ပါ assumption ဖြင့် ကြာချိန်ကို တွက်ချက်ပါ — chunk ၁,၀၀၀,၀၀၀ ခု၊ throughput ၅,၀၀၀ chunks/sec။

**Hints:** အချိန် = စုစုပေါင်းအရေအတွက် ÷ rate formula ကို ပြပါ။ စက္ကန့်မှ နာရီသို့ ပြောင်းလဲပါ။

**Expected behavior:** စုစုပေါင်းကြာချိန် (၂၀၀ စက္ကန့် ≈ ၀.၀၆ နာရီ) ကို formula နှင့်အတူ print ထုတ်ပါ။ တွက်ချက်ထားသော တန်ဖိုးနှင့် output ကိုက်ညီရမည်။

## လေ့ကျင့်ခန်း ၃ — Dead-letter queue နဲ့ retry ရေးပါ

Batch pipeline တွင် fail ဖြစ်သော record များ မပျောက်ဆုံးစေရန် စီမံမည်။

**Task:** Record အချို့ process လုပ်ရာတွင် exception ပေးမည့် simulation တွင် retry ၃ ကြိမ် ပြုလုပ်ပြီး မအောင်မြင်ပါက dead-letter list ထဲ ထည့်သော Python function ရေးပါ။

**Hints:** `random` မသုံးရပါ — record id အပေါ် အခြေခံသော deterministic failure rule သတ်မှတ်ပါ။

**Expected behavior:** Fail ဖြစ်သော record id များကို dead-letter ထဲ တွေ့ရမည်။ Retry ၃ ကြိမ် ပြည့်မှသာ ထည့်ကြောင်း counter ဖြင့် ပြနိုင်ရမည်။ Output သည် run တိုင်း တူညီရမည်။

## လေ့ကျင့်ခန်း ၄ — Dual-write နဲ့ shadow index ပြောင်းကြည့်ပါ

Embedding version ပြောင်းလဲချိန် migration အဆင့်များကို simulation လုပ်မည်။

**Task:** Shadow index ကို အရင်ဖြည့်ပြီး cut-over အချိန်တွင် read path ကို ပြောင်းလဲသော script ရေးပါ။

**Hints:** Version string ("v1", "v2") ဖြင့် index dict နှစ်ခု ထားပါ။ Cut-over မတိုင်မီ query result ကို နှိုင်းယှဉ်ပြပါ။

**Expected behavior:** Cut-over မတိုင်မီ v1 result သာ ပြပြီး cut-over နောက်ပိုင်းတွင် v2 result ပြကြောင်း output တွင် တွေ့ရမည်။

## လေ့ကျင့်ခန်း ၅ — DAG dependency ကို topological sort နဲ့ ဖြေရှင်းပါ

Airflow နှင့် Dagster တို့သည် task များကို DAG (Directed Acyclic Graph) အဖြစ် ကိုင်တွယ်သည်။

**Task:** Task dependency table မှ run order တွက်ပေးသော topological sort function ရေးပါ။

**Hints:** `graphlib.TopologicalSorter` (standard library, Python ၃.၉+) သုံးပါ။ "chunk" → "embed" → "index" → "validate" dependency တည်ဆောက်ပါ။

**Expected behavior:** Task များသည် dependency အစီအစဉ်အတိုင်း run order တွင် ထွက်ပေါ်ရမည်။ Dependency cycle ရှိပါက `CycleError` ထွက်ကြောင်း စမ်းသပ်ပါ။

## လေ့ကျင့်ခန်း ၆ — Streaming window နဲ့ CDC style changelog စမ်းပါ

Streaming ingestion တွင် changelog ကို window ခွဲ၍ ထုတ်ယူခြင်းကို လေ့ကျင့်မည်။

**Task:** CDC သဘောတရားအတိုင်း record snapshot နှစ်ခုကို diff လုပ်ပြီး INSERT/UPDATE/DELETE event ထုတ်ပေးသော Python function ရေးပါ။

**Hints:** Primary key ဖြင့် old version နှင့် new version dict နှစ်ခုကို နှိုင်းယှဉ်ပါ။ Batch window ၅ ခုအတွက် event list ကို အစဉ်လိုက် print ထုတ်ပါ။

**Expected behavior:** အသစ်ထည့်သော record များကို INSERT event၊ ပြောင်းလဲသော record များကို UPDATE event၊ ဖျက်လိုက်သော record များကို DELETE event အဖြစ် အတိအကျ ထွက်ပေါ်ရမည်။ Output သည် run တိုင်း တူညီစေရန် deterministic ဖြစ်ရမည်။

အားလုံးအတွက် သတိပြုရန် — ဤလေ့ကျင့်ခန်းများသည် runtime တွင် database ချိတ်ဆက်မှု မလိုအပ်ပါ။ DAG သဘောတရားကို Airflow (https://airflow.apache.org/docs/) နှင့် Dagster (https://docs.dagster.io/) official doc များတွင် ဆက်လက်ဖတ်ရှုပါ။ pgvector အတွက် https://github.com/pgvector/pgvector တွင် ရှိသည်။
