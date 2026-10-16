## လေ့ကျင့်ခန်း ၁ — tsvector ဆောက်ခြင်း (အခြေခံ)

PostgreSQL ၏ `tsvector` သည် စာအပိုဒ်အတွင်းရှိ token များကို lexeme + position အဖြစ် သိမ်းဆည်းသည်။ ဒီနေရာတွင် DB ချိတ်ဆက်မည်မဟုတ်ဘဲ `to_tsvector` ၏ logic ကို Python dict ဖြင့် simulate လုပ်ပြထားသည်။

```python
# Simulating PostgreSQL's to_tsvector(): word -> list of positions (1-based)
def make_tsvector(text):
    """Build a tsvector-like dict: {lexeme: [positions]} from raw text."""
    tsvector = {}
    for position, word in enumerate(text.split(), start=1):
        lexeme = word.lower()  # basic normalization (real PG also stems words)
        tsvector.setdefault(lexeme, []).append(position)
    return tsvector

docs = [
    "the quick brown fox",
    "the lazy dog the",          # 'the' repeats -> positions [1, 4]
    "postgres vector search guide",
]

for doc in docs:
    print(doc, "->", make_tsvector(doc))
# Expected output:
# the quick brown fox -> {'the': [1], 'quick': [2], 'brown': [3], 'fox': [4]}
# the lazy dog the -> {'the': [1, 4], 'lazy': [2], 'dog': [3]}
# postgres vector search guide -> {'postgres': [1], 'vector': [2], 'search': [3], 'guide': [4]}
```

**အဓိကအချက်** — `tsvector` သည် lexeme နှင့် position များကို သိမ်းဆည်းထားသဖြင့် နောက်ပိုင်း matching နှင့် ranking အဆင့်များ၏ အခြေခံ input ဖြစ်သည်။

## လေ့ကျင့်ခန်း ၂ — tsquery matching နှင့် ranking (ts_rank style)

`tsquery` သည် query term များကို document ၏ lexeme များနှင့် match လုပ်ပြီး `ts_rank` ကဲ့သို့ score ထုတ်ပေးသည်။ ဒီနေရာတွင် matched word count ကိုသာ သုံးထားပြီး ရလဒ်များကို score descending ဖြင့် စီစဉ်ပြထားသည်။

```python
# tsvector simulation (from Exercise 1) + tsquery matching -> simple rank score
def make_tsvector(text):
    tsvector = {}
    for position, word in enumerate(text.split(), start=1):
        tsvector.setdefault(word.lower(), []).append(position)
    return tsvector

def match_score(tsvector, query_words):
    """Score = number of distinct query words present in the document."""
    doc_words = set(tsvector.keys())
    return len(doc_words.intersection(query_words))

docs = {
    "doc1": "postgres vector search guide",
    "doc2": "mysql administration handbook",
    "doc3": "search guide for postgres",
}
query = ["postgres", "search"]

results = []
for name, text in docs.items():
    score = match_score(make_tsvector(text), query)
    results.append((name, score))

# Sort by score descending (name as deterministic tie-break)
results.sort(key=lambda item: (-item[1], item[0]))
for name, score in results:
    print(name, score)

# Negative test: a word that matches nothing scores 0
print("mysql-only query on doc1:",
      match_score(make_tsvector(docs["doc1"]), ["mysql"]))
# Expected output:
# doc1 2
# doc3 2
# doc2 0
# mysql-only query on doc1: 0
```

**အဓိကအချက်** — Ranking score ၏ အရိုးရှင်းဆုံး ပုံစံသည် match ဖြစ်သော query term အရေအတွက်ပင် ဖြစ်သည်။

## လေ့ကျင့်ခန်း ၃ — Trigram similarity (3-gram Jaccard)

Trigram သည် စာလုံး ၃ လုံး window ဖြစ်ပြီး ရှေ့နောက် space ၂ လုံး pad လုပ်ကာ set ဆောက်သည်။ PostgreSQL ၏ `pg_trgm` extension သည် ဤ logic ဖြင့် similarity တွက်ချက်ပြီး စာလုံးပေါင်းလွဲမှားမှုများကို ဖမ်းယူပေးသည်။

```python
# 3-gram Jaccard similarity, as pg_trgm / GiST trigram indexes approximate
def trigrams(word):
    padded = "  " + word + "  "   # pad with two spaces on each side
    return {padded[i:i + 3] for i in range(len(padded) - 2)}

def jaccard(a, b):
    sa, sb = trigrams(a), trigrams(b)
    common = len(sa & sb)
    union = len(sa | sb)
    return common / union if union else 0.0

pairs = [("postgres", "postgresql"), ("postgres", "banana")]
for w1, w2 in pairs:
    sa, sb = trigrams(w1), trigrams(w2)
    print(w1, "trigrams:", sorted(sa))
    print(w2, "trigrams:", sorted(sb))
    print("common:", len(sa & sb), "union:", len(sa | sb))
    print("similarity:", jaccard(w1, w2))
    print("---")
# Expected output:
# postgres trigrams: ['  p', ' po', 'es ', 'gre', 'ost', 'pos', 'res', 's  ', 'stg', 'tgr']
# postgresql trigrams: ['  p', ' po', 'esq', 'gre', 'l  ', 'ost', 'pos', 'ql ', 'res', 'sql', 'stg', 'tgr']
# common: 8 union: 14
# similarity: 0.5714285714285714
# ---
# postgres trigrams: ['  p', ' po', 'es ', 'gre', 'ost', 'pos', 'res', 's  ', 'stg', 'tgr']
# banana trigrams: ['  b', ' ba', 'a  ', 'ana', 'ban', 'na ', 'nan']
# common: 0 union: 17
# similarity: 0.0
# ---
```

**အဓိကအချက်** — Trigram Jaccard သည် `postgres`/`postgresql` ကဲ့သို့ နီးစပ်သော စကားလုံးစုံတွဲများတွင် typo ကောင်းစွာ ဖမ်းယူနိုင်သည်။

## လေ့ကျင့်ခန်း ၄ — BM25 score တွက်ခြင်း

**အဆင့် ၁ — corpus statistics**

```
d1: tokens 4  ('the quick brown fox')
d2: tokens 9  ('the quick quick fox sleeps in the warm sun')
d3: tokens 6  ('a sleepy fox in the barn')
avgdl = (4 + 9 + 6) / 3 = 6.3333
df(quick) = 2 (d1, d2)   df(fox) = 3 (d1, d2, d3)
```

**အဆင့် ၂ — IDF** (N = 3)

```
idf(quick) = ln(1 + (3 − 2 + 0.5) / (2 + 0.5)) = ln(1.6) = 0.470004
idf(fox)   = ln(1 + (3 − 3 + 0.5) / (3 + 0.5)) = ln(1.142857) = 0.133531
```

**အဆင့် ၃ — Per-term score** (k1 = 1.2, b = 0.75)

d1 (|D| = 4) — `quick` f=1:
`0.470004 · (1·2.2) / (1 + 1.2·(0.25 + 0.75·4/6.3333))` = `1.034 / 1.8667` = **0.5534**
`fox` f=1: `0.133531 · 2.2 / 1.8667` = **0.1572** → total **0.7106**

d2 (|D| = 9) — `quick` f=2:
`0.470004 · (2·2.2) / (2 + 1.2·(0.25 + 0.75·9/6.3333))` = `2.068 / 3.5746` = **0.5778**
`fox` f=1: `0.133531 · 2.2 / 3.5746` = **0.1139** → total **0.6917**

d3 (|D| = 6) — `fox` f=1:
`0.133531 · 2.2 / (1 + 1.2·(0.25 + 0.75·6/6.3333))` = `0.2938 / 2.1491` = **0.1365** → total **0.1365**

**Ranking: d1 (0.7106) > d2 (0.6917) > d3 (0.1365)**

**Observation:** d2 တွင် `quick` ၂ ကြိမ် ပါဝင်သော်လည်း d1 အောက် ရောက်သည်။ အကြောင်းရင်း နှစ်ချက် —
(၁) tf saturation — `k1` ကြောင့် f=2 ၏ အမြတ်သည် f=1 ထက် အများကြီး မတိုးပါ
(၂) length normalization — d2 သည် token ၉ လုံးရှိ၍ ပျမ်းမျှ (6.3333) ထက် ရှည်ပြီး penalty ရသည်။ ဤနှစ်ချက် ပေါင်းစပ်သွားသဖြင့် document တိုဖြစ်သော d1 က ဦးဆောင်သည်။

## လေ့ကျင့်ခန်း ၅ — Weighted sum တွင် score normalization ၏ အရေးပါမှု

Vector score သည် [0, 1] range တွင်ရှိပြီး BM25 score သည် magnitude ~10 ရှိနိုင်သဖြင့် တိုက်ရိုက်ပေါင်းပါက BM25 lane တစ်ခုတည်းက fusion ရလဒ်ကို လွှမ်းမိုးသည်။ Min-max normalize လုပ်မှသာ lane နှစ်ခုလုံး ညီမျှစွာ ပါဝင်လာသည်။

```python
# Weighted sum: raw scores vs min-max normalized scores (0.5/0.5 weights)
def min_max(values):
    lo, hi = min(values), max(values)
    if hi == lo:
        return [0.0] * len(values)   # edge case: all equal -> avoid zero division
    return [(x - lo) / (hi - lo) for x in values]

docs = ["A", "B", "C"]
vector_scores = [0.9, 0.8, 0.7]
bm25_scores = [5.0, 12.0, 20.0]

# (1) raw weighted sum, 0.5/0.5
raw = [0.5 * v + 0.5 * b for v, b in zip(vector_scores, bm25_scores)]
# (2) normalized weighted sum, 0.5/0.5
norm_v = min_max(vector_scores)
norm_b = min_max(bm25_scores)
norm = [0.5 * v + 0.5 * b for v, b in zip(norm_v, norm_b)]

def ranked(scores):
    return [docs[i] for i in sorted(range(len(scores)), key=lambda i: -scores[i])]

print("raw sums:    ", [round(s, 4) for s in raw],     "-> ranking:", ranked(raw))
print("norm vector: ", [round(s, 4) for s in norm_v])
print("norm bm25:   ", [round(s, 4) for s in norm_b])
print("norm sums:   ", [round(s, 4) for s in norm],     "-> ranking:", ranked(norm))
# Expected output:
# raw sums:     [2.95, 6.4, 10.35] -> ranking: ['C', 'B', 'A']
# norm vector:  [1.0, 0.5, 0.0]
# norm bm25:    [0.0, 0.4667, 1.0]
# norm sums:    [0.5, 0.4833, 0.5] -> ranking: ['A', 'C', 'B']
```

**အဓိကအချက်** — Scale မတူသော score များကို ပေါင်းမီ normalize လုပ်ရန် လိုအပ်သည်။ မလုပ်ပါက scale ကြီးသော lane က ranking ကို လွှမ်းမိုးသည်။

## လေ့ကျင့်ခန်း ၆ — Reciprocal Rank Fusion (RRF) အခြေခံ

RRF သည် score value ကို လုံးဝမသုံးဘဲ rank ကိုသာ `1 / (k + rank)` ဖြင့် ပြောင်းလဲ၍ ပေါင်းသဖြင့် scale ပြဿနာကို အလုံးစုံ ရှောင်ရှားနိုင်သည်။ `k = 60` သည် Elasticsearch/OpenSearch တွင် သုံးလေ့ရှိသော တန်ဖိုးဖြစ်သည်။

```python
# Reciprocal Rank Fusion: rrf_score = sum over lists of 1 / (k + rank)
K = 60

def rrf_score(ranks, k):
    """ranks: list of this doc's rank in each list (1-based). Missing list = skip."""
    return sum(1.0 / (k + r) for r in ranks)

vector_rank_list  = ["A", "B", "C", "D"]   # A best on vector path
keyword_rank_list = ["B", "C", "A", "D"]   # B best on keyword path

ranks = {}
for rank, doc in enumerate(vector_rank_list, start=1):
    ranks.setdefault(doc, []).append(rank)
for rank, doc in enumerate(keyword_rank_list, start=1):
    ranks.setdefault(doc, []).append(rank)

scores = {doc: rrf_score(rs, K) for doc, rs in ranks.items()}
final = sorted(scores.items(), key=lambda item: -item[1])

for doc, rs in sorted(ranks.items()):
    print(doc, "ranks:", rs, "rrf:", scores[doc])
print("final ranking k=60:", [doc for doc, _ in final])
# Expected output:
# A ranks: [1, 3] rrf: 0.032266458495966696
# B ranks: [2, 1] rrf: 0.03252247488101534
# C ranks: [3, 2] rrf: 0.03200204813108039
# D ranks: [4, 4] rrf: 0.03125
# final ranking k=60: ['B', 'A', 'C', 'D']
```

**အဓိကအချက်** — RRF တွင် B သည် vector lane rank 2 နှင့် keyword lane rank 1 ပေါင်းစပ်မှုကြောင့် vector lane rank 1 ဖြစ်သော A ကို အနည်းငယ် ကျော်တက်သွားသည် — score scale မသုံးဘဲ ranking နှစ်ခု ပေါင်းစပ်နိုင်ကြောင်း ပြသသည်။

## လေ့ကျင့်ခန်း ၇ — Full hybrid pipeline: နှစ်လမ်း fan-out ပြီး RRF ဖြင့် fusion

နောက်ဆုံး လေ့ကျင့်ခန်းတွင် query တစ်ခုကို keyword path နှင့် vector path နှစ်လမ်းသို့ fan-out ပြီး ရလာသော rank များကို RRF ဖြင့် fuse လုပ်သော hybrid search ၏ simplified model ကို တည်ဆောက်သည်။ Vector path အတွက် real embedding model အစား ကြိုတင်သတ်မှတ်ထားသော deterministic vector များဖြင့် cosine similarity ကို standard library သုံး၍ တွက်ချက်သည်။

```python
# Full hybrid pipeline: keyword match score + cosine similarity -> RRF fusion.
# No real embedding model: vectors are hardcoded so everything is deterministic & offline.
import math

def make_tsvector(text):
    tsvector = {}
    for pos, word in enumerate(text.split(), start=1):
        tsvector.setdefault(word.lower(), []).append(pos)
    return tsvector

def keyword_score(text, query_words):
    return len(set(make_tsvector(text)).intersection(query_words))

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0

def ranks_from(scores):
    """Rank docs by score descending; ties broken by doc name for determinism."""
    ordered = sorted(scores, key=lambda d: (-scores[d], d))
    return {doc: i + 1 for i, doc in enumerate(ordered)}

def rrf_fuse(rank_dicts, k):
    total = {}
    for rd in rank_dicts:
        for doc, rank in rd.items():
            total[doc] = total.get(doc, 0.0) + 1.0 / (k + rank)
    return total

docs = {
    "A": "postgres vector search guide",
    "B": "hybrid search with rrf fusion",
    "C": "database indexing and performance",
    "D": "machine learning for search ranking",
    "E": "vector database embeddings guide",
}
query_words = ["postgres", "search", "guide"]
query_vec = [1, 0]   # scripted stand-in for an embedding model output
doc_vecs = {          # hardcoded deterministic "embeddings"
    "A": [4, 3], "B": [3, 4], "C": [1, 3], "D": [1, 7], "E": [7, 2],
}

kw_scores  = {d: keyword_score(t, query_words) for d, t in docs.items()}
vec_scores = {d: cosine(query_vec, v) for d, v in doc_vecs.items()}
kw_rank  = ranks_from(kw_scores)
vec_rank = ranks_from(vec_scores)
print("keyword scores:", kw_scores)
print("vector cosines:", {d: round(s, 4) for d, s in vec_scores.items()})

for k in (60, 1):
    fused = rrf_fuse([kw_rank, vec_rank], k)
    top3 = sorted(fused.items(), key=lambda item: -item[1])[:3]
    print(f"top-3 with k={k}:", [(d, round(s, 6)) for d, s in top3])

print("observation: with k=1 the winner's lead over the runner-up is ~0.4167,")
print("with k=60 only ~0.0008 -> smaller k makes top ranks dominate much harder.")
# Expected output:
# keyword scores: {'A': 3, 'B': 1, 'C': 0, 'D': 1, 'E': 1}
# vector cosines: {'A': 0.8, 'B': 0.6, 'C': 0.3162, 'D': 0.1414, 'E': 0.9615}
# top-3 with k=60: [('A', 0.032522), ('E', 0.032018), ('B', 0.032002)]
# top-3 with k=1: [('A', 0.833333), ('E', 0.7), ('B', 0.583333)]
# observation: with k=1 the winner's lead over the runner-up is ~0.4167,
# with k=60 only ~0.0008 -> smaller k makes top ranks dominate much harder.
```

**အဓိကအချက်** — Lane နှစ်ခုလုံးတွင် အလယ်အလတ် ကောင်းမွန်သော document (B) ကို RRF က မြှင့်တင်ပေးပြီး `k` သေးသွားပါက top rank များ၏ အလေးချိန် သိသိသာသာ ပိုကြသွားသည်။
