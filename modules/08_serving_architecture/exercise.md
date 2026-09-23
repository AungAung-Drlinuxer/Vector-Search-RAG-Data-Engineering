## လေ့ကျင့်ခန်း ၁ — Retrieval API function ရေးပါ

**Task:** `/search` ဆိုတဲ့ retrieval API endpoint ကို simulate လုပ်ပေမယ့် Python function တစ်ခု ရေးပါ။ function က `(query_vector, top_k, filters)` ကို accept လုပ်ရမယ်။ `filters` မှာ `"tenant_id"` ပါရင် ဒါက ACL-like filter (tenant တစ်ခုစီက ကိုယ့် data ကိုပဲ မြင်ရတဲ့ ကန့်သတ်ချက်) အဖြစ် အသုံးချပါ။

**Hints:** metadata dict list တစ်ခု အလွဲလွဲ (hard-code) လုပ်ပါ။ tenant မတူတဲ့ result တွေကို filter နဲ့ ဖယ်ရှားပါ။ real system မှာဆိုရင် SQL `WHERE` clause နဲ့ filter လုပ်တာပါလို့ comment မှာ ရေးပေးပါ။

**Expected behavior:** tenant_id မတူတဲ့ items တွေ ဘယ်တော့မှ မပြပါနဲ့။ top_k ထက်မပိုစေနဲ့။

## လေ့ကျင့်ခန်း ၂ — Embedding cache တည်ဆောက်ပါ

**Task:** query embedding အတွက် cache class တစ်ခု ရေးပါ။ cache key က query string ဖြစ်ရမယ်။ cache miss ဖြစ်ရင် deterministic stand-in embedding ထုတ်ပြီး cache ထဲ သိမ်းပါ။ hit ဖြစ်ရင် stored vector ကို ပြန်ပေးပါ။

**Hints:** real system မှာဆို ရင် embedding API က ကုန်ကျစရိတ်နဲ့ latency ရှိပါတယ် — ဒါကြောင့် cache လိုအပ်ပါတယ်။ stand-in function က string ရဲ့ character ordinals ကနေ fixed-size vector တည်ဆောက်ပေးပါ။ cache hit count နဲ့ miss count ကို ဖော်ပြပေးပါ။

**Expected behavior:** query တူလျှင် cache hit ဖြစ်ပြီး miss count မတိုးပါနဲ့။ hit နဲ့ miss counts တွေက မှန်ကန်စွာ ပေါ်ပါလာရမယ်။

## လေ့ကျင့်ခန်း ၃ — Result cache (query + filter hash key)

**Task:** result cache တစ်ခု ရေးပါ။ cache key က (query, filters) နှစ်ခုလုံး ပါဝင်ရမယ်။ query တူပေမယ့် filter မတူရင် cache hit မဖြစ်ရပါဘူး။

**Hints:** key ကို JSON serialize လုပ်ပြီး တည်နေရာပါစေဖို့ သတိထားပါ — dict order က အရေးကြီးပါတယ်။ `sort_keys=True` သုံးပါ။

**Expected behavior:** query တူ၊ filter တူမှ hit ဖြစ်ရမယ်။ filter ကွာလျှင် miss ဖြစ်ပြီး cache ထဲ entry အသစ် ထည့်ရမယ်။

## လေ့ကျင့်ခန်း ၄ — Pool နဲ့ concurrency simulation

**Task:** retrieval connection pool class တစ်ခု ရေးပါ။ pool size 3 ရှိမယ်။ `acquire()` / `release()` methods ပါဝင်ရမယ်။ `queue.Queue` သုံးပြီး connection တွေ သိမ်းဆည်းပါ။ acquire တုန်း pool ဗလာ မရှိရင် block ဖြစ်စေပါ။

**Hints:** real system မှာ Postgres connection တစ်ခုချင်းစီက အကန့်အသတ်ရှိပါတယ်။ pool က connection ပြန်လည်အသုံးပြုခြင်းနဲ့ အလွန်အကျွံ ဖွင့်မခံ့စေဖို့ အသုံးဝင်ပါတယ်။ connection တွေက dummy object တွေပါ။

**Expected behavior:** acquire ၃ ခါ အောင်မြင်ရမယ်၊ စတုတ္ထအကြိမ်က release မခဏမခင်း စောင့်ရမယ် (timeout နဲ့ စစ်ပါ)။ release ပြီးရင် ရရှိမယ်။

## လေ့ကျင့်ခန်း ၅ — pgvector SQL ရေးပါ (အလုပ်မလုပ်ပါဘူး၊ ဖတ်ဖို့ပါ)

**Task:** pgvector သုံးပြီး hybrid filter (tenant + score) ပါတဲ့ SQL query တစ်ခု ရေးပါ။ documents table (id, tenant_id, embedding vector(4), content) ဆိုပြီး ယူဆပါ။ cosine distance နဲ့ top 3 ရွေးပါ။ ဒါက exercise သက်သက် — SQL ကို run မခံ့ပါဘူး။

**Hints:** `<=>` operator က cosine distance အတွက်ပါ (pgvector README မှာ ဖော်ပြထားပါတယ်)။ `ORDER BY ... LIMIT` သုံးပါ။ စာရင်းအင်း (index) မတပ်ရသေးရင် exact search ပါလို့ comment ရေးပါ။

**Expected behavior:** SQL fence တစ်ခုထဲမှာ၊ PostgreSQL + pgvector အတွက် valid ဖြစ်ရမယ်။ tenant_id filter က WHERE clause ထဲ ပါရမယ်။

## လေ့ကျင့်ခန်း ၆ — Hybrid architecture စာတမ်းရေးပါ (essay)

**Task:** စာတမ်းတစ်ခု ရေးပါ — ဘာကြောင့် Postgres ကို source of truth အဖြစ် ထားပြီး Qdrant ကဲ့သို့ vector store သီးသန့်တစ်ခုကို တွဲသုံးသင့်တာလဲ။ အောက်ပါ official docs တွေကို ကိုးကားပါ — https://github.com/pgvector/pgvector၊ https://qdrant.tech/documentation/။

**Hints:** မေးခွန်းတွေကို ဖြေပါ — (၁) transactional data နဲ့ relational integrity က ဘယ်မှာ အရေးကြီးလဲ၊ (၂) vector-only store က scale-out အတွက် ဘာအားသာချက်ရှိလဲ၊ (၃) sync ပြဿနာ (data နှစ်ခုကွာသွားရင်) ကို ဘယ်လိုကိုင်တွယ်မလဲ။ ကိုယ်တိုင်ရှာဖွေထားတဲ့ number တွေ မထည့်နဲ့ — docs က မဟုတ်တဲ့အထိ ဂဏန်းမှ စကားပြောပါနဲ့။

**Expected behavior:** စာတမ်းက (၁)(၂)(၃) မေးခွန်းသုံးခုလုံးကို အဖြေရှင်းပြီး official docs URL နှစ်ခု ကိုးကားရမယ်။ ဂဏန်းတွေကို အထောက်အထားမရှိဘဲ မထည့်ရပါဘူး။
