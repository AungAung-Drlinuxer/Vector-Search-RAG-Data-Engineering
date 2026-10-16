## လေ့ကျင့်ခန်း ၁ — Retrieval API function ရေးပါ

**Task:** `/search` retrieval API endpoint ကို simulate လုပ်သော Python function တစ်ခု ရေးပါ။ Function သည် `(query_vector, top_k, filters)` ကို accept လုပ်ရမည်။ `filters` တွင် `"tenant_id"` ပါဝင်ပါက ACL-like filter အဖြစ် ဆောင်ရွက်ပါ။

**Hints:** metadata dict list တစ်ခုကို hard-code ပြုလုပ်ပါ။ tenant မတူညီသော result များကို filter ဖြင့် ဖယ်ထုတ်ပါ။ Real system တွင် ဤ filter ကို SQL `WHERE` clause အဖြစ် အကောင်အထည်ဖော်ကြောင်း comment တွင် ဖော်ပြပါ။

**Expected behavior:** tenant_id မတူညီသော item များ response တွင် ပါဝင်မည် မဟုတ်ပါ။ Result အရေအတွက်သည် top_k ကို မကျော်လွန်ရပါ။

## လေ့ကျင့်ခန်း ၂ — Embedding cache တည်ဆောက်ပါ

**Task:** query embedding အတွက် cache class တစ်ခု ရေးပါ။ Cache key သည် query string ဖြစ်ရမည်။ Cache miss တွင် deterministic stand-in embedding ထုတ်ပြီး cache ထဲ သိမ်းပါ။ Hit တွင် stored vector ကို ပြန်ပေးပါ။

**Hints:** Real system တွင် embedding API call သည် ကုန်ကျစရိတ်နှင့် latency ရှိသဖြင့် cache လိုအပ်သည်။ Stand-in function သည် string ၏ character ordinals မှ fixed-size vector တည်ဆောက်ပေးပါ။ Cache hit count နှင့် miss count ကို ထုတ်ပြပါ။

**Expected behavior:** query တူညီပါက cache hit ဖြစ်ပြီး miss count မတိုးရပါ။ Hit နှင့် miss count များ မှန်ကန်စွာ ထွက်ပေါ်ရမည်။

## လေ့ကျင့်ခန်း ၃ — Result cache (query + filter hash key)

**Task:** result cache တစ်ခု ရေးပါ။ Cache key သည် (query, filters) နှစ်ခုလုံး ပေါ်တွင် အခြေခံရမည်။ Query တူသော်လည်း filter မတူပါက cache hit မဖြစ်ရပါ။

**Hints:** Key ကို JSON serialize လုပ်ရာတွင် determinism ကို သေချာစေပါ — dict order သည် အရေးပါသဖြင့် `sort_keys=True` သုံးပါ။

**Expected behavior:** query နှင့် filter နှစ်ခုလုံး တူညီမှသာ hit ဖြစ်ရမည်။ Filter ကွာပါက miss ဖြစ်ပြီး cache ထဲ entry အသစ် ထည့်ရမည်။

## လေ့ကျင့်ခန်း ၄ — Pool နဲ့ concurrency simulation

**Task:** retrieval connection pool class တစ်ခု ရေးပါ။ Pool size 3 ရှိမည်။ `acquire()` / `release()` method များ ပါဝင်ရမည်။ `queue.Queue` သုံးပြီး connection များ သိမ်းဆည်းပါ။ Pool ဗလာဖြစ်နေချိန်တွင် acquire က block ဖြစ်စေပါ။

**Hints:** Real system တွင် Postgres connection အရေအတွက်သည် ကန့်သတ်ချက်ရှိသည်။ Pool သည် connection reuse ဖြင့် အလွန်အကျွံ connection ဖွင့်ခြင်းကို ကာကွယ်ပေးသည်။ Connection များအစား dummy object များ သုံးပါ။

**Expected behavior:** acquire သုံးကြိမ် အောင်မြင်ရမည်။ စတုတ္ထအကြိမ်သည် release မလုပ်မချင်း block ဖြစ်ရမည် (timeout ဖြင့် စစ်ဆေးပါ)။ Release ပြီးနောက် acquire အောင်မြင်ရမည်။

## လေ့ကျင့်ခန်း ၅ — pgvector SQL ရေးပါ (အလုပ်မလုပ်ပါဘူး၊ ဖတ်ဖို့ပါ)

**Task:** pgvector သုံးပြီး hybrid filter (tenant + score) ပါဝင်သော SQL query တစ်ခု ရေးပါ။ documents table (id, tenant_id, embedding vector(4), content) ရှိသည်ဟု ယူဆပါ။ Cosine distance ဖြင့် top 3 ရွေးချယ်ပါ။ ဤ exercise သည် read-only ဖြစ်ပြီး SQL ကို execute မလုပ်ရပါ။

**Hints:** `<=>` operator သည် cosine distance အတွက် ဖြစ်သည် (pgvector README တွင် ဖော်ပြထားသည်)။ `ORDER BY ... LIMIT` သုံးပါ။ Vector index မရှိပါက exact search ဖြစ်ကြောင်း comment ရေးပါ။

**Expected behavior:** SQL fence တစ်ခုတည်းအတွင်း PostgreSQL + pgvector အတွက် valid ဖြစ်ရမည်။ tenant_id filter သည် WHERE clause ထဲ ပါဝင်ရမည်။

## လေ့ကျင့်ခန်း ၆ — Hybrid architecture စာတမ်းရေးပါ (essay)

**Task:** Postgres ကို source of truth အဖြစ်ထားပြီး Qdrant ကဲ့သို့ dedicated vector store ကို တွဲဖက်သုံးစွဲသင့်သည့် အကြောင်းရင်းအပေါ် စာတမ်းတစ်စောင် ရေးပါ။ Official docs များကို ကိုးကားပါ — https://github.com/pgvector/pgvector၊ https://qdrant.tech/documentation/။

**Hints:** အောက်ပါမေးခွန်းများကို ဖြေဆိုပါ — (၁) transactional data နှင့် relational integrity သည် မည်သည့်အလွှာတွင် အရေးပါသနည်း၊ (၂) vector-only store သည် scale-out အတွက် မည်သည့် အားသာချက်ရှိသနည်း၊ (၃) sync ပြဿနာ (store နှစ်ခုကြား data drift) ကို မည်သို့ ကိုင်တွယ်မည်နည်း။ ကိုယ်ပိုင်တိုင်းတာထားခြင်းမရှိသော ဂဏန်းများ မထည့်သွင်းပါနှင့် — docs တွင် မပါဝင်သော ကိန်းဂဏန်း claim များ ရှောင်ပါ။

**Expected behavior:** စာတမ်းသည် (၁)(၂)(၃) မေးခွန်းသုံးခုလုံးကို ဖြေဆိုပြီး official docs URL နှစ်ခု ကိုးကားရမည်။ အထောက်အထားမရှိသော ဂဏန်းများ မပါဝင်ရပါ။
