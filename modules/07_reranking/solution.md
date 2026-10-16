## လေ့ကျင့်ခန်း ၁ — Bi-encoder vs Cross-encoder Architectural Differences

Bi-encoder သည် query နှင့် document များကို သီးခြားစီ encode လုပ်သဖြင့် document embeddings များကို offline compute လုပ်ကာ vector database တွင် cache ပြုလုပ်နိုင်သည်။ Cross-encoder သည် (query, document) pair ကို model ထဲသို့ joint input အဖြစ် ထည့်သွင်း၍ full cross-attention ဖြင့် direct relevance score တွက်ချက်သည်။ ဤ structural differences များကို အောက်ပါ script တွင် အကျဉ်းချုပ် ဖော်ပြထားသည်။

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

**အဓိကအယူအဆ** — Large corpus မှ high-throughput first-stage candidate retrieval အတွက် bi-encoder ကို အသုံးပြုပြီး top-k candidates ၏ high-precision reranking အတွက် cross-encoder ကို အသုံးပြုသည်။

---

## လေ့ကျင့်ခန်း ၂ — Cosine Similarity Scoring & Top-K Manual Reranking

Standard library `math` ဖြင့် query vector နှင့် candidate document vectors ၅ ခုကြား cosine similarity တွက်ချက်ကာ descending order အတိုင်း top-3 candidates ကို rerank ပြုလုပ်ပုံ ဖြစ်သည်။

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
    nb = math.sqrt(sum(y * y for y in b))
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

**အဓိကအယူအဆ** — First-stage candidate pool အား secondary similarity metrics သို့မဟုတ် alternative scoring functions များဖြင့် descending sort ပြုလုပ်ခြင်းသည် reranking ၏ algorithmic foundation ဖြစ်သည်။

---

## လေ့ကျင့်ခန်း ၃ — Cross-encoder Reranking Latency Cost Modeling

Cross-encoder သည် candidate တစ်ခုချင်းစီအတွက် neural forward pass လိုအပ်သဖြင့် candidate size (top-k) နှင့် linear အချိုးအစားအတိုင်း latency overhead ဖြစ်ပေါ်စေပုံကို အောက်ပါ formula ဖြင့် သရုပ်ပြထားသည်။

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

**အဓိကအယူအဆ** — Reranker overhead သည် `top_k * per_call_ms` အတိုင်း တိုးပွားသဖြင့် system p95 latency budget နှင့် ကိုက်ညီသော top-k candidate threshold ကို စနစ်တကျ သတ်မှတ်ရမည်။

---

## လေ့ကျင့်ခန်း ၄ — HyDE (Hypothetical Document Embeddings) Retrieval Alignment

Raw question embedding နှင့် LLM-generated hypothetical answer document embedding တို့၏ target corpus စာရွက်စာတမ်းများနှင့် cosine similarity ကွာခြားချက်ကို နှိုင်းယှဉ်ထားသည်။

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
    nb = math.sqrt(sum(y * y for y in b))
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

**အဓိကအယူအဆ** — HyDE သည် query intent ကို answer-like structure အဖြစ် ကြိုတင် projection ပြုလုပ်ပေးသဖြင့် direct question match ထက် semantic overlap ပိုမိုမြင့်မားသော documents (ဥပမာ d2) ကို ရှာဖွေနိုင်စွမ်း တိုးတက်စေသည်။

---

## လေ့ကျင့်ခန်း ၅ — Multi-Query Expansion & RRF Score Fusion

Query paraphrases ၃ ခုမှ ထွက်ပေါ်လာသော independent ranking lists များကို Reciprocal Rank Fusion (`1 / (60 + rank)`) ဖြင့် consensus fused ranking အဖြစ် ပေါင်းစပ်ပုံ ဖြစ်သည်။

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

**အဓိကအယူအဆ** — RRF သည် absolute scores များကို normalize လုပ်ရန် မလိုဘဲ rank ordering အပေါ်တွင် aggregate ပြုလုပ်သဖြင့် diverse query formulations များမှ consensus candidate ranking ကို တည်ငြိမ်စွာ ထုတ်ယူနိုင်သည်။

---

## လေ့ကျင့်ခန်း ၆ — MMR (Maximal Marginal Relevance) Diversity Selection

Hyperparameter λ (relevance vs diversity weight) တန်ဖိုးနှစ်ခု (0.9 vs 0.3) ဖြင့် greedy MMR selection algorithm ကို execute လုပ်ပြီး redundant candidates များကို penalize ပြုလုပ်ပုံ ဖြစ်သည်။

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
    nb = math.sqrt(sum(y * y for y in b))
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

**အဓိကအယူအဆ** — λ=0.9 တွင် query နှင့် အလွန်ဆင်တူသော near-duplicates များ (d1, d3, d2) ရွေးချယ်ခံရပြီး λ=0.3 တွင် redundant candidates များကို ရှောင်ရှား၍ information space ကို ပိုမိုလွှမ်းခြုံနိုင်သော diverse documents (d1, d6, d5) ကို ရွေးချယ်ပေးသည်။
