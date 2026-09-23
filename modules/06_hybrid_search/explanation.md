# M6 — Hybrid Search: Full-text၊ Trigram နှင့် RRF ပေါင်းစပ်ခြင်း

> **မူရင်းစာအုပ်မှတ်ချက်** — ဒါက တရားဝင် open documentation တွေကနေ ကိုယ်တိုင်ရေးထားတဲ့ လေ့လာစာအုပ်ပါ။ မည်သည့်ကုန်သွယ်စာအုပ်တစ်ခုကိုမှ ကူးယူ သို့မဟုတ် ပြန်ရေးထားတာ မဟုတ်ဘူး။ အသုံးပြုထားတဲ့ တရားဝင် documentation များ — PostgreSQL text search (https://www.postgresql.org/docs/current/textsearch-controls.html, https://www.postgresql.org/docs/current/textsearch-indexes.html), Elasticsearch RRF (https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion), OpenSearch vector search (https://opensearch.org/docs/latest/vector-search/)။

---

## Subtopic 1 — PostgreSQL Full-text Search နှင့် Ranking

### ဘာကို ဆိုလိုတာလဲ

Full-text search (စာသားအပြည့်အစုံရှာခြင်း) ဆိုတာ စကားလုံးတွေကို ရှာပေးတဲ့ နည်းပါ။ `tsvector` ဆိုတာ document ရဲ့ စကားလုံးတွေကို သိမ်းထားတဲ့ data type ပါ။ `tsquery` ဆိုတာ ရှာမယ့် query ကို ကိုယ်စားပြုတဲ့ data type ပါ။ ranking (အစဉ်လိုက် အမှတ်ပေးခြင်း) ကတော့ `ts_rank` ဆိုတဲ့ function နဲ့ လုပ်ပါတယ်။

### ဘာကြောင့် လဲ

Vector search တစ်ခုတည်းနဲ့ဆိုရင် ပျိုးတာပါ။ ဥပမာ — query ထဲမှာ "invoice ID 45123" လို့ ပါရင် vector search က အဓိပ္ပာယ် အနီးစပ်ဆုံး စာများကိုပဲ ပြနေတယ်။ ဒါပေမယ့် စာသားအတိအကျ ကိုက်ညီမှုက အရေးကြီးတဲ့ အခါ ရှိပါတယ်။ Full-text index မရှိရင် LIKE query ကို သုံးရပြီး တစ်ကွန်တန်းချင်း စကင်ရပါတယ်။ ဒါက စာရွက်များလာရင် နှေးသွားပါတယ်။ GIN index နဲ့ `tsvector` က ဒီပြဿနာကို ဖြေရပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

PostgreSQL full-text pipeline က ဒီလိုပါ —

၁။ စာသားကို parser က စကားလုံးတွေအဖြစ် ခွဲပါတယ်။
၂။ စကားလုံးတွေကို lexeme (စကားလုံးရဲ့ အခြေခံပုံစံ) အဖြစ် ပြောင်းပါတယ်။ ဥပမာ "running" က "run" ဖြစ်သွားတယ်။
၃။ `tsvector` ထဲမှာ lexeme တွေနဲ့ အနေရာတွေ သိမ်းပါတယ်။
၄။ query ကို `tsquery` အဖြစ် ပြောင်းပြီး `@@` operator နဲ့ တိုက်ဆိုင်ပါတယ်။
၅။ `ts_rank` က ကိုက်ညီမှု အမှတ်ပေးပါတယ်။ ဒါက အနီးစပ်ဆုံး စကားလုံး သဘောမဟုတ်ဘူး — စကားလုံး အရေအတွက်နဲ့ အခြေအနေပေါ် မူတည်ပါတယ်။

```sql
-- Valid for PostgreSQL with the pgvector extension (NOT executed by lessons).
CREATE TABLE docs (
  id   bigserial PRIMARY KEY,
  body text
);
ALTER TABLE docs ADD COLUMN search_vec tsvector
  GENERATED ALWAYS AS (to_tsvector('english', body)) STORED;
CREATE INDEX docs_search_idx ON docs USING gin (search_vec);

SELECT id, ts_rank(search_vec, query) AS rank
FROM docs, websearch_to_tsquery('english', 'invoice payment') AS query
WHERE search_vec @@ query
ORDER BY rank DESC
LIMIT 10;
```

### ဥပမာ

PostgreSQL ကို ချိတ်မထားပါ။ အောက်က code က stemming (စကားလုံးအခြေခံပုံစံ ပြောင်းခြင်း) သဘောကို standard Python နဲ့ ပြနေပါတယ်။

```python
# Deterministic offline demo: a tiny suffix-stripping stemmer,
# a stand-in for PostgreSQL's stemming step. No database is used here.
# Where a real PostgreSQL instance would run, we say so in a comment.

def simple_stem(word):
    # Very small English suffix stripper (demo only).
    for suffix in ("ing", "ed", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word

def to_fake_tsvector(text):
    # Stand-in for to_tsvector(): ordered (lexeme, positions) list.
    words = text.lower().split()
    return [(simple_stem(w), i) for i, w in enumerate(words)]

doc = "running invoices were processed"
query_words = ["runs", "invoice"]

doc_lexemes = {lex for lex, _ in to_fake_tsvector(doc)}
query_lexemes = {simple_stem(w) for w in query_words}
matched = doc_lexemes & query_lexemes

print("doc lexemes :", sorted(doc_lexemes))
print("query lexemes:", sorted(query_lexemes))
print("matched     :", sorted(matched))
# Expected output:
# doc lexemes : ['invoice', 'process', 'runn', 'were']
# query lexemes: ['invoice', 'run']
# matched     : ['invoice']
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

RAG system တိုင်းမှာ keyword လမ်းက လိုအပ်ပါတယ်။ အမည်တွေ၊ ID တွေ၊ error code တွေက vector embedding နဲ့ မှားတတ်ပါတယ်။ PostgreSQL docs အရ GIN index က `tsvector` column ပေါ် အသုံးပြုနိုင်ပြီး မြန်စွာ ရှာပေးပါတယ်။ ဒါက hybrid search ရဲ့ ပထမ ခြေထောက်ပါ။

---

## Subtopic 2 — Trigram Similarity

### ဘာကို ဆိုလိုတာလဲ

Trigram (စာလုံးသုံးလုံးစဉ်) ဆိုတာ စကားလုံးထဲက စာလုံး သုံးလုံးစီ အစီအစဉ်ပါ။ ဥပမာ "cat" ရဲ့ trigram တွေက `  c`, ` ca`, `cat`, `at ` ဖြစ်ပါတယ်။ trigram similarity ဆိုတာ စကားလုံးနှစ်လုံးရဲ့ trigram တွေ ဘယ်လောက် တူတယ်ဆိုတာ တွက်တဲ့ score ပါ။ PostgreSQL က ဒါကို `pg_trgm` extension နဲ့ ပေးပါတယ်။

### ဘာကြောင့် လဲ

Full-text search က lexeme အတိအကျ ကိုက်မှရပါတယ်။ စာလုံးပေါင်း မှားနေရင် ရှာမတွေ့ပါ။ ဥပမာ — user က "Postgers" လို့ ရိုက်မိရင် "PostgreSQL" ကို အတိအကျ မကိုက်ပါ။ trigram က စာလုံးပေါင်းမှားမှု (typo) ကို ခံနိုင်ရည်ရှိပါတယ်။ ဘာကြောင့်လဲဆိုတော့ စာလုံးတစ်လုံးမှားရုံနဲ့ trigram အများစုက မပျက်ပါဘူး။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ `pg_trgm` extension ကို install လုပ်ပါတယ်။
၂။ `show_trgm('word')` က trigram စုစည်းမှု ထုတ်ပေးပါတယ်။
၃။ `similarity(a, b)` က 0 ကနေ 1 အတွင်း score ပေးပါတယ် — 1 ဆိုတာ တူတယ်။
၄။ `%` operator က similarity threshold ထက်ကြီးရင် true ပြပါတယ်။
၅။ GIN index ကို trigram ပေါ် တည်ဆောက်နိုင်ပြီး fuzzy ရှာမှုကို မြန်စေပါတယ်။

```sql
-- Valid for PostgreSQL with the pgvector extension (NOT executed by lessons).
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX docs_body_trgm ON docs USING gin (body gin_trgm_ops);

SELECT id, similarity(body, 'postgers') AS sim
FROM docs
WHERE body % 'postgers'
ORDER BY sim DESC
LIMIT 10;
```

### ဥပမာ

```python
# Deterministic offline demo of trigram similarity, standard library only.
# Where a real PostgreSQL instance would run, we say so in a comment.

def trigrams(s):
    # Pad with spaces, then take all 3-character windows (PostgreSQL style).
    p = " " + s.lower() + " "
    return {p[i : i + 3] for i in range(len(p) - 2)}

def similarity(a, b):
    # Jaccard-style ratio: shared trigrams / union trigrams.
    A, B = trigrams(a), trigrams(b)
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)

print("similarity('PostgreSQL', 'Postgers') =",
      round(similarity("PostgreSQL", "Postgers"), 3))
print("similarity('PostgreSQL', 'elephant') =",
      round(similarity("PostgreSQL", "elephant"), 3))
# Expected output:
# similarity('PostgreSQL', 'Postgers') = 0.286
# similarity('PostgreSQL', 'elephant') = 0.0
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

User တွေ စာလုံးပေါင်း မှားတတ်ပါတယ်။ trigram မရှိရင် typo တစ်ခုကို ဘာမှ မရပါဘူး။ PostgreSQL docs အရ `pg_trgm` က LIKE query တွေကိုပင် GIN index နဲ့ မြန်စေပါတယ်။ ဒါက hybrid search မှာ တတိယ လမ်းကြောင်း ဖြစ်ပါတယ်။

---

## Subtopic 3 — Score Normalization (အမှတ်ပေးချက် တူညီအောင် လုပ်ခြင်း)

### ဘာကို ဆိုလိုတာလဲ

Normalization (အချိုးကျ ဖြစ်အောင် ပြောင်းခြင်း) ဆိုတာ score တွေရဲ့ အတိုင်းအတွဲကို တူညီတဲ့ အပိုင်းအခြားထဲ ပြောင်းတာပါ။ vector score က cosine similarity အဖြစ် -1 ကနေ 1 အတွင်း ပါ။ BM25 ကတော့ 0 ကနေ တရာမသိ ကြီးနိုင်ပါတယ်။

### ဘာကြောင့် လဲ

နှစ်လမ်းဖြန့်ပြီး score နှစ်ခုကို တိုက်ရိုက် ပေါင်းရင် ပျက်ပါတယ်။ ဘာကြောင့်လဲဆိုတော့ BM25 က ကြီးတဲ့ တန်ဖိုးထွက်နိုင်လို့ vector score ကို ဖိသွားပါတယ်။ ဥပမာ — vector score 0.8 ကို BM25 score 34.2 က လုံးဝ ဖုံးပစ်ပါတယ်။ ဒါက weighted sum (အလေးချိန် ပေါင်းခြင်း) နည်းရဲ့ အားနည်းချက်ပါ။ RRF က ranking (အစဉ်အလိုက် အမှတ်စဉ်) ကိုပဲ သုံးလို့ ဒီပြဿနာ မရှိပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

weighted sum နည်းမှာ —

၁။ နှစ်လမ်းစလုံးက score တွေ ထုတ်ပါတယ်။
၂။ တစ်ခုချင်းကို တူညီတဲ့ range (ဥပမာ 0 ကနေ 1) ထဲ ပြောင်းပါတယ်။
၃။ အလေးချိန် `w` တွေနဲ့ မြှောက်ပြီး ပေါင်းပါတယ်။
၄။ ပေါင်းထွက် score နဲ့ အစဉ်လိုက် စီပါတယ်။

### ဥပမာ

```python
# Deterministic offline demo: why normalization matters before a weighted sum.
# Assumption (clearly labelled): scores come from two notional search lanes.

# Lane A: cosine similarity, naturally in [0, 1].
vec_scores = {"d1": 0.80, "d2": 0.40}

# Lane B: BM25-style scores, unbounded scale (assumption: these magnitudes).
bm25_scores = {"d1": 2.0, "d2": 34.2}

# Weighted sum WITHOUT normalization.
raw = {d: 0.5 * vec_scores[d] + 0.5 * bm25_scores[d] for d in vec_scores}
print("raw weighted sum:", raw)

# Normalize lane B to [0, 1] using max normalization (in-lesson formula shown):
# normalized(d) = bm25(d) / max(bm25)
m = max(bm25_scores.values())
bm25_norm = {d: s / m for d, s in bm25_scores.items()}
final = {d: 0.5 * vec_scores[d] + 0.5 * bm25_norm[d] for d in vec_scores}
print("normalized weighted sum:", {d: round(v, 3) for d, v in final.items()})
# Expected output:
# raw weighted sum: {'d1': 1.4, 'd2': 17.3}
# normalized weighted sum: {'d1': 0.429, 'd2': 0.7}
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

ဒီဥပမာမှာ d1 က vector အလိုက် ပိုကောင်းပေမယ့် raw sum က d2 ကို အမြင့် ပေးပါတယ်။ ဘာကြောင့်လဲဆိုတော့ d2 ရဲ့ BM25 score က scale ကြီးနေလို့ပါ။ OpenSearch ရဲ့ vector search docs အရ score တွေက hybrid မှာ တိုက်ရိုက် နှိုင်းလို့ မရပါဘူး။ ဒါကြောင့် normalization ဒါမှမဟုတ် RRF က စံနည်း ဖြစ်ပါတယ်။

---

## Subtopic 4 — Reciprocal Rank Fusion (RRF)

### ဘာကို ဆိုလိုတာလဲ

RRF (အစဉ်အလိုက် ပြောင်းပြန်ပေါင်းခြင်း) ဆိုတာ score တွေမသုံးဘဲ အစဉ်အလိုက် အမှတ်စဉ်တွေကိုပဲ သုံးတဲ့ fusion နည်းပါ။ Elasticsearch docs အရ formula က —

`RRF(d) = Σ (1 / (k + rank_i(d)))`

ဒီမှာ `k` က tuning constant (ညှိနိုင်တဲ့ ကိန်းသေ) ပါ။ `rank_i(d)` က lane i မှာ document d ရရှိတဲ့ အစဉ်ပါ။ အပေါ်ဆုံးက rank 1 ပါ။

### ဘာကြောင့် လဲ

weighted sum မှာ သုံးပြဿနာ ရှိပါတယ် — score scale တွေ မတူလို့ တိုက်ရိုက်ပေါင်းလို့ မရပါ။ normalization က ကူပေမယ့် ရွေးစရာ များပါတယ် — min-max, z-score, စသဖြင့်။ RRF က ဒီအားလုံးကို ကျော်လွှားပါတယ်။ ဘာကြောင့်လဲဆိုတော့ rank (အစဉ်) က scale မဲ့ ဖြစ်လို့နေပြီး နှစ် lane က တူတဲ့ ပုံစံနဲ့ ထွက်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ vector lane က document တွေကို အစဉ်လိုက် စီပါတယ် — rank 1, 2, 3...
၂။ keyword lane (full-text/trigram) ကလည်း အစဉ်လိုက် စီပါတယ်။
၃။ document တစ်ခုစီအတွက် တစ် lane ချင်း `1 / (k + rank)` တွက်ပါတယ်။
၄။ document တစ်ခုက နှစ် lane လုံးမှာ ပါရင် နှစ်ခုကို ပေါင်းပါတယ်။
၅။ ပေါင်းထွက် RRF score နဲ့ နောက်ဆုံး စီပါတယ်။

`k` ရဲ့ သဘော — k ကြီးရင် အပေါ်ဆုံး rank တွေရဲ့ ကွာခြားချက် ချော့သွားပါတယ်။ k သေးရင် top rank တွေက ပို အလေးပါပါတယ်။

### ဥပမာ

```python
# Deterministic offline demo of RRF, standard library only.
# Lane A stands in for a pgvector cosine ranking (a real engine would run there).
# Lane B stands in for a tsvector/BM25-style ranking (a real DB would run there).

K = 60  # Standard k value; the formula itself defines all numbers below.

# Assumption: ranked lists from the two lanes (top-ranked first, rank starts at 1).
vector_ranking = ["d1", "d3", "d4"]
keyword_ranking = ["d2", "d1", "d4"]

def rrf_score(ranked_lists, k):
    # For each doc, sum 1 / (k + rank) across the lists it appears in.
    scores = {}
    for lst in ranked_lists:
        for pos, doc in enumerate(lst, start=1):
            scores[doc] = scores.get(doc, 0.0) + 1.0 / (k + pos)
    return scores

scores = rrf_score([vector_ranking, keyword_ranking], K)
# Show the arithmetic for d1: 1/(60+1) + 1/(60+2) = 1/61 + 1/62
print("d1 arithmetic: 1/61 + 1/62 =",
      round(1 / 61 + 1 / 62, 6))

final = sorted(scores.items(), key=lambda x: -x[1])
print("RRF ranking:", final)
# Expected output:
# d1 arithmetic: 1/61 + 1/62 = 0.032522
# RRF ranking: [('d1', 0.03252247488101534), ('d4', 0.031746031746031744), ('d2', 0.01639344262295082), ('d3', 0.016129032258064516)]
```

**မှတ်ချက်** — d1 နဲ့ d4 ရဲ့ RRF တွက်ချက်မှု အတိအကျ —

- d1: rank 1 (vector) + rank 2 (keyword) → `1/61 + 1/62 ≈ 0.016393 + 0.016129 = 0.032523` (ပို တိတိကျကျ — 0.0325226...)
- d4: rank 3 (vector) + rank 3 (keyword) → `1/63 + 1/63 ≈ 0.015873 + 0.015873 = 0.031746`

ဒါကြောင့် နောက်ဆုံး ranking က — d1 (≈0.0325226), d4 (≈0.031746), d2 (≈0.016393), d3 (≈0.
