# M6 — Hybrid Search: Full-text၊ Trigram နှင့် RRF ပေါင်းစပ်ခြင်း

> **မူရင်းစာအုပ်မှတ်ချက်** — ဒါက တရားဝင် open documentation တွေကနေ ကိုယ်တိုင်ရေးထားတဲ့ လေ့လာစာအုပ်ပါ။ မည်သည့်ကုန်သွယ်စာအုပ်တစ်ခုကိုမှ ကူးယူ သို့မဟုတ် ပြန်ရေးထားတာ မဟုတ်ဘူး။ အသုံးပြုထားတဲ့ တရားဝင် documentation များ — PostgreSQL text search (https://www.postgresql.org/docs/current/textsearch-controls.html, https://www.postgresql.org/docs/current/textsearch-indexes.html), Elasticsearch RRF (https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion), OpenSearch vector search (https://opensearch.org/docs/latest/vector-search/)။

---

## Subtopic 1 — PostgreSQL Full-text Search နှင့် Ranking

### ဘာကို ဆိုလိုတာလဲ

Full-text search (စာသားအပြည့်အစုံရှာခြင်း) ဆိုတာ စကားလုံးတွေကို ရှာပေးတဲ့ နည်းပါ။ `tsvector` ဆိုတာ document ရဲ့ စကားလုံးတွေကို သိမ်းထားတဲ့ data type ပါ။ `tsquery` ဆိုတာ ရှာမယ့် query ကို ကိုယ်စားပြုတဲ့ data type ပါ။ ranking (အစဉ်လိုက် အမှတ်ပေးခြင်း) ကတော့ `ts_rank` ဆိုတဲ့ function နဲ့ လုပ်ပါတယ်။

### ဘာကြောင့် လဲ

Vector search တစ်ခုတည်းနဲ့ဆိုရင် အားနည်းတာပါ။ ဥပမာ — query ထဲမှာ "invoice ID 45123" လို့ ပါရင် vector search က အဓိပ္ပာယ် အနီးစပ်ဆုံး စာများကိုပဲ ပြနေတယ်။ ဒါပေမယ့် စာသားအတိအကျ ကိုက်ညီမှုက အရေးကြီးတဲ့ အခါ ရှိပါတယ်။ Full-text index မရှိရင် LIKE query ကို သုံးရပြီး တစ်ခုချင်း စကင်ရပါတယ်။ ဒါက စာရွက်များလာရင် နှေးသွားပါတယ်။ GIN index နဲ့ `tsvector` က ဒီပြဿနာကို ဖြေရပါတယ်။

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

## Subtopic 2 — BM25 Ranking (စကားလုံး တူညီမှု အမှတ်ပေးခြင်း)

### ဘာကို ဆိုလိုတာလဲ

BM25 (Best Matching 25 — Okapi BM25) ဆိုတာ query ထဲက စကားလုံးတွေ ပါဝင်ပုံ အခြေခံပြီး
document တစ်ခုချင်းစီကို အမှတ်ပေးတဲ့ **ranking function** ဖြစ်ပါတယ်။ probabilistic
information retrieval သီအိုရီ (Robertson & Zaragoza) ကနေ ဆင်းသက်လာပြီး
Elasticsearch၊ OpenSearch (Lucene) တို့ရဲ့ **default ranking algorithm** ဖြစ်ပါတယ်။
PostgreSQL ရဲ့ `ts_rank` နဲ့ အလုပ်လုပ်ပုံ မတူပါ — BM25 မှာ document အရှည်
(length normalization) နဲ့ စကားလုံး ထပ်တလဲလဲ ပါဝင်မှု (term frequency saturation)
ကို သင်္ချာနဲ့ ထိန်းချုပ်ပေးပါတယ်။

### ဘာကြောင့် လဲ

ရိုးရိုး term count (စကားလုံး ရေတွက်) နဲ့ အမှတ်ပေးရင် ပြဿနာ နှစ်ခု ရှိပါတယ် —

1. **စကားလုံး ထပ်တလဲလဲ ပါရုံနဲ့ အမှတ် ဆက်တက်နေမယ်** — "quick" ၁၀ ကြိမ် ပါတဲ့
   document က ၁ ကြိမ် ပါတာထက် ၁၀ ဆ ကောင်းတာ မဟုတ်ပါဘူး။
2. **စာရှည် document တွေ အားသာမယ်** — စာရှည်ရင် စကားလုံး ပါဖို့ အခွင့်အလမ်း
   ပိုများလို့ ရေတွက်ရုံနဲ့ဆို မျှတမှု မရှိပါဘူး။

BM25 က ဒီနှစ်ခုလုံးကို ဖြေရှင်းပါတယ် — tf ကို သတ်မှတ်ထားတဲ့ အမြင့်ဆုံး အထိသာ
တက်ခွင့်ပြု (saturation) ပြီး document အရှည်ကို corpus ပျမ်းမျှ အရှည်နဲ့ ချိန်ပေးပါတယ်။
tf-idf ထက် ရလဒ် ပိုကောင်းတဲ့ အကြောင်းရင်းလည်း ဒါပါပဲ။

### ဘယ်လို အလုပ်လုပ်လဲ

Query ထဲက စကားလုံး တစ်လုံးချင်းစီအတွက် အောက်ပါ ပုံသေနည်း အတိုင်း တွက်ပြီး
စုစုပေါင်း ပေါင်းပါတယ် —

```
score(D, Q) = Σ IDF(qᵢ) · (f(qᵢ,D) · (k1 + 1))
                         / (f(qᵢ,D) + k1 · (1 − b + b · |D| / avgdl))

IDF(qᵢ) = ln(1 + (N − n(qᵢ) + 0.5) / (n(qᵢ) + 0.5))
```

| သင်္ကေတ | အဓိပ္ပာယ် |
|---|---|
| `f(qᵢ,D)` | document D ထဲ စကားလုံး qᵢ ပါဝင်ရေ (term frequency) |
| `|D|` | document D ရဲ့ စကားလုံး အရေအတွက် |
| `avgdl` | corpus ထဲက document တွေရဲ့ ပျမ်းမျှ စကားလုံး အရေအတွက် |
| `N` | corpus ထဲက document အရေအတွက် |
| `n(qᵢ)` | စကားလုံး qᵢ ပါတဲ့ document အရေအတွက် |
| `k1` | tf saturation ထိန်းချုပ်မှု — ပုံမှန် 1.2–2.0 |
| `b` | length normalization ထိန်းချုပ်မှု — 0 (မထိန်း) မှ 1 (အပြည့်ထိန်း)၊ ပုံမှန် 0.75 |

IDF (inverse document frequency) က ရှားပါးစကားလုံးကို ပိုအလေးပေးပါတယ် — corpus
တစ်ခုလုံးမှာ ပါတဲ့ စကားလုံး (ဥပမာ "the") က IDF နည်းပြီး ရှားတဲ့ စကားလုံးက များပါတယ်။

**tf-idf vs BM25 vs ts_rank နှိုင်းယှဉ်ချက်**

| အချက် | tf-idf | BM25 | PostgreSQL `ts_rank` |
|---|---|---|---|
| tf handling | ရိုးရိုး မြှောက် | saturation (`k1`) | weights ဖြင့် ထိန်း |
| document အရှည် | မထိန်း | normalization (`b`) | ပါ/မပါ အလိုက် ပြောင်း |
| ဘယ်မှာ သုံးလဲ | အခြေခံ ဥပမာများ | Elasticsearch/OpenSearch default | PostgreSQL full-text |

### ဥပမာ

```python
# Deterministic offline demo of Okapi BM25, standard library only.
# No database is used here. k1=1.5, b=0.75 are typical values.
import math

docs = {
    'd1': 'postgres vector search with pgvector',
    'd2': 'postgres full text search ranking with tsvector and tsquery in postgres',
    'd3': 'vector search ranking comparison',
}
query = ['postgres', 'ranking']
k1, b = 1.5, 0.75

tokens = {d: t.split() for d, t in docs.items()}
N = len(docs)
avgdl = sum(len(t) for t in tokens.values()) / N
df = {q: sum(1 for t in tokens.values() if q in t) for q in query}

def idf(q):
    return math.log(1 + (N - df[q] + 0.5) / (df[q] + 0.5))

def bm25_score(d):
    total = 0.0
    for q in query:
        f = tokens[d].count(q)
        denom = f + k1 * (1 - b + b * len(tokens[d]) / avgdl)
        total += idf(q) * (f * (k1 + 1)) / denom if f else 0.0
    return total

# Expected output:
# avgdl = 6.6667 | df = {'postgres': 2, 'ranking': 2}
# d1 total = 0.5296
# d2 total = 0.9190
# d3 total = 0.5732
# ranking: d2 > d3 > d1
```

ရှင်းလင်းချက် — d2 က စကားလုံး နှစ်လုံးစလုံး ပါလို့ ထိပ်က ရောက်ပါတယ်။ 'ranking'
စကားလုံး တစ်လုံးချင်း ကြည့်ရင် d2 (စာရှည်) က 0.3636 ပဲ ရပြီး d3 (စာတို) က
0.5732 ရပါတယ် — တူညီတဲ့ tf=1 ဖြစ်ပေမယ့် length normalization ကြောင့်
စာတို document က အမှတ် ပိုရတာပါ။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

- **Elasticsearch/OpenSearch** ရဲ့ default ranking က BM25 ဖြစ်လို့ keyword search
  engine သုံးရင် ဒီသင်္ချာ နားလည်ထားရင် score တွေ ရှင်းပါတယ်။
- **PostgreSQL** က native BM25 မပေးပါ — `ts_rank` ကွဲပါတယ်။ Lucene အခြေခံ
  extension များ (ဥပမာ ParadeDB `pg_search`) က PostgreSQL ထဲ BM25 index
  ယူဆောင်လာပေးပါတယ်။
- **Hybrid search** မှာ BM25 က lexical lane (စကားလုံး လမ်း) ရဲ့ အမှတ်ပေးစနစ် ဖြစ်ပြီး
  dense vector က semantic lane (အဓိပ္ပာယ် လမ်း) ဖြစ်ပါတယ် — နှစ်လမ်း score/rank
  ကို Subtopic 4 (normalization) နှင့် Subtopic 5 (RRF) နဲ့ ပေါင်းပါတယ်။
- Sparse neural retriever များ (ဥပမာ SPLADE) က BM25 ရဲ့ lexical အားသာချက်ကို
  neural နည်းနဲ့ ချဲ့ထွင်တာ ဖြစ်ပါတယ် — နောက်ပိုင်း ခေါင်းစဉ်များတွင် ဆက်လေ့လာနိုင်ပါတယ်။

## Subtopic 3 — Trigram Similarity

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
python
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

## Subtopic 4 — Score Normalization (အမှတ်ပေးချက် တူညီအောင် လုပ်ခြင်း)

### ဘာကို ဆိုလိုတာလဲ

Normalization (အချိုးကျ ဖြစ်အောင် ပြောင်းခြင်း) ဆိုတာ score တွေရဲ့ အတိုင်းအတာကို တူညီတဲ့ အပိုင်းအခြားထဲ ပြောင်းတာပါ။ vector score က cosine similarity အဖြစ် -1 ကနေ 1 အတွင်း ပါ။ BM25 ကတော့ 0 ကနေ တရာမသိ ကြီးနိုင်ပါတယ်။

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

## Subtopic 5 — Reciprocal Rank Fusion (RRF)

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

`k` ရဲ့ သဘော — k ကြီးရင် အပေါ်ဆုံး rank တွေရဲ့ ကွာခြားချက် ချောသွားပါတယ်။ k သေးရင် top rank တွေက ပို အလေးပေးပါတယ်။

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

ဒါကြောင့် နောက်ဆုံး ranking က — d1 (≈0.0325226), d4 (≈0.031746), d2 (≈0.016393), d3 (≈0.016129)။ d2 က vector အရ ထိပ်မှာ ရှိပေမယ့် keyword အရ အောက်ဆုံး ဖြစ်နေလို့ RRF အရ အောက်ကို ဆင်းသွားတယ်။ ဒါက RRF ရဲ့ စရိုက် ဖြစ်တယ် — list တစ်ခုတည်း ထိပ်ဖျားက အားသာချက်ကို လျှော့ပြီး list နှစ်ခုလုံးမှာ ကောင်းတဲ့ document ကို ရှေ့တင်ပေးတယ်။

## အနှစ်ချုပ်

- Hybrid search က vector (အဓိပ္ပာယ်) နဲ့ keyword (စာလုံး) ကို တွဲသုံးတာ — တစ်ခုတည်း သုံးတာထက် ပိုကောင်းတာ များတယ်။
- Keyword ဘက်ကို `tsvector` နဲ့ `ts_rank_cd`၊ trigram (`pg_trgm`) ဒါမှမဟုတ် BM25 extend နဲ့ လုပ်နိုင်တယ်။
- ရမှတ် နှစ်မျိုးက scale မတူလို့ တိုက်ရိုက် ပေါင်းလို့ မရ — normalize လုပ်ရတယ်။
- RRF က score ကို မကြည့်ဘဲ rank ကိုသာ သုံးတာမို့ tuning မလိုဘဲ ခိုင်မာတယ်၊ `1/(k + rank)` နဲ့ ပေါင်းတယ်။
- `k` တန်ဖိုး ပြောင်းရင် အဆင့် ပြောင်းတယ် — ကိုယ့် eval set နဲ့ စမ်းပြီး ရွေးပါ။
- Fusion ပြီးမှ reranking ထည့်ရင် အရည်အသွေး နောက်တစ်ဆင့် တက်နိုင်တယ်။
