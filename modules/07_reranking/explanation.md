# M7 — Reranking နှင့် Query ပြောင်းလဲခြင်း

ဒီ module မှာ retrieval ရလဒ်ကို ပိုကောင်းအောင် လုပ်နိုင်တဲ့ နည်းလမ်းတွေကို လေ့လာကြမယ်။
Official documentation တွေကတော့ https://sbert.net/ , https://arxiv.org/abs/2212.10496 , https://docs.ragas.io/ တို့ ဖြစ်ပါတယ်။
ဒီသင်ခန်းစာတွေက original study material ပါ။ အားလုံးက standard-library Python နဲ့ အော့ဖ်လိုင်း အလုပ်လုပ်ပါတယ်။

---

## ၁။ Bi-encoder နှင့် Cross-encoder

### ဘာကို ဆိုလိုတာလဲ

Bi-encoder က query နဲ့ document ကို သီးသန့် vector အဖြစ် ပြောင်းပေးတဲ့ model ပါ။
Cross-encoder က query နဲ့ document နှစ်ခုကို တစ်ပေါင်းတည်း ထည့်ပြီး relevance score တစ်ခုတည်း ထုတ်ပေးတဲ့ model ပါ။

### ဘာကြောင့် လဲ

Bi-encoder တစ်ခုတည်းနဲ့ပဲ ရှာရင် အချက်အလက်တွေ လွဲသွားတတ်ပါတယ်။
Query နဲ့ document ကို သီးသန့် embed လုပ်လို့ စကားလုံးအဓိပ္ပာယ် တိုက်ဆိုင်မှု လုံးဝ မပေါ်နိုင်လို့ပါ။
ဒါကြောင့် ပိုတိကျတဲ့ အမှတ်ပေးတဲ့ cross-encoder ကို နောက်ဆင့်မှာ သုံးကြတာပါ။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Bi-encoder က query ကို vector တစ်ခု ထုတ်ပါတယ်။
၂။ Document အားလုံးရဲ့ vector ကို အရင်ကတည်းက သိမ်းထားပါတယ်။
၃။ Cosine similarity နဲ့ အနီးစပ်ဆုံး ရှာပါတယ်။
၄။ Cross-encoder က query နဲ့ document စာကို တွဲပြီး score တစ်ခုတည်း ထုတ်ပါတယ်။
၅။ SBert docs မှာ ဒီနှစ်မျိုးကို cross-encoder/re-ranker နဲ့ bi-encoder လို့ ခေါ်ပါတယ်။

### ဥပမာ

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

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Bi-encoder က vector database တွေနဲ့ တွဲဖက်လို့ ရပါတယ်။
ဒါပေမယ့် နောက်ဆုံး ranking က အနီးစပ်ဆုံးပဲ ဖြစ်နေတတ်ပါတယ်။
Cross-encoder က တိတိကျပေမယ့် document တိုင်းကို တစ်ခုချင်း တွက်ရလို့ နှေးတတ်ပါတယ်။
ဒါကြောင့် အမြန်ရှာပြီးမှ တိကျတဲ့ ပြန်စီမယ့် နည်းလမ်း လိုအပ်တာပါ။

---

## ၂။ Reranking Latency ကုန်ကျစရိတ် နှင့် Top-k ရွေးချယ်ခြင်း

### ဘာကို ဆိုလိုတာလဲ

Reranking ဆိုတာ အမြန်ရှာထားတဲ့ ရလဒ်ပေါ်မှာ ပိုတိကျတဲ့ model နဲ့ ပြန် rank လုပ်တာပါ။
Top-k ဆိုတာ rerank လုပ်မယ့် အရင်ဆုံး candidate အရေအတွက်ကို ဆိုလိုတာပါ။

### ဘာကြောင့် လဲ

Reranking မလုပ်ဘဲ ရှာတဲ့အခါ အရေးကြီးတဲ့ စာသားတွေ အောက်ဆင့်ထဲ ရောက်နေတတ်ပါတယ်။
ကျနော်တို့က top-N လောက်ပဲ LLM ကို ပြမယ်ဆိုရင် အဲဒါတွေ ပျောက်သွားနိုင်ပါတယ်။
ဒါပေမယ့် k ကြီးလေ rerank များလေ နှောင့်နှေးလေ ဖြစ်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Vector search နဲ့ candidate N ခု အမြန်ရှာပါတယ်။
၂။ အဲဒီထဲကမှ top-k ခုကိုပဲ reranker ထဲ ထည့်ပါတယ်။
၃။ Reranker က တစ်စုံချင်း score ထုတ်ပါတယ်။
၄။ Score အမြင့်ဆုံးအတိုင်း ပြန်စီပါတယ်။
၅။ ကျနော်တို့က k နဲ့ N ကို ကိန်းဂဏန်းနဲ့ တွက်ပြီး ဆုံးဖြတ်ရပါတယ်။

### ဥပမာ

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

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

k က အရမ်းကြီးရင် query တစ်ခုချင်းစီမှာ စောင့်ရအချိန် တက်သွားပါတယ်။
k က အရမ်းသေးရင် ကောင်းတဲ့ candidate ထဲမှာ မပါတော့ပဲ အရည်အသွေးကျပါတယ်။
တွက်တာကတော့ ပထမဆုံး ခန့်မှန်းချက်ပါ။ ကိုယ်တိုင် system မှာ measure လုပ်ပြီးမှ ဆုံးဖြတ်ရပါတယ်။

---

## ၃။ HyDE — Hypothetical Document Embedding

### ဘာကို ဆိုလိုတာလဲ

HyDE ဆိုတာ query အတွက် "ဖြစ်နိုင်တဲ့ အဖြေစာ" တစ်ခုကို အရင် ဖန်တီးပြီး၊ အဲဒါရဲ့ embedding နဲ့ ရှာတဲ့ နည်းပါ။

### ဘာကြောင့် လဲ

User ရဲ့ question က တိုတောင်းပြီး အဖြေစာနဲ့ အသုံးအနှုန်း မတူတတ်ပါတယ်။
Question နဲ့ answer document က vector space မှာ ဝေးကြနိုင်တာပါ။
အဖြေစာ တစ်ခုကို အရင်စဉ်းစားထုတ်ရင် question-document ကွာဟချက်က သေးသွားနိုင်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ User query ကိုယူပါတယ်။
၂။ LLM တစ်ခုနဲ့ hypothetical answer တစ်ခု ရေးခိုင်းပါတယ်။
၃။ အဲဒီ hypothetical document ကို embed လုပ်ပါတယ်။
၄။ အဲဒီ vector နဲ့ document collection ထဲမှာ ရှာပါတယ်။
၅။ ရလဒ်တွေကို ပုံမှန်အတိုင်း rerank လုပ်ပါတယ်။

### ဥပမာ

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

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

HyDE က question ပုံစံ query တွေမှာ အထူးသဖြင့် အကူအညီဖြစ်နိုင်ပါတယ်။
ဒါပေမယ့် ဖန်တီးတဲ့ အဖြေစာက မှားနေရင် ရလဒ်လည်း မှားနိုင်ပါတယ်။
ဒါကြောင့် HyDE ရလဒ်ကို နောက်ဆုံး rerank နဲ့ စစ်ဆေးသင့်ပါတယ်။

---

## ၄။ Multi-query Expansion နှင့် Fusion (RRF)

### ဘာကို ဆိုလိုတာလဲ

Multi-query ဆိုတာ user query တစ်ခုကို မတူတဲ့ phrasing တွေအဖြစ် ပြောင်းပြီး အားလုံးနဲ့ ရှာတာပါ။
Fusion ဆိုတာ ရလဒ်စာရင်း တွေကို တစ်ခုတည်း ပေါင်းစပ်တာပါ။

### ဘာကြောင့် လဲ

Query တစ်ခုတည်းက wording တစ်မျိုးတည်းပဲ ဖမ်းနိုင်ပါတယ်။
Document တစ်ခုက အခေါ်အဝေါ် အမျိုးမျိုးနဲ့ ရေးထားနိုင်ပါတယ်။
Query အမျိုးမျိုးနဲ့ ရှာရင် ဖမ်းတွေ့နိုင်ခြေ တက်ပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Query တစ်ခုကို variant တွေအဖြစ် ပြောင်းပါတယ်။
၂။ Variant တစ်ခုချင်းစီနဲ့ ရှာပါတယ်။
၃။ ရလဒ်စာရင်းတစ်ခုစီမှာ document တွေရဲ့ rank ကို ယူပါတယ်။
၄။ Reciprocal Rank Fusion (RRF) နဲ့ score တွေ ပေါင်းပါတယ်။
၅။ RRF score မြင့်တဲ့အတိုင်း ပြန်စီပါတယ်။

### ဥပမာ

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

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Multi-query fusion က recall တက်အောင် ကူညီနိုင်ပါတယ်။
Query decomposition က ရှုပ်တဲ့ မေးခွန်းတွေကို သေးသေးလေး အပိုင်းလေးတွေအဖြစ် ခွဲပါတယ်။
ဒါက ရှုပ်ထွေးတဲ့ မေးခွန်းတွေမှာ ပိုတိကျတဲ့ retrieval ပေးနိုင်ပါတယ်။
ဒါပေမယ့် query အရေအတွက် တက်လေ search cost လည်း တက်လေပါ။

---

## ၅။ MMR — Maximal Marginal Relevance ဖြင့် Diversity

### ဘာကို ဆိုလိုတာလဲ

MMR ဆိုတာ သက်ဆိုင်တဲ့ document တွေကို သူတို့ချင်း ထပ်နေမှုနည်းအောင် ရွေးတဲ့ နည်းပါ။
Diversity ဆိုတာ ရလဒ်တွေက အခြေအနေအမျိုးမျိုးကနေ လာတာကို ဆိုလိုတာပါ။

### ဘာကြောင့် လဲ

Document တွေ အချင်းချင်း အလွန်တူနေရင် ရလဒ်က တစ်မျိုးတည်း ထပ်နေပါတယ်။
User က အချက်အလက် နေရာအမျိုးမျိုးကနေ သိချင်တာပါ။
MMR က relevance နဲ့ diversity နှစ်ခုလုံးကို ချိန်ပြီး ရွေးပေးပါတယ်။

### ဘယ်လို အလုပ်လုပ်လဲ

၁။ Candidate တွေနဲ့ query ရဲ့ relevance ကို တွက်ပါတယ်။
၂။ ရွေးထားပြီးသား document တွေနဲ့ candidate တိုင်းရဲ့ similarity ကို တွက်ပါတယ်။
၃။ MMR = relevance − lambda × (max similarity to already-selected) ဆိုပြီး တွက်ပါတယ်။
၄။ MMR အမြင့်ဆုံး candidate ကို ရွေးပါတယ်။
၅။ လိုအပ်တဲ့ အရေအတွက်ရောက်တဲ့အထိ ပြန်လည် repetition လုပ်ပါတယ်။

### ဥပမာ

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

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

RAG pipeline တစ်ခုမှာ သက်ဆိုင်တဲ့ context တူညီတဲ့ စာသားတွေ ပိုမိုများပါက အဖြေက တစ်ဖက်စောင်း ဖြစ်သွားနိုင်ပါတယ်။
MMR က ထပ်နေတဲ့ chunk တွေကို ဖယ်ပြီး အချက်အလက် ကျယ်ဝန်းအောင် လုပ်ပေးပါတယ်။
Retrieval quality ကို ragas (https://docs.ragas.io/) လို tool တွေနဲ့တော့ တိုင်းတာစစ်ဆေးရပါတယ်။

---

## အနှစ်ချုပ်

- Bi-encoder က အမြန် vector ရှာပါတယ်၊ cross-encoder က query-document တွဲပြီး တိတိကျ score ထုတ်ပါတယ်။
- Reranking က k ကြီးလေ နှောင့်နှေးလေပါ၊ ကျနော်ကြာလေ အရည်အသွေးတက်နိုင်လေပါ၊ trade-off ကို တွက်ပြီး ရွေးရပါတယ်။
- HyDE က အဖြေစာ စဉ်းစားပြီး အဲဒါနဲ့ရှာတာပါ၊ question-answer wording ကွာဟချက်ကို လျှော့ပေးပါတယ်။
- Multi-query နဲ့ RRF fusion က query variant တွေ အားလုံးကို ပေါင်းစည်းပေးပါတယ်။
