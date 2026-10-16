## လေ့ကျင့်ခန်း ၁ — Pipeline အဆင့်များကို အစီအစဉ်ချမယ်

RAG pipeline ၏ stage ၈ ခုကို sequence အတိုင်း စီစဉ်ထားပြီး stage တစ်ခုချင်းစီ၏ architectural dependency ကို ဖော်ပြထားသည်။ အောက်ပါ code သည် sequence နှင့် ရွေးချယ်မှု အကြောင်းပြချက်ကို ပြသသည်။

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

**အဓိကအယူအဆ** — Pipeline stage များသည် dependency အလိုက် အစဉ်လိုက် ချိတ်ဆက်နေပြီး evaluation မပါရှိပါက tuning ပြုလုပ်ရန် benchmark မရှိနိုင်ပါ။

## လေ့ကျင့်ခန်း ၂ — Chunk ဆိုတာ ဘာလဲ ရေးဖော်မယ်

Chunk သည် document တစ်ခုမှ embed လုပ်၍ retrieve ပြန်နိုင်သော atomic retrieval unit ဖြစ်သည်။ Chunk size အလွန်သေးငယ်ခြင်းနှင့် အလွန်ကြီးမားခြင်းတို့၏ trade-off နှိုင်းယှဉ်ချက်ကို အောက်ပါ script တွင် ဖော်ပြထားသည်။

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

**အဓိကအယူအဆ** — Chunk size ရွေးချယ်မှုသည် retrieval precision နှင့် context completeness ကြား အဓိက trade-off ဖြစ်သည်။

## လေ့ကျင့်ခန်း ၃ — Cosine similarity ကို Python နဲ့ တွက်မယ်

Cosine similarity သည် vector နှစ်ခုကြား angle ၏ cosine တန်ဖိုးကို တိုင်းတာခြင်း ဖြစ်ပြီး formula မှာ `(a · b) / (||a|| * ||b||)` ဖြစ်သည်။ Standard library `math` ဖြင့် dot product နှင့် vector norm တွက်ချက်ထားသည်။

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

**အဓိကအယူအဆ** — pgvector ၏ `<=>` distance operator ကဲ့သို့သော distance calculation များသည် ဤ mathematical definition အတိုင်း vector angle အပေါ် အခြေခံ၍ distance တိုင်းတာခြင်း ဖြစ်သည်။

## လေ့ကျင့်ခန်း ၄ — Vector search နဲ့ keyword search ရွေးမယ်

Query သုံးခု၏ လက္ခဏာအလိုက် သင့်လျော်သော search modality (keyword, vector, hybrid) ကို latency နှင့် result quality trade-off အပေါ် အခြေခံ၍ ဆုံးဖြတ်ထားသည်။

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

**အဓိကအယူအဆ** — Exact token match လိုအပ်သော query များအတွက် inverted index သုံးပြီး semantic paraphrase လိုအပ်ပါက dense vector search သုံးကာ နှစ်မျိုးလုံး လိုအပ်ပါက hybrid search ကို ရွေးချယ်ရသည်။

## လေ့ကျင့်ခန်း ၅ — Chunking ရဲ့ memory အရွယ်အစား တွက်မယ်

fp32 encoding တွင် dimension တစ်ခုလျှင် 4 bytes သုံးစွဲသဖြင့် dimension 768 ပါသော chunk တစ်ခုသည် `768 * 4 = 3072 bytes` ယူသည်။ 1,000,000 chunks အတွက် raw vector storage ကို အောက်ပါ script ဖြင့် အဆင့်ဆင့် တွက်ချက်ပြထားသည်။

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

**အဓိကအယူအဆ** — Raw vector storage သည် chunk count နှင့် dimension နှစ်ခုလုံးနှင့် linear အချိုးကျ တိုးပွားသည်။

## လေ့ကျင့်ခန်း ၆ — Reciprocal Rank Fusion ကို ကိုယ်တိုင်ဆောက်မယ်

Vector ranking နှင့် keyword ranking နှစ်ခုကို RRF formula `score = Σ 1 / (k + rank)` ဖြင့် ပေါင်းစပ်၍ single fused ranking ထုတ်ယူသည်။ Standard library pure Python ဖြင့် implement လုပ်ထားသည်။

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

**အဓိကအယူအဆ** — RRF သည် raw score calibration မလိုအပ်ဘဲ rank positions သာ အသုံးပြုသဖြင့် scale မတူသော retrieval lane များကို ပေါင်းစပ်ရာတွင် robust ဖြစ်သည်။
