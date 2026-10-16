## လေ့ကျင့်ခန်း ၁ — Fixed-size chunking ကို လက်တွေ့စမ်းကြည့်ပါ

ဒီလေ့ကျင့်ခန်းတွင် fixed-size chunking ကို Python ဖြင့် တည်ဆောက်ပါ။ စာသားတစ်ခုကို စာလုံး ၅၀ စီဖြင့် ဖြတ်တောက်ပြီး chunk စာရင်း ထုတ်ပါ။ ကိုယ်ပိုင်ရေးသားထားသော စာသားဖြင့် စမ်းသပ်ပါ။

**Hints:** `range` နှင့် list slicing ကို သုံးပါ။ Word-level ခွဲခြမ်းရန် `str.split()` လုံလောက်သည်။

**Expected behavior:** စာသားကို စာလုံး ၅၀ စီပါသော chunk များအဖြစ် ထုတ်ပြသည်။ Chunk တိုင်း၏ အရွယ်အစား အတိအကျ ၅၀ ဖြစ်မှုကို စစ်ဆေးနိုင်သည်။

## လေ့ကျင့်ခန်း ၂ — Overlap ထည့်ပြီး စာကြောင်းပျက်မှု ကာကွယ်ပါ

Overlap မပါသော fixed-size chunking တွင် စာကြောင်းတစ်ခု နှစ်ပိုင်း ကွဲသွားခြင်းကို တွေ့ရမည်။ chunk size ၃၀ နှင့် overlap ၁၀ သုံးပြီး boundary ပြတ်တောက်မှု သက်သာသွားကြောင်း ပြသပါ။ Configuration နှစ်မျိုးလုံး၏ output ကို နှိုင်းယှဉ်ရေးပါ။

**Hints:** step ကို `chunk_size - overlap` ဖြင့် သတ်မှတ်ပါ။ Overlap ၁၀ မှ သုညအထိ ပြောင်းလဲစမ်းသပ်ပါ။

**Expected behavior:** Overlap မပါသောအခါ စာကြောင်းတစ်ကြောင်း chunk နှစ်ခုကြား ပြတ်တောက်သွားသည်။ Overlap ထည့်ပါက ထပ်နေသော စာလုံးများကြောင့် context ဆက်စပ်မှု မပြတ်တောက်ကြောင်း စစ်ဆေးနိုင်သည်။

## လေ့ကျင့်ခန်း ၃ — Recursive text splitting အလုပ်လုပ်ပုံ ပြန်ရေးပါ

Recursive splitter သည် sentence boundary ကို အဘယ်ကြောင့် ထိန်းသိမ်းနိုင်ကြောင်း ကိုယ်ပိုင်ရေးသားသော Python function ဖြင့် သက်သေပြပါ။ separator list `["\n\n", "\n", ". ", " "]` ကို အဆင့်လိုက် အသုံးပြုပြီး chunk size မကျော်လွန်အောင် ခွဲပါ။

**Hints:** Separator တစ်ခု မကိုက်ညီပါက နောက်တစ်ခုသို့ ဆင်းပါ။ LangChain docs ၏ recursive splitting သဘောတရားနှင့် နှိုင်းယှဉ်ရန် https://python.langchain.com/docs/concepts/text_splitters/ တွင် ဖတ်ရှုပါ။

**Expected behavior:** ရလဒ် chunk များတွင် စာကြောင်းပြတ်တောက်မှု သိသာစွာ လျော့နည်းသည်။ Separator အဆင့်ဆင်း အသုံးပြုမှု မှတ်တမ်းကို print လုပ်၍ စောင့်ကြည့်နိုင်သည်။

## လေ့ကျင့်ခန်း ၄ — Token-based chunking နဲ့ ဂဏန်းခြင်း

Token နှင့် စာလုံး၏ ကွာခြားချက်ကို တွက်ချက်ပြပါ။ Simple tokenizer တစ်ခုကို `re.findall(r"\w+|\S", text)` ဖြင့် ရေးပါ။ ယူဆချက် — 10,000 tokens၊ chunk size 512 tokens၊ overlap 64 tokens ဖြစ်ပါက စုစုပေါင်း chunk အရေအတွက်ကို formula ဖြင့် တွက်ချက်ပြပါ။

**Hints:** formula မှာ `1 + ceil((total - chunk) / (chunk - overlap))` ဖြစ်သည်။ တွက်ချက်မှုကို print လုပ်ပြပါ။ Hugging Face tokenizers အကြောင်းကို https://huggingface.co/docs/tokenizers/index တွင် ဖတ်ရှုပါ။

**Expected behavior:** Tokenized result နှင့် chunk count တွက်ချက်မှု နှစ်ခုလုံး ထွက်ရှိသည်။ သတ်မှတ်ထားသော parameter များဖြင့် formula အရ 20 chunks ရရှိကြောင်း ကိုယ်တိုင် တွက်ချက်အတည်ပြုနိုင်သည်။

## လေ့ကျင့်ခန်း ၅ — Parent-child indexing နဲ့ small-to-big retrieval

Small-to-big retrieval (retrieval unit သည် child chunk၊ generation unit သည် parent) ကို Python dict များဖြင့် တည်ဆောက်ပါ။ Child chunk များတွင် keyword search (`in` operator ဖြင့်) ပြုလုပ်ပြီး score အမြင့်ဆုံး child ၏ parent အပြည့်အစုံကို ပြန်လည်ထုတ်ပြရမည်။ Parent များကို paragraphs၊ child များကို sentences အဖြစ် ယူဆပါ။

**Hints:** Parent တစ်ခုကို `{"parent_id", "parent_text", "children"}` ပုံစံဖြင့် သိမ်းပါ။ Child ရလဒ်သည် parent ကို ပြန်လည်ညွှန်းဆိုရမည်။ LlamaIndex ၏ သက်ဆိုင်ရာ အယူအဆကို https://docs.llamaindex.ai/en/stable/ တွင် ဖတ်ရှုပါ။

**Expected behavior:** Query နှင့် ကိုက်ညီသော child chunk ကို ရှာတွေ့ပြီး၊ ပြန်လည်ထုတ်ပြရာတွင် parent paragraph အပြည့်အစုံ ထွက်ရှိသည်။ Child မှ parent သို့ ညွှန်းပြသော ဆက်သွယ်မှုကို စစ်ဆေးနိုင်သည်။

## လေ့ကျင့်ခန်း ၆ — Chunk metadata ဒီဇိုင်းနဲ့ permission filter

ခန်း ၆ တွင် metadata ပါဝင်သော chunk schema တစ်ခု ဒီဇိုင်းချပါ။ Field များမှာ `source`, `section`, `page`, `permission`, `chunk_index` တို့ ဖြစ်သည်။ Permission မတူညီသော user နှစ်ယောက်အတွက် retrieval simulation ရေးပြီး secret document filtered-out ဖြစ်ကြောင်း ပြသပါ။ pgvector အတွက် SQL တစ်ခုလည်း ရေးပါ။

**Hints:** `filter(allowed, chunks)` pure function တစ်ခု ရေးပါ။ `cosine similarity` နေရာတွင် deterministic keyword score ဖြင့် အစားထိုးပါ။

```sql
-- Valid for PostgreSQL with pgvector; not executed by this lesson.
SELECT id, source, section, 1 - (embedding <=> :query_vec) AS score
FROM chunks
WHERE permission = ANY(:user_permissions)
ORDER BY embedding <=> :query_vec
LIMIT 5;
```

**Expected behavior:** Admin user သည် document အားလုံး ရရှိပြီး guest user သည် secret document ရရှိခြင်း မရှိပါ။ Permission filter သည် retrieval ရလဒ်အပေါ် တိုက်ရိုက် သက်ရောက်ကြောင်း စောင့်ကြည့်နိုင်သည်။
