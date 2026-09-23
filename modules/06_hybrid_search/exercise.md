# M6 — လေ့ကျင့်ခန်းများ (Hybrid Search: Full-text, Trigram နှင့် RRF)

ဒီလေ့ကျင့်ခန်းတွေက M6 သင်ခန်းစာအတွက် အိမ်စာဖြစ်ပါတယ်။
Python standard library တစ်ခုတည်းနဲ့ ရေးရပါမယ်။
Database ချိတ်ရန် မလိုပါဘူး — SQL ကို ဖတ်ပြီး လေ့လာရုံပဲ ဖြစ်ပါတယ်။

## လေ့ကျင့်ခန်း ၁ — tsvector ဆောက်ခြင်း (စာလုံး အခြေခံ)

PostgreSQL မှာ full-text search (စာအပိုဒ်တစ်ခုထဲက စာလုံးတွေကို index လုပ်တဲ့ နည်း) က `tsvector` နဲ့ စတင်ပါတယ်။

**Task:** အင်္ဂလိပ်စာ ၃ ကြောင်းကို lowercase လုပ်ပြီး စာလုံးတွေခွဲပါ။ ပြီးရင် တစ်ခုစီအတွက် lexeme (အဓိပ္ပာယ်ဆောင်တဲ့ စာလုံးအခြေ) နဲ့ အနေရာ (position) ကို dict နဲ့ ပြပါ။ `tsvector` ရဲ့ logic ကို တုပြီး ရေးတာပါ — DB မချိတ်ပါဘူး။

**Hints:** စာကို `.split()` နဲ့ ခွဲပါ။ position က 1 ကနေ စပါတယ်။ တူတဲ့ စာလုံး ထပ်ပေါ်ရင် position အားလုံးကို list ထဲ မှတ်ပါ။

**Expected behavior:** `"the quick brown fox"` မှာ `the: [1], quick: [2], brown: [3], fox: [4]` ဆိုတဲ့ dict ရပါတယ်။ `"the lazy dog the"` မှာ `the` ရဲ့ value က `[1, 4]` ဖြစ်ပါတယ်။

## လေ့ကျင့်ခန်း ၂ — tsquery matching နဲ့ ranking (ts_rank style)

`tsvector` ကို query နဲ့ တိုက်စစ်ပြီး score ထုတ်တာက PostgreSQL ရဲ့ ranking အခြေခံပါ။

**Task:** လေ့ကျင့်ခန်း ၁ ရဲ့ tsvector dict ကို ယူပါ။ query ထဲက စာလုံးတွေထဲက ဘယ်လုံးတွေ document ထဲ ရှိလဲ ရှာပါ။ match ရတဲ့ စာလုံး အရေအတွက်ကို score အဖြစ် ပြန်ပါ။

**Hints:** set intersection (`.intersection()`) ကို သုံးလို့ ရပါတယ်။ ရှုပ်ထွေးမှု မတိုးပါနဲ့ — matched word count လောက်ပဲ လိုပါတယ်။

**Expected behavior:** doc `"postgres vector search guide"` မှာ query `["postgres", "search"]` က score `2` ရပါတယ်။ query `["mysql"]` က score `0` ရပါတယ်။ ရလဒ်တွေကို score အမြင့်နဲ့ စီပြပါ။

## လေ့ကျင့်ခန်း ၃ — Trigram similarity (3-gram Jaccard)

Trigram (စာလုံး ၃ လုံးတွဲ) similarity က စာလုံးပေါင်းလွဲတာတွေကို ရှာပေးပါတယ်။ PostgreSQL က GiST index နဲ့ ဒီလို အလုပ်လုပ်ပါတယ်။

**Task:** စကားလုံးတစ်ခုစီက trigram set ဆောက်ပါ — စာလုံး ၃ လုံးတွဲ၊ ရှေ့နောက်မှာ space ၂ လုံး ဖြည့်ပါ။ ပြီးရင် Jaccard similarity (ဘုံ set အရွယ် စား ပေါင်း set အရွယ်) နဲ့ နှစ်ခု နိုင်ငံခြားချင်း တိုက်စစ်ပါ။

**Hints:** `"  word  "` ဆိုပြီး space ဖြည့်ပြီးမှ trigram ခွဲပါ။ ဥပမာ `"cat"` → `{'  c', ' ca', 'cat', 'at '}` မျိုး ရပါတယ်။ ဘုံ trigram ရေကို ပေါင်း trigram ရေနဲ့ စားပါ။

**Expected behavior:** `"postgres"` vs `"postgresql"` က similarity တန်ဖိုးတစ်ခု ရပါတယ် (arithmetic ကို ကိုယ်တိုင် တွက်ပြပါ)။ `"postgres"` vs `"banana"` က 0 နဲ့ နီးပါတယ်။ တွက်ချက်မှု အဆင့်ဆင့်ကို ပရင့်ထုတ်ပြပါ။

## လေ့ကျင့်ခန်း ၄ — Weighted sum မှာ score normalization ရဲ့ အရေးကြီးမှု

Vector score နဲ့ BM25 score (စာလုံးရှာမှုရဲ့ ranking score) က scale မတူပါ။ normalization (အတိုးအကျယ် ညီမျှောင်းတဲ့နည်း) မလုပ်ရင် ပေါင်းတဲ့အခါ တစ်ဖက်က အလွန်ကိုင်းပါတယ်။

**Task:** vector score တွေက `[0.9, 0.8, 0.7]` နဲ့ BM25 score တွေက `[5.0, 12.0, 20.0]` ဆိုပါစို့။ (၁) တိုက်ရိုက်ပေါင်းပြီး rank လုပ်ပါ။ (၂) တစ်ခုစီကို min-max normalize (0–1 ဖြစ်အောင်) လုပ်ပြီးမှ 0.5/0.5 weight နဲ့ ပေါင်းပါ။ ရလဒ်နှစ်မျိုး ကွဲပုံကို ပြန်ပါ။

**Hints:** min-max normalization က `(x - min) / (max - min)` ပါ။ rank ပြောင်းသွားတဲ့ document ရှိမရှိ စစ်ပါ။ max-min ညီတဲ့ edge case (အားလုံး တူတာ) ကို zero-division ကာဖို့ သတိထားပါ။

**Expected behavior:** နည်း (၁) မှာ BM25 ကြီးတဲ့ document က ထိပ်မှာ ရောက်ပါတယ်။ နည်း (၂) မှာ ranking က ပြောင်းသွားပါတယ်။ ဒီနှိုင်းယှဉ်ချက်က normalization ဘာကြောင့် လိုအပ်တယ်ဆိုတာ ပြပါတယ်။

## လေ့ကျင့်ခန်း ၅ — Reciprocal Rank Fusion (RRF) အခြေခံ

RRF (rank အားဖြင့် ပေါင်းတဲ့နည်း) က score scale ကို မှားစရာ မရှိပါဘူး — rank ပေါ်တည်းချက်ပါတယ်။ Elasticsearch/OpenSearch တို့မှာ ဒီ parameter `k` နဲ့ အလုပ်လုပ်ပါတယ်။

**Task:** `rrf_score = 1 / (k + rank)` formula ကို သုံးပါ။ rank က 1 ကနေ စပါတယ်။ vector rank list နဲ့ keyword rank list နှစ်ခု ရှိရင် တစ်ခုစီရဲ့ RRF တန်ဖိုးကို ပေါင်းပြီး နောက်ဆုံး ranking ထုတ်ပါ။ `k = 60` နဲ့ စမ်းပါ — ဒါက docs တွေမှာ သုံးလေ့ရှိတဲ့ တန်ဖိုးပါ။

**Hints:** document တစ်ခုက တစ်ဖက်လမ်းထဲမှာပဲ ရှိရင် အဲဒီဖက်ကိလည်း ပေါင်းပါ။ rank 1 → `1/61`၊ rank 2 → `1/62` မျိုး ဖြစ်ပါတယ်။ score တွေကို float အတိအကျ ပရင့်ပါ။

**Expected behavior:** doc A က vector rank 1၊ keyword rank 3 ဖြစ်ပြီး doc B က vector rank 4၊ keyword rank 1 ဆိုရင် — `k=60` နဲ့ A ရဲ့ RRF က `1/61 + 1/63` ဖြစ်ပြီး B ရဲ့ RRF က `1/64 + 1/61` ဖြစ်ပါတယ်။ နောက်ဆုံး ranking က B ပို တက်သွားပုံ ပြပါ။

## လေ့ကျင့်ခန်း ၆ — Full hybrid pipeline: နှစ်လမ်းဖြန့်ပြီး RRF နဲ့ ပေါင်းခြင်း

ဒီနောက်ဆုံး လေ့ကျင့်ခန်းက တကယ့် hybrid search (vector နဲ့ keyword နှစ်လမ်း ပေါင်းရှာတာ) ရဲ့ သေးသေးလေး မော်ဒယ်ပါ။

**Task:** docs ၅ ခု ရှိရင် — (၁) keyword path အတွက် လေ့ကျင့်ခန်း ၂ ရဲ့ matching score နဲ့ rank ထုတ်ပါ။ (၂) vector path အတွက် cosine similarity (cos တူညီမှု အတိုင်းအတွေး — standard library နဲ့ တွက်ရန်) ကို ကြိုးကြိုးသတ်မှတ်ထားတဲ့ ရိုးရိုး vector တွေနဲ့ တွက်ပါ။ (၃) နှစ်လမ်းက rank တွေကို RRF (`k=60`) နဲ့ ပေါင်းပြီး top-3 ထုတ်ပါ။

**Hints:** vector တွေကို `[0.1, 0.2]` လိုမျိုး ကြို သတ်မှတ်ပါ — runtime မှာ ဘာမှ မွေးပါနဲ့၊ deterministic ဖြစ်ရပါမယ်။ cosine similarity က dot product စား norm နှစ်ခုမြှောက်ကိန်းပါ။ norm က `math.sqrt(sum(x*x for x in v))` ပါ။ rank ထုတ်တဲ့အခါ score အမြင့်ဆိုင်ကို sort လုပ်ပါ။

**Expected behavior:** query တစ်ခုက နှစ်လမ်းလုံးမှာ ကွဲပြားတဲ့ docs ကို ထိပ်မှာ တင်ပါတယ်။ RRF က နှစ်လမ်းလုံးမှာ အလယ်အလတ် ကောင်းတဲ့ doc ကို မြှင့်တင်ပေးပုံကို top-3 ရလဒ်နဲ့ ပြပါ။ `k=1` နဲ့ `k=60` နှိုင်းယှဉ်ပြီး — `k` သေးရင် rank ထိပ်ကို ပိုပြင်းတယ်ဆိုတာ observation တစ်ကြောင်း ထည့်ပါ။

---

အားလုံးပြီးရင် M6 ရဲ့ ဗီဒီယို/စာအုပ်အတွက် အဖြေများကို ကြည့်ပါ။ မဖြေရသေးရင်လည်း ကိုယ်တိုင် စမ်းကြည့်တာက အကောင်းဆုံးပါ။ နောက် module M7 မှာ vector index (ANN search) အကြောင်း ဆက်ပါမယ်နော်။
