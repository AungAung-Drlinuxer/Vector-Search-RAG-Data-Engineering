## လေ့ကျင့်ခန်း ၁ — Embedding ထဲက PII စစ်ဆေးပါ

Text chunk တွေထဲမှာ PII (နာမည်၊ ဖုန်းနံပါတ်၊ email လို ကိုယ်ရေးအချက်အလက်) ပါနေတတ်တာကြောင့် embedding ထဲ ထည့်လိုက်ရင် အန္တရာယ်ရှိတယ်ဆိုတာကို နားလည်အောင် လေ့ကျင့်ပါ။

**Task:** Python standard library နဲ့ regex သုံးပြီး ဖုန်းနံပါတ်နဲ့ email ကို ရှာပြီး `[REDACTED]` လို့ အစားထိုးတဲ့ function တစ်ခု ရေးပါ။ အစားထိုးပြီးတဲ့ chunk ကို ပြနိုင်အောင်ပါ ရေးပါ။

**Hints:** `re.sub()` ကို သုံးပါ။ Pattern နှစ်ခု — email အတွက်နဲ့ ဒီဂျစ်တစ်ချို့နဲ့ ဒက်တွေ ပါတဲ့ ဖုန်းပုံစံအတွက် ရေးပါ။ ဒါက RAG pipeline ရဲ့ ingestion အဆင့်မှာ သူ့အလုပ်လုပ်တယ်၊ database နဲ့ ချိတ်မနေပါဘူးနော်။

**Expected behavior:** Input string ထဲမှာ `aung@example.com` နဲ့ `09-777-123` ပါရင် output မှာ `[REDACTED]` နှစ်ခုပြီး ကျန်တဲ့ စာသားတွေ မပျက်ပဲ ပေါ်ပါတယ်။ Redaction မလုပ်ခင် PII က embedding ထဲ ဝင်သွားပြီး search လုပ်သူက indirect နည်းနဲ့ ဆွဲထုတ်လို့ ရနိုင်တယ်ဆိုတာကို သင်သတိထားမိတာကို လေ့လာသင့်ပါတယ်။

## လေ့ကျင့်ခန်း ၂ — ACL filter ကို cosine ranking ထဲ ထည့်ပါ

Retrieval လုပ်တဲ့အခါ user မ မြင်နိုင်တဲ့ document ကို permission အလိုက် ချန်လိုက်ရတယ်ဆိုတာက document-level ACL ရဲ့ အဓိကအချက်ပါ။

**Task:** ကျွန်တော်တို့ရဲ့ baseline ဖြစ်တဲ့ cosine similarity ranking function ထဲမှာ `allowed_doc_ids` parameter ထည့်ပြီး filter လုပ်ပါ။ Standard library နဲ့ပဲ ရေးပါ။

**Hints:** Cosine similarity က `(A·B)/(||A||·||B||)` ပါ။ Rank တွက်ပြီးမှ allowed list ထဲ မပါတဲ့ doc တွေကို ဖျက်ပါ။ ဒီဟာက PostgreSQL `pgvector` + row-level security နဲ့ တူတဲ့ mechanics ကို သင်ကိုယ်တိုင် ပြန်တည်ဆောက်တာပါ။

**Expected behavior:** သုံးစွဲသူအတွက် allowed မဟုတ်တဲ့ doc တစ်ခု score အမြင့်ဆုံး ရှိနေလည်း top-k ထဲ မပါတာကို မြင်ရပါတယ်။ Filter မရှိရင် permission ချိုးဖျက်တဲ့ document ပေါ်လာမယ်ဆိုတာက ဒီလေ့ကျင့်ခန်းရဲ့ သင်ချက်ပါ။

## လေ့ကျင့်ခန်း ၃ — pgvector + row-level security အတွက် SQL ရေးပါ

PostgreSQL မှာ document-level ACL ကို row-level security (row တစ်ခုစီကို policy နဲ့ ထိန်းတဲ့ feature) နဲ့ တည်ဆောက်ပါတယ်။ အဲဒါက ACL filter ကို database အထိ ရောက်အောင် တွန်းတဲ့ နည်းပါ။

**Task:** `documents` table မှာ `owner` column နဲ့ `embedding vector(4)` ပါတဲ့ DDL၊ RLS enable policy နဲ့ user က ကိုယ်ပိုင် doc တွေကိုပဲ cosine distance (`<=>`) နဲ့ ရှာတဲ့ SELECT query သုံးခု ရေးပါ။

**Hints:** Official doc က https://www.postgresql.org/docs/current/ddl-rowseecurity.html ... မှားပါတယ် — မှန်တာက `https://www.postgresql.org/docs/current/ddl-rowsecurity.html` ပါ။ Policy ကို `USING (owner = current_user)` ပုံစံနဲ့ ရေးပါ။ Query မှာ `ORDER BY embedding <=> '[0.1,0.2,0.3,0.4]' LIMIT 3` လိုမျိုး သုံးပါ။ SQL ကို သင် run မှာ မဟုတ်ဘူး၊ fence ထဲမှာပဲ ပြပါ။

**Expected behavior:** SQL သုံးခုလုံး PostgreSQL + pgvector မှာ valid ဖြစ်ပြီး၊ RLS ကြောင့် သူမကိုယ်ပိုင်တဲ့ row ကို user က query ထဲ မမြင်ရတာ ဖြစ်ပါတယ်။ Database အစား Python filter နဲ့ တူတဲ့အချက်က လေ့ကျင့်ခန်း ၂ နဲ့ ဆက်စပ်တယ်ဆိုတာ သတိပြုပါ။

## လေ့ကျင့်ခန်း ၄ — Multi-tenant isolation နည်းလမ်းနှစ်မျိုး နှိုင်းယှဉ်ပါ

Tenant (ဆိုင်ရာအဖွဲ့အစည်းတစ်ခုချင်းရဲ့ ဒေတာအုပ်စု) တွေကို ခွဲထားဖို့ schema-per-tenant နဲ့ shared-table-with-tenant-id ဆိုတဲ့ နည်းနှစ်မျိုး ရှိပါတယ်။

**Task:** Python မှာ `tenants` ကို dict-of-dicts နဲ့ ခွဲထားတဲ့ ပုံစံနဲ့ list ထဲ `tenant_id` ထည့်ထားတဲ့ ပုံစံ နှစ်ခုလုံးကို query လုပ်တဲ့ function ရေးပြီး tenant အလိုက် မရောက်စေရန် စမ်းပါ။

**Hints:** Shared-table ပုံစံမှာ query တိုင်းမှာ `tenant_id` match စစ်ဖို့ လိုပါတယ်။ ဒါကမှ real system မှာ `tenant_id = current_setting('app.tenant_id')` လို policy နဲ့ ချိတ်တာပါ။ နှစ်မျိုးလုံး offline၊ deterministic ဖြစ်အောင် ရေးပါ။

**Expected behavior:** Tenant A က query လုပ်ရင် Tenant B ရဲ့ doc ဘယ်တစ်ခုမှ ရလာဒ်ထဲ မပါတာကို မြင်ရပါတယ်။ Filter တစ်ကြိမ် မေ့လိုက်ရင် cross-tenant leak ဖြစ်တယ်ဆိုတာကို စမ်းသပ်မှုနဲ့ သက်သေပြနိုင်ရပါမယ်။

## လေ့ကျင့်ခန်း ၅ — Audit log နဲ့ access မှတ်တမ်း ရေးပါ

ဘယ် user က ဘယ်ချိန်မှာ ဘယ် document ကို ကြည့်ခဲ့လဲဆိုတာ မှတ်တမ်းတင်တာက audit log ပါ။ နောက်ပြန်စစ်ဆေးဖို့ သေချာတဲ့ အထောက်အထားပါ။

**Task:** Python မှာ `retrieval_request(user, query, results, allowed)` လို event တွေကို JSON line တစ်ကြောင်းချင်း append တဲ့ audit logger ရေးပါ။ Timestamp က deterministic ဖြစ်အောင် function ထဲကနေ ယူပါ။

**Hints:** `json.dumps` နဲ့ list ထဲ ထည့်ပြီး နောက်ဆုံး ပရင့်လုပ်ပါ။ Denied result တွေကိုပါ log ထဲ မှတ်ပါ။ Real system မှာ append-only table နဲ့ သင်ထားပြီး၊ ဒီလေ့ကျင့်ခန်းမှာက အဲဒီ mechanics ကို ကျွန်တော်တို့ပဲ ပြန်တည်ဆောက်တာပါနော်။

**Expected behavior:** Log တစ်ကြောင်းချင်းစီမှာ user၊ query၊ result ids၊ allowed flag နဲ့ timestamp ပါတာကို မြင်ရပါတယ်။ Allowed မဟုတ်တဲ့ result တွေကို ဖျက်ခဲ့တဲ့ မှတ်တမ်းပါ ပေါ်ပါတယ်။

## လေ့ကျင့်ခန်း ၆ — Delete propagation နှင့် provenance မှတ်တမ်းပါ

User တစ်ယောက်က data ဖျက်ပါစေခိုင်းရင် source doc တစ်ခုတည်း မဟုတ်ဘူး၊ သူ့ကနေ ဆွဲထုတ်ထားတဲ့ chunk၊ embedding တွေအထိ ဖျက်ရပါတယ်။

**Task:** `docs` dict ထဲက doc တစ်ခုကို delete လုပ်ရင် chunk တွေ၊ embedding တွေနဲ့ audit log ထဲက reference တွေပါ cascade (တစ်ခုကို တစ်ခုဆက် လိုက်ဖျက်တဲ့ ပုံစံ) နဲ့ ဖျက်တဲ့ function ရေးပါ။ Doc တစ်ခုချင်းမှာ `source_url` နဲ့ `license` ကို provenance (ဒေတာ ဘယ်ကနေလာသလဲဆိုတဲ့ မှတ်တမ်း) အနေနဲ့ သင်ပါ။

**Hints:** `dict.pop()` နဲ့ list comprehension သုံးပြီး orphan chunk (အမိ doc မရှိတော့တဲ့ chunk) တွေ ရှာပါ။ Retention (ဒေတာကို ဘယ်လောက်ကြာ ထားမလဲဆိုတဲ့ သတ်မှတ်ချက်) စည်းကို မှတ်တမ်းအသစ်မှာ ပြပါ။

**Expected behavior:** Doc ကို ဖျက်ပြီးရင် သူ့ကို ညွှန်နေတဲ့ chunk နဲ့ embedding တွေ အကုန် ပျက်သွားပြီး၊ ဖျက်တဲ့ မှတ်တမ်းနဲ့ provenance ကတော့ ကျန်ရှိတာကို မြင်ရပါတယ်။ Source ဖျက်လို့ embedding ကျန်နေရင် PII ဒါမှမဟုတ် license ချိုးဖျက်မှု ဖြစ်နိုင်တယ်ဆိုတာက ဒီလေ့ကျင့်ခန်းရဲ့ အဓိကသင်ချက်ပါတယ်။
