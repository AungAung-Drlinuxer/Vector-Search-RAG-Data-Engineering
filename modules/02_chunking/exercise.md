## လေ့ကျင့်ခန်း ၁ — Fixed-size chunking ကို လက်တွေ့စမ်းကြည့်ပါ

ဒီလေ့ကျင့်ခန်းမှာ fixed-size chunking (စာသားကို အရွယ်အတိအကျ ဖြတ်တာ) ကို Python နဲ့ ရေးပါ။ စာသားတစ်ခုကို စာလုံး ၅၀ စီနဲ့ ဖြတ်ပြီး chunk စာရင်း ထုတ်ပါ။ ကိုယ်တိုင်ရေးထားတဲ့ စာသားနဲ့ စမ်းပါ။

**Hints:** `range` နဲ့ list slicing ကိုသုံးပါ။ စာလုံးခွဲရန် `str.split()` လုံလောက်ပါတယ်။

**Expected behavior:** စာသားကို စာလုံး ၅၀ စီရှိတဲ့ အပိုင်းများအဖြစ် ပြပါတယ်။ chunk တိုင်းရဲ့ အရွယ်အစား အတိအကျ ၅၀ ရှိမှုကို လက်တွေ့ကြည့်ရှုနိုင်ပါတယ်။

## လေ့ကျင့်ခန်း ၂ — Overlap ထည့်ပြီး စာကြောင်းပျက်မှု ကာကွယ်ပါ

Overlap (chunk နှစ်ခုကြား ထပ်နေတဲ့ စာသား) မပါတဲ့ fixed-size chunking မှာ ဝါကျတစ်ခု နှစ်ပိုင်းကွဲသွားတာကို မြင်ရပါမယ်။ chunk size ၃၀ နဲ့ overlap ၁၀ သုံးပြီး ဒီပျက်ကွက်မှု သက်သာသွားတာကို ပြပါ။ နှစ်မျိုးစလုံးရဲ့ output ကို ယှဉ်ပြီး ရေးပါ။

**Hints:** step ကို `chunk_size - overlap` သုံးပါ။ overlap ၁၀ မှ သုညအထိ ပြောင်းကြည့်ပါ။

**Expected behavior:** overlap မပါတဲ့အခါ ဝါကျတစ်ချောင်း နှစ် chunk ကြား ပြတ်သွားတာ မြင်ရပါတယ်။ overlap ထည့်ရင် ထပ်နေတဲ့ စာလုံးများကြောင့် အဓိပ္ပာယ် ဆက်နေတာ လက်တွေ့စစ်ကြည့်နိုင်ပါတယ်။

## လေ့ကျင့်ခန်း ၃ — Recursive text splitting အလုပ်လုပ်ပုံ ပြန်ရေးပါ

Recursive splitter (ကြားခံ အမှတ်အသားများနဲ့ အဆင့်ဆင်း ဖြတ်တဲ့ နည်း) က ဘာကြောင့် ဝါကျနယ်နိမိတ်ကို ထိန်းပေးနိုင်တယ်ဆိုတာ ကိုယ်တိုင်ရေးတဲ့ Python function နဲ့ သက်သေပြပါ။ separator စာရင်း `["\n\n", "\n", ". ", " "]` ကို အဆင့်လိုက် သုံးပြီး chunk size ကို မကျော်အောင် ခွဲပါ။

**Hints:** separator တစ်ခုမကျော်ရင် နောက်တစ်ခုဆီ ဆင်းပါ။ LangChain docs ရဲ့ recursive splitting သဘောနဲ့ ယှဉ်ဖို့ https://python.langchain.com/docs/concepts/text_splitters/ ဖွင့်ကြည့်ပါ။

**Expected behavior:** ရလဒ် chunk များမှာ ဝါကျပျက်မှု သိသိသာသာ နည်းသွားတာကို မြင်ရပါတယ်။ separator အဆင့်ဆင်းခြင်း မှတ်တမ်းကို print လုပ်ပြီး စောင့်ကြည့်နိုင်ပါတယ်။

## လေ့ကျင့်ခန်း ၄ — Token-based chunking နဲ့ ဂဏန်းခြင်း

Token (model ဖတ်တဲ့ စာသားယူနစ်) နဲ့ စာလုံးရဲ့ ကွာခြားချက်ကို တွက်ပြပါ။ ကိုယ်တိုင်ရေးတဲ့ simple tokenizer တစ်ခုကို `re.findall(r"\w+|\S", text)` နဲ့ ရေးပါ။ ယူဆချက်က 10,000 tokens၊ chunk size 512 tokens၊ overlap 64 tokens ဆိုရင် စုစုပေါင်း chunk အရေအတွက်ကို formula နဲ့ တွက်ပြပါ။

**Hints:** formula က `1 + ceil((total - chunk) / (chunk - overlap))` ပါတယ်။ တွက်ချက်မှုကို print လုပ်ပြပါ။ Hugging Face tokenizers အစစ်ကို https://huggingface.co/docs/tokenizers/index မှာ ဖတ်ပါ။

**Expected behavior:** tokenized result နဲ့ တွက်ချက်မှု နှစ်မျိုးလုံး ထွက်ပါတယ်။ ယူဆချက် အရေအတွက်နဲ့ formula ကနေ 20 chunks ရမယ် ဆိုတာ မိမိကိုယ်တိုင် တွက်ပြီး အတည်ပြုနိုင်ပါတယ်။

## လေ့ကျင့်ခန်း ၅ — Parent-child indexing နဲ့ small-to-big retrieval

Small-to-big retrieval (ရှာဖွေရင်း သေးတဲ့ chunk၊ ပြန်တင်ပြရင်း ကြီးတဲ့ parent) ကို Python dict တွေနဲ့ ပြန်ရေးပါ။ child chunk များမှာ keyword search (`in` စစ်ချက်နဲ့) လုပ်ပြီး အမှတ်အများဆုံး child က parent အပြည့်အစုံကို ပြနိုင်ရပါမယ်။ parent တွေကို paragraphs၊ child တွေက sentences အဖြစ် ယူဆပါ။

**Hints:** parent တစ်ခုကို `{"parent_id", "parent_text", "children"}` ပုံစံနဲ့ သိမ်းပါ။ child ရလဒ်က parent ကို ပြန်ညွှန်ရပါတယ်။ LlamaIndex ရဲ့ ဆီလျော်တဲ့ အယူအဆကို https://docs.llamaindex.ai/en/stable/ မှာ ဖတ်ပါ။

**Expected behavior:** ရှာဖွေတဲ့ query က သေးငယ်တဲ့ child ကို တွေ့ပြီး ပြန်တင်တဲ့အခါ ကြီးတဲ့ parent paragraph အပြည့် ထွက်ပါတယ်။ child မှ parent ဆီ ညွှန်ပြတဲ့ ဆက်သွယ်မှုကို လက်တွေ့စစ်ကြည့်နိုင်ပါတယ်။

## လေ့ကျင့်ခန်း ၆ — Chunk metadata ဒီဇိုင်းနဲ့ permission filter

ခန်း ၆ မှာ metadata (chunk နဲ့အတူ သိမ်းတဲ့ အချက်အလက်) ပါတဲ့ chunk schema တစ်ခု ဒီဇိုင်းပါ။ field တွေက `source`, `section`, `page`, `permission`, `chunk_index` ပါ။ permission မတူတဲ့ user နှစ်ယောက်အတွက် retrieval simulation ရေးပြီး secret document ကို filtered-out ဖြစ်တာ ပြပါ။ SQL တစ်ခုလည်း pgvector အတွက် ရေးပြပါ။

**Hints:** `filter(allowed, chunks)` ဆိုတဲ့ pure function ရေးပါ။ `cosine similarity` နေရာမှာ ရိုးရိုး keyword score နဲ့ အစားထိုးပြီး deterministic ဖြစ်အောင် လုပ်ပါ။

```sql
-- Valid for PostgreSQL with pgvector; not executed by this lesson.
SELECT id, source, section, 1 - (embedding <=> :query_vec) AS score
FROM chunks
WHERE permission = ANY(:user_permissions)
ORDER BY embedding <=> :query_vec
LIMIT 5;
```

**Expected behavior:** admin user က document အားလုံး မြင်ပြီး guest user က secret document မြင်မရပါ။ permission filter က ရလဒ် မျက်နှာပြင်မှာ တိုက်ရိုက် သက်ရောက်တာကို စောင့်ကြည့်နိုင်ပါတယ်။
