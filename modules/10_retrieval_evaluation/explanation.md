# M10 — Retrieval အကဲဖြတ်ခြင်း: recall@k၊ MRR၊ nDCG၊ Golden Set နှင့် Regression Gate

ဒီ module က retrieval quality ကို quantitative metric များဖြင့် တိုင်းတာသည့် နည်းလမ်းများကို ကိုင်တွယ်သည်။
မှတ်ချက် — ဒီ material ဟာ တရားဝင် open documentation တွေအပေါ် အခြေခံပြီး ရေးထားတဲ့ မူရင်း သင်ယူမှု material ပါ။
Official sources: https://docs.ragas.io/ , https://arxiv.org/abs/2104.08663 , https://huggingface.co/spaces/mteb/leaderboard

---

## Subtopic 1 — Golden Set ဖွဲ့ခြင်း

### ဘာကို ဆိုလိုတာလဲ
Golden set ဆိုသည်မှာ query တစ်ခုနှင့် ၎င်းအတွက် relevant ဖြစ်သော chunk id များ၏ mapping စာရင်းဖြစ်သည်။ Query တစ်ခုစီအတွက် မည်သည့် chunk တွင် အဖြေပါဝင်သည်ကို human annotator က label ပေးထားပြီး၊ ၎င်းကို ground truth ဟုခေါ်သည်။

### ဘာကြောင့် လဲ
Retrieval system တစ်ခုကို ပြင်ဆင်ပြီးတိုင်း အရည်အသွေး မြင့်တက်/ကျဆင်း ဆိုသည်ကို deterministic အဖြေဖြင့် အတည်ပြုရန် လိုအပ်သည်။ Ground truth မရှိပါက အကဲဖြတ်မှုသည် anecdotal ဖြစ်နေပြီး reproducible မဖြစ်ပါ။ Golden set ရှိပါက ပြောင်းလဲမှုတိုင်းကို တူညီသော dataset ပေါ်တွင် ပြန်လည်တိုင်းတာနိုင်ပြီး၊ subjective ခန့်မှန်းမှုကို quantitative တိုင်းတာမှုဖြင့် အစားထိုးနိုင်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ Representative query များကို စုဆောင်းသည်။
၂။ Query တစ်ခုချင်းစီအတွက် corpus ထဲမှ relevant chunk များကို label ပေးသည်။
၃။ Annotator နှစ်ဦး သို့မဟုတ် သုံးဦး၏ inter-annotator agreement ကို စစ်ဆေးသည်။
၄။ သဘောကွဲလွဲသော query များကို ဖယ်ထုတ်ပြီး ကျန် label များကို finalize လုပ်သည်။
၅။ JSON ကဲ့သို့ structured format ဖြင့် သိမ်းဆည်းပြီး CI တွင် အသုံးပြုသည်။

### ဥပမာ

```python
# A tiny golden set: query -> list of relevant chunk ids.
# In production this would be stored as JSON and reviewed by multiple annotators.
golden_set = [
    {"query": "vector search kya ah", "relevant": ["c1", "c3"]},
    {"query": "cosine similarity hmel", "relevant": ["c2"]},
    {"query": "HNSW graph", "relevant": ["c4"]},
]

# Sanity checks every golden set should pass before use.
for item in golden_set:
    assert isinstance(item["relevant"], list) and len(item["relevant"]) > 0

print("golden set size:", len(golden_set))
print("total relevant chunks:", sum(len(i["relevant"]) for i in golden_set))
# Expected output:
# golden set size: 3
# total relevant chunks: 4
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
RAG system ၏ failure အများစုသည် generation အဆင့်တွင် မဟုတ်ဘဲ retrieval အဆင့်တွင် ဖြစ်ပေါ်သည်။ Relevant chunk ကို retrieve မလုပ်နိုင်ပါက LLM မည်မျှစွမ်းရည်မြင့်မားစေကာမူ အဖြေမှန် ထုတ်ပေးနိုင်မည်မဟုတ်ပါ။ ထို့ကြောင့် retrieval ကို သီးသန့်အကဲဖြတ်ရန် golden set သည် ပထမဆုံး လိုအပ်ချက်ဖြစ်သည်။ MTEB leaderboard တွင်လည်း ဤပုံစံအတိုင်း standard benchmark များ သတ်မှတ်၍ တိုင်းတာကြောင်း တွေ့ရသည် (https://huggingface.co/spaces/mteb/leaderboard)။

---

## Subtopic 2 — recall@k နဲ့ precision@k

### ဘာကို ဆိုလိုတာလဲ
recall@k ဆိုသည်မှာ relevant chunk အားလုံးအနက် top-k results အတွင်း ပြန်လည်ရောက်ရှိလာသည့် အချိုးအစားဖြစ်သည်။ precision@k ဆိုသည်မှာ top-k results အနက် relevant ဖြစ်သည့် အချိုးအစားဖြစ်သည်။

### ဘာကြောင့် လဲ
RAG တွင် LLM context အတွင်း chunk အလွန်အကျွံ ထည့်သွင်းခြင်းသည် context pollution ဖြစ်စေသည်။ တစ်ဖက်တွင်လည်း relevant chunk တစ်ခု လွတ်သွားပါက အဖြေ လုံးဝမှားယွင်းနိုင်သည်။ ထို့ကြောင့် metric နှစ်ခုကို ခွဲခြားစောင့်ကြည့်ရန် လိုအပ်သည်။ Recall နိမ့်ပါက retrieval က relevant chunk များကို လွတ်နေခြင်းဖြစ်ပြီး၊ precision နိမ့်ပါက irrelevant chunk များက result set ကို ညစ်ညမ်းစေခြင်းဖြစ်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ
recall@k = (relevant အနက် top-k အတွင်း ရောက်ရှိသည့် အရေအတွက်) ÷ (relevant စုစုပေါင်း)။
precision@k = (top-k အတွင်းရှိ relevant အရေအတွက်) ÷ k။
၁။ Retrieved list နှင့် relevant set ကို ရယူသည်။
၂။ Retrieved list ကို top-k သို့ truncate လုပ်သည်။
၃။ နှစ်ခု၏ overlap ကို တွက်ချက်သည်။
၄။ အချိုးနှစ်ခုကို သီးခြား တွက်ချက်သည်။

### ဥပမာ

```python
def recall_at_k(retrieved, relevant, k):
    """Fraction of relevant chunks found in the top-k results."""
    top_k = retrieved[:k]
    hits = len(set(top_k) & set(relevant))
    return hits / len(relevant)

def precision_at_k(retrieved, relevant, k):
    """Fraction of top-k results that are relevant."""
    top_k = retrieved[:k]
    hits = len(set(top_k) & set(relevant))
    return hits / k

retrieved = ["c1", "c9", "c3", "c7", "c2"]
relevant  = ["c1", "c3", "c5"]

r3 = recall_at_k(retrieved, relevant, 3)   # hits in top-3: c1, c3 -> 2 of 3
p3 = precision_at_k(retrieved, relevant, 3)
r5 = recall_at_k(retrieved, relevant, 5)   # hits in top-5: c1, c3, c2? no c5 -> 2 of 3

print("recall@3 =", r3)
print("precision@3 =", p3)
print("recall@5 =", r5)
# Expected output:
# recall@3 = 0.6666666666666666
# precision@3 = 0.6666666666666666
# recall@5 = 0.6666666666666666
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
RAG အတွက် recall@k သည် precision@k ထက် ပိုမိုအရေးပါလေ့ရှိသည်။ LLM သည် ပေးထားသော context အတွင်းမှ irrelevant claim များကို စိစစ်ဖယ်ရှားနိုင်သော်လည်း retrieve မလုပ်ရသော အချက်အလက်ကို ထုတ်ပေးနိုင်စွမ်း မရှိသောကြောင့်ဖြစ်သည်။ RAGAS docs တွင်လည်း retrieval metric များကို သီးသန့် first-class အဖြစ် သတ်မှတ်ထားသည် (https://docs.ragas.io/)။

---

## Subtopic 3 — MRR နဲ့ nDCG

### ဘာကို ဆိုလိုတာလဲ
MRR (Mean Reciprocal Rank) သည် ပထမဆုံး relevant result ၏ rank ကို reciprocal (1 ÷ rank) အဖြစ် ပြောင်း၍ query အားလုံးအတွက် ပျမ်းမျှယူသော metric ဖြစ်သည် — rank 1 တွင် ရှိပါက 1.0၊ rank 3 တွင် ရှိပါက 1/3 ဖြစ်သည်။ nDCG (normalized Discounted Cumulative Gain) သည် အပေါ်ပိုင်း rank ရှိ relevant result များကို အလေးချိန်ပိုပေးပြီး rank ကျဆင်းလာသည်နှင့်အမျှ gain ကို logarithmic discount ဖြင့် လျှော့ချပေးသော metric ဖြစ်သည်။

### ဘာကြောင့် လဲ
recall@k သည် relevant chunk ရောက်ရှိမှု ရှိ/မရှိကိုသာ တိုင်းတာပြီး rank position ကို ထည့်သွင်းစဉ်းစားခြင်း မရှိပါ။ Relevant chunk သည် rank အောက်ဆုံးတွင် ရောက်နေပါက LLM context အတွင်း ၎င်း၏ အသုံးဝင်မှု သိသိသာသာ ကျဆင်းသွားသည်။ Rank 1 hit နှင့် rank အနိမ့် hit တို့၏ အကျိုးသက်ရောက်မှု ကွာခြားမှုကို MRR နှင့် nDCG က rank-aware အဖြစ် ဖမ်းယူနိုင်သည်။

### ဘယ်လို အလုပ်လုပ်လဲ
MRR တွက်ချက်မှု — ၁။ Query တစ်ခုချင်းစီအတွက် ပထမဆုံး relevant result ၏ rank ကို ရှာသည်။
၂။ Reciprocal rank (1 ÷ rank) ကို တွက်ချက်သည်။
၃။ Query အားလုံး၏ reciprocal rank များကို ပျမ်းမျှယူသည်။
nDCG တွက်ချက်မှု — ၁။ Relevant hit တစ်ခုချင်းစီ၏ gain ကို log2(rank+1) ဖြင့် discount လုပ်သည်။
၂။ Discounted gain များ ပေါင်းလဒ်မှာ DCG ဖြစ်သည်။
၃။ Ideal ranking ၏ DCG (IDCG) ဖြင့် စား၍ normalize လုပ်သည်။

### ဥပမာ

```python
import math

def reciprocal_rank(retrieved, relevant):
    """1/rank of the first relevant result, 0 if none found."""
    for i, chunk_id in enumerate(retrieved, start=1):
        if chunk_id in relevant:
            return 1.0 / i
    return 0.0

def ndcg(retrieved, relevant, k):
    """Binary-relevance nDCG@k with standard log2 discount."""
    dcg = 0.0
    for i, chunk_id in enumerate(retrieved[:k], start=1):
        if chunk_id in relevant:
            dcg += 1.0 / math.log2(i + 1)
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, min(k, len(relevant)) + 1))
    return dcg / idcg

# Two queries against a tiny golden set.
cases = [
    (["c1", "c2", "c3"], ["c1"]),        # first hit at rank 1
    (["c7", "c8", "c2"], ["c2"]),       # first hit at rank 3
]
mrr = sum(reciprocal_rank(r, rel) for r, rel in cases) / len(cases)
n1 = ndcg(cases[0][0], cases[0][1], 3)
n2 = ndcg(cases[1][0], cases[1][1], 3)

print("MRR =", mrr)
print("nDCG query1 =", n1)
print("nDCG query2 =", n2)
# Expected output:
# MRR = 0.6666666666666666
# nDCG query1 = 1.0
# nDCG query2 = 0.5
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
Rank-aware metric များသည် reranker ၏ အကျိုးသက်ရောက်မှုကို ပိုမိုတိကျစွာ ဖော်ပြနိုင်သည် — reranker သည် retrieved document အစုကို မပြောင်းလဲဘဲ ranking order ကိုသာ ပြောင်းလဲသောကြောင့် recall@k ဖြင့် ခြားနားချက် မပေါ်နိုင်ပါ။ ထို့အပြင် paper 2104.08663 သည် retrieval evaluation အတွက် BEIR benchmark ကို မိတ်ဆက်ပြီး dataset အမျိုးမျိုးပေါ်တွင် ranking metric များ တိုင်းတာထားသည် (https://arxiv.org/abs/2104.08663)။ Dataset အလိုက် metric တန်ဖိုးများ သိသိသာသာ ကွာခြားနိုင်သည်ကို ဖော်ပြထားခြင်းက benchmark ရွေးချယ်မှု၏ အရေးပါမှုကို ထောက်ပြသည်။

---

## Subtopic 4 — Chunk-level နဲ့ Document-level အကဲဖြတ်မှု

### ဘာကို ဆိုလိုတာလဲ
Chunk-level evaluation သည် golden set ရှိ chunk id များနှင့် retrieved chunk id များကို တိုက်ရိုက် တိုက်စစ်သည်။ Document-level evaluation သည် retrieved result များကို document အဆင့်သို့ map ပြောင်းပြီး relevant document ပါဝင်မှုကို စစ်ဆေးသည်။

### ဘာကြောင့် လဲ
Chunk id များသည် pipeline configuration အပေါ် မူတည်ပြီး မတည်ငြိမ်ပါ — chunk size ပြောင်းလိုက်ရင် chunk id အားလုံး ပြောင်းလဲသွားသဖြင့် chunk-id-based evaluation သည် နှိုင်းယှဉ်မရတော့ပါ။ Document identity ကမူ chunking strategy ပြောင်းလဲမှုကို ခံနိုင်ရည်ရှိသည်။ ထို့ကြောင့် document-level metric သည် ပိုမိုတည်ငြိမ်သော longitudinal measurement ပေးသည်။ Chunk-level က ပိုမိုတိကျပြီး document-level က ပိုမိုခံနိုင်ရည်ရှိသဖြင့် ဂုဏ်သတ္တိနှစ်ရပ် ကွာခြားသည်။

### ဘယ်လို အလုပ်လုပ်လဲ
၁။ Chunk-level — golden set ရှိ chunk id များနှင့် retrieved chunk id များကို တိုက်ရိုက်နှိုင်းယှဉ်သည်။
၂။ Document-level — chunk id များကို document id သို့ map ပြောင်းပြီး နှိုင်းယှဉ်သည်။
၃။ Metric နှစ်မျိုးလုံးကို တွဲဖက်စောင့်ကြည့်သည် — ၎င်းတို့၏ ကွာခြားချက်သည် chunking strategy ၏ အကျိုးသက်ရောက်မှုကို ညွှန်ပြသည်။

### ဥပမာ

```python
# Mapping: chunk id -> document id (would come from the chunking pipeline).
chunk_to_doc = {"c1": "dA", "c2": "dA", "c3": "dB", "c4": "dB", "c9": "dC"}

golden_doc = ["dA", "dB"]              # correct documents
retrieved = ["c1", "c9", "c4"]          # chunk ids from the retriever

# Chunk-level: strict, exact chunk id comparison.
gold_chunks = ["c1", "c2", "c3", "c4"]
chunk_hit = len(set(retrieved) & set(gold_chunks))
print("chunk-level hits:", chunk_hit, "/", len(gold_chunks))

# Document-level: map retrieved chunks to documents, then compare.
retrieved_docs = {chunk_to_doc[c] for c in retrieved}
doc_hit = len(retrieved_docs & set(golden_doc))
print("document-level hits:", doc_hit, "/", len(golden_doc))
# Expected output:
# chunk-level hits: 2 / 4
# document-level hits: 2 / 2
```

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ
Pipeline iteration အတွင်း chunking strategy ပြောင်းလဲမှုသည် မကြာခဏ ဖြစ်ပေါ်လေ့ရှိပြီး၊ chunk-id-based evaluation များ ထိုအခါ အသုံးမဝင်တော့ပါ။ Document-level metric သည် long-horizon comparison အတွက် ပိုမိုသင့်လျော်သော ရွေးချယ်မှုဖြစ်သည်။ လက်တွေ့ production setup အများစုသည် အဆင့်နှစ်မျိုးလုံးကို တွဲဖက်အသုံးပြုလေ့ရှိသည်။

---

## Subtopic 5 — Drift ကြောင့် CI Regression Gate နဲ့ Deterministic LLM Judge

### ဘာကို ဆိုလိုတာလဲ
Regression gate ဆိုသည်မှာ CI pipeline အတွင်း evaluation metric များကို အလိုအလျောက် run ပြီး metric တစ်ခုခု baseline အောက် ကျဆင်းပါက build ကို fail လုပ်သော gate ဖြစ်သည်။ Drift ဆိုသည်မှာ data distribution သို့မဟုတ် model ပြောင်းလဲမှုကြောင့် quality metric များ တဖြည်းဖြည်း ကျဆင်းလာသော ဖြစ်စဉ်ဖြစ်သည်။ LLM judge ဆိုသည်မှာ ရလဒ်များ၏ အရည်အသွေးကို rubric အခြေခံဖြင့် LLM ဖြင့် score ပေးသော နည်းလမ်းဖြစ်သည်။ ဒီသင်ခန်းစာ၏ lab တွင် judge ကို scripted deterministic stand-in ဖြင့် အစားထိုးပြီး scoring mechanism ကို ပြသထားသည်။

### လက်တွေ့မှာ ဘာကြောင့် အရေးကြီးလဲ

Retrieval pipeline ကို measurement မရှိဘဲ ပြောင်းလဲခြင်းသည် မျက်စိမှိတ်၍ ဆုံးဖြတ်ခြင်းနှင့် အတူတူဖြစ်သည်။ Golden set နှင့် recall@k baseline ရှိထားပါက chunking သို့မဟုတ် embedding model ပြောင်းလဲမှုတိုင်း၏ အကျိုးသက်ရောက်မှုကို ဂဏန်းဖြင့် အတိအကျ သိရှိနိုင်သည်။

## အနှစ်ချုပ်

- Golden set သည် query နှင့် relevant chunk id mapping ဖြစ်သည်။
- recall@k သည် relevant chunk များ၏ top-k coverage ကို တိုင်းတာသည်။
- MRR သည် ပထမဆုံး relevant result ၏ rank ကို တိုင်းတာသည်။
- nDCG သည် rank-weighted ranking quality ကို တိုင်းတာသည်။
- Evaluation ကို CI gate အဖြစ် တည်ဆောက်ပြီး regression ကို အလိုအလျောက် detect လုပ်ပါ။
