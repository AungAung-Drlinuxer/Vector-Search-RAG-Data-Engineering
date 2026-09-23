## လေ့ကျင့်ခန်း ၁ — JSON ဒေတာအမျိုးအစား သိမ်းတယ်

PostgreSQL ရဲ့ `json` နဲ့ `jsonb` ကွာခြားချက်ကို မှတ်စာရေးပါတယ်။
ဒီနောက် Python `dict` တစ်ခုကို JSON string အဖြစ် `json.dumps` နဲ့ ပြောင်းပြပါတယ်။
ဒါက ingest pipeline ထဲ `json` column မှာ ဘာ data သွားမလဲ ကြိုမြင်ရတာပါ။

**Hints:** https://www.postgresql.org/docs/current/datatype-json.html ကို ဖတ်ပါတယ်။
`json` က input text ကို အတိုင်းသိမ်းတယ်၊ `jsonb` က parsed binary format ပါတယ်။

**Expected behavior:** `{"doc_id": 1, "lang": "my"}` ဆိုတဲ့ dict ကို
`json.dumps` နဲ့ string ပြနိုင်ရတယ်။ key တွေမှာ quote တွေပါရတယ်။

## လေ့ကျင့်ခန်း ၂ — Text extraction နဲ့ boilerplate ဖယ်တယ်

ပေးထားတဲ့ HTML string တစ်ခုကနေ tag တွေဖြုတ်ပြီး text ထုတ်ပါတယ်။
`<nav>` နဲ့ `<footer>` အတွင်းက text တွေက boilerplate ပါ။
ဒါတွေကို မဖြုတ်ခင် marker နဲ့ အစားထိုးပြီး၊ နောက်မှ ဖယ်ပါတယ်။

**Hints:** `re.sub(r'<[^>]+>', ' ', html)` နဲ့ tag တွေဖျက်လို့ရတယ်။
Boilerplate ကို marker `[[BOILER]]` နဲ့ အစားထိုးပြီး နောက်မှ အဲဒီ marker ရှိတဲ့ အပိုင်းကို ဖျက်ပါတယ်။

**Expected behavior:** nav/footer text မပါတဲ့ စိတ်ချရတဲ့ plain text ရရတယ်။
Main content text ကိုတော့ ကျန်ရစ်ရတယ်။

## လေ့ကျင့်ခန်း ၃ — Unicode normalization လုပ်တယ်

Burmese text နှစ်ကြောင်းကို `unicodedata.normalize` နဲ့ နှိုင်းယှဉ်ပါတယ်။
NFC form က composed form ဖြစ်တာကြောင့် တူညီမှု စစ်ဖို့ သုံးတာပါ။
Normalize မလုပ်ခင် မတူနိုင်တဲ့ string တွေကို ပြပါတယ်။

**Hints:** `unicodedata.normalize('NFC', s)` ကို သုံးပါတယ်။
`unicodedata.name()` နဲ့ codepoint နာမည်တွေ ကြည့်လို့ရတယ်။

**Expected behavior:** Normalize မလုပ်ခင် `==` မှာ False ဖြစ်နိုင်ပြီး၊
NFC လုပ်ပြီးရင် True ဖြစ်ရတယ်။ ရှင်းလင်းတဲ့ ရလဒ်ကို print လုပ်ပါတယ်။

## လေ့ကျင့်ခန်း ၄ — Duplicate စစ်ဖို့ content fingerprint သုံးတယ်

Document ငါးပိုင်းကို SHA-256 hash နဲ့ fingerprint ထုတ်ပါတယ်။
တူညီတဲ့ content နှစ်ခုကို ရောထားပါတယ်။
Hash တွေကို set ထဲထည့်ပြီး duplicate တွေကို ဖော်ပြပါတယ်။

**Hints:** `hashlib.sha256(text.encode('utf-8')).hexdigest()` က fingerprint ပါတယ်။
Normalize လုပ်ပြီးမှ hash လုပ်တာက whitespace ကွာခြားမှုကိုလည်း ဖမ်းပေးတယ်။

**Expected behavior:** Document ငါးခုမှာ unique content ၃ မျိုးပဲရတယ်။
Duplicate group တွေကို doc id နဲ့ တွဲပြရတယ်။

## လေ့ကျင့်ခန်း ၅ — Incremental update စစ်တယ်

ဒါနောက် chunk တွေကို (doc_id, text) အဖြစ် ရောက်လာတယ်။
Fingerprint နဲ့ ရှေ့အဆင့်က မှတ်ထားတဲ့ state နဲ့ နှိုင်းပါတယ်။
အသစ်၊ ပြောင်းလဲ၊ ဖျက်ရမည့် အုပ်စုသုံးမျိုးကို ခွဲပါတယ်။

**Hints:** State က dict — key က doc_id၊ value က fingerprint ပါတယ်။
New = state မှာမရှိ၊ changed = fingerprint မတူ၊ deleted = state မှာရှိပေမယ့် input မှာမရှိပါ။

**Expected behavior:** ရလဒ်က `new: [3]`, `changed: [2]`, `deleted: [5]` လိုမျိုး ပါတယ်။
ပေးထားတဲ့ input နဲ့ state အပေါ် မူတည်ပြီး အတိအကျရရတယ်။

## လေ့ကျင့်ခန်း ၆ — Idempotent upsert နဲ့ delete pipeline

Pipeline function တစ်ခုကို ရေးပါတယ်။
Batch တစ်ခုကို လက်ခံပြီး upsert နဲ့ delete ကို အလုံးစုံ လုပ်ပေးရတယ်။
Batch တစ်ခုကို နှစ်ခါ ပြေးလိုက်ရင် ရလဒ် အတူတူပဲ ဖြစ်ရတယ်။
ဒါက idempotency (ထပ်ပြေးလည်း ရလဒ်မပြောင်း) ပါ။

**Hints:** SQL upsert က `INSERT ... ON CONFLICT (doc_id) DO UPDATE SET ...` ပါတယ်။
pgvector target ဖြစ်နေလို့ `RETURNING` နဲ့ သက်ဆိုင်ရာကို ချိတ်မပြပါနှင့် — comment နဲ့ ရှင်းပြပါတယ်။
DAG scheduling အကြောင်းက https://airflow.apache.org/docs/ မှာ ရှိတာပါ၊ prose နဲ့ ရှင်းပါတယ်။

**Expected behavior:** Batch တစ်ခုကို အရင်ပြေးတုန်းက state ရရတယ်။
Batch ကို ဒုတိယအကြိမ် ထပ်ပြောလိုက်တော့ ဘာမှ ပြောင်းလဲသွားတာမရှိပါနှင့်။
