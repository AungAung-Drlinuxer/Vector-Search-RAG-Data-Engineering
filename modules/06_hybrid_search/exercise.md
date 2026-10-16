# M6 — လေ့ကျင့်ခန်းများ (Hybrid Search: Full-text, Trigram နှင့် RRF)

ဒီလေ့ကျင့်ခန်းများသည် M6 သင်ခန်းစာအတွက် အိမ်စာဖြစ်သည်။
Python standard library တစ်ခုတည်းဖြင့် ရေးသားရမည်။
Database ချိတ်ဆက်ရန် မလိုအပ်ပါ — SQL ကို ဖတ်ရှုလေ့လာရုံသာဖြစ်သည်။

## လေ့ကျင့်ခန်း ၁ — tsvector ဆောက်ခြင်း (အခြေခံ)

PostgreSQL full-text search သည် `tsvector` ဖြင့် စတင်သည်။

**Task:** အင်္ဂလိပ်စာ ၃ ကြောင်းကို lowercase ပြုလုပ်၍ token ခွဲပါ။ တစ်ခုစီအတွက် lexeme နှင့် position ကို dict ဖြင့် ထုတ်ပြပါ။ `tsvector` ၏ logic ကို simulate လုပ်ခြင်းဖြစ်ပြီး DB ချိတ်ဆက်မည် မဟုတ်ပါ။

**Hints:** `.split()` ဖြင့် token ခွဲပါ။ Position ကို 1 မှ စတင်ရေတွက်ပါ။ Lexeme တစ်ခု ထပ်ပေါ်ပါက position အားလုံးကို list တွင် မှတ်တမ်းတင်ပါ။

**Expected behavior:** `"the quick brown fox"` အတွက် `the: [1], quick: [2], brown: [3], fox: [4]` dict ရရှိမည်။ `"the lazy dog the"` အတွက် `the` ၏ value မှာ `[1, 4]` ဖြစ်မည်။

## လေ့ကျင့်ခန်း ၂ — tsquery matching နှင့် ranking (ts_rank style)

`tsvector` ကို query ဖြင့် match လုပ်ပြီး score ထုတ်ခြင်းသည် PostgreSQL ranking ၏ အခြေခံဖြစ်သည်။

**Task:** လေ့ကျင့်ခန်း ၁ ၏ tsvector dict ကို အသုံးပြုပါ။ Query term များအနက် မည်သည်တို့ document အတွင်း ပါဝင်သည်ကို ရှာဖွေပြီး matched word count ကို score အဖြစ် ပြန်လည်ထုတ်ပြပါ။

**Hints:** Set intersection (`.intersection()`) အသုံးပြုနိုင်သည်။ ရှုပ်ထွေးမှု မတိုးစေရ — matched word count လောက်သာ လိုအပ်သည်။

**Expected behavior:** doc `"postgres vector search guide"` တွင် query `["postgres", "search"]` က score `2` ရရှိမည်။ Query `["mysql"]` က score `0` ရရှိမည်။ ရလဒ်များကို score descending ဖြင့် စီစဉ်ပြသပါ။

## လေ့ကျင့်ခန်း ၃ — Trigram similarity (3-gram Jaccard)

Trigram similarity သည် စာလုံးပေါင်းလွဲမှားမှုများကို ဖမ်းယူပေးသည်။ PostgreSQL ၏ `pg_trgm` သည် ဤနည်းဖြင့် အလုပ်လုပ်သည်။

**Task:** စကားလုံးတစ်ခုစီအတွက် trigram set ဆောက်ပါ — စာလုံး ၃ လုံး window ယူပြီး ရှေ့နောက် space ၂ လုံးစီ pad လုပ်ပါ။ ထို့နောက် Jaccard similarity (intersection size / union size) ဖြင့် စကားလုံးစုံတွဲများကို တွက်ချက်ပါ။

**Hints:** `"  word  "` ဟု pad လုပ်ပြီးမှ trigram ခွဲပါ။ ဥပမာ `"cat"` → `{'  c', ' ca', 'cat', 'at '}`။ Intersection size ကို union size ဖြင့် စားပါ။

**Expected behavior:** `"postgres"` vs `"postgresql"` သည် similarity တန်ဖိုးတစ်ခု ရရှိမည် (arithmetic ကို ကိုယ်တိုင် တွက်ချက်ပြသပါ)။ `"postgres"` vs `"banana"` သည် 0 နှင့် နီးကပ်မည်။ တွက်ချက်မှု အဆင့်ဆင့်ကို print ထုတ်ပြပါ။

## လေ့ကျင့်ခန်း ၄ — BM25 score တွက်ခြင်း

BM25 သည် keyword search engine များ (Elasticsearch/OpenSearch) ၏ default ranking ဖြစ်သည်။ ဒီလေ့ကျင့်ခန်းတွင် ပုံသေနည်းကို လက်ဖြင့် တွက်ချက်မည်။

**Task:** အောက်ပါ corpus အတွက် query `['quick', 'fox']` ၏ BM25 score များ
တွက်ချက်ပြီး document များကို score descending ဖြင့် စီပါ — `k1=1.2`, `b=0.75` သုံးပါ။

```
d1: 'the quick brown fox'
d2: 'the quick quick fox sleeps in the warm sun'
d3: 'a sleepy fox in the barn'
```

အဆင့်များ — (၁) Token ခွဲပြီး document အလိုက် အရှည်နှင့် `avgdl` တွက်ပါ။
(၂) Query term တစ်ခုချင်းစီအတွက် `df` (document frequency) ရှာပြီး IDF တွက်ပါ။
(၃) ပုံသေနည်းအတိုင်း term တစ်ခုချင်းစီ score ထုတ်ပြီး ပေါင်းပါ။

**Hints:** `math.log` ကို သုံးပါ — `math.log(1 + (N - df + 0.5) / (df + 0.5))`။
`f(q, D)` သည် document အတွင်း term ပါဝင်မှု အကြိမ်ရေဖြစ်သည် (d2 တွင် `quick` ၂ ကြိမ်)။
Denominator တွင် document အလိုက် `|D| / avgdl` ပြန်လည်တွက်ချက်ရန် မမေ့ပါနှင့်။

**Expected behavior:**
- `avgdl = 6.3333`၊ `df(quick) = 2`၊ `df(fox) = 3`
- `idf(quick) = 0.470004`၊ `idf(fox) = 0.133531`
- စုစုပေါင်း: `d1 = 0.7106`၊ `d2 = 0.6917`၊ `d3 = 0.1365` — ranking: **d1 > d2 > d3**
- Observation တစ်ကြောင်း ရေးပါ — d2 တွင် `quick` ၂ ကြိမ် ပါဝင်သော်လည်း ဘာကြောင့်
  d1 အောက် ရောက်သွားသနည်း (saturation + length normalization)။

## လေ့ကျင့်ခန်း ၅ — Weighted sum တွင် score normalization ၏ အရေးပါမှု

Vector score နှင့် BM25 score သည် scale မတူပါ။ Normalization မလုပ်ဘဲ ပေါင်းပါက lane တစ်ဖက်က fusion ရလဒ်ကို လွှမ်းမိုးသွားသည်။

**Task:** Vector score များ `[0.9, 0.8, 0.7]` နှင့် BM25 score များ `[5.0, 12.0, 20.0]` ဟု သတ်မှတ်ပါ။ (၁) တိုက်ရိုက်ပေါင်း၍ rank လုပ်ပါ။ (၂) Lane တစ်ခုစီကို min-max normalize ([0, 1]) လုပ်ပြီးမှ 0.5/0.5 weight ဖြင့် ပေါင်းပါ။ ရလဒ်နှစ်မျိုး ကွာခြားပုံကို ပြန်လည်တင်ပြပါ။

**Hints:** min-max normalization မှာ `(x - min) / (max - min)` ဖြစ်သည်။ Rank ပြောင်းလဲသွားသော document ရှိ/မရှိ စစ်ဆေးပါ။ max == min ဖြစ်သော edge case (score အားလုံးတူ) တွင် zero-division ကာကွယ်ရန် သတိပြုပါ။

**Expected behavior:** နည်း (၁) တွင် BM25 score ကြီးသော document ထိပ်ဆုံးရောက်သည်။ နည်း (၂) တွင် ranking ပြောင်းလဲသွားသည်။ ဤနှိုင်းယှဉ်ချက်က normalization ဘာကြောင့် လိုအပ်သည်ကို ပြသသည်။

## လေ့ကျင့်ခန်း ၆ — Reciprocal Rank Fusion (RRF) အခြေခံ

RRF သည် raw score ကို မသုံးဘဲ rank ပေါ်တွင်သာ အခြေခံသဖြင့် scale ပြဿနာ ကင်းဝေးသည်။ Elasticsearch/OpenSearch တွင် parameter `k` ဖြင့် အလုပ်လုပ်သည်။

**Task:** `rrf_score = 1 / (k + rank)` formula ကို သုံးပါ။ Rank ကို 1 မှ စတင်ရေတွက်သည်။ Vector rank list နှင့် keyword rank list နှစ်ခုရှိပါက တစ်ခုစီ၏ RRF component ကို ပေါင်းပြီး final ranking ထုတ်ပါ။ `k = 60` ဖြင့် စမ်းသပ်ပါ — documentation များတွင် သုံးလေ့ရှိသော တန်ဖိုးဖြစ်သည်။

**Hints:** Document သည် lane တစ်ခုတည်းတွင်သာ ပါဝင်ပါက ထို lane ၏ component ကိုသာ ပေါင်းသည်။ rank 1 → `1/61`၊ rank 2 → `1/62`။ Score များကို float အတိအကျ print ထုတ်ပါ။

**Expected behavior:** doc A သည် vector rank 1၊ keyword rank 3 ဖြစ်ပြီး doc B သည် vector rank 4၊ keyword rank 1 ဆိုပါက — `k=60` ဖြင့် A ၏ RRF မှာ `1/61 + 1/63` ဖြစ်ပြီး B ၏ RRF မှာ `1/64 + 1/61` ဖြစ်သည်။ Final ranking တွင် B ပိုမိုမြင့်တက်လာပုံကို ပြသပါ။

## လေ့ကျင့်ခန်း ၇ — Full hybrid pipeline: နှစ်လမ်း fan-out ပြီး RRF ဖြင့် fusion

ဒီနောက်ဆုံး လေ့ကျင့်ခန်းသည် လက်တွေ့ hybrid search (vector + keyword နှစ်လမ်း) ၏ simplified model ဖြစ်သည်။

**Task:** Document ၅ ခု ရှိပါက — (၁) keyword path အတွက် လေ့ကျင့်ခန်း ၂ ၏ matching score ဖြင့် rank ထုတ်ပါ။ (၂) vector path အတွက် cosine similarity ကို ကြိုတင်သတ်မှတ်ထားသော vector များဖြင့် standard library သုံး၍ တွက်ပါ။ (၃) Lane နှစ်ခု၏ rank များကို RRF (`k=60`) ဖြင့် fuse လုပ်ပြီး top-3 ထုတ်ပါ။

**Hints:** Vector များကို `[0.1, 0.2]` ကဲ့သို့ ကြိုတင်သတ်မှတ်ပါ — runtime တွင် random မထုတ်ရ၊ deterministic ဖြစ်ရမည်။ Cosine similarity မှာ dot product စား norms မြှောက်လဒ်ဖြစ်ပြီး norm က `math.sqrt(sum(x*x for x in v))` ဖြစ်သည်။ Rank ထုတ်ရာတွင် score descending ဖြင့် sort လုပ်ပါ။

**Expected behavior:** Query တစ်ခုသည် lane နှစ်ခုလုံးတွင် မတူညီသော document များကို ထိပ်ဆုံးတင်သည်။ RRF သည် lane နှစ်ခုလုံးတွင် အလယ်အလတ်ကောင်းသော document ကို မြှင့်တင်ပေးပုံကို top-3 ရလဒ်ဖြင့် ပြသပါ။ `k=1` နှင့် `k=60` ကို နှိုင်းယှဉ်ပြီး — `k` သေးလေ top rank ၏ အလေးချိန် ပိုကြလေဆိုသော observation တစ်ကြောင်း ထည့်သွင်းပါ။

---

အားလုံးပြီးဆုံးပါက M6 ၏ အဖြေများကို စစ်ဆေးကြည့်ရှုပါ။ မဖြေဆိုရသေးပါက ကိုယ်တိုင် စမ်းသပ်ခြင်းသည် အကောင်းဆုံးဖြစ်သည်။ နောက် module M7 တွင် reranking နှင့် query transformation အကြောင်း ဆက်လက်လေ့လာမည်။
