## လေ့ကျင့်ခန်း ၁ — Bi-encoder နဲ့ Cross-encoder ကွာခြားချက် ဖော်ပြခြင်း

Bi-encoder က query နဲ့ document ကို သီးသန့်သီးသန့် embed လုပ်ပြီး vector တွေချင်း နှိုင်းတတ်ပါတယ်၊ ဒါကြောင့် document embedding တွေကို ကြိုတင်ပြီး offline မှာ cache လုပ်လို့ရပါတယ်။ Cross-encoder ကတော့ query နဲ့ document နှစ်ခုကို တွဲပြီး တစ်ပြိုင်နက်တည်း သုံးသပ်ပြီး score တစ်ခုတည်း ထုတ်ပေးတာပါ။ ဒါကြောင့် bi-encoder က သန်းနဲ့ချီတဲ့ corpus ကနေ မြန်မြန် retrieve လုပ်ဖို့၊ cross-encoder က top-k အနည်းငယ်ကိုပဲ တိကျစွာ rerank လုပ်ဖို့ သင့်တော်ပါတယ်။

```python
# Deterministic, offline illustration of the bi-encoder vs cross-encoder distinction
# (text comes from sbert.net's description; no model is called here).

facts = [
    "1) Bi-encoder embeds query and document SEPARATELY, then compares vectors -> document embeddings can be cached offline.",
    "2) Cross-encoder feeds (query, document) PAIRS through one model -> produces one relevance score, no reusable doc embedding.",
    "3) Use bi-encoder for fast retrieval over a huge corpus; use cross-encoder to rerank only the top-k candidates.",
]
for f in facts:
    print(f)
# Expected output:
# 1) Bi-encoder embeds query and document SEPARATELY, then compares vectors -> document embeddings can be cached offline.
# 2) Cross-encoder feeds (query, document) PAIRS through one model -> produces one relevance score, no reusable doc embedding.
# 3) Use bi-encoder for fast retrieval over a huge corpus; use cross-encoder to rerank only the top-k candidates.
```

**အဓိကအယူဆ** — Bi-encoder က cache လုပ်လို့ရတဲ့ သီးသန့် embedding နဲ့ မြန်မြန် retrieve လုပ်ပေးပြီး cross-encoder က တွဲသုံးသပ်တဲ့ အတွက် ပိုတိကျပေးမယ် ဆိုတာပါ။

## လေ့ကျင့်ခန်း ၂ — Cosine Score နဲ့ Manual Reranking

Query တစ်ခုနဲ့ document ၅ ခုကို vector အနေနဲ့ သတ်မှတ်ပြီး cosine similarity ကို ကိုယ်တိုင်တွက်ပြပါမယ်။ ပြီးတဲ့နောက် score အမြင့်ဆုံး ၃ ခုကို sorted နဲ့ reverse=True သုံးပြီး rerank လုပ်ပြမယ်နော်။

```python
# Manual cosine scoring + reranking using only the standard library (math).
import math

query = [1.0, 0.0]
docs = {
    "d1": [0.9, 0.1],
    "d2": [0.5, 0.5],
    "d3": [0.0, 1.0],
    "d4": [0.8, -0.6],
    "d5": [-0.5, 0.5],
}

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb)

scored = {doc_id: cosine(query, vec) for doc_id, vec in docs.items()}
for doc_id, score in scored.items():
    print(doc_id, round(score, 3))

# Rerank: keep top-3, highest score first
top3 = sorted(scored.items(), key=lambda item: item[1], reverse=True)[:3]
print("Reranked top-3:", [doc_id for doc_id, _ in top3])
# Expected output:
# d1 0.994
# d2 0.707
# d3 0.0
# d4 0.8
# d5 -0.707
# Reranked top-3: ['d1', 'd4', 'd2']
```

**အဓိကအယူဆ** — Score အားလုံးကို အရင်တွက်ပြီးမှ sorted နဲ့ key=lambda, reverse=True သုံးပြီး top-3 ကို အမြင့်ဆုံးက ရှေ့ရှိစေပြီး ရွေးနိုင်တယ်ဆိုတာပါ။

## လေ့ကျင့်ခန်း ၃ — Latency ကုန်ကျစရိတ် တွက်ချက်ခြင်း

Cross-encoder က document တစ်ခုချင်းစီအတွက် ခေါ်ရတဲ့အတွက် ကုန်ကျစရိတ်က top-k အရေအတွက်ပေါ် မူတည်ပါတယ်။ Formula က (top-k × per-call ms) ပါ၊ ဒါကြောင့် 20 × 50 ms = 1,000 ms ဖြစ်ပြီး retrieve တာထက် သိသိသာသာ ပိုကြာပါတယ်နော်။

```python
# Latency cost calculation for a cross-encoder reranking stage.
# NOTE: all numbers depend on the stated assumptions, not real measurements.
per_call_ms = 50      # assumed cross-encoder latency per (query, doc) pair
top_k = 20            # how many candidates we rerank
retrieve_only_ms = 30 # assumed latency of pure vector retrieval (no rerank)

# Formula: rerank_latency_ms = top_k * per_call_ms
rerank_ms = top_k * per_call_ms

print("per cross-encoder call:", per_call_ms, "ms")
print("top-k candidates:", top_k)
print("rerank cost:", rerank_ms, "ms")
print("retrieve-only latency:", retrieve_only_ms, "ms")

total_ms = retrieve_only_ms + rerank_ms
extra_ms = total_ms - retrieve_only_ms
print("total with rerank:", total_ms, "ms")
print("extra vs retrieve-only:", extra_ms, "ms")
# Expected output:
# per cross-encoder call: 50 ms
# top-k candidates: 20
# rerank cost: 1000 ms
# retrieve-only latency: 30 ms
# total with rerank: 1030 ms
# extra vs retrieve-only: 1000 ms
```

**အဓိကအယူဆ** — Rerank ရဲ့ latency က top-k × per-call ms အတိုင်း တိုးလို့ top-k ကို သေးသေး ထိန်းထားမှ စရိတ်ချုံ့လို့ရတယ်ဆိုတာပါ။

## လေ့ကျင့်ခန်း ၄ — HyDE (Hypothetical Document Embedding) စမ်းသပ်ခြင်း

HyDE မှာ query အတွက် hypothetical answer တစ်ခု ရေးပြီး အဲဒီစာရဲ့ embedding နဲ့ document တွေကို နှိုင်းတာပါ (arxiv.org/abs/2212.10496)။ တကယ့် LLM မသုံးဘဲ hypothetical answer ကို hardcoded လုပ်ထားပြီး query တိုက်ရိုက် score နဲ့ နှိုင်းပြပါမယ်။

```python
# HyDE comparison: query-direct embedding vs hypothetical-document embedding.
# The "hypothetical answer" is HARDCODED because a real LLM call is not allowed
# offline; it stands in for what an LLM would generate.
import math

query = [1.0, 0.2, 0.0]                # embedding of the raw question
hypothetical = [0.9, 0.8, 0.1]         # hardcoded "hypothetical answer" embedding
docs = {
    "d1": [0.95, 0.1, 0.0],
    "d2": [0.6, 0.5, 0.0],
    "d3": [0.0, 1.0, 0.0],
}

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb)

for doc_id, vec in docs.items():
    direct = cosine(query, vec)
    hyde = cosine(hypothetical, vec)
    print(doc_id, "direct:", round(direct, 3), "| HyDE:", round(hyde, 3))
# Expected output:
# d1 direct: 0.996 | HyDE: 0.81
# d2 direct: 0.879 | HyDE: 0.996
# d3 direct: 0.196 | HyDE: 0.662
```

**အဓိကအယူဆ** — HyDE က question ပုံစံ query ထက် answer ပုံစံ hypothetical document က document တွေနဲ့ ပိုတူညီမှုရှိလို့ d2 နဲ့ d3 ရဲ့ score တွေ တက်လာတာ မြင်ရတယ်ဆိုတာပါ။

## လေ့ကျင့်ခန်း ၅ — Multi-query Expansion နဲ့ RRF Fusion

Query တစ်ခုကို paraphrase ၃ မျိုးရေးပြီး တစ်ခုစီအတွက် ranked list သတ်မှတ်ပါမယ်။ ပြီးတာနဲ့ RRF formula (score = sum of 1/(k + rank), k=60) သုံးပြီး ranking တွေကို တစ်ခုတည်းသော fused ranking အဖြစ် ပေါင်းပြပါမယ်။

```python
# Multi-query expansion fused with Reciprocal Rank Fusion (RRF).
# Rankings are hardcoded deterministic stand-ins for three vector searches.

K = 60  # standard RRF constant
rankings = {
    "paraphrase 1": ["d1", "d2", "d3", "d4"],
    "paraphrase 2": ["d2", "d1", "d4", "d3"],
    "paraphrase 3": ["d3", "d1", "d2", "d4"],
}

# Show each paraphrase's ranking (rank starts at 1)
for name, ranked in rankings.items():
    print(name, "->", {doc_id: rank for rank, doc_id in enumerate(ranked, start=1)})

# RRF: score = sum over queries of 1 / (K + rank)
rrf_scores = {}
for ranked in rankings.values():
    for rank, doc_id in enumerate(ranked, start=1):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (K + rank)

fused = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)
for doc_id, score in fused:
    print(doc_id, round(score, 4))
print("Fused order:", [doc_id for doc_id, _ in fused])
# Expected output:
# paraphrase 1 -> {'d1': 1, 'd2': 2, 'd3': 3, 'd4': 4}
# paraphrase 2 -> {'d2': 1, 'd1': 2, 'd4': 3, 'd3': 4}
# paraphrase 3 -> {'d3': 1, 'd1': 2, 'd2': 3, 'd4': 4}
# d1 0.0487
# d2 0.0484
# d3 0.0479
# d4 0.0471
# Fused order: ['d1', 'd2', 'd3', 'd4']
```

**အဓိကအယူဆ** — RRF က score အစား rank ကို အသုံးပြုလို့ scale မတူတဲ relevance score တွေရှိစေကာမှ ranking များစွာကို တညီတည်း ပေါင်းနိုင်တယ်ဆိုတာပါ။

## လေ့ကျင့်ခန်း ၆ — MMR (Maximal Marginal Relevance) အပြည့်အစုံ

Document ၆ ခုရဲ့ embedding တွေကို သတ်မှတ်ပြီး MMR formula (score = lambda × sim(q,d) − (1 − lambda) × max sim(d, selected)) နဲ့ lambda 0.3 နဲ့ 0.9 ၂ မျိုး သုံးပြီး ရွေးပါမယ်။ Lambda မြင့်ရင် relevance က ထင်ရှားပြီး lambda နိမ့်ရင် diversity က ထင်ရှားလာပါတယ်နော်။

```python
# Full MMR (Maximal Marginal Relevance) selection with two lambda values.
import math

query = [1.0, 0.0]
docs = {
    "d1": [0.98, 0.1],
    "d2": [0.96, 0.2],
    "d3": [0.95, -0.15],
    "d4": [0.6, 0.8],
    "d5": [0.7, -0.7],
    "d6": [0.3, 0.9],
}

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb)

relevance = {doc_id: cosine(query, vec) for doc_id, vec in docs.items()}

def mmr_select(lam, n=3):
    selected = []
    while len(selected) < n:
        best_id, best_score = None, None
        for doc_id in docs:
            if doc_id in selected:
                continue
            if not selected:  # empty selected list -> pure relevance
                score = lam * relevance[doc_id]
            else:
                max_sim = max(cosine(docs[doc_id], docs[s]) for s in selected)
                score = lam * relevance[doc_id] - (1 - lam) * max_sim
            if best_score is None or score > best_score:
                best_id, best_score = doc_id, score
        selected.append(best_id)
    return selected

for lam in (0.9, 0.3):
    print("lambda =", lam, "->", mmr_select(lam))
# Expected output:
# lambda = 0.9 -> ['d1', 'd3', 'd2']
# lambda = 0.3 -> ['d1', 'd6', 'd5']
```

**အဓိကအယူဆ** — lambda = 0.9 မှာ d1 နဲ့ တူတဲ့ d2, d3 တွေ ဆက်ရွေးခံရပေမယ့် lambda = 0.3 မှာတော့ တူတဲ့ document တွေကို ကြဉ်ပြီး ကွဲပြားတဲ့ d6, d5 တွေ ရွေးခံရတာပါ။
