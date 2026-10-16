# M7 — Reranking & Query Transformation

Retrieval architecture တွင် first-stage retriever (vector search သို့မဟုတ် hybrid search) သည် high recall ကို ဦးတည်ပြီး second-stage reranker သည် high precision ကို ဦးတည်သည်။ ဤ module တွင် bi-encoder နှင့် cross-encoder ၏ computational trade-offs၊ latency modeling၊ HyDE၊ multi-query expansion နှင့် MMR diversity selection တို့ကို programmatic နည်းလမ်းဖြင့် လေ့လာမည်။

---

## ၁။ Bi-encoder နှင့် Cross-encoder Architecture

### Overview

Bi-encoder သည် query နှင့် document များကို သီးခြား neural networks (သို့မဟုတ် shared-weight Siamese network) ဖြင့် independent vector representations အဖြစ် encode လုပ်ပြီး vector distance (cosine similarity) ဖြင့် နှိုင်းယှဉ်သည်။ Cross-encoder သည် query နှင့် document ကို single sequence အဖြစ် concatenate လုပ်ပြီး full self-attention layer များမှတစ်ဆင့် joint relevance score တစ်ခုတည်းကို ထုတ်ပေးသည်။

### Engineering Rationale

Bi-encoder သည် document vectors များကို offline ကြိုတင်တွက်ချက်၍ vector database တွင် HNSW index ဖြင့် သိမ်းဆည်းထားနိုင်သဖြင့် query latency နည်းပါးပြီး million-scale corpus များတွင် scalable ဖြစ်သည်။ သို့ရာတွင် query tokens နှင့် document tokens အကြား cross-attention interaction မရှိသဖြင့် fine-grained token-level matching တွင် precision အားနည်းနိုင်သည်။ Cross-encoder သည် token-level interactions အားလုံးကို attention matrix တွင် တိုက်ရိုက်တွက်ချက်သဖြင့် precision သိသိသာသာ မြင့်မားသော်လည်း O(N) candidate-level inference cost ရှိပြီး pre-computation မပြုလုပ်နိုင်ပေ။

### Python Demonstration

```python
# Toy stand-in: a real cross-encoder would score (query, passage) jointly.
# Here we simulate that joint scoring with a simple word-overlap heuristic.

def bi_encoder_score(query_vec, doc_vec):
    # Cosine similarity between two precomputed vectors.
    dot = sum(a * b for a, b in zip(query_vec, doc_vec))
    norm = (sum(a * a for a in query_vec) ** 0.5) * (sum(b * b for b in doc_vec) ** 0.5)
    return dot / norm

def cross_encoder_score(query, passage):
    # Stand-in for a joint model; higher overlap means more relevant.
    q_words = set(query.lower().split())
    p_words = set(passage.lower().split())
    return len(q_words & p_words) / len(q_words | p_words)

query = "vector search index"
passages = ["hnsw graph for vector search", "cooking rice recipes"]
q_vec = [1.0, 0.9, 0.1]
d_vecs = [[0.9, 1.0, 0.2], [0.1, 0.0, 0.9]]

for p, v in zip(passages, d_vecs):
    print(f"{p}: bi={bi_encoder_score(q_vec, v):.3f}, cross={cross_encoder_score(query, p):.3f}")
# Expected output:
# hnsw graph for vector search: bi=0.992, cross=0.333
# cooking rice recipes: bi=0.156, cross=0.000
```

### Production Considerations

Two-stage retrieval pipeline များတွင် bi-encoder ဖြင့် large corpus မှ top-K candidates (ဥပမာ K=50 သို့မဟုတ် 100) ကို retrieve လုပ်ပြီးမှ cross-encoder ဖြင့် high-precision reranking ပြုလုပ်ကာ top-N (ဥပမာ N=5 သို့မဟုတ် 10) ကို LLM generation context သို့ ပို့ဆောင်သည့် pattern ကို အသုံးပြုသည်။ SBERT documentation (https://sbert.net/) တွင် cross-encoder pretrained models များကို အသေးစိတ် ဖော်ပြထားသည်။

---

## ၂။ Reranking Latency Cost Modeling နှင့် Top-k Budgeting

### Overview

Reranking အဆင့်သည် second-stage inference overhead ကို မလွဲမသွေ ဖြစ်ပေါ်စေသည်။ Top-k candidate size ကြီးမားလာသည်နှင့်အမျှ query p95/p99 latency linear အချိုးအစားအတိုင်း မြင့်တက်လာသည်။

### Engineering Rationale

Cross-encoder inference သည် model parameters နှင့် candidate sequence length အပေါ် မူတည်၍ compute-intensive ဖြစ်သည်။ Reranker ထံသို့ candidate အရေအတွက် မည်မျှ forward လုပ်မည်ကို SLA budget (ဥပမာ < 200 ms total latency) နှင့် target recall တိုးတက်မှုအပေါ် အခြေခံ၍ budget သတ်မှတ်ရသည်။

### Latency Estimation Formula

```python
# Assumption: reranking one candidate costs 10 ms (a made-up, clearly-labelled number).
# We only show the arithmetic; real systems must be measured, not assumed.

CAND_PER_SEC = 100          # 10 ms per candidate, from the assumption above
RECALL_TARGET = 50          # show this many final results

for n in (20, 50, 200, 1000):
    # Candidates reranked per query, capped at N.
    rerank_ms = (1000 * n) / CAND_PER_SEC
    print(f"N={n:4d} -> rerank time ~{rerank_ms:6.0f} ms per query")
# Expected output:
# N=  20 -> rerank time ~   200 ms per query
# N=  50 -> rerank time ~   500 ms per query
# N= 200 -> rerank time ~  2000 ms per query
# N=1000 -> rerank time ~ 10000 ms per query
```

### Production Considerations

Batch inference API များ သို့မဟုတ် lightweight rerankers (ဥပမာ BGE-Reranker-Large, Cohere Rerank) သုံးစွဲသည့်တိုင် candidate အရေအတွက်ကို 30–100 ကြား ကန့်သတ်ထားခြင်းသည် cost-to-recall trade-off အတွက် standard practice ဖြစ်သည်။

---

## ၃။ HyDE — Hypothetical Document Embeddings

### Overview

HyDE (Hypothetical Document Embeddings) သည် user ၏ short question query ကို အခြေခံ၍ zero-shot LLM prompting ဖြင့် hypothetical (စိတ်ကူးယဉ်) answer document တစ်ခုကို ကြိုတင် generate လုပ်ပြီး အဆိုပါ generated document ၏ embedding vector ဖြင့် corpus documents များကို retrieve လုပ်သည့် နည်းလမ်းဖြစ်သည်။

### Engineering Rationale

Question များနှင့် Answer documents များသည် vector embedding space တွင် lexical/syntactic structure မတူညီသဖြင့် semantic distance ကွာဟချက် (asymmetric retrieval gap) ဖြစ်ပေါ်နိုင်သည်။ HyDE သည် query space ကို document-like space သို့ projection လုပ်ပေးသဖြင့် factual documents များနှင့် cosine similarity ပိုမိုမြင့်မားစေသည်။

### Python Demonstration

```python
# Deterministic stand-in for the LLM step: a fixed template, no real model call.

def fake_hypothetical_doc(query):
    # Scripted stand-in; a real pipeline would prompt an LLM here.
    return "Answer: " + query.strip().rstrip("?") + " uses a vector index to search data."

def embed(text):
    # Deterministic toy embedding: counts of a few known letters.
    letters = "aeiou"
    return [text.lower().count(c) for c in letters]

query = "how does vector search work?"
hyp = fake_hypothetical_doc(query)
print("Hypothetical doc:", hyp)
print("Embedding:", embed(hyp))
# Expected output:
# Hypothetical doc: Answer: how does vector search work uses a vector index to search data.
# Embedding: [6, 8, 1, 6, 1]
```

### Production Considerations

HyDE သည် LLM generation latency တစ်ဆင့် ထပ်တိုးစေပြီး hypothetical answer တွင် hallucination ပါဝင်ပါက retrieval drift ဖြစ်ပေါ်နိုင်သောကြောင့် high-ambiguity domain queries များတွင်သာ selectively သုံးသင့်သည်။

---

## ၄။ Multi-Query Expansion နှင့် Reciprocal Rank Fusion (RRF)

### Overview

Multi-query expansion သည် single query တစ်ခုကို alternative phrasings/paraphrases များအဖြစ် prompt ဖြင့် generate ပြုလုပ်ပြီး query တစ်ခုချင်းစီအတွက် candidate rankings များကို retrieve ပြုလုပ်ကာ Reciprocal Rank Fusion (RRF) ဖြင့် ပေါင်းစပ်သည့် pattern ဖြစ်သည်။

### Engineering Rationale

User ၏ query wording သည် corpus document ထဲရှိ phrasing နှင့် match မဖြစ်နိုင်သည့် vocabulary mismatch ပြဿနာကို query variations များဖြင့် mitigate လုပ်နိုင်သည်။ RRF formula `score = Σ [1 / (k + rank)]` သည် score distribution calibration မလိုအပ်ဘဲ rank positions အပေါ်တွင်သာ အခြေခံသဖြင့် variance နည်းပါးသည်။

### Python Demonstration

```python
# RRF: score(d) = sum over lists of 1 / (k + rank(d)), with a fixed k.
# The arXiv survey of retrieval augmentation (arxiv.org/abs/2212.10496)
# describes multi-query retrieval with RRF-style fusion.

K = 60  # standard constant used in RRF descriptions

def rrf_fusion(ranked_lists):
    scores = {}
    for one_list in ranked_lists:
        for rank, doc in enumerate(one_list, start=1):
            scores[doc] = scores.get(doc, 0.0) + 1.0 / (K + rank)
    return sorted(scores, key=lambda d: -scores[d]), scores

# Three query variants, each returning its own ranking (rank 1 first).
lists = [
    ["doc_a", "doc_b", "doc_c"],
    ["doc_b", "doc_c", "doc_a"],
    ["doc_c", "doc_a", "doc_b"],
]
fused, scores = rrf_fusion(lists)
for d in fused:
    print(f"{d}: rrf={scores[d]:.4f}")
# Expected output:
# doc_a: rrf=0.0484
# doc_b: rrf=0.0484
# doc_c: rrf=0.0484
```

---

## ၅။ MMR (Maximal Marginal Relevance) ဖြင့် Diversity Optimization

### Overview

MMR သည် query relevance နှင့် already-selected documents များကြား redundancy (similarity) ကို ချိန်ညှိ၍ context pool အတွင်း diverse candidates များကို ရွေးချယ်ပေးသော greedy selection algorithm ဖြစ်သည်။

### Engineering Formulation

$$MMR = \operatorname{argmax}_{d_i \in R \setminus S} \left[ \lambda \cdot \operatorname{Sim}(d_i, q) - (1 - \lambda) \cdot \max_{d_j \in S} \operatorname{Sim}(d_i, d_j) \right]$$

- `λ = 1`: Pure relevance selection (near-duplicates အများအပြား ပါဝင်နိုင်သည်)
- `λ = 0`: Maximum diversity selection
- `0 < λ < 1`: Relevance နှင့် novelty အကြား balanced trade-off

### Python Demonstration

```python
# MMR picks items balancing relevance to the query and dissimilarity
# to already-picked items. Lambda (0..1) controls the trade-off.

LAMBDA = 0.7

def cos(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    return dot / (na * nb)

def mmr_select(query, docs, k):
    selected = []
    remaining = list(docs.keys())
    while len(selected) < k and remaining:
        best, best_score = None, None
        for d in remaining:
            rel = cos(query, docs[d])
            red = max((cos(docs[d], docs[s]) for s in selected), default=0.0)
            score = LAMBDA * rel - (1 - LAMBDA) * red
            if best_score is None or score > best_score:
                best, best_score = d, score
        selected.append(best)
        remaining.remove(best)
    return selected

query = [1.0, 0.0]
docs = {
    "near_dup_1": [0.99, 0.05],
    "near_dup_2": [0.98, 0.10],
    "different":  [0.20, 0.95],
}
print(mmr_select(query, docs, 3))
# Expected output:
# ['near_dup_1', 'near_dup_2', 'different']
```

## Summary Checklist

- Bi-encoder သည် first-stage recall အတွက် scalable ဖြစ်ပြီး Cross-encoder သည် second-stage precision reranking အတွက် သင့်လျော်သည်။
- Reranking candidate size (top-k) ကို SLA latency budget နှင့် ချိန်ညှိ၍ 30–100 ကြား ထားရှိပါ။
- HyDE သည် asymmetric query-document semantics ကို ဖြေရှင်းသော်လည်း inference latency နှင့် hallucination risk ရှိသည်။
- Multi-query expansion သည် vocabulary mismatch ကို ဖြေရှင်းရန် RRF fusion ဖြင့် ပေါင်းစပ်သည်။
- MMR သည် redundant duplicate chunks များကို penalize လုပ်၍ prompt context diversity ကို မြှင့်တင်ပေးသည်။
