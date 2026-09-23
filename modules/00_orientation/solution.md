## လေ့ကျင့်ခန်း ၁ — Pipeline အဆင့်များကို အစီအစဉ်ချမယ်

RAG pipeline ရဲ့ အဆင့် ၈ ခုကို မှန်ကန်တဲ့ အစီအစဉ်နဲ့ စီပြီး အဆင့်တစ်ခုချင်း ဘာကြောင့် အဲဒီနေရာမှာ ရှိရတယ်ဆိုတာ ရှင်းပြပါမယ်။ အောက်က code က အဆင့်တွေကို စီပြီး တစ်ခုချင်း အကြောင်းပြချက် ထုတ်ပြပါတယ်နော်။

```python
# Correct order of the 8 RAG pipeline stages, with a one-line reason each.
pipeline = [
    ("ingest",   "Collect and clean raw source documents first; nothing downstream exists without data."),
    ("chunk",    "Split documents into small passages so each retrievable unit carries one focused idea."),
    ("embed",    "Turn each chunk into a numeric vector that captures semantic meaning."),
    ("index",    "Store vectors in an index (e.g., pgvector) so search is fast, not a full scan."),
    ("retrieve", "At query time, fetch the most similar chunks using the index."),
    ("rerank",   "Reorder the retrieved candidates with a stronger (often cross-encoder) scorer."),
    ("generate", "Feed the top chunks to the LLM (here a scripted stand-in, no real model call) to answer."),
    ("evaluate", "Finally, measure the quality of the answer so the pipeline can be tuned."),
]

for i, (stage, why) in enumerate(pipeline, 1):
    print(f"{i}. {stage}: {why}")
print("Full order:", " -> ".join(s for s, _ in pipeline))
# Expected output:
# 1. ingest: Collect and clean raw source documents first; nothing downstream exists without data.
# 2. chunk: Split documents into small passages so each retrievable unit carries one focused idea.
# 3. embed: Turn each chunk into a numeric vector that captures semantic meaning.
# 4. index: Store vectors in an index (e.g., pgvector) so search is fast, not a full scan.
# 5. retrieve: At query time, fetch the most similar chunks using the index.
# 6. rerank: Reorder the retrieved candidates with a stronger (often cross-encoder) scorer.
# 7. generate: Feed the top chunks to the LLM (here a scripted stand-in, no real model call) to answer.
# 8. evaluate: Finally, measure the quality of the answer so the pipeline can be tuned.
# Full order: ingest -> chunk -> embed -> index -> retrieve -> rerank -> generate -> evaluate
```

**အဓိကအယူဆ** — Pipeline အဆင့်တွေက အစီအစဉ်မှန်မှ ရလဒ်ကို တိုင်းတာလို့ ရပါတယ်။

## လေ့ကျင့်ခန်း ၂ — Chunk ဆိုတာ ဘာလဲ ရေးဖော်မယ်

Chunk ဆိုတာ document ကြီးတစ်ခုကနေ ခွဲထုတ်လိုက်တဲ့ စာပိုဒ်ငယ် အပိုင်းသေးပါ။ ရှာတဲ့အခါ ဒီအပိုဒ်ငယ်တွေကို တစ်ခုချင်း ရှာပြီး LLM ဆီ ပို့တာပါနော်။ Chunk အရွယ်အစား အလွန်သေးတာနဲ့ အလွန်ကြီးတာရဲ့ အားသာချက် အားနည်းချက်ကို ဇယားနဲ့ ပြပါမယ်။

```python
# Define a chunk in our own words, then compare very small vs very large chunks.
definition = ("A chunk is a small, self-contained piece of a larger document "
              "(e.g., a paragraph or fixed-length passage) that is the unit "
              "we embed, index, and retrieve in a RAG pipeline.")
print(definition)

rows = [
    ("(a) very small chunks",
     "Precise matches; search finds the exact sentence; low memory per chunk",
     "Context is cut off; the retriever returns fragments too short for the LLM to use"),
    ("(b) very large chunks",
     "Rich context; the LLM gets the full surrounding story",
     "Diluted similarity; a vector averages many ideas, so ranking is noisy and costs are high"),
]
print()
print(f"{'chunk size':<28} | {'PROS':<52} | {'CONS'}")
for label, pros, cons in rows:
    print(f"{label:<28} | {pros:<52} | {cons}")
print()
print("Example: the phrase 'E-4471 means pump overheat' is easy to hit with a")
print("small chunk, but if the chunk is 5 pages long its vector also encodes")
print("unrelated maintenance text, so the similarity score gets watered down.")
# Expected output:
# A chunk is a small, self-contained piece of a larger document (e.g., a paragraph or fixed-length passage) that is the unit we embed, index, and retrieve in a RAG pipeline.
# 
# chunk size                   | PROS                                                 | CONS
# (a) very small chunks        | Precise matches; search finds the exact sentence; low memory per chunk | Context is cut off; the retriever returns fragments too short for the LLM to use
# (b) very large chunks        | Rich context; the LLM gets the full surrounding story | Diluted similarity; a vector averages many ideas, so ranking is noisy and costs are high
# 
# Example: the phrase 'E-4471 means pump overheat' is easy to hit with a
# small chunk, but if the chunk is 5 pages long its vector also encodes
# unrelated maintenance text, so the similarity score gets watered down.
```

**အဓိကအယူဆ** — Chunk အရွယ်အစားက search တိကျမှုနဲ့ context ပြည့်မှု နှစ်ခုကြားမှာ ညှိရတဲ့ ကိစ္စပါ။

## လေ့ကျင့်ခန်း ၃ — Cosine similarity ကို Python နဲ့ တွက်မယ်

Cosine similarity က vector နှစ်ခုရဲ့ ထောင့်ကို တိုင်းတာတာပါ။ Formula က `(a · b) / (||a|| * ||b||)` ပါ။ `math` module နဲ့ တွက်ပြီး a နဲ့ b၊ a နဲ့ c ရဲ့ similarity ထုတ်ပါမယ်။

```python
# Cosine similarity with only the standard library.
import math

def cosine_similarity(a, b):
    """cos(a, b) = (a . b) / (||a|| * ||b||)"""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b)

a = [1.0, 0.0]
b = [0.0, 1.0]
c = [1.0, 1.0]

sim_ab = cosine_similarity(a, b)
sim_ac = cosine_similarity(a, c)
print(f"cosine(a, b) = {sim_ab:.4f}")   # perpendicular -> 0.0
print(f"cosine(a, c) = {sim_ac:.4f}")   # 45 degrees -> ~0.7071
# Expected output:
# cosine(a, b) = 0.0000
# cosine(a, c) = 0.7071
```

**အဓိကအယူဆ** — pgvector ရဲ့ `<=>` operator လိုမျိုး တိုင်းတာမှုတွေဟာ ဒီ formula အတိုင်း ထောင့်အရ နီးနီးတူမှု တွက်ပေးတာပါ။

## လေ့ကျင့်ခန်း ၄ — Vector search နဲ့ keyword search ရွေးမယ်

Query သုံးခုအတွက် ဘယ် search အမျိုးအစား သင့်တော်လဲ ရွေးပြီး latency နဲ့ ရလဒ် အရည်အသွေး နှစ်ခုစလုံးနဲ့ အကြောင်းပြပါမယ်နော်။

```python
# BURMESE-DATA-OK: Burmese sample text used as test data.
# Choose the best search type per query, with latency + quality reasoning.
decisions = [
    ("error code E-4471",
     "keyword search",
     "Exact codes like E-4471 must match character-for-character; a vector may"
     " 'semantically' drift to other error codes. Keyword search on an inverted"
     " index is cheap and low-latency, and the hits are precise."),
    ("ဆီးချိုရောဂါအတွက် အစားအသောက် အကြံပြုချက်",
     "vector search",
     "Users phrase health questions in many ways ('sugar disease', 'high blood"
     " sugar'); embedding search catches those paraphrases that keywords miss."
     " Vector search costs a bit more compute, but answer quality is much higher."),
    ("မြန်မာနိုင်ငံ ခရီးသွား အကြံပြုချက် ၂၀၂၄",
     "hybrid search",
     "The topic ('travel tips') is semantic, but '2024' and 'Myanmar' are exact"
     " filters; hybrid (vector + keyword, e.g., fused with RRF) gets fresh and"
     " precise results at a moderate latency."),
]

for query, choice, reason in decisions:
    print(f"query:   {query}")
    print(f"choice:  {choice}")
    print(f"reason:  {reason}")
    print()
# Expected output:
# query:   error code E-4471
# choice:  keyword search
# reason:  Exact codes like E-4471 must match character-for-character; a vector may 'semantically' drift to other error codes. Keyword search on an inverted index is cheap and low-latency, and the hits are precise.
# 
# query:   ဆီးချိုရောဂါအတွက် အစားအသောက် အကြံပြုချက်
# choice:  vector search
# reason:  Users phrase health questions in many ways ('sugar disease', 'high blood sugar'); embedding search catches those paraphrases that keywords miss. Vector search costs a bit more compute, but answer quality is much higher.
# 
# query:   မြန်မာနိုင်ငံ ခရီးသွား အကြံပြုချက် ၂၀၂၄
# choice:  hybrid search
# reason:  The topic ('travel tips') is semantic, but '2024' and 'Myanmar' are exact filters; hybrid (vector + keyword, e.g., fused with RRF) gets fresh and precise results at a moderate latency.
```

**အဓိကအယူဆ** — စာလုံးအတိအက ကိုက်ရမရနဲ့ သဘောတရားနီးစာ ရှာရမလဲဆိုတာကို query အရ ဆုံးဖြတ်ရပါတယ်။

## လေ့ကျင့်ခန်း ၅ — Chunking ရဲ့ memory အရွယ်အစား တွက်မယ်

fp32 ဆိုတာ dimension တစ်ခုကို 4 byte ယူတာပါ။ ဒါဆို chunk တစ်ခု `768 * 4` bytes နဲ့ 1,000,000 chunks ရဲ့ စုစုပေါင်း GB ကို အဆင့်ဆင့် တွက်ပြပါမယ်။

```python
# Step-by-step embedding memory math, standard library only.
num_chunks = 1_000_000
dimensions = 768
bytes_per_float = 4          # fp32 = 32 bits = 4 bytes
bytes_per_chunk = dimensions * bytes_per_float
total_bytes = num_chunks * bytes_per_chunk
gb = 1024 * 1024 * 1024
total_gb = total_bytes / gb

print(f"bytes per chunk      = {dimensions} dims * {bytes_per_float} B = {bytes_per_chunk} B")
print(f"total bytes          = {num_chunks} * {bytes_per_chunk} = {total_bytes} B")
print(f"total GB             = {total_bytes} / {gb} = {total_gb:.2f} GB")
# Expected output:
# bytes per chunk      = 768 dims * 4 B = 3072 B
# total bytes          = 1000000 * 3072 = 3072000000 B
# total GB             = 3072000000 / 1073741824 = 2.86 GB
```

**အဓိကအယူဆ** — Embedding storage က dimension အရေအတွက်နဲ့ chunk အရေအတွက် နှစ်ခုလုံးပေါ် တန်းတင်တက်သွားတာပါ။

## လေ့ကျင့်ခန်း ၆ — Reciprocal Rank Fusion ကို ကိုယ်တိုင်ဆောက်မယ်

Vector ranking နဲ့ keyword ranking နှစ်ခုကို RRF formula `1/(k+rank)` နဲ့ ပေါင်းပြီး နောက်ဆုံး ranking ထုတ်ပါမယ်။ Database မချိတ်ပါဘူး — pgvector hybrid search ရဲ့ အတုအစား သဘောသဘာဝပါနော်။

```python
# Reciprocal Rank Fusion: merge two rankings, k=60, standard library only.
# This is a deterministic, in-memory stand-in for a pgvector hybrid search setup.
vector_ranking = ["doc_c", "doc_a", "doc_b"]
keyword_ranking = ["doc_a", "doc_b", "doc_d"]
k = 60

scores = {}
for ranking in (vector_ranking, keyword_ranking):
    for rank, doc in enumerate(ranking, start=1):   # rank starts at 1
        scores[doc] = scores.get(doc, 0.0) + 1.0 / (k + rank)

final_ranking = sorted(scores, key=lambda d: scores[d], reverse=True)

for doc in final_ranking:
    print(f"{doc}: {scores[doc]:.4f}")
print("Final ranking:", " > ".join(final_ranking))
# Expected output:
# doc_a: 0.0325
# doc_b: 0.0320
# doc_c: 0.0164
# doc_d: 0.0159
# Final ranking: doc_a > doc_b > doc_c > doc_d
```

**အဓိကအယူဆ** — Ranking နှစ်ခုကို score အရ ပေါင်းလိုက်တာက hybrid search ရဲ့ ရိုးရိုးရှင်းရှင်း နည်းလမ်းကောင်းပါ။
