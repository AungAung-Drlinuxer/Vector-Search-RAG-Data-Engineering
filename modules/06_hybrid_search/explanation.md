# M6 — Hybrid Search: Full-text၊ Trigram နှင့် RRF ပေါင်းစပ်ခြင်း

> **မူရင်းစာအုပ်မှတ်ချက်** — ဒါက တရားဝင် open documentation တွေကနေ ကိုယ်တိုင်ရေးထားတဲ့ လေ့လာစာအုပ်ပါ။ မည်သည့်ကုန်သွယ်စာအုပ်တစ်ခုကိုမှ ကူးယူ သို့မဟုတ် ပြန်ရေးထားတာ မဟုတ်ဘူး။ အသုံးပြုထားတဲ့ တရားဝင် documentation များ — PostgreSQL text search (https://www.postgresql.org/docs/current/textsearch-controls.html, https://www.postgresql.org/docs/current/textsearch-indexes.html), Elasticsearch RRF (https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion), OpenSearch vector search (https://opensearch.org/docs/latest/vector-search/)။

---
## Subtopic 1 — PostgreSQL Full-text Search နှင့် Ranking

### အဓိပ္ပာယ်

Full-text search သည် စာသားအတွင်းရှိ token များကို index လုပ်၍ ရှာဖွေသော နည်းလမ်းဖြစ်သည်။ `tsvector` သည် document ၏ lexeme (token position များအပါအဝင်) များကို သိမ်းဆည်းသည့် data type ဖြစ်ပြီး `tsquery` သည် search query ၏ operator representation ဖြစ်သည်။ Ranking ကို `ts_rank` function ဖြင့် တွက်ချက်သည်။

### လိုအပ်ချက်

Dense vector search တစ်ခုတည်းတွင် exact lexical match လိုအပ်သော query များ (ဥပမာ "invoice ID 45123") အတွက် weakness ရှိသည် — semantic similarity အနီးစပ်ဆုံး chunk များသာ ပြန်ရပြီး token-level exact match ကို အာမခံမပေးနိုင်ပါ။ Full-text index မရှိပါက LIKE query ဖြင့် sequential scan လုပ်ရပြီး row အရေအတွက် တိုးလာသည်နှင့်အမျှ latency တိုးသည်။ GIN index နှင့် `tsvector` က ဤပြဿနာကို ဖြေရှင်းပေးသည်။

### လုပ်ဆောင်ပုံ

PostgreSQL full-text pipeline ၏ အဆင့်များ —

၁။ Parser က စာသားကို token များအဖြစ် ခွဲထုတ်သည်။
၂။ Token များကို lexeme (normalized base form) အဖြစ် ပြောင်းလဲသည်။ ဥပမာ "running" → "run"။
၃။ `tsvector` အတွင်း lexeme နှင့် position များကို သိမ်းဆည်းသည်။
၄။ Query ကို `tsquery` အဖြစ် ပြောင်းပြီး `@@` operator ဖြင့် match လုပ်သည်။
၅။ `ts_rank` က match အပေါ် အခြေခံ၍ score ပေးသည် — ၎င်းသည် semantic similarity မဟုတ်ဘဲ term frequency နှင့် weight setting များအပေါ် မူတည်သည်။

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

PostgreSQL ကို ချိတ်ဆက်မထားပါ။ အောက်ပါ code သည် PostgreSQL ၏ stemming အဆင့်ကို standard Python ဖြင့် stand-in အဖြစ် ပြသသည်။

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

### လက်တွေ့ အရေးပါမှု

RAG system အများစုတွင် lexical lane သည် မရှိမဖြစ် လိုအပ်သည်။ အမည်များ၊ ID များ၊ error code များသည် vector embedding တွင် collision ဖြစ်လွယ်သည်။ PostgreSQL docs အရ GIN index ကို `tsvector` column ပေါ်တွင် တည်ဆောက်နိုင်ပြီး ရှာဖွေမှုကို မြန်ဆန်စေသည်။ ၎င်းသည် hybrid search ၏ ပထမ lane ဖြစ်သည်။

---

## Subtopic 2 — BM25 Ranking

### အဓိပ္ပာယ်

BM25 (Okapi BM25) သည် query term များ၏ document အတွင်း ပါဝင်မှုအပေါ် အခြေခံ၍ relevance score ပေးသော ranking function ဖြစ်ပြီး Elasticsearch/OpenSearch (Lucene) ၏ default scoring algorithm ဖြစ်သည်။ Probabilistic information retrieval သီအိုရီ (Robertson & Zaragoza) မှ ဆင်းသက်လာသည်။ PostgreSQL ၏ `ts_rank` နှင့် မတူဘဲ BM25 သည် document အရှည် (length normalization) နှင့် term frequency saturation ကို parameter များဖြင့် ထိန်းချုပ်သည်။

### လိုအပ်ချက်

Raw term count ဖြင့် score ပေးပါက ပြဿနာ နှစ်ခု ရှိသည် —

1. **Term frequency က အဆမတန် တိုးနေမည်** — "quick" ၁၀ ကြိမ်ပါသော document သည် ၁ ကြိမ်ပါသော document ထက် ၁၀ ဆ ပိုသက်ဆိုင်သည်ဟု မဆိုနိုင်ပါ။
2. **Document ရှည်များ အားသာမည်** — document ရှည်လေ term ပါဝင်နိုင်ခြေ များလေဖြစ်၍ raw count သည် length bias ဖြစ်စေသည်။

BM25 သည် ဤနှစ်ခုလုံးကို ဖြေရှင်းသည် — tf ကို saturation point အထိသာ တက်ခွင့်ပြုပြီး document အရှည်ကို corpus ၏ ပျမ်းမျှအရှည် (avgdl) ဖြင့် ချိန်ညှိသည်။ tf-idf ထက် ရလဒ်ပိုကောင်းရသည့် အကြောင်းရင်းမှာ ဤအချက်ဖြစ်သည်။

### လုပ်ဆောင်ပုံ

Query term တစ်ခုချင်းစီအတွက် အောက်ပါ ပုံသေနည်းဖြင့် တွက်ချက်ပြီး စုစုပေါင်း ပေါင်းယူသည် —

```
score(D, Q) = Σ IDF(qᵢ) · (f(qᵢ,D) · (k1 + 1))
                         / (f(qᵢ,D) + k1 · (1 − b + b · |D| / avgdl))

IDF(qᵢ) = ln(1 + (N − n(qᵢ) + 0.5) / (n(qᵢ) + 0.5))
```
| သင်္ကေတ | အဓိပ္ပာယ် |
|---|---|
| `f(qᵢ,D)` | document D အတွင်း term qᵢ ၏ term frequency |
| `|D|` | document D ၏ token အရေအတွက် |
| `avgdl` | corpus အတွင်း document များ၏ ပျမ်းမျှ token အရေအတွက် |
| `N` | corpus အတွင်း document အရေအတွက် |
| `n(qᵢ)` | term qᵢ ပါဝင်သော document အရေအတွက် (document frequency) |
| `k1` | tf saturation parameter — ပုံမှန် 1.2–2.0 |
| `b` | length normalization parameter — 0 (ပိတ်) မှ 1 (အပြည့်)၊ ပုံမှန် 0.75 |

IDF (inverse document frequency) သည် ရှားပါး term များကို ပိုမိုအလေးပေးသည် — corpus တစ်ခုလုံးတွင် ပျံ့နှံ့သော term (ဥပမာ "the") ၏ IDF နိမ့်ပြီး ရှားပါး term ၏ IDF မြင့်သည်။

**tf-idf vs BM25 vs ts_rank နှိုင်းယှဉ်ချက်**
| အချက် | tf-idf | BM25 | PostgreSQL `ts_rank` |
|---|---|---|---|
| tf handling | ရိုးရိုး မြှောက် | saturation (`k1`) | weights ဖြင့် ထိန်း |
| document အရှည် | မထိန်း | normalization (`b`) | ပါ/မပါ အလိုက် ပြောင်း |
| အသုံးပြုရာ | အခြေခံ ဥပမာများ | Elasticsearch/OpenSearch default | PostgreSQL full-text |

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

ရှင်းလင်းချက် — d2 သည် query term နှစ်ခုလုံး ပါဝင်သဖြင့် ထိပ်ဆုံးရောက်သည်။ Term 'ranking' တစ်ခုတည်းကို ကြည့်ပါက d2 (document ရှည်) သည် 0.3636 သာရပြီး d3 (document တို) သည် 0.5732 ရသည် — tf=1 တူညီသော်လည်း length normalization ကြောင့် document တိုက ပိုမြင့်သော per-term score ရသည်။

### လက်တွေ့ အရေးပါမှု

- **Elasticsearch/OpenSearch** ၏ default ranking သည် BM25 ဖြစ်သဖြင့် keyword search engine သုံးစွဲရာတွင် ဤသင်္ချာကို နားလည်ထားပါက score distribution ကို ရှင်းလင်းစွာ အဓိပ္ပာယ်ကောက်နိုင်သည်။
- **PostgreSQL** သည် native BM25 မပေးပါ — `ts_rank` ၏ scoring သည် ကွဲပြားသည်။ Lucene အခြေခံ extension များ (ဥပမာ ParadeDB `pg_search`) က PostgreSQL အတွင်း BM25 index ယူဆောင်လာပေးသည်။
- **Hybrid search** တွင် BM25 သည် lexical lane ၏ scoring function ဖြစ်ပြီး dense vector သည် semantic lane ဖြစ်သည် — lane နှစ်ခု၏ score/rank ကို Subtopic 4 (normalization) နှင့် Subtopic 5 (RRF) တို့ဖြင့် ပေါင်းစပ်သည်။
- Sparse neural retriever များ (ဥပမာ SPLADE) သည် BM25 ၏ lexical အားသာချက်ကို neural method ဖြင့် ချဲ့ထွင်ထားခြင်းဖြစ်သည် — နောက်ပိုင်း ခေါင်းစဉ်များတွင် ဆက်လက်လေ့လာနိုင်သည်။

## Subtopic 3 — Trigram Similarity

### အဓိပ္ပာယ်

Trigram ဆိုသည်မှာ စကားလုံးတစ်ခုမှ စာလုံးသုံးလုံးဆက် window များဖြစ်သည်။ ဥပမာ "cat" ၏ trigram များမှာ `  c`, ` ca`, `cat`, `at ` တို့ဖြစ်သည်။ Trigram similarity သည် စကားလုံးနှစ်ခု၏ trigram set တူညီမှုကို တွက်ချက်သော score ဖြစ်ပြီး PostgreSQL က `pg_trgm` extension ဖြင့် ပေးသည်။

### လိုအပ်ချက်

Full-text search သည် lexeme exact match လိုအပ်သဖြင့် စာလုံးပေါင်းမှားနေပါက match မဖြစ်ပါ။ ဥပမာ user က "Postgers" ဟု typo လုပ်ပါက "PostgreSQL" နှင့် exact match မဖြစ်ပါ။ Trigram သည် typo-tolerant ဖြစ်သည် — စာလုံးတစ်လုံးမှားရုံဖြင့် trigram အများစု မပျက်စီးသောကြောင့်ဖြစ်သည်။

### လုပ်ဆောင်ပုံ

၁။ `pg_trgm` extension ကို install လုပ်သည်။
၂။ `show_trgm('word')` က trigram set ကို ထုတ်ပေးသည်။
၃။ `similarity(a, b)` က [0, 1] range အတွင်း score ပေးသည် — 1 သည် အတူတူဖြစ်သည်။
၄။ `%` operator သည် similarity threshold (`pg_trgm.similarity_threshold`) ထက်ကျော်ပါက true ပြန်သည်။
၅။ GIN index ကို trigram operator class ဖြင့် တည်ဆောက်နိုင်ပြီး fuzzy search ကို မြန်ဆန်စေသည်။

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

### လက်တွေ့ အရေးပါမှု

User input တွင် typo ပါဝင်နိုင်သည်။ Trigram မရှိပါက typo တစ်ခုသည် result သုညဖြစ်စေသည်။ PostgreSQL docs အရ `pg_trgm` သည် LIKE query များကိုပင် GIN index ဖြင့် အရှိန်မြှင့်ပေးသည်။ ၎င်းသည် hybrid search ၏ တတိယ lane အဖြစ် သုံးနိုင်သည်။

---

## Subtopic 4 — Score Normalization

### အဓိပ္ပာယ်

Normalization ဆိုသည်မှာ score များ၏ scale ကို တူညီသော range အတွင်းသို့ ပြောင်းလဲခြင်းဖြစ်သည်။ Vector score သည် cosine similarity အဖြစ် -1 မှ 1 အတွင်းရှိပြီး BM25 score သည် 0 မှ အထက်ပိုင်း unbounded ဖြစ်နိုင်သည်။

### လိုအပ်ချက်

Lane နှစ်ခုမှ raw score ကို တိုက်ရိုက်ပေါင်းပါက fusion ပျက်စီးသည်။ BM25 score magnitude သည် ကြီးမားနိုင်သဖြင့် vector score ကို လွှမ်းမိုးသွားသည် — ဥပမာ vector score 0.8 ကို BM25 score 34.2 က လုံးဝ ဖုံးအုပ်သွားသည်။ ဤသည်မှာ weighted sum ချဉ်းကပ်မှု၏ အားနည်းချက်ဖြစ်သည်။ RRF သည် raw score အစား rank ကိုသာ သုံးသဖြင့် ဤပြဿနာ ကင်းဝေးသည်။

### လုပ်ဆောင်ပုံ

Weighted sum ချဉ်းကပ်မှုတွင် —

၁။ Lane နှစ်ခုလုံးမှ score များကို ရယူသည်။
၂။ Lane တစ်ခုချင်းစီကို တူညီသော range (ဥပမာ [0, 1]) အတွင်း normalize လုပ်သည်။
၃။ Weight `w` များဖြင့် မြှောက်၍ ပေါင်းသည်။
၄။ ပေါင်းလဒ် score ဖြင့် ပြန်လည်စီစဉ်သည်။

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

### လက်တွေ့ အရေးပါမှု

ဤဥပမာတွင် d1 သည် vector lane အရ ပိုကောင်းသော်လည်း raw sum က d2 ကို အနိုင်ပေးသည် — d2 ၏ BM25 score magnitude ကြီးမားသောကြောင့်ဖြစ်သည်။ OpenSearch ၏ vector search docs အရ hybrid configuration တွင် lane score များကို တိုက်ရိုက်နှိုင်းယှဉ်၍မရပါ။ ထို့ကြောင့် normalization သို့မဟုတ် RRF သည် စံချဉ်းကပ်မှုဖြစ်သည်။

---

## Subtopic 5 — Reciprocal Rank Fusion (RRF)

### အဓိပ္ပာယ်

RRF သည် raw score များကို လုံးဝမသုံးဘဲ rank position များကိုသာ အသုံးပြုသော fusion method ဖြစ်သည်။ Elasticsearch docs အရ formula မှာ —

`RRF(d) = Σ (1 / (k + rank_i(d)))`

`k` သည် tuning constant ဖြစ်ပြီး `rank_i(d)` သည် lane i အတွင်း document d ရရှိသော rank (ထိပ်ဆုံး = rank 1) ဖြစ်သည်။

### လိုအပ်ချက်

Weighted sum တွင် ပြဿနာ သုံးခုရှိသည် — score scale မတူသဖြင့် တိုက်ရိုက်ပေါင်း၍မရခြင်း၊ normalization method ရွေးချယ်စရာ များပြားခြင်း (min-max, z-score စသည်)၊ နှင့် normalization ရွေးချယ်မှုက ရလဒ်အပေါ် သက်ရောက်ခြင်း။ RRF သည် ဤအားလုံးကို ကျော်လွှားသည် — rank သည် scale-free metric ဖြစ်ပြီး lane အားလုံးမှ တူညီသော ပုံစံဖြင့် ထွက်ရှိသောကြောင့်ဖြစ်သည်။

### လုပ်ဆောင်ပုံ

၁။ Vector lane မှ document များကို rank စီသည် — rank 1, 2, 3...
၂။ Keyword lane (full-text/trigram) ကိုလည်း rank စီသည်။
၃။ Document တစ်ခုစီအတွက် lane တစ်ခုချင်းစီတွင် `1 / (k + rank)` တွက်သည်။
၄။ Document သည် lane နှစ်ခုလုံးတွင် ပါဝင်ပါက အစိတ်အပိုင်း နှစ်ခုကို ပေါင်းသည်။
၅။ စုစုပေါင်း RRF score ဖြင့် final ranking ထုတ်သည်။

`k` ၏ သဘော — k ကြီးလေ top rank များအကြား ကွာခြားချက် ပြေလျော့လေဖြစ်ပြီး k သေးလေ top rank များ အလေးချိန် ပိုကြလေဖြစ်သည်။

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

**မှတ်ချက်** — d1 နှင့် d4 တို့၏ RRF တွက်ချက်မှု အသေးစိတ် —

- d1: rank 1 (vector) + rank 2 (keyword) → `1/61 + 1/62 ≈ 0.016393 + 0.016129 = 0.032523` (ပိုတိကျစွာ — 0.0325226...)
- d4: rank 3 (vector) + rank 3 (keyword) → `1/63 + 1/63 ≈ 0.015873 + 0.015873 = 0.031746`

ထို့ကြောင့် final ranking မှာ — d1 (≈0.0325226), d4 (≈0.031746), d2 (≈0.016393), d3 (≈0.016129)။ d2 သည် vector lane တွင် မပါဝင်သော်လည်း keyword lane တွင် rank 1 ဖြစ်သည် — သို့သော် တစ် lane တည်းတွင်သာ ပါဝင်သဖြင့် RRF တွင် အောက်သို့ ရောက်သည်။ ဤသည်မှာ RRF ၏ သဘောသဘာဝဖြစ်သည် — lane တစ်ခုတည်း၏ ထိပ်ဆုံးနေရာ အားသာချက်ကို လျှော့ချပြီး lane နှစ်ခုလုံးတွင် ကောင်းမွန်သော document ကို အထက်သို့ တင်ပေးသည်။

## အနှစ်ချုပ်

- Hybrid search သည် vector (semantic) lane နှင့် keyword (lexical) lane ကို တွဲဖက်သုံးစွဲခြင်းဖြစ်ပြီး single-lane retrieval ထက် retrieval quality ပိုကောင်းလေ့ရှိသည်။
- Keyword lane ကို `tsvector` + `ts_rank_cd`၊ trigram (`pg_trgm`)၊ သို့မဟုတ် BM25 extension ဖြင့် အကောင်အထည်ဖော်နိုင်သည်။
- Lane နှစ်ခု၏ score scale မတူသဖြင့် တိုက်ရိုက်ပေါင်း၍မရ — normalization လိုအပ်သည်။
- RRF သည် score အစား rank ကိုသာ သုံးသဖြင့် scale tuning မလိုဘဲ robust ဖြစ်ပြီး `1/(k + rank)` ဖြင့် ပေါင်းစပ်သည်။
- `k` တန်ဖိုး ပြောင်းလဲပါက ranking ပြောင်းလဲသည် — မိမိ၏ eval set ဖြင့် စမ်းသပ်၍ ရွေးချယ်သင့်သည်။
- Fusion အပြီး reranking အဆင့် ထပ်ထည့်ပါက retrieval quality နောက်တစ်ဆင့် တိုးတက်နိုင်သည်။
