## လေ့ကျင့်ခန်း ၁ — JSON Data Serialization & Canonicalization

PostgreSQL `json` နှင့် `jsonb` column များ၏ storage mechanism ကွာခြားချက်ကို သုံးသပ်ပြီး Python `dict` မှ canonical JSON format သို့ `json.dumps` ဖြင့် serialize လုပ်သည့် logic ကို ရေးသားပါ။

**Hints:** PostgreSQL official documentation (https://www.postgresql.org/docs/current/datatype-json.html) ကို ကိုးကားပါ။ `json` သည် input raw text အတိုင်း သိမ်းဆည်းပြီး `jsonb` သည် whitespace normalization နှင့် key deduplication ပြုလုပ်ထားသော parsed binary format ဖြစ်သည်။

**Expected behavior:** `{"doc_id": 1, "lang": "my"}` dictionary ကို serialize လုပ်ပြီး format နှင့် key formatting ကို အတည်ပြုနိုင်ရမည်။

---

## လေ့ကျင့်ခန်း ၂ — Text Extraction နှင့် Targeted Boilerplate Removal

HTML document တစ်ခုမှ `<nav>` နှင့် `<footer>` tags များအတွင်းရှိ boilerplate စာသားများကို ဖယ်ရှားပြီး `<main>` အကြောင်းအရာကိုသာ plain text အဖြစ် clean ထုတ်ယူပါ။

**Hints:** Regex substitution (`re.sub`) ဖြင့် boilerplate block များကို temporary marker (`[[BOILER]]`) ဖြင့် အစားထိုးပြီးမှ tag stripping ပြုလုပ်ခြင်းသည် content pollution ကို တားဆီးပေးသည်။

**Expected behavior:** Navigation link များနှင့် copyright footer များ မပါရှိဘဲ core content သာ ကျန်ရှိသော normalized text string ရရှိရမည်။

---

## လေ့ကျင့်ခန်း ၃ — Unicode Normalization (NFC)

Visually တူညီသော်လည်း byte sequence ကွဲပြားသော string များကို `unicodedata.normalize` ဖြင့် NFC (Canonical Decomposition, followed by Canonical Composition) format သို့ ပြောင်းလဲ နှိုင်းယှဉ်ပါ။

**Hints:** `unicodedata.normalize('NFC', text)` ကို သုံးပါ။ `ord()` နှင့် `unicodedata.name()` ဖြင့် underlying codepoints များကို စစ်ဆေးနိုင်သည်။

**Expected behavior:** Pre-normalization တွင် equality check (`==`) သည် `False` ဖြစ်ပြီး NFC normalization ပြုလုပ်ပြီးနောက် `True` ဖြစ်ရမည်။

---

## လေ့ကျင့်ခန်း ၄ — Content Fingerprinting ဖြင့် Exact Duplicate Detection

Corpus အတွင်းရှိ documents များကို whitespace normalization ပြုလုပ်ပြီး SHA-256 hash ဖြင့် fingerprint ထုတ်ယူကာ duplicate content များကို grouping ပြုလုပ်ပါ။

**Hints:** `hashlib.sha256(text.encode('utf-8')).hexdigest()` ကို အသုံးပြုပါ။ Dictionary တွင် fingerprint ကို key အဖြစ် သတ်မှတ်၍ document IDs များကို bucket လုပ်ပါ။

**Expected behavior:** Document ၅ ခုတွင် duplicate ဖြစ်နေသော group များကို ခွဲခြားဖော်ထုတ်နိုင်ပြီး unique content count ကို တိကျစွာ ရရှိရမည်။

---

## လေ့ကျင့်ခန်း ၅ — Incremental Update Diff Engine

လက်ရှိ pipeline state (doc_id -> fingerprint) နှင့် အသစ်ရောက်ရှိလာသော batch ကို နှိုင်းယှဉ်၍ `new`, `changed`, `deleted` set ၃ ခုကို ခွဲခြားသတ်မှတ်ပါ။

**Hints:** State တွင် မရှိသေးပါက `new`၊ fingerprint ကွဲပြားပါက `changed`၊ state တွင် ရှိသော်လည်း batch တွင် မပါဝင်တော့ပါက `deleted` အဖြစ် categorize လုပ်ပါ။

**Expected behavior:** Target batch အတွက် `new`, `changed`, `deleted` ID list များကို သီးခြားစီ တိကျစွာ output ထုတ်ပေးရမည်။

---

## လေ့ကျင့်ခန်း ၆ — Idempotent Upsert & Delete Pipeline

Batch တစ်ခုကို ထပ်ခါတလဲလဲ execute လုပ်သော်လည်း database state မပြောင်းလဲစေမည့် idempotent pipeline function တစ်ခုကို implement လုပ်ပါ။

**Hints:** State mutation ပြုလုပ်ရာတွင် content fingerprint ပြောင်းလဲမှသာ write ပြုလုပ်သည့် check ထည့်သွင်းပါ။ PostgreSQL ၏ `INSERT ... ON CONFLICT (doc_id) DO UPDATE` semantics နှင့် ကိုက်ညီရမည်။

**Expected behavior:** ပထမအကြိမ် execution တွင် writes များဖြစ်ပေါ်ပြီး ဒုတိယအကြိမ် ထပ်မံ execute ပြုလုပ်ချိန်တွင် write count သည် 0 ဖြစ်ကာ final state သည် identical ဖြစ်နေရမည်။
